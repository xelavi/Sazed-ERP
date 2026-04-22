from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    Invoice, InvoiceLine, InvoiceLineTax,
    InvoiceSeries, InvoiceTimeline, Payment, EventLog,
)
from .verifactu import VeriFactuHashService


class InvoiceService:
    """Lógica de negocio para facturas."""

    @staticmethod
    def approve(invoice):
        """Aprueba factura: asigna número, bloquea, snapshot cliente."""
        if invoice.status != 'Draft':
            raise ValidationError('Solo se pueden aprobar borradores.')

        invoice.number = invoice.series.generate_number()
        invoice.status = 'Approved'
        invoice.locked_at = timezone.now()
        invoice.customer_name_snapshot = invoice.customer.name
        invoice.customer_vat_snapshot = invoice.customer.vat_id or ''
        invoice.customer_address_snapshot = {
            'address': invoice.customer.address,
            'city': invoice.customer.city,
            'province': invoice.customer.province,
            'postal_code': invoice.customer.postal_code,
            'country': invoice.customer.country,
        }

        if invoice.total_amount == 0:
            invoice.status = 'Paid'

        invoice.save()

        # ── VeriFactu: sellar la factura (hash encadenado) ──
        VeriFactuHashService.seal(invoice)

        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='approved',
            action=f'Factura {invoice.number} aprobada',
            actor='System',
            date=timezone.now().date(),
        )
        EventLog.objects.create(
            invoice=invoice,
            accion='Alta',
            detalles=(
                f'Factura {invoice.number} aprobada y sellada con '
                f'VeriFactu. Hash: {invoice.hash_actual[:16]}…'
            ),
        )
        return invoice

    @staticmethod
    def void(invoice):
        """Anula factura aprobada sin cobros."""
        if invoice.status != 'Approved':
            raise ValidationError(
                'Solo se pueden anular facturas aprobadas sin cobros.',
            )
        if invoice.payments.exists():
            raise ValidationError(
                'No se puede anular una factura con cobros registrados.',
            )

        invoice.status = 'Voided'
        invoice.balance_due = Decimal('0.00')
        invoice.save(update_fields=['status', 'balance_due'])
        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='voided',
            action=f'Factura {invoice.number} anulada',
            actor='System',
            date=timezone.now().date(),
        )
        return invoice

    @staticmethod
    def record_payment(invoice, payment_data):
        """Registra un cobro en la factura."""
        if invoice.status not in ('Approved', 'PartiallyPaid'):
            raise ValidationError(
                'No se puede registrar cobro en esta factura.',
            )

        amount = min(
            Decimal(str(payment_data['amount'])),
            invoice.balance_due,
        )

        payment = Payment.objects.create(
            invoice=invoice,
            date=payment_data['date'],
            amount=amount,
            method=payment_data.get('method', 'Transfer'),
            reference=payment_data.get('reference'),
            notes=payment_data.get('notes'),
        )

        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='payment',
            action=f'Cobro de {amount} € registrado',
            actor='System',
            date=payment_data['date'],
        )

        return payment

    @staticmethod
    def create_credit_note(invoice):
        """Crea nota de crédito a partir de factura existente."""
        if invoice.status not in ('Approved', 'Paid', 'PartiallyPaid'):
            raise ValidationError(
                'No se puede rectificar esta factura.',
            )

        rec_series = InvoiceSeries.objects.filter(
            prefix='REC', active=True,
        ).first()
        if not rec_series:
            raise ValidationError(
                'No hay serie de rectificativas configurada.',
            )

        credit_note = Invoice.objects.create(
            invoice_type='CreditNote',
            status='Draft',
            series=rec_series,
            customer=invoice.customer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            customer_notes=f'Rectificación de factura {invoice.number}.',
            rectified_invoice=invoice,
        )

        # Copiar líneas con cantidades negativas
        for line in invoice.lines.all():
            new_line = InvoiceLine.objects.create(
                invoice=credit_note,
                position=line.position,
                product=line.product,
                description=f'{line.description} (devolución)',
                quantity=-line.quantity,
                unit_price=line.unit_price,
                discount_type=line.discount_type,
                discount_value=line.discount_value,
            )
            for tax in line.taxes.all():
                InvoiceLineTax.objects.create(
                    invoice_line=new_line,
                    tax_rate=tax.tax_rate,
                    tax_name=tax.tax_name,
                    tax_percent=tax.tax_percent,
                    is_retention=tax.is_retention,
                    tax_amount=-tax.tax_amount,
                )

        credit_note.recalculate_totals()

        # Marcar la original como Rectified
        invoice.status = 'Rectified'
        invoice.save(update_fields=['status'])

        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='rectified',
            action=f'Factura rectificada. Nota de crédito: Draft #{credit_note.id}',
            actor='System',
            date=timezone.now().date(),
        )

        return credit_note

    @staticmethod
    def duplicate(invoice):
        """Duplica factura como nuevo borrador."""
        default_series = InvoiceSeries.objects.filter(
            is_default=True, active=True,
        ).first()

        dup = Invoice.objects.create(
            invoice_type=invoice.invoice_type,
            status='Draft',
            series=default_series or invoice.series,
            customer=invoice.customer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            discount_type=invoice.discount_type,
            discount_value=invoice.discount_value,
            customer_notes=invoice.customer_notes,
            internal_notes=invoice.internal_notes,
        )

        for line in invoice.lines.all():
            new_line = InvoiceLine.objects.create(
                invoice=dup,
                position=line.position,
                product=line.product,
                description=line.description,
                quantity=abs(line.quantity),
                unit_price=line.unit_price,
                discount_type=line.discount_type,
                discount_value=line.discount_value,
            )
            for tax in line.taxes.all():
                InvoiceLineTax.objects.create(
                    invoice_line=new_line,
                    tax_rate=tax.tax_rate,
                    tax_name=tax.tax_name,
                    tax_percent=tax.tax_percent,
                    is_retention=tax.is_retention,
                    tax_amount=abs(tax.tax_amount),
                )

        dup.recalculate_totals()

        InvoiceTimeline.objects.create(
            invoice=dup,
            event_type='created',
            action=f'Duplicado desde {invoice.number or f"Draft #{invoice.id}"}',
            actor='System',
            date=timezone.now().date(),
        )

        return dup
