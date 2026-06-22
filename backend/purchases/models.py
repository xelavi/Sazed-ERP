import re
from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class PurchaseInvoice(models.Model):

    class InvoiceType(models.TextChoices):
        STANDARD = 'Standard', 'Factura'
        CREDIT_NOTE = 'CreditNote', 'Nota de crèdit'

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Esborrany'
        APPROVED = 'Approved', 'Aprovada'
        PARTIALLY_PAID = 'PartiallyPaid', 'Parcialment pagada'
        PAID = 'Paid', 'Pagada'
        VOIDED = 'Voided', 'Anul·lada'
        RECTIFIED = 'Rectified', 'Rectificada'

    # Empresa propietària (multitenença directa — no s'infereix via sèrie)
    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='purchase_invoices', null=True, blank=True,
    )

    invoice_type = models.CharField(
        max_length=12, choices=InvoiceType.choices, default='Standard',
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default='Draft',
    )

    # Número introduït manualment (el número del proveïdor, no generat per nosaltres)
    number = models.CharField(max_length=30, null=True, blank=True)

    provider = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='purchase_invoices',
        limit_choices_to={'is_supplier': True},
    )
    provider_name_snapshot = models.CharField(max_length=200, blank=True)
    provider_vat_snapshot = models.CharField(max_length=20, blank=True)
    provider_address_snapshot = models.JSONField(null=True, blank=True)

    issue_date = models.DateField()
    due_date = models.DateField()

    payment_method = models.CharField(max_length=50, default='Transferència 30 dies')
    currency = models.CharField(max_length=3, default='EUR')

    discount_type = models.CharField(max_length=10, blank=True, null=True)
    discount_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retention = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    provider_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    rectified_invoice = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='credit_notes',
    )

    is_template = models.BooleanField(default=False, db_index=True)

    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=100, blank=True)

    # Integració Odoo
    odoo_id = models.PositiveIntegerField(
        null=True, blank=True, db_index=True,
        help_text='ID del account.move (in_invoice) associat a Odoo.',
    )

    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

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
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
    )
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    discount_type = models.CharField(max_length=10, blank=True, null=True)
    discount_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
    tax_rate = models.ForeignKey('core.TaxRate', on_delete=models.PROTECT)
    tax_name = models.CharField(max_length=50)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_retention = models.BooleanField(default=False)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.tax_name} on line {self.invoice_line.position}'


class PurchasePayment(models.Model):

    class Method(models.TextChoices):
        TRANSFER = 'Transfer', 'Transferència'
        DIRECT_DEBIT = 'DirectDebit', 'Domiciliació'
        CARD = 'Card', 'Targeta'
        CASH = 'Cash', 'Efectiu'
        OTHER = 'Other', 'Altre'

    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, related_name='payments',
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=15, choices=Method.choices, default='Transfer')
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
        CREATED = 'created', 'Creat'
        UPDATED = 'updated', 'Actualitzat'
        APPROVED = 'approved', 'Aprovat'
        SENT = 'sent', 'Enviat'
        PAYMENT = 'payment', 'Pagament'
        PAID = 'paid', 'Pagat'
        VOIDED = 'voided', 'Anul·lat'
        RECTIFIED = 'rectified', 'Rectificat'

    invoice = models.ForeignKey(
        PurchaseInvoice, on_delete=models.CASCADE, related_name='timeline',
    )
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    action = models.CharField(max_length=300)
    actor = models.CharField(max_length=100)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type}: {self.action}'


class RecurringPurchaseInvoice(models.Model):
    """Pla de facturació recurrent de compra."""

    from core.recurrence import RecurrenceFrequency

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='recurring_purchase_invoices', null=True, blank=True,
    )
    template = models.ForeignKey(
        PurchaseInvoice, on_delete=models.PROTECT,
        related_name='recurrence_plans',
    )
    frequency = models.CharField(
        max_length=12, choices=RecurrenceFrequency.choices,
        default=RecurrenceFrequency.MONTHLY,
    )
    interval = models.PositiveIntegerField(default=1)
    payment_term_days = models.PositiveIntegerField(default=30)
    start_date = models.DateField()
    next_run = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True)
    max_occurrences = models.PositiveIntegerField(null=True, blank=True)
    occurrences = models.PositiveIntegerField(default=0)
    last_run = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True, db_index=True)

    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-active', 'next_run']

    def __str__(self):
        return f'Recurrència compra {self.get_frequency_display()} — plantilla #{self.template_id}'

    @property
    def is_finished(self):
        if not self.active:
            return True
        if self.end_date and self.next_run > self.end_date:
            return True
        if self.max_occurrences and self.occurrences >= self.max_occurrences:
            return True
        return False


class PurchaseQuoteDoc(models.Model):
    """Pressupost de compra complet (amb línies i conversió a factura)."""

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Esborrany'
        SENT = 'Sent', 'Sol·licitat'
        ACCEPTED = 'Accepted', 'Acceptat'
        REJECTED = 'Rejected', 'Rebutjat'
        EXPIRED = 'Expired', 'Expirat'
        CONVERTED = 'Converted', 'Convertit'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='purchase_quote_docs', null=True, blank=True,
    )
    name = models.CharField(max_length=200)
    provider = models.ForeignKey(
        'customers.Customer',
        on_delete=models.PROTECT,
        related_name='purchase_quote_docs',
        limit_choices_to={'is_supplier': True},
    )
    issue_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default='EUR')
    status = models.CharField(max_length=15, choices=Status.choices, default='Draft')

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    provider_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    converted_invoice = models.ForeignKey(
        PurchaseInvoice, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='source_quotes',
    )

    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return f'PQ-{self.pk} {self.name}'

    def recalculate_totals(self):
        lines = self.lines.all()
        subtotal = Decimal('0.00')
        total_tax = Decimal('0.00')
        for ln in lines:
            subtotal += ln.subtotal
            for lt in ln.taxes.all():
                if not lt.is_retention:
                    total_tax += lt.tax_amount
        self.subtotal = subtotal
        self.total_tax = total_tax
        self.total_amount = subtotal + total_tax
        self.save(update_fields=['subtotal', 'total_tax', 'total_amount'])


class PurchaseQuoteDocLine(models.Model):
    """Línia de pressupost de compra."""

    quote = models.ForeignKey(
        PurchaseQuoteDoc, on_delete=models.CASCADE, related_name='lines',
    )
    position = models.IntegerField(default=0)
    product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
    )
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['position']

    def save(self, *args, **kwargs):
        gross = (self.quantity or Decimal('0')) * (self.unit_price or Decimal('0'))
        self.subtotal = gross.quantize(Decimal('0.01'))
        super().save(*args, **kwargs)


class PurchaseQuoteDocLineTax(models.Model):
    """Impost d'una línia de pressupost de compra (snapshot consistent amb InvoiceLineTax)."""

    quote_line = models.ForeignKey(
        PurchaseQuoteDocLine, on_delete=models.CASCADE, related_name='taxes',
    )
    tax_rate = models.ForeignKey('core.TaxRate', on_delete=models.PROTECT)
    tax_name = models.CharField(max_length=50)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_retention = models.BooleanField(default=False)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.tax_name} on quote line {self.quote_line.position}'
