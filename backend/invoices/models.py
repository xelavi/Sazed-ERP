import re
from datetime import date
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.utils import timezone


class InvoiceSeries(models.Model):
    """Series de numeración de facturas."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='invoice_series', null=True, blank=True,
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
        verbose_name_plural = 'invoice series'
        ordering = ['-is_default', 'name']

    def __str__(self):
        return f'{self.prefix} — {self.name}'

    def generate_number(self):
        """Genera el siguiente número de factura en la serie, saltando los ya usados."""
        year = date.today().year
        seq_match = re.search(r'\{SEQ:(\d+)\}', self.pattern)
        width = int(seq_match.group(1)) if seq_match else 4

        for _ in range(200):  # máximo de intentos por si hay muchos huecos
            candidate = self.pattern.replace('{PREFIX}', self.prefix)
            candidate = candidate.replace('{YEAR}', str(year))
            if seq_match:
                candidate = candidate.replace(
                    seq_match.group(0), str(self.next_seq).zfill(width),
                )
            self.next_seq += 1
            self.save(update_fields=['next_seq'])
            # Saltar si el número ya existe en CUALQUIER factura (constraint global eliminado,
            # pero lo comprobamos para mayor seguridad en caso de colisiones entre series)
            if not Invoice.objects.filter(number=candidate).exists():
                return candidate

        raise ValueError('No se pudo generar un número único para la serie %s' % self.prefix)


class Invoice(models.Model):
    """Factura de venta o nota de crédito."""

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

    # Tipo y estado
    invoice_type = models.CharField(
        max_length=12, choices=InvoiceType.choices, default='Standard',
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default='Draft',
    )

    # Numeración
    series = models.ForeignKey(
        InvoiceSeries, on_delete=models.PROTECT, related_name='invoices',
    )
    number = models.CharField(
        max_length=30, null=True, blank=True,
    )

    # Cliente
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT,
        related_name='invoices',
    )
    # Snapshots al aprobar (inmutabilidad fiscal)
    customer_name_snapshot = models.CharField(max_length=200, blank=True)
    customer_vat_snapshot = models.CharField(max_length=20, blank=True)
    customer_address_snapshot = models.JSONField(null=True, blank=True)

    # Fechas
    issue_date = models.DateField()
    due_date = models.DateField()

    # Condiciones
    payment_method = models.CharField(
        max_length=50, default='Transfer 30 days',
    )
    currency = models.CharField(max_length=3, default='EUR')

    # Descuento global
    discount_type = models.CharField(
        max_length=10, blank=True, null=True,
    )
    discount_value = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )

    # Totales
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

    # Notas
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Rectificativa
    rectified_invoice = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='credit_notes',
    )

    # Bloqueo
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=100, blank=True)

    # ── VeriFactu / AEAT ────────────────────────────────
    class AeatStatus(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        ENVIADO_MOCK = 'Enviado_Mock', 'Enviado (Mock)'
        ACEPTADO = 'Aceptado', 'Aceptado'
        RECHAZADO = 'Rechazado', 'Rechazado'

    hash_anterior = models.CharField(max_length=64, blank=True, default='')
    hash_actual = models.CharField(max_length=64, blank=True, default='')
    estado_aeat = models.CharField(
        max_length=15, choices=AeatStatus.choices,
        default='Pendiente', blank=True,
    )
    fecha_generacion_registro = models.DateTimeField(null=True, blank=True)
    tipo_factura_verifactu = models.CharField(
        max_length=2, blank=True, default='',
        help_text='F1=Ordinaria, R1=Rectificativa (VeriFactu)',
    )
    verifactu_csv = models.CharField(
        max_length=100, blank=True,
        help_text='CSV devuelto por la AEAT al aceptar el registro',
    )

    # Auditoría
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
                name='unique_invoice_number_per_series',
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
        """Recalcula subtotal, impuestos y total desde las líneas."""
        lines = self.lines.all()
        self.subtotal = sum(l.subtotal for l in lines)

        # Descuento global
        if self.discount_type == 'percent' and self.discount_value:
            self.discount_amount = self.subtotal * self.discount_value / 100
        elif self.discount_type == 'fixed' and self.discount_value:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = Decimal('0.00')

        self.tax_base = self.subtotal - self.discount_amount

        # Impuestos por línea
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


class InvoiceLine(models.Model):
    """Línea de factura."""

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='lines',
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


class InvoiceLineTax(models.Model):
    """Impuestos aplicados a una línea de factura."""

    invoice_line = models.ForeignKey(
        InvoiceLine, on_delete=models.CASCADE, related_name='taxes',
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


class Payment(models.Model):
    """Cobros/pagos asociados a una factura."""

    class Method(models.TextChoices):
        TRANSFER = 'Transfer', 'Transferencia'
        DIRECT_DEBIT = 'DirectDebit', 'Domiciliación'
        CARD = 'Card', 'Tarjeta'
        CASH = 'Cash', 'Efectivo'
        OTHER = 'Other', 'Otro'

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='payments',
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
        # Recalcular pagados en la factura
        invoice = self.invoice
        invoice.paid_amount = invoice.payments.aggregate(
            total=Sum('amount'),
        )['total'] or Decimal('0.00')
        invoice.balance_due = invoice.total_amount - invoice.paid_amount
        # Actualizar estado
        if invoice.balance_due <= 0:
            invoice.status = 'Paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'PartiallyPaid'
        invoice.save(update_fields=['paid_amount', 'balance_due', 'status'])


class InvoiceTimeline(models.Model):
    """Historial de eventos de una factura (audit log simplificado)."""

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
        Invoice, on_delete=models.CASCADE, related_name='timeline',
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


class EventLog(models.Model):
    """Registro de auditoría de acciones sobre facturas (VeriFactu / AEAT)."""

    class Action(models.TextChoices):
        ALTA = 'Alta', 'Alta de factura'
        INTENTO_MODIFICACION = 'Intento_Modificacion', 'Intento de modificación'
        INTENTO_BORRADO = 'Intento_Borrado', 'Intento de borrado'
        ENVIO_AEAT = 'Envio_AEAT', 'Envío a AEAT'
        ACEPTADO_AEAT = 'Aceptado_AEAT', 'Aceptado por AEAT'
        RECHAZADO_AEAT = 'Rechazado_AEAT', 'Rechazado por AEAT'
        GENERACION_PDF = 'Generacion_PDF', 'Generación de PDF'

    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE,
        related_name='event_logs', null=True, blank=True,
    )
    usuario = models.CharField(max_length=100, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=30, choices=Action.choices)
    detalles = models.TextField(blank=True)
    ip = models.CharField(max_length=45, blank=True)

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f'[{self.fecha_hora:%Y-%m-%d %H:%M}] {self.accion} — {self.usuario}'
