from decimal import Decimal

from django.db import models
from django.db.models import Min
from django.utils.text import slugify


class Category(models.Model):
    """Categorías de productos."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='categories', null=True, blank=True,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='children',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Producto o servicio del catálogo."""

    class ProductType(models.TextChoices):
        PRODUCT = 'Product', 'Producto'
        SERVICE = 'Service', 'Servicio'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Activo'
        INACTIVE = 'Inactive', 'Inactivo'
        ARCHIVED = 'Archived', 'Archivado'

    class ShippingClass(models.TextChoices):
        STANDARD = 'Standard', 'Standard'
        BULKY = 'Bulky', 'Bulky'
        FRAGILE = 'Fragile', 'Fragile'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='products', null=True, blank=True,
    )

    # Datos principales
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    product_type = models.CharField(
        max_length=10, choices=ProductType.choices, default='Product',
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default='Active',
    )
    unit = models.CharField(max_length=20, default='ud')

    # Categorización
    category = models.ForeignKey(
        Category, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products',
    )
    brand = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField('core.Tag', blank=True, related_name='products')

    # Precios
    price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    price_excl_tax = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    tax_rate = models.ForeignKey(
        'core.TaxRate', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products',
    )
    currency = models.CharField(max_length=3, default='EUR')

    # Inventario
    stock = models.IntegerField(null=True, blank=True)
    reserved = models.IntegerField(default=0)
    min_stock = models.IntegerField(null=True, blank=True)
    reorder_point = models.IntegerField(null=True, blank=True)
    warehouse = models.ForeignKey(
        'core.Warehouse', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='products',
    )
    location = models.CharField(max_length=50, blank=True)
    lot_tracking = models.BooleanField(default=False)

    # Envío
    weight = models.CharField(max_length=30, blank=True)
    dimensions = models.CharField(max_length=50, blank=True)
    shipping_class = models.CharField(
        max_length=20, choices=ShippingClass.choices,
        default='Standard', blank=True,
    )
    digital = models.BooleanField(default=False)

    # Opciones
    sellable = models.BooleanField(default=True)
    purchasable = models.BooleanField(default=True)

    # Canales de venta
    channels = models.ManyToManyField(
        'core.SalesChannel', blank=True, related_name='products',
    )

    # Imagen principal
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Notas
    notes = models.TextField(blank=True)

    # Auditoría
    created_by = models.CharField(max_length=100, blank=True)
    modified_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.sku} — {self.name}'

    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def variants_count(self):
        return self.variants.count()

    @property
    def margin(self):
        if self.price and self.cost and self.price > 0:
            return ((self.price - self.cost) / self.price * 100).quantize(
                Decimal('0.1'),
            )
        return None

    @property
    def price_from(self):
        """Precio mínimo entre variantes."""
        if self.has_variants:
            return self.variants.aggregate(
                min_price=Min('price'),
            )['min_price']
        return None


class ProductImage(models.Model):
    """Galería de imágenes del producto."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='gallery',
    )
    image = models.ImageField(upload_to='products/gallery/')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']


class ProductAttribute(models.Model):
    """Atributos de un producto (Talla, Color, etc.)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='attributes',
    )
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ['product', 'name']

    def __str__(self):
        return f'{self.product.sku} — {self.name}'


class ProductAttributeValue(models.Model):
    """Valores de un atributo (S, M, L, XL)."""

    attribute = models.ForeignKey(
        ProductAttribute, on_delete=models.CASCADE, related_name='values',
    )
    value = models.CharField(max_length=100)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.value


class ProductVariant(models.Model):
    """Variante de producto (combinación de atributos)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants',
    )
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(null=True, blank=True)
    ean = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.sku} — {self.name}'


class PriceList(models.Model):
    """Tarifas de precio por producto."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='price_lists',
    )
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name}: {self.price}'


class ProductSupplier(models.Model):
    """Relación producto-proveedor (N:M con datos adicionales)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='suppliers',
    )
    supplier = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE,
        related_name='supplied_products',
        limit_choices_to={'is_supplier': True},
    )
    supplier_sku = models.CharField(max_length=50, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    lead_time = models.CharField(max_length=30, blank=True)
    min_order = models.IntegerField(default=1)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ['product', 'supplier']

    def __str__(self):
        return f'{self.product.sku} ← {self.supplier.name}'


class StockMovement(models.Model):
    """Movimientos de stock."""

    class MovementType(models.TextChoices):
        IN = 'In', 'Entrada'
        OUT = 'Out', 'Salida'
        ADJUST = 'Adjust', 'Ajuste'
        RETURN = 'Return', 'Devolución'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='stock_movements',
    )
    variant = models.ForeignKey(
        ProductVariant, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='stock_movements',
    )
    movement_type = models.CharField(
        max_length=10, choices=MovementType.choices,
    )
    quantity = models.IntegerField()
    document_ref = models.CharField(max_length=50, blank=True)
    user = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.movement_type} {self.quantity} × {self.product.sku}'


class ReorderRule(models.Model):
    """Regla de reabastecimiento automático por producto y almacén."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reorder_rules',
    )
    warehouse = models.ForeignKey(
        'core.Warehouse', on_delete=models.CASCADE,
        related_name='reorder_rules',
    )
    min_stock = models.IntegerField(
        help_text='Trigger reorder when stock falls to this level.',
    )
    reorder_qty = models.IntegerField(
        help_text='Quantity to reorder.',
    )
    max_stock = models.IntegerField(
        null=True, blank=True,
        help_text='Maximum desired stock level.',
    )
    enabled = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'warehouse']
        ordering = ['product__name']

    def __str__(self):
        return f'{self.product.sku} @ {self.warehouse.name}: min={self.min_stock}'


class ProductAttachment(models.Model):
    """Documentos adjuntos del producto."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='attachments',
    )
    file = models.FileField(upload_to='products/attachments/')
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name
