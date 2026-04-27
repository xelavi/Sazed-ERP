from decimal import Decimal

from django.db import models
from django.db.models import Sum


class Provider(models.Model):

    class ContactType(models.TextChoices):
        COMPANY = 'Company', 'Empresa'
        PERSON = 'Person', 'Persona'

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Activo'
        INACTIVE = 'Inactive', 'Inactivo'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='providers', null=True, blank=True,
    )

    name = models.CharField(max_length=200)
    contact_type = models.CharField(max_length=10, choices=ContactType.choices)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default='Active')

    vat_id = models.CharField(max_length=20, blank=True, null=True)
    legal_name = models.CharField(max_length=200, blank=True)

    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='España')

    payment_method = models.CharField(
        max_length=50, blank=True, default='Transferencia 30 días',
    )
    bank_account = models.CharField(max_length=34, blank=True)

    avatar_color = models.CharField(max_length=200, blank=True)
    initials = models.CharField(max_length=4, blank=True)

    internal_notes = models.TextField(blank=True)

    tags = models.ManyToManyField('core.Tag', blank=True, related_name='providers')

    linked_contacts = models.ManyToManyField('self', blank=True, symmetrical=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_purchased(self):
        return self.purchase_orders.exclude(
            status='Draft'
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    @property
    def pending_balance(self):
        return self.purchase_orders.filter(
            status__in=['Approved', 'PartiallyPaid']
        ).aggregate(total=Sum('balance_due'))['total'] or Decimal('0.00')

    @property
    def total_documents(self):
        return self.purchase_orders.count()


class ProviderNote(models.Model):

    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name='notes',
    )
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Note #{self.pk} for {self.provider}'


class ProviderActivity(models.Model):

    class ActivityType(models.TextChoices):
        MEETING = 'Reunión', 'Reunión'
        CALL = 'Llamada', 'Llamada'
        EMAIL = 'Email', 'Email'
        VISIT = 'Visita', 'Visita'
        OTHER = 'Otro', 'Otro'

    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name='activities',
    )
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    date = models.DateField()
    subject = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'provider activities'

    def __str__(self):
        return f'{self.activity_type}: {self.subject}'


class PurchaseOrder(models.Model):

    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Borrador'
        APPROVED = 'Approved', 'Aprobado'
        PARTIALLY_PAID = 'PartiallyPaid', 'Parcialmente pagado'
        PAID = 'Paid', 'Pagado'
        CANCELLED = 'Cancelled', 'Cancelado'

    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name='purchase_orders',
    )
    number = models.CharField(max_length=30, unique=True)
    concept = models.CharField(max_length=300)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default='Draft',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.number} — {self.concept}'
