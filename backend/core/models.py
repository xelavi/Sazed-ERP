from django.db import models


class TaxRate(models.Model):
    """Tipos impositivos configurables (IVA, IGIC, retenciones)."""

    class TaxType(models.TextChoices):
        VAT = 'VAT', 'IVA'
        IGIC = 'IGIC', 'IGIC'
        RETENTION = 'RETENTION', 'Retención'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='tax_rates', null=True, blank=True,
    )
    name = models.CharField(max_length=50)
    tax_type = models.CharField(max_length=20, choices=TaxType.choices, default='VAT')
    percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Etiquetas reutilizables para productos y clientes."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='tags', null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    """Almacenes."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='warehouses', null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SalesChannel(models.Model):
    """Canales de venta: Web, Marketplace, etc."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='sales_channels', null=True, blank=True,
    )
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
