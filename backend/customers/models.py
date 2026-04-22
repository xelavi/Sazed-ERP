from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Customer(models.Model):
    """Contacto (cliente y/o proveedor)."""

    class ContactType(models.TextChoices):
        COMPANY = 'Company', 'Empresa'
        PERSON = 'Person', 'Persona'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Activo'
        INACTIVE = 'Inactive', 'Inactivo'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='customers', null=True, blank=True,
    )

    # Datos principales
    name = models.CharField(max_length=200)
    contact_type = models.CharField(max_length=10, choices=ContactType.choices)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default='Active')

    # Identificación fiscal
    vat_id = models.CharField(max_length=20, blank=True, null=True)
    legal_name = models.CharField(max_length=200, blank=True)

    # Dirección fiscal
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='España')

    # Opciones comerciales
    payment_method = models.CharField(
        max_length=50, blank=True, default='Transferencia 30 días',
    )
    bank_account = models.CharField(max_length=34, blank=True)
    is_customer = models.BooleanField(default=True)
    is_supplier = models.BooleanField(default=False)

    # Visual
    avatar_color = models.CharField(max_length=200, blank=True)
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
            status__in=['Draft', 'Voided']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    @property
    def pending_balance(self):
        """Saldo pendiente de cobro."""
        return self.invoices.filter(
            status__in=['Approved', 'PartiallyPaid']
        ).aggregate(total=Sum('balance_due'))['total'] or Decimal('0.00')

    @property
    def total_documents(self):
        """Número total de documentos."""
        return self.invoices.count()


class CustomerNote(models.Model):
    """Notas asociadas a un cliente."""

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='notes',
    )
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Note #{self.pk} for {self.customer}'


class CustomerActivity(models.Model):
    """Actividades CRM: reuniones, llamadas, emails, visitas."""

    class ActivityType(models.TextChoices):
        MEETING = 'Reunión', 'Reunión'
        CALL = 'Llamada', 'Llamada'
        EMAIL = 'Email', 'Email'
        VISIT = 'Visita', 'Visita'
        OTHER = 'Otro', 'Otro'

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='activities',
    )
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    date = models.DateField()
    subject = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'customer activities'

    def __str__(self):
        return f'{self.activity_type}: {self.subject}'


class Quote(models.Model):
    """Presupuestos asociados a un cliente."""

    class Status(models.TextChoices):
        DRAFT = 'Borrador', 'Borrador'
        SENT = 'Enviado', 'Enviado'
        ACCEPTED = 'Aceptado', 'Aceptado'
        REJECTED = 'Rechazado', 'Rechazado'
        EXPIRED = 'Expirado', 'Expirado'

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='quotes',
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
