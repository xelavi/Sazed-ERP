# Diseño del Backend — Django + PostgreSQL

> **Fecha:** 2026-04-08
> **Proyecto:** Sazed ERP (TFG)
> **Stack:** Django 5.x + Django REST Framework + PostgreSQL 16
> **Frontend:** Vue 3 SPA (ya implementada)

---

## 1. Resumen ejecutivo

Este documento define la arquitectura completa del backend que dará persistencia y lógica de negocio al ERP. Se ha realizado mediante ingeniería inversa del frontend existente, identificando cada estructura de datos hardcodeada en los componentes Vue y traduciéndola a modelos Django con sus relaciones, validaciones, endpoints API y lógica de dominio.

---

## 2. Estructura de datos identificada en el frontend

### 2.1 Módulo de Productos (`Products.vue` + `ProductFormModal.vue` + `ProductDetailDrawer.vue`)

**Campos de la tabla (nivel superior):**
| Campo frontend | Tipo | Descripción |
|---|---|---|
| `id` | int | Identificador |
| `sku` | string | Código único de producto |
| `name` | string | Nombre del producto |
| `status` | enum | `Active`, `Inactive`, `Archived` |
| `type` | enum | `Product`, `Service` |
| `category` | string | Categoría (Clothing, Footwear, etc.) |
| `stock` | int/null | Stock actual (null para servicios) |
| `reserved` | int/null | Stock reservado |
| `price` | decimal | PVP (precio de venta con impuestos) |
| `priceFrom` | decimal/null | Precio mínimo si hay variantes |
| `hasVariants` | bool | Tiene variantes |
| `variantsCount` | int | Nº de variantes |
| `cost` | decimal | Coste medio |
| `tax` | string | Impuesto aplicable ("21% IVA") |
| `supplier` | string/null | Proveedor principal |
| `channels` | array[string] | Canales de venta: `Web`, `Marketplace` |
| `updatedAt` | datetime | Última actualización |
| `image` | string/null | URL de imagen principal |

**Campos del detalle (`product.detail`):**
| Campo | Tipo | Descripción |
|---|---|---|
| `description` | text | Descripción larga |
| `tags` | array[string] | Etiquetas |
| `unit` | string | Unidad de medida (ud, kg, hora, pair, project) |
| `sellable` | bool | Se puede vender |
| `purchasable` | bool | Se puede comprar |
| `brand` | string/null | Marca |
| `gallery` | array[string] | Imágenes adicionales |
| `priceExclTax` | decimal | Precio sin impuestos |
| `currency` | string | Divisa (EUR) |
| `priceLists` | array[object] | Tarifas: {name, price, from, to} |
| `minStock` | int/null | Stock mínimo |
| `reorderPoint` | int/null | Punto de pedido |
| `warehouse` | string | Almacén |
| `location` | string/null | Ubicación dentro del almacén |
| `lotTracking` | bool | Seguimiento por lotes |
| `stockMovements` | array[object] | Movimientos: {date, type, document, qty, user} |
| `attributes` | array[object] | Atributos: {name, values[]} |
| `variants` | array[object] | Variantes: {name, sku, price, stock, ean} |
| `suppliers` | array[object] | Proveedores: {name, sku, price, leadTime, minOrder, primary} |
| `recentSales` | array[object] | Ventas: {document, customer, date, qty, unitPrice, total} |
| `returns` | array[object] | Devoluciones: {document, customer, date, qty, reason} |
| `relatedProducts` | array[string] | Productos relacionados |
| `weight` | string/null | Peso |
| `dimensions` | string/null | Dimensiones |
| `shippingClass` | string/null | Clase de envío (Standard, Bulky, Fragile) |
| `digital` | bool | Es producto digital |
| `attachments` | array[object] | Adjuntos: {name, size} |
| `notes` | text | Notas internas |
| `createdBy` | string | Creador |
| `createdAt` | string | Fecha creación |
| `modifiedBy` | string | Último editor |

### 2.2 Módulo de Clientes (`Customers.vue` + `CustomerFormModal.vue` + `CustomerDetailDrawer.vue`)

**Campos de la tabla (nivel superior):**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | int | Identificador |
| `name` | string | Nombre |
| `type` | enum | `Company`, `Person` |
| `email` | string | Email de contacto |
| `city` | string | Ciudad |
| `status` | enum | `Active`, `Inactive` |
| `vatId` | string/null | NIF/CIF |
| `avatarColor` | string | Gradiente CSS para avatar |
| `initials` | string | Iniciales para avatar |
| `linked` | array[string] | Contactos vinculados (nombres) |

**Campos del detalle (`customer.detail`):**
| Campo | Tipo | Descripción |
|---|---|---|
| `phone` | string | Teléfono |
| `website` | string | Web |
| `address` | string | Dirección fiscal |
| `province` | string | Provincia |
| `postalCode` | string | Código postal |
| `country` | string | País |
| `legalName` | string | Razón social |
| `paymentMethod` | string | Forma de pago por defecto |
| `bankAccount` | string | IBAN |
| `internalNotes` | text | Notas internas |
| `tags` | array[string] | Etiquetas |
| `isCustomer` | bool | Es cliente |
| `isSupplier` | bool | Es proveedor |
| `totalInvoiced` | decimal | Total facturado (calculado) |
| `pendingBalance` | decimal | Saldo pendiente (calculado) |
| `totalDocuments` | int | Nº documentos (calculado) |
| `notes` | array[object] | Notas: {id, date, author, content} |
| `quotes` | array[object] | Presupuestos: {id, number, concept, amount, date, validDays, notes, status} |
| `invoices` | array[object] | Facturas: {id, number, date, amount, status} |
| `activities` | array[object] | Actividades CRM: {id, type, date, subject, notes} |
| `purchases` | array[object] | Compras: {id, product, amount, date, quantity, status} |

### 2.3 Módulo de Facturas (`Invoices.vue` + `InvoiceFormModal.vue` + `InvoiceDetailDrawer.vue`)

**Campos principales:**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | int | Identificador |
| `type` | enum | `Standard`, `CreditNote` |
| `status` | enum | `Draft`, `Approved`, `PartiallyPaid`, `Paid`, `Voided`, `Rectified` |
| `series` | string | Serie: `FAC`, `SRV`, `REC` |
| `number` | string/null | Nº factura (null en borrador) |
| `customer` | object | Snapshot: {id, name, vatId, email, avatarColor, initials} |
| `issueDate` | date | Fecha de emisión |
| `dueDate` | date | Fecha de vencimiento |
| `paymentMethod` | string | Forma de pago |
| `currency` | string | Divisa |
| `lines` | array[object] | Líneas: {id, description, quantity, unitPrice, discount, tax, subtotal} |
| `subtotal` | decimal | Subtotal |
| `discountAmount` | decimal | Descuento global |
| `taxSummary` | array[object] | Resumen impuestos: {name, base, amount, isRetention} |
| `totalTax` | decimal | Total impuestos |
| `totalAmount` | decimal | Total factura |
| `paidAmount` | decimal | Total cobrado |
| `balanceDue` | decimal | Saldo pendiente |
| `payments` | array[object] | Cobros: {id, date, amount, method, reference} |
| `customerNotes` | text | Notas para el cliente (PDF) |
| `internalNotes` | text | Notas internas |
| `lockedAt` | datetime/null | Momento de aprobación |
| `timeline` | array[object] | Historial: {type, action, actor, date} |

### 2.4 Módulo Dashboard (`Home.vue`)

**Tareas (tasks):**
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador |
| `title` | string | Título de la tarea |
| `completed` | bool | Estado completado |
| `tags` | array[object] | Tags: {label, colorClass} |
| `dueDate` | string | Fecha límite |
| `status` | enum | `upcoming`, `overdue`, `completed` |

### 2.5 Módulo Wallet (`Wallet.vue`)

El wallet actualmente es estático y no maneja datos. Los datos se derivarán de:
- Saldo disponible: suma de pagos recibidos
- Saldo pendiente: balance de facturas aprobadas
- Pagos recientes: últimos registros de Payment

---

## 3. Diseño de modelos Django

### 3.1 App `core` — Modelos base y configuración

```python
# core/models.py

class TaxRate(models.Model):
    """Tipos impositivos configurables."""
    class TaxType(models.TextChoices):
        VAT = 'VAT', 'IVA'
        IGIC = 'IGIC', 'IGIC'
        RETENTION = 'RETENTION', 'Retención'

    name = models.CharField(max_length=50)               # "IVA 21%", "IRPF -15%"
    tax_type = models.CharField(max_length=20, choices=TaxType.choices)
    percent = models.DecimalField(max_digits=5, decimal_places=2)  # Negativo para retenciones
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    """Etiquetas reutilizables para productos y clientes."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Warehouse(models.Model):
    """Almacenes."""
    name = models.CharField(max_length=100)               # "Warehouse Madrid"
    address = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SalesChannel(models.Model):
    """Canales de venta: Web, Marketplace, etc."""
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)
```

### 3.2 App `customers` — CRM y contactos

```python
# customers/models.py

class Customer(models.Model):
    """Contacto (cliente y/o proveedor)."""
    class ContactType(models.TextChoices):
        COMPANY = 'Company', 'Empresa'
        PERSON = 'Person', 'Persona'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Activo'
        INACTIVE = 'Inactive', 'Inactivo'

    # Datos principales
    name = models.CharField(max_length=200)
    contact_type = models.CharField(max_length=10, choices=ContactType.choices)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default='Active')

    # Identificación fiscal
    vat_id = models.CharField(max_length=20, blank=True, null=True)  # NIF/CIF
    legal_name = models.CharField(max_length=200, blank=True)        # Razón social

    # Dirección fiscal
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='España')

    # Opciones comerciales
    payment_method = models.CharField(max_length=50, blank=True, default='Transferencia 30 días')
    bank_account = models.CharField(max_length=34, blank=True)  # IBAN
    is_customer = models.BooleanField(default=True)
    is_supplier = models.BooleanField(default=False)

    # Visual
    avatar_color = models.CharField(max_length=200, blank=True)  # CSS gradient
    initials = models.CharField(max_length=4, blank=True)

    # Notas
    internal_notes = models.TextField(blank=True)

    # Etiquetas
    tags = models.ManyToManyField('core.Tag', blank=True, related_name='customers')

    # Contactos vinculados (relación M2M consigo mismo)
    linked_contacts = models.ManyToManyField('self', blank=True, symmetrical=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_invoiced(self):
        """Suma total de facturas pagadas/aprobadas de este cliente."""
        return self.invoices.exclude(
            status__in=['Draft', 'Voided', 'Deleted']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    @property
    def pending_balance(self):
        """Saldo pendiente de cobro."""
        return self.invoices.filter(
            status__in=['Approved', 'PartiallyPaid']
        ).aggregate(total=Sum('balance_due'))['total'] or Decimal('0.00')


class CustomerNote(models.Model):
    """Notas asociadas a un cliente."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    author = models.CharField(max_length=100)  # Futuro: FK a User
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class CustomerActivity(models.Model):
    """Actividades CRM: reuniones, llamadas, emails, visitas."""
    class ActivityType(models.TextChoices):
        MEETING = 'Reunión', 'Reunión'
        CALL = 'Llamada', 'Llamada'
        EMAIL = 'Email', 'Email'
        VISIT = 'Visita', 'Visita'
        OTHER = 'Otro', 'Otro'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    date = models.DateField()
    subject = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']


class Quote(models.Model):
    """Presupuestos asociados a un cliente."""
    class Status(models.TextChoices):
        DRAFT = 'Borrador', 'Borrador'
        SENT = 'Enviado', 'Enviado'
        ACCEPTED = 'Aceptado', 'Aceptado'
        REJECTED = 'Rechazado', 'Rechazado'
        EXPIRED = 'Expirado', 'Expirado'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='quotes')
    number = models.CharField(max_length=30, unique=True)
    concept = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    valid_days = models.IntegerField(default=30)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default='Borrador')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
```

### 3.3 App `products` — Catálogo y stock

```python
# products/models.py

class Category(models.Model):
    """Categorías de productos."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']


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

    # Datos principales
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=10, choices=ProductType.choices, default='Product')
    status = models.CharField(max_length=10, choices=Status.choices, default='Active')
    unit = models.CharField(max_length=20, default='ud')  # ud, kg, hora, pair, project

    # Categorización
    category = models.ForeignKey(Category, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='products')
    brand = models.CharField(max_length=100, blank=True)
    tags = models.ManyToManyField('core.Tag', blank=True, related_name='products')

    # Precios
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # PVP
    price_excl_tax = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate = models.ForeignKey('core.TaxRate', null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='products')
    currency = models.CharField(max_length=3, default='EUR')

    # Inventario
    stock = models.IntegerField(null=True, blank=True)     # null para servicios
    reserved = models.IntegerField(default=0)
    min_stock = models.IntegerField(null=True, blank=True)
    reorder_point = models.IntegerField(null=True, blank=True)
    warehouse = models.ForeignKey('core.Warehouse', null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name='products')
    location = models.CharField(max_length=50, blank=True)  # Ej: "A-12-03"
    lot_tracking = models.BooleanField(default=False)

    # Envío
    weight = models.CharField(max_length=30, blank=True)     # "0.18 kg"
    dimensions = models.CharField(max_length=50, blank=True)  # "30 × 25 × 2 cm"
    shipping_class = models.CharField(max_length=20, choices=ShippingClass.choices,
                                      default='Standard', blank=True)
    digital = models.BooleanField(default=False)

    # Opciones
    sellable = models.BooleanField(default=True)
    purchasable = models.BooleanField(default=True)

    # Canales de venta
    channels = models.ManyToManyField('core.SalesChannel', blank=True, related_name='products')

    # Imagen principal
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Notas
    notes = models.TextField(blank=True)

    # Auditoría
    created_by = models.CharField(max_length=100, blank=True)  # Futuro: FK a User
    modified_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.sku} — {self.name}"

    @property
    def has_variants(self):
        return self.variants.exists()

    @property
    def variants_count(self):
        return self.variants.count()

    @property
    def margin(self):
        if self.price and self.cost and self.price > 0:
            return ((self.price - self.cost) / self.price * 100).quantize(Decimal('0.1'))
        return None

    @property
    def price_from(self):
        """Precio mínimo entre variantes."""
        if self.has_variants:
            return self.variants.aggregate(min_price=Min('price'))['min_price']
        return None


class ProductImage(models.Model):
    """Galería de imágenes del producto."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position']


class ProductAttribute(models.Model):
    """Atributos de un producto (Talla, Color, etc.)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=50)    # "Size", "Color"

    class Meta:
        unique_together = ['product', 'name']


class ProductAttributeValue(models.Model):
    """Valores de un atributo (S, M, L, XL)."""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)  # "S", "M", "Black"
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ['position']


class ProductVariant(models.Model):
    """Variante de producto (combinación de atributos)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=200)          # "S / White"
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.IntegerField(null=True, blank=True)
    ean = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['name']


class PriceList(models.Model):
    """Tarifas de precio por producto."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_lists')
    name = models.CharField(max_length=50)    # "Retail", "Wholesale", "HoReCa"
    price = models.DecimalField(max_digits=12, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']


class ProductSupplier(models.Model):
    """Relación producto-proveedor (N:M con datos adicionales)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='suppliers')
    supplier = models.ForeignKey('customers.Customer', on_delete=models.CASCADE,
                                 related_name='supplied_products',
                                 limit_choices_to={'is_supplier': True})
    supplier_sku = models.CharField(max_length=50, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    lead_time = models.CharField(max_length=30, blank=True)    # "7 days"
    min_order = models.IntegerField(default=1)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ['product', 'supplier']


class StockMovement(models.Model):
    """Movimientos de stock."""
    class MovementType(models.TextChoices):
        IN = 'In', 'Entrada'
        OUT = 'Out', 'Salida'
        ADJUST = 'Adjust', 'Ajuste'
        RETURN = 'Return', 'Devolución'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    variant = models.ForeignKey(ProductVariant, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='stock_movements')
    movement_type = models.CharField(max_length=10, choices=MovementType.choices)
    quantity = models.IntegerField()  # Positivo para entradas, negativo para salidas
    document_ref = models.CharField(max_length=50, blank=True)  # "SO-2045", "PO-1120"
    user = models.CharField(max_length=100, blank=True)         # Futuro: FK a User
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ProductAttachment(models.Model):
    """Documentos adjuntos del producto."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='products/attachments/')
    file_name = models.CharField(max_length=200)
    file_size = models.IntegerField()  # Bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

### 3.4 App `invoices` — Facturación

```python
# invoices/models.py

class InvoiceSeries(models.Model):
    """Series de numeración de facturas."""
    name = models.CharField(max_length=100)         # "Facturas generales"
    prefix = models.CharField(max_length=10)        # "FAC"
    pattern = models.CharField(max_length=50,
                               default='{PREFIX}-{YEAR}-{SEQ:4}')
    next_seq = models.IntegerField(default=1)
    reset_yearly = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'invoice series'

    def generate_number(self):
        """Genera el siguiente número de factura en la serie."""
        import datetime
        year = datetime.date.today().year
        number = self.pattern.replace('{PREFIX}', self.prefix)
        number = number.replace('{YEAR}', str(year))
        seq_match = re.search(r'\{SEQ:(\d+)\}', number)
        if seq_match:
            width = int(seq_match.group(1))
            number = number.replace(seq_match.group(0), str(self.next_seq).zfill(width))
        self.next_seq += 1
        self.save(update_fields=['next_seq'])
        return number


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
    invoice_type = models.CharField(max_length=12, choices=InvoiceType.choices, default='Standard')
    status = models.CharField(max_length=15, choices=Status.choices, default='Draft')

    # Numeración
    series = models.ForeignKey(InvoiceSeries, on_delete=models.PROTECT, related_name='invoices')
    number = models.CharField(max_length=30, null=True, blank=True, unique=True)

    # Cliente
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT,
                                 related_name='invoices')
    # Snapshots al aprobar (inmutabilidad fiscal)
    customer_name_snapshot = models.CharField(max_length=200, blank=True)
    customer_vat_snapshot = models.CharField(max_length=20, blank=True)
    customer_address_snapshot = models.JSONField(null=True, blank=True)

    # Fechas
    issue_date = models.DateField()
    due_date = models.DateField()

    # Condiciones
    payment_method = models.CharField(max_length=50, default='Transfer 30 days')
    currency = models.CharField(max_length=3, default='EUR')

    # Descuento global
    discount_type = models.CharField(max_length=10, blank=True, null=True)  # 'percent' o 'fixed'
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retention = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Notas
    customer_notes = models.TextField(blank=True)   # Visible en PDF
    internal_notes = models.TextField(blank=True)   # Solo interno

    # Rectificativa
    rectified_invoice = models.ForeignKey('self', null=True, blank=True,
                                          on_delete=models.SET_NULL,
                                          related_name='credit_notes')

    # Bloqueo
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.CharField(max_length=100, blank=True)  # Futuro: FK a User

    # Auditoría
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return self.number or f"Draft #{self.id}"

    @property
    def is_overdue(self):
        from datetime import date
        if self.status not in ['Approved', 'PartiallyPaid']:
            return False
        return self.due_date < date.today()

    def approve(self):
        """Aprueba la factura: asigna número, bloquea y crea snapshot."""
        if self.status != 'Draft':
            raise ValueError('Solo se pueden aprobar borradores.')
        self.number = self.series.generate_number()
        self.status = 'Approved'
        self.locked_at = timezone.now()
        # Snapshot del cliente
        self.customer_name_snapshot = self.customer.name
        self.customer_vat_snapshot = self.customer.vat_id or ''
        self.customer_address_snapshot = {
            'address': self.customer.address,
            'city': self.customer.city,
            'province': self.customer.province,
            'postal_code': self.customer.postal_code,
            'country': self.customer.country,
        }
        self.save()

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
            self.discount_amount = 0

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
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='lines')
    position = models.IntegerField(default=0)
    product = models.ForeignKey('products.Product', null=True, blank=True,
                                on_delete=models.SET_NULL)
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4)
    discount_type = models.CharField(max_length=10, blank=True, null=True)
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['position']

    def save(self, *args, **kwargs):
        gross = self.quantity * self.unit_price
        if self.discount_type == 'percent' and self.discount_value:
            self.discount_amount = gross * self.discount_value / 100
        elif self.discount_type == 'fixed' and self.discount_value:
            self.discount_amount = self.discount_value
        else:
            self.discount_amount = 0
        self.subtotal = gross - self.discount_amount
        super().save(*args, **kwargs)


class InvoiceLineTax(models.Model):
    """Impuestos aplicados a una línea de factura."""
    invoice_line = models.ForeignKey(InvoiceLine, on_delete=models.CASCADE, related_name='taxes')
    tax_rate = models.ForeignKey('core.TaxRate', on_delete=models.PROTECT)
    tax_name = models.CharField(max_length=50)        # Snapshot: "IVA 21%"
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_retention = models.BooleanField(default=False)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class Payment(models.Model):
    """Cobros/pagos asociados a una factura."""
    class Method(models.TextChoices):
        TRANSFER = 'Transfer', 'Transferencia'
        DIRECT_DEBIT = 'DirectDebit', 'Domiciliación'
        CARD = 'Card', 'Tarjeta'
        CASH = 'Cash', 'Efectivo'
        OTHER = 'Other', 'Otro'

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=15, choices=Method.choices, default='Transfer')
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalcular pagados en la factura
        invoice = self.invoice
        invoice.paid_amount = invoice.payments.aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
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

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='timeline')
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    action = models.CharField(max_length=300)   # Texto descriptivo
    actor = models.CharField(max_length=100)    # Futuro: FK a User
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
```

### 3.5 App `tasks` — Tareas del Dashboard

```python
# tasks/models.py

class TaskTag(models.Model):
    """Etiqueta de tarea con color."""
    label = models.CharField(max_length=50)
    color_class = models.CharField(max_length=30)  # "tag-purple", "tag-red", etc.

class Task(models.Model):
    """Tarea personal del dashboard."""
    class Status(models.TextChoices):
        UPCOMING = 'upcoming', 'Próxima'
        OVERDUE = 'overdue', 'Vencida'
        COMPLETED = 'completed', 'Completada'

    title = models.CharField(max_length=300)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(TaskTag, blank=True, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default='upcoming')
    # Futuro: assigned_to = FK a User
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
```

---

## 4. Diagrama de relaciones (ER)

```
┌──────────────┐      ┌──────────────────┐
│   TaxRate    │      │    Warehouse     │
│              │      │                  │
└───────┬──────┘      └────────┬─────────┘
        │                      │
        │                      │
┌───────┴──────────────────────┴───────────────────┐
│                    Product                        │
│  sku, name, description, type, status, unit       │
│  price, cost, stock, reserved, min_stock          │
│  sellable, purchasable, digital, lot_tracking     │
├──────────────────────────────────────────────────┤
│  FK: category, tax_rate, warehouse               │
│  M2M: tags, channels                             │
└──────┬───────┬────────┬────────┬────────┬────────┘
       │       │        │        │        │
       ▼       ▼        ▼        ▼        ▼
 Variant  PriceList  Attribute  Image  Attachment
                         │
                         ▼
                  AttributeValue

       │
       ▼
 ProductSupplier ──────────► Customer
       │
 StockMovement


┌──────────────────────────────────────────────────┐
│                    Customer                       │
│  name, type, email, phone, status                 │
│  vat_id, legal_name, address, city, country       │
│  is_customer, is_supplier                         │
├──────────────────────────────────────────────────┤
│  M2M: tags, linked_contacts (self)               │
└──────┬───────┬────────┬────────┬─────────────────┘
       │       │        │        │
       ▼       ▼        ▼        ▼
    Note   Activity   Quote   Invoice


┌──────────────────────────────────────────────────┐
│                    Invoice                        │
│  type, status, number, issue_date, due_date       │
│  subtotal, total_tax, total_amount, balance_due   │
│  customer_notes, internal_notes, locked_at        │
├──────────────────────────────────────────────────┤
│  FK: series, customer, rectified_invoice         │
└──────┬───────┬────────┬──────────────────────────┘
       │       │        │
       ▼       ▼        ▼
 InvoiceLine Payment  Timeline
       │
       ▼
 InvoiceLineTax ──► TaxRate
```

---

## 5. Django Apps y estructura del proyecto

```
backend/
├── manage.py
├── requirements.txt
├── config/                     # Configuración del proyecto Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Settings compartidos
│   │   ├── development.py     # Dev: DEBUG=True, CORS localhost
│   │   └── production.py      # Prod: seguridad, HTTPS, etc.
│   ├── urls.py                # URLs raíz
│   ├── wsgi.py
│   └── asgi.py
├── core/                       # App: modelos base y utilidades
│   ├── models.py              # TaxRate, Tag, Warehouse, SalesChannel
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── customers/                  # App: CRM
│   ├── models.py              # Customer, CustomerNote, Activity, Quote
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   └── admin.py
├── products/                   # App: Catálogo
│   ├── models.py              # Product, Variant, PriceList, Supplier, etc.
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   └── admin.py
├── invoices/                   # App: Facturación
│   ├── models.py              # Invoice, InvoiceLine, Payment, Timeline, etc.
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   ├── services.py            # Lógica de negocio (aprobar, anular, etc.)
│   └── admin.py
├── tasks/                      # App: Tareas del Dashboard
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── .env                        # Variables de entorno (no commit)
```

---

## 6. API REST — Endpoints

### 6.1 Productos (`/api/products/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/products/` | Listar productos (filtros: search, status, type, category, channel) |
| POST | `/api/products/` | Crear producto |
| GET | `/api/products/{id}/` | Detalle de producto (incluye variantes, proveedores, movimientos, etc.) |
| PUT | `/api/products/{id}/` | Actualizar producto |
| PATCH | `/api/products/{id}/` | Actualización parcial |
| DELETE | `/api/products/{id}/` | Eliminar producto (soft delete → Archived) |
| GET | `/api/products/{id}/stock-movements/` | Movimientos de stock |
| POST | `/api/products/{id}/stock-movements/` | Registrar movimiento de stock |
| GET | `/api/products/export/` | Exportar productos (CSV) |
| GET | `/api/categories/` | Listar categorías |
| POST | `/api/categories/` | Crear categoría |

### 6.2 Clientes (`/api/customers/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/customers/` | Listar clientes (filtros: search, type, status, city) |
| POST | `/api/customers/` | Crear cliente |
| GET | `/api/customers/{id}/` | Detalle (incluye notas, actividades, facturas, presupuestos) |
| PUT | `/api/customers/{id}/` | Actualizar cliente |
| PATCH | `/api/customers/{id}/` | Actualización parcial |
| DELETE | `/api/customers/{id}/` | Desactivar (soft delete → Inactive) |
| GET | `/api/customers/{id}/notes/` | Notas del cliente |
| POST | `/api/customers/{id}/notes/` | Añadir nota |
| GET | `/api/customers/{id}/activities/` | Actividades CRM |
| POST | `/api/customers/{id}/activities/` | Añadir actividad |
| GET | `/api/customers/{id}/invoices/` | Facturas del cliente |
| GET | `/api/customers/export/` | Exportar clientes (CSV) |

### 6.3 Facturas (`/api/invoices/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/invoices/` | Listar facturas (filtros: search, status, customer, series, date range) |
| POST | `/api/invoices/` | Crear borrador |
| GET | `/api/invoices/{id}/` | Detalle completo (líneas, pagos, timeline) |
| PUT | `/api/invoices/{id}/` | Actualizar borrador |
| DELETE | `/api/invoices/{id}/` | Eliminar borrador |
| POST | `/api/invoices/{id}/approve/` | Aprobar factura (genera número, bloquea) |
| POST | `/api/invoices/{id}/void/` | Anular factura |
| POST | `/api/invoices/{id}/duplicate/` | Duplicar como borrador |
| POST | `/api/invoices/{id}/send/` | Enviar por email |
| GET | `/api/invoices/{id}/pdf/` | Descargar PDF |
| POST | `/api/invoices/{id}/payments/` | Registrar cobro |
| GET | `/api/invoices/{id}/payments/` | Listar cobros |
| POST | `/api/invoices/{id}/rectify/` | Crear nota de crédito |
| POST | `/api/invoices/bulk-approve/` | Aprobar múltiples |
| POST | `/api/invoices/bulk-delete/` | Eliminar múltiples borradores |
| GET | `/api/invoices/export/` | Exportar facturas (CSV) |
| GET | `/api/invoice-series/` | Listar series |
| POST | `/api/invoice-series/` | Crear serie |

### 6.4 Configuración (`/api/config/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/tax-rates/` | Listar tipos impositivos |
| POST | `/api/tax-rates/` | Crear tipo impositivo |
| GET | `/api/warehouses/` | Listar almacenes |
| GET | `/api/sales-channels/` | Listar canales de venta |
| GET | `/api/tags/` | Listar etiquetas |

### 6.5 Tareas (`/api/tasks/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/tasks/` | Listar tareas (filtros: status, upcoming/overdue/completed) |
| POST | `/api/tasks/` | Crear tarea |
| PUT | `/api/tasks/{id}/` | Actualizar tarea |
| PATCH | `/api/tasks/{id}/` | Toggle completado |
| DELETE | `/api/tasks/{id}/` | Eliminar tarea |

### 6.6 Dashboard (`/api/dashboard/`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/dashboard/summary/` | KPIs: total facturado, pendiente, nº facturas, nº clientes activos |
| GET | `/api/dashboard/wallet/` | Saldos: disponible, pendiente, pagos recientes |

---

## 7. Serializers — Ejemplo clave

```python
# products/serializers.py

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer para la tabla/listado de productos."""
    category = serializers.StringRelatedField()
    tax = serializers.CharField(source='tax_rate.name', read_only=True)
    supplier = serializers.SerializerMethodField()
    channels = serializers.StringRelatedField(many=True)
    has_variants = serializers.BooleanField(read_only=True)
    variants_count = serializers.IntegerField(read_only=True)
    margin = serializers.DecimalField(read_only=True, max_digits=5, decimal_places=1)
    price_from = serializers.DecimalField(read_only=True, max_digits=12, decimal_places=2)

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'status', 'product_type', 'category',
            'stock', 'reserved', 'price', 'price_from', 'has_variants',
            'variants_count', 'cost', 'tax', 'supplier', 'channels',
            'updated_at', 'image', 'margin'
        ]

    def get_supplier(self, obj):
        primary = obj.suppliers.filter(is_primary=True).first()
        return primary.supplier.name if primary else None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer para el detalle completo de un producto."""
    # Incluye: variantes, atributos, price_lists, suppliers, stock_movements,
    #          gallery, attachments, recent_sales ...
    variants = ProductVariantSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    price_lists = PriceListSerializer(many=True, read_only=True)
    suppliers = ProductSupplierSerializer(many=True, read_only=True)
    stock_movements = StockMovementSerializer(many=True, read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)
    attachments = ProductAttachmentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    # ... etc

    class Meta:
        model = Product
        fields = '__all__'
```

---

## 8. Filtros y búsqueda

Se usará `django-filter` para implementar los filtros que ya existen en el frontend:

```python
# products/filters.py
import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.ChoiceFilter(choices=Product.Status.choices)
    product_type = django_filters.ChoiceFilter(field_name='product_type',
                                               choices=Product.ProductType.choices)
    category = django_filters.CharFilter(field_name='category__name')
    channel = django_filters.CharFilter(method='filter_channel')

    class Meta:
        model = Product
        fields = ['status', 'product_type', 'category']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(sku__icontains=value) |
            Q(category__name__icontains=value) |
            Q(suppliers__supplier__name__icontains=value)
        ).distinct()

    def filter_channel(self, queryset, name, value):
        return queryset.filter(channels__name=value)


# customers/filters.py
class CustomerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    contact_type = django_filters.ChoiceFilter(field_name='contact_type',
                                               choices=Customer.ContactType.choices)
    status = django_filters.ChoiceFilter(choices=Customer.Status.choices)
    city = django_filters.CharFilter(field_name='city')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value) |
            Q(vat_id__icontains=value)
        ).distinct()


# invoices/filters.py
class InvoiceFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')
    status = django_filters.CharFilter(method='filter_status')
    customer = django_filters.NumberFilter(field_name='customer__id')
    series = django_filters.CharFilter(field_name='series__prefix')
    date_from = django_filters.DateFilter(field_name='issue_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='issue_date', lookup_expr='lte')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(number__icontains=value) |
            Q(customer__name__icontains=value) |
            Q(total_amount__icontains=value)
        ).distinct()

    def filter_status(self, queryset, name, value):
        if value == 'overdue':
            from datetime import date
            return queryset.filter(
                status__in=['Approved', 'PartiallyPaid'],
                due_date__lt=date.today()
            )
        return queryset.filter(status=value)
```

---

## 9. Lógica de negocio — Service Layer

```python
# invoices/services.py

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
        InvoiceTimeline.objects.create(
            invoice=invoice, event_type='approved',
            action='Invoice approved', actor='System', date=timezone.now().date()
        )
        return invoice

    @staticmethod
    def void(invoice):
        """Anula factura aprobada sin cobros."""
        if invoice.status != 'Approved':
            raise ValidationError('Solo se pueden anular facturas aprobadas.')
        if invoice.payments.exists():
            raise ValidationError('No se puede anular una factura con cobros.')

        invoice.status = 'Voided'
        invoice.balance_due = 0
        invoice.save()
        InvoiceTimeline.objects.create(
            invoice=invoice, event_type='voided',
            action='Invoice voided', actor='System', date=timezone.now().date()
        )

    @staticmethod
    def record_payment(invoice, payment_data):
        """Registra un cobro en la factura."""
        if invoice.status not in ['Approved', 'PartiallyPaid']:
            raise ValidationError('No se puede cobrar esta factura.')

        amount = min(payment_data['amount'], invoice.balance_due)
        payment = Payment.objects.create(
            invoice=invoice,
            date=payment_data['date'],
            amount=amount,
            method=payment_data.get('method', 'Transfer'),
            reference=payment_data.get('reference'),
            notes=payment_data.get('notes'),
        )
        # El save() del Payment actualiza paid_amount, balance_due y status
        return payment

    @staticmethod
    def create_credit_note(invoice):
        """Crea nota de crédito a partir de factura existente."""
        if invoice.status not in ['Approved', 'Paid', 'PartiallyPaid']:
            raise ValidationError('No se puede rectificar esta factura.')

        rec_series = InvoiceSeries.objects.filter(prefix='REC', active=True).first()
        if not rec_series:
            raise ValidationError('No hay serie de rectificativas configurada.')

        credit_note = Invoice.objects.create(
            invoice_type='CreditNote',
            status='Draft',
            series=rec_series,
            customer=invoice.customer,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date(),
            payment_method=invoice.payment_method,
            currency=invoice.currency,
            customer_notes=f'Rectifying invoice for {invoice.number}.',
            rectified_invoice=invoice,
        )

        # Copiar líneas con cantidades negativas
        for line in invoice.lines.all():
            new_line = InvoiceLine.objects.create(
                invoice=credit_note,
                position=line.position,
                product=line.product,
                description=f'{line.description} (return)',
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

        return credit_note

    @staticmethod
    def duplicate(invoice):
        """Duplica factura como nuevo borrador."""
        default_series = InvoiceSeries.objects.filter(is_default=True, active=True).first()
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
                invoice=dup, position=line.position,
                product=line.product, description=line.description,
                quantity=abs(line.quantity), unit_price=line.unit_price,
                discount_type=line.discount_type, discount_value=line.discount_value,
            )
            for tax in line.taxes.all():
                InvoiceLineTax.objects.create(
                    invoice_line=new_line, tax_rate=tax.tax_rate,
                    tax_name=tax.tax_name, tax_percent=tax.tax_percent,
                    is_retention=tax.is_retention, tax_amount=abs(tax.tax_amount),
                )

        dup.recalculate_totals()
        return dup
```

---

## 10. Dependencias Python

```
# requirements.txt
Django>=5.1,<6.0
djangorestframework>=3.15
django-cors-headers>=4.3
django-filter>=24.0
psycopg[binary]>=3.2            # Driver PostgreSQL moderno
python-decouple>=3.8            # Variables de entorno
Pillow>=10.0                    # Procesamiento de imágenes
gunicorn>=22.0                  # Servidor WSGI (producción)
whitenoise>=6.5                 # Archivos estáticos
dj-database-url>=2.1            # Configuración DB desde URL
```

---

## 11. Configuración CORS y conexión con el frontend

```python
# config/settings/development.py

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",     # Vite dev server
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

---

## 12. Consideraciones de diseño

### 12.1 Autenticación (futuro)
El frontend actual no tiene autenticación. Cuando se implemente:
- **Django REST Framework Token Auth** o **JWT** (vía `djangorestframework-simplejwt`)
- Roles: `owner`, `admin`, `sales`, `accountant` (como define la spec)
- Los campos `created_by`, `modified_by`, `actor` pasarán de `CharField` a `ForeignKey(User)`

### 12.2 Multi-tenancy (futuro)
El diseño actual es single-tenant. Si se necesitara multi-tenant:
- Añadir `tenant_id` a todos los modelos
- Middleware para filtrar por tenant automáticamente

### 12.3 Inmutabilidad fiscal
Las facturas aprobadas NO se pueden modificar. Se implementa mediante:
- Validación en el serializer/service: rechazar PUT/PATCH si `status != Draft`
- Snapshots del cliente al aprobar (campos `*_snapshot`)
- Solo acciones permitidas: cobrar, enviar, rectificar, anular

### 12.4 Cálculos server-side
Todos los totales se recalculan en el servidor para garantizar integridad:
- `InvoiceLine.save()` calcula subtotal
- `Invoice.recalculate_totals()` agrega desde líneas
- `Payment.save()` actualiza `paid_amount` y `balance_due`

### 12.5 Soft delete
- Productos: cambian a status `Archived` (no se eliminan)
- Clientes: cambian a status `Inactive`
- Facturas borrador: `status = Deleted` (no borrado físico)

---

## 13. Seeds / Datos iniciales

Se creará un comando de Django (`manage.py seed`) que cargue los datos hardcodeados actuales del frontend:
- 10 productos con sus variantes, proveedores, movimientos
- 12 clientes con notas, actividades, presupuestos
- 10 facturas con líneas, pagos, timeline
- Tax rates: IVA 21%, IVA 10%, IVA 4%, IRPF -15%
- Series: FAC, SRV, REC
- Categorías: Clothing, Footwear, Accessories, Electronics, Food & Drink, Furniture, Beauty, Services
- Canales: Web, Marketplace
- Almacén: Warehouse Madrid
- Tareas del dashboard

Esto permite que el frontend funcione exactamente igual tras conectar con el backend, con los mismos datos que ahora están hardcodeados.
