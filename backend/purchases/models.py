import re
from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class PurchaseSeries(models.Model):
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='purchase_series', null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=10)
    pattern = models.CharField(
        max_length=50, default='{PREFIX}-{YEAR}-{SEQ:4}',
    )
    next_seq = models.IntegerField(default=1)
    reset_yearly = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'purchase series'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f'{self.prefix} — {self.name}'

    def generate_number(self):
        year = date.today().year
        seq_match = re.search(r'\{SEQ:(\d+)\}', self.pattern)
        width = int(seq_match.group(1)) if seq_match else 4

        for _ in range(200):
            candidate = self.pattern.replace('{PREFIX}', self.prefix)
            candidate = candidate.replace('{YEAR}', str(year))
            if seq_match:
                candidate = candidate.replace(
                    seq_match.group(0), str(self.next_seq).zfill(width),
                )
            self.next_seq += 1
            self.save(update_fields=['next_seq'])
            if not PurchaseInvoice.objects.filter(number=candidate).exists():
                return candidate

        raise ValueError('No se pudo generar un número único para la serie %s' % self.prefix)


class PurchaseInvoice(models.Model):
    class InvoiceType(models.TextChoices):
        STANDARD = 'Standard', 'Factura'
        CREDIT_NOTE = 'CreditNote', 'Nota de crédito'

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Borrador'
        APPROVED = 'Approved', 'Aprobada'
        PARTIALLY_PAID = 'PartiallyPaid', 'Parcialmente pagada'
        PAID = 'Paid', 'Pagada'
        VOIDED = 'Voided', 'Anulada'
        RECTIFIED = 'Rectified', 'Rectificada'

    invoice_type = models.CharField(
        max_length=12, choices=InvoiceType.choices, default='Standard',
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default='Draft',
    )

    series = models.ForeignKey(
        PurchaseSeries, on_delete=models.PROTECT, related_name='purchase_invoices',
    )
    number = models.CharField(max_length=30, null=True, blank=True)

    provider = models.ForeignKey(
        'providers.Provider', on_delete=models.PROTECT,
        related_name='purchase_invoices',
    )
    provider_name_snapshot = models.CharField(max_length=200, blank=True)
    provider_vat_snapshot = models.CharField(max_length=20, blank=True)
    provider_address_snapshot = models.JSONField(null=True, blank=True)

    issue_date = models.DateField()
    due_date = models.DateField()

    payment_method = models.CharField(
        max_length=50, default='Transfer 30 days',
    )
    currency = models.CharField(max_length=3, default='EUR')

    discount_type = models.CharField(
        max_length=10, blank=True, null=True,
    )
    discount_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retention = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    paid_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    balance_due = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )

    provider_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    rectified_invoice = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='credit_notes',
    )

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=100, blank=True)

    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['series', 'number'],
                condition=models.Q(number__isnull=False),
                name='unique_purchase_invoice_number_per_series',
            ),
        ]

    def __str__(self):
        return self.number or f'Draft #{self.id}'

    @property
    def is_overdue(self):
        if self.status not in ('Approved', 'PartiallyPaid'):
            return False
        return self.due_date < date.today()

    def recalculate_totals(self):
        lines = self.lines.all()
        self.subtotal = sum(l.subtotal for l in lines)

        if self.discount_type == 'percent' and self.discount_value:
            self.discount_amount = self.subtotal * self.discount_value / 100
        elif self.discount_type == 'fixed' and self.discount_value:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal('0.00')

        self.tax_base = self.subtotal - self.discount_amount

        total_tax = Decimal('0.00')
        total_retention = Decimal('0.00')
        for line in lines:
            for line_tax in line.taxes.all():
                if line_tax.is_retention:
                    total_retention += abs(line_tax.tax_amount)
                else:
                    total_tax += line_tax.tax_amount

        self.total_tax = total_tax
        self.total_retention = total_retention
        self.total_amount = self.tax_base + total_tax - total_retention
        self.balance_due = self.total_amount - self.paid_amount
        self.save()


class PurchaseInvoiceLine(models.Model):
    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, related_name='lines',
    )
    position = models.IntegerField(default=0)
    product = models.ForeignKey(
        'products.Product', null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField()
    quantity = models.DecimalField(
        max_digits=10, decimal_places=3, default=1,
    )
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    discount_type = models.CharField(
        max_length=10, blank=True, null=True,
    )
    discount_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f'Line {self.position}: {self.description[:50]}'

    def save(self, *args, **kwargs):
        gross = self.quantity * self.unit_price
        if self.discount_type == 'percent' and self.discount_value:
            self.discount_amount = gross * self.discount_value / 100
        elif self.discount_type == 'fixed' and self.discount_value:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal('0.00')
        self.subtotal = gross - self.discount_amount
        super().save(*args, **kwargs)


class PurchaseInvoiceLineTax(models.Model):
    invoice_line = models.ForeignKey(
        PurchaseInvoiceLine, on_delete=models.CASCADE, related_name='taxes',
    )
    tax_rate = models.ForeignKey(
        'core.TaxRate', on_delete=models.PROTECT,
    )
    tax_name = models.CharField(max_length=50)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_retention = models.BooleanField(default=False)
    tax_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )

    def __str__(self):
        return f'{self.tax_name} on line {self.invoice_line.position}'


class PurchasePayment(models.Model):
    class Method(models.TextChoices):
        TRANSFER = 'Transfer', 'Transferencia'
        DIRECT_DEBIT = 'DirectDebit', 'Domiciliación'
        CARD = 'Card', 'Tarjeta'
        CASH = 'Cash', 'Efectivo'
        OTHER = 'Other', 'Otro'

    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, related_name='payments',
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(
        max_length=15, choices=Method.choices, default='Transfer',
    )
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Payment {self.amount} on {self.date}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        invoice = self.invoice
        invoice.paid_amount = invoice.payments.aggregate(
            total=Sum('amount'),
        )['total'] or Decimal('0.00')
        invoice.balance_due = invoice.total_amount - invoice.paid_amount
        if invoice.balance_due <= 0:
            invoice.status = 'Paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'PartiallyPaid'
        invoice.save(update_fields=['paid_amount', 'balance_due', 'status'])


class PurchaseInvoiceTimeline(models.Model):
    class EventType(models.TextChoices):
        CREATED = 'created', 'Creado'
        UPDATED = 'updated', 'Actualizado'
        APPROVED = 'approved', 'Aprobado'
        SENT = 'sent', 'Enviado'
        PAYMENT = 'payment', 'Pago'
        PAID = 'paid', 'Pagado'
        VOIDED = 'voided', 'Anulado'
        RECTIFIED = 'rectified', 'Rectificado'

    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, related_name='timeline',
    )
    event_type = models.CharField(
        max_length=20, choices=EventType.choices,
    )
    action = models.CharField(max_length=300)
    actor = models.CharField(max_length=100)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type}: {self.action}'


class PurchaseQuote(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Borrador', 'Borrador'
        SENT = 'Enviado', 'Enviado'
        ACCEPTED = 'Aceptado', 'Aceptado'
        REJECTED = 'Rechazado', 'Rechazado'
        EXPIRED = 'Expirado', 'Expirado'

    provider = models.ForeignKey(
        'providers.Provider', on_delete=models.CASCADE,
        related_name='purchase_quotes',
    )
    number = models.CharField(max_length=30, unique=True)
    concept = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    valid_days = models.IntegerField(default=30)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default='Borrador',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.number} — {self.concept}'
