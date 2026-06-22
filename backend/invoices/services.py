from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import Company
from core.recurrence import add_period
from .models import (
    Invoice, InvoiceLine, InvoiceLineTax,
    InvoiceSeries, InvoiceTimeline, Payment, EventLog,
    RecurringInvoice,
)
from .verifactu import VeriFactuHashService


class InvoiceService:
    """Lógica de negocio para facturas."""

    @staticmethod
    @transaction.atomic
    def approve(invoice):
        """Aprueba factura: asigna número, bloquea, snapshot cliente.

        Usa SELECT FOR UPDATE en dos niveles para serializar aprobaciones
        concurrentes de forma correcta:
          1. Empresa  — serializa la cadena hash VeriFactu entre TODAS las series
                        de la empresa (evita bifurcación si dos series se aprueban
                        en paralelo, ya que la cadena es por empresa según RD 1007/2023).
          2. Serie    — garantiza numeración correlativa sin huecos dentro de la serie.
        El orden empresa → serie es fijo para evitar deadlocks.
        """
        if invoice.status != 'Draft':
            raise ValidationError('Solo se pueden aprobar borradores.')

        # Paso 1: bloquear la empresa (serializa la cadena hash entre todas sus series).
        company_id = InvoiceSeries.objects.values_list('company_id', flat=True).get(pk=invoice.series_id)
        Company.objects.select_for_update().get(pk=company_id)

        # Paso 2: bloquear la serie (garantiza numeración correlativa sin huecos).
        series = InvoiceSeries.objects.select_for_update().get(pk=invoice.series_id)
        invoice.series = series
        invoice.number = series.generate_number()
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


def _clone_invoice_lines(source, target):
    """Copia las líneas e impuestos de una factura a otra."""
    for line in source.lines.all():
        new_line = InvoiceLine.objects.create(
            invoice=target,
            position=line.position,
            product=line.product,
            description=line.description,
            quantity=line.quantity,
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
                tax_amount=tax.tax_amount,
            )


class RecurringInvoiceService:
    """Gestión de facturas recurrentes de venta."""

    @staticmethod
    @transaction.atomic
    def create_plan(source_invoice, data, created_by=''):
        """Crea un plan de recurrencia a partir de una factura existente.

        Duplica la factura origen en una plantilla oculta (is_template=True);
        la factura origen no se modifica.
        """
        template = Invoice.objects.create(
            company=source_invoice.company,
            invoice_type=source_invoice.invoice_type,
            status='Draft',
            is_template=True,
            series=source_invoice.series,
            customer=source_invoice.customer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            payment_method=source_invoice.payment_method,
            currency=source_invoice.currency,
            discount_type=source_invoice.discount_type,
            discount_value=source_invoice.discount_value,
            customer_notes=source_invoice.customer_notes,
            internal_notes=source_invoice.internal_notes,
        )
        _clone_invoice_lines(source_invoice, template)
        template.recalculate_totals()

        start_date = data['start_date']
        plan = RecurringInvoice.objects.create(
            company=source_invoice.company,
            template=template,
            frequency=data['frequency'],
            interval=data.get('interval', 1) or 1,
            payment_term_days=data.get('payment_term_days', 30) or 30,
            start_date=start_date,
            next_run=start_date,
            end_date=data.get('end_date'),
            max_occurrences=data.get('max_occurrences'),
            created_by=created_by,
        )
        return plan

    @staticmethod
    @transaction.atomic
    def generate_one(plan):
        """Genera y aprueba una factura desde la plantilla del plan."""
        template = plan.template
        issue = plan.next_run
        invoice = Invoice.objects.create(
            company=template.company,
            invoice_type=template.invoice_type,
            status='Draft',
            is_template=False,
            series=template.series,
            customer=template.customer,
            issue_date=issue,
            due_date=issue + timedelta(days=plan.payment_term_days),
            payment_method=template.payment_method,
            currency=template.currency,
            discount_type=template.discount_type,
            discount_value=template.discount_value,
            customer_notes=template.customer_notes,
            internal_notes=template.internal_notes,
            created_by='RecurringInvoice',
        )
        _clone_invoice_lines(template, invoice)
        invoice.recalculate_totals()

        InvoiceService.approve(invoice)

        plan.occurrences += 1
        plan.last_run = issue
        plan.next_run = add_period(issue, plan.frequency, plan.interval)
        if plan.is_finished:
            plan.active = False
        plan.save(update_fields=[
            'occurrences', 'last_run', 'next_run', 'active', 'updated_at',
        ])
        return invoice

    @staticmethod
    def generate_due(today=None, company=None):
        """Genera todas las facturas recurrentes pendientes hasta hoy.

        Devuelve la lista de facturas generadas.
        """
        today = today or date.today()
        plans = RecurringInvoice.objects.filter(
            active=True, next_run__lte=today,
        )
        if company is not None:
            plans = plans.filter(company=company)

        generated = []
        for plan in plans.select_related('template'):
            # Un plan puede tener varios vencimientos atrasados; generar todos.
            guard = 0
            while plan.active and plan.next_run <= today and guard < 60:
                generated.append(RecurringInvoiceService.generate_one(plan))
                guard += 1
        return generated
