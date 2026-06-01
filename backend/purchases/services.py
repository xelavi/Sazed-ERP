from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.recurrence import add_period
from .models import (
    PurchaseInvoice, PurchaseInvoiceLine, PurchaseInvoiceLineTax,
    PurchaseSeries, PurchaseInvoiceTimeline, PurchasePayment,
    RecurringPurchaseInvoice,
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


def _clone_purchase_lines(source, target):
    """Copia las líneas e impuestos de una factura de compra a otra."""
    for line in source.lines.all():
        new_line = PurchaseInvoiceLine.objects.create(
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
            PurchaseInvoiceLineTax.objects.create(
                invoice_line=new_line,
                tax_rate=tax.tax_rate,
                tax_name=tax.tax_name,
                tax_percent=tax.tax_percent,
                is_retention=tax.is_retention,
                tax_amount=tax.tax_amount,
            )


class RecurringPurchaseInvoiceService:
    """Gestión de facturas recurrentes de compra."""

    @staticmethod
    @transaction.atomic
    def create_plan(source_invoice, data, created_by=''):
        template = PurchaseInvoice.objects.create(
            invoice_type=source_invoice.invoice_type,
            status='Draft',
            is_template=True,
            series=source_invoice.series,
            provider=source_invoice.provider,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            payment_method=source_invoice.payment_method,
            currency=source_invoice.currency,
            discount_type=source_invoice.discount_type,
            discount_value=source_invoice.discount_value,
            provider_notes=source_invoice.provider_notes,
            internal_notes=source_invoice.internal_notes,
        )
        _clone_purchase_lines(source_invoice, template)
        template.recalculate_totals()

        start_date = data['start_date']
        plan = RecurringPurchaseInvoice.objects.create(
            company=getattr(source_invoice.series, 'company', None),
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
        template = plan.template
        issue = plan.next_run
        invoice = PurchaseInvoice.objects.create(
            invoice_type=template.invoice_type,
            status='Draft',
            is_template=False,
            series=template.series,
            provider=template.provider,
            issue_date=issue,
            due_date=issue + timedelta(days=plan.payment_term_days),
            payment_method=template.payment_method,
            currency=template.currency,
            discount_type=template.discount_type,
            discount_value=template.discount_value,
            provider_notes=template.provider_notes,
            internal_notes=template.internal_notes,
            created_by='RecurringPurchaseInvoice',
        )
        _clone_purchase_lines(template, invoice)
        invoice.recalculate_totals()

        PurchaseInvoiceService.approve(invoice)

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
        today = today or date.today()
        plans = RecurringPurchaseInvoice.objects.filter(
            active=True, next_run__lte=today,
        )
        if company is not None:
            plans = plans.filter(company=company)

        generated = []
        for plan in plans.select_related('template'):
            guard = 0
            while plan.active and plan.next_run <= today and guard < 60:
                generated.append(
                    RecurringPurchaseInvoiceService.generate_one(plan),
                )
                guard += 1
        return generated
