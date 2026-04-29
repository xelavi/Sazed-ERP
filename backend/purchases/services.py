from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    PurchaseInvoice, PurchaseInvoiceLine, PurchaseInvoiceLineTax,
    PurchaseSeries, PurchaseInvoiceTimeline, PurchasePayment,
)


class PurchaseInvoiceService:

    @staticmethod
    def approve(invoice):
        if invoice.status != 'Draft':
            raise ValidationError('Solo se pueden aprobar borradores.')

        invoice.number = invoice.series.generate_number()
        invoice.status = 'Approved'
        invoice.locked_at = timezone.now()
        invoice.provider_name_snapshot = invoice.provider.name
        invoice.provider_vat_snapshot = invoice.provider.vat_id or ''
        invoice.provider_address_snapshot = {
            'address': invoice.provider.address,
            'city': invoice.provider.city,
            'province': invoice.provider.province,
            'postal_code': invoice.provider.postal_code,
            'country': invoice.provider.country,
        }

        if invoice.total_amount == 0:
            invoice.status = 'Paid'

        invoice.save()

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='approved',
            action=f'Factura de compra {invoice.number} aprobada',
            actor='System',
            date=timezone.now().date(),
        )
        return invoice

    @staticmethod
    def void(invoice):
        if invoice.status != 'Approved':
            raise ValidationError(
                'Solo se pueden anular facturas aprobadas sin pagos.',
            )
        if invoice.payments.exists():
            raise ValidationError(
                'No se puede anular una factura con pagos registrados.',
            )

        invoice.status = 'Voided'
        invoice.balance_due = Decimal('0.00')
        invoice.save(update_fields=['status', 'balance_due'])
        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='voided',
            action=f'Factura de compra {invoice.number} anulada',
            actor='System',
            date=timezone.now().date(),
        )
        return invoice

    @staticmethod
    def record_payment(invoice, payment_data):
        if invoice.status not in ('Approved', 'PartiallyPaid'):
            raise ValidationError(
                'No se puede registrar pago en esta factura.',
            )

        amount = min(
            Decimal(str(payment_data['amount'])),
            invoice.balance_due,
        )

        payment = PurchasePayment.objects.create(
            invoice=invoice,
            date=payment_data['date'],
            amount=amount,
            method=payment_data.get('method', 'Transfer'),
            reference=payment_data.get('reference'),
            notes=payment_data.get('notes'),
        )

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='payment',
            action=f'Pago de {amount} € registrado',
            actor='System',
            date=payment_data['date'],
        )

        return payment

    @staticmethod
    def create_credit_note(invoice):
        if invoice.status not in ('Approved', 'Paid', 'PartiallyPaid'):
            raise ValidationError(
                'No se puede rectificar esta factura.',
            )

        rec_series = PurchaseSeries.objects.filter(
            prefix='PREC', active=True,
        ).first()
        if not rec_series:
            rec_series = PurchaseSeries.objects.filter(active=True).first()
        if not rec_series:
            raise ValidationError(
                'No hay serie de rectificativas de compra configurada.',
            )

        credit_note = PurchaseInvoice.objects.create(
            invoice_type='CreditNote',
            status='Draft',
            series=rec_series,
            provider=invoice.provider,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            provider_notes=f'Rectificación de factura {invoice.number}.',
            rectified_invoice=invoice,
        )

        for line in invoice.lines.all():
            new_line = PurchaseInvoiceLine.objects.create(
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
                PurchaseInvoiceLineTax.objects.create(
                    invoice_line=new_line,
                    tax_rate=tax.tax_rate,
                    tax_name=tax.tax_name,
                    tax_percent=tax.tax_percent,
                    is_retention=tax.is_retention,
                    tax_amount=-tax.tax_amount,
                )

        credit_note.recalculate_totals()

        invoice.status = 'Rectified'
        invoice.save(update_fields=['status'])

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='rectified',
            action=f'Factura rectificada. Nota de crédito: Draft #{credit_note.id}',
            actor='System',
            date=timezone.now().date(),
        )

        return credit_note

    @staticmethod
    def duplicate(invoice):
        default_series = PurchaseSeries.objects.filter(
            is_default=True, active=True,
        ).first()

        dup = PurchaseInvoice.objects.create(
            invoice_type=invoice.invoice_type,
            status='Draft',
            series=default_series or invoice.series,
            provider=invoice.provider,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            discount_type=invoice.discount_type,
            discount_value=invoice.discount_value,
            provider_notes=invoice.provider_notes,
            internal_notes=invoice.internal_notes,
        )

        for line in invoice.lines.all():
            new_line = PurchaseInvoiceLine.objects.create(
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
                PurchaseInvoiceLineTax.objects.create(
                    invoice_line=new_line,
                    tax_rate=tax.tax_rate,
                    tax_name=tax.tax_name,
                    tax_percent=tax.tax_percent,
                    is_retention=tax.is_retention,
                    tax_amount=abs(tax.tax_amount),
                )

        dup.recalculate_totals()

        PurchaseInvoiceTimeline.objects.create(
            invoice=dup,
            event_type='created',
            action=f'Duplicado desde {invoice.number or f"Draft #{invoice.id}"}',
            actor='System',
            date=timezone.now().date(),
        )

        return dup
