"""
Multi-company accounts system.

Models:
- User: Custom user model (email-based auth)
- Company: Organisation / business entity
- Membership: Links User ↔ Company with a role
"""

import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


# ── Custom User ────────────────────────────────────────


class UserManager(BaseUserManager):
    """Manager for email-based User model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user — email as unique identifier.
    A user can belong to multiple companies via Membership.
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def initials(self):
        parts = [self.first_name, self.last_name]
        return ''.join(p[0].upper() for p in parts if p)


# ── Company ────────────────────────────────────────────


class Company(models.Model):
    """
    Business entity. All data (products, customers, invoices…)
    belongs to a company, enabling full multi-tenancy.
    """

    class Plan(models.TextChoices):
        FREE = 'free', 'Gratuito'
        STARTER = 'starter', 'Starter'
        PRO = 'pro', 'Pro'

    # Identity
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tax_id = models.CharField(
        max_length=20, blank=True,
        help_text='CIF / NIF de la empresa',
    )
    legal_name = models.CharField(max_length=300, blank=True)

    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)

    # Address
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default='España')

    # Branding
    logo = models.ImageField(upload_to='companies/logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#667eea')

    # Plan / billing
    plan = models.CharField(
        max_length=10, choices=Plan.choices, default='free',
    )

    # Settings
    currency = models.CharField(max_length=3, default='EUR')
    fiscal_year_start = models.IntegerField(
        default=1, help_text='Mes de inicio del año fiscal (1=Enero)',
    )
    invoice_prefix = models.CharField(max_length=10, default='FAC')

    # Members
    members = models.ManyToManyField(
        'User',
        through='Membership',
        through_fields=('company', 'user'),
        related_name='companies',
    )

    # Audit
    created_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL,
        null=True, related_name='created_companies',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'companies'
        ordering = ['name']

    def __str__(self):
        return self.name


# ── Membership (User ↔ Company with Role) ─────────────


class Membership(models.Model):
    """
    Associates a User with a Company, defining the role.
    A user can have different roles in different companies.
    """

    class Role(models.TextChoices):
        OWNER = 'owner', 'Propietario'
        ADMIN = 'admin', 'Administrador'
        EDITOR = 'editor', 'Editor'
        VIEWER = 'viewer', 'Solo lectura'

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='memberships',
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='memberships',
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default='viewer',
    )
    is_default = models.BooleanField(
        default=False,
        help_text='Empresa activa por defecto al iniciar sesión',
    )
    invited_by = models.ForeignKey(
        'User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sent_invitations',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'company']
        ordering = ['-is_default', 'company__name']

    def __str__(self):
        return f'{self.user.email} → {self.company.name} ({self.role})'

    def save(self, *args, **kwargs):
        # If marking as default, clear other defaults for this user
        if self.is_default:
            Membership.objects.filter(
                user=self.user, is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    # ── Permission helpers ──

    @property
    def can_edit(self):
        return self.role in ('owner', 'admin', 'editor')

    @property
    def can_manage(self):
        """Can manage company settings & members."""
        return self.role in ('owner', 'admin')

    @property
    def is_owner(self):
        return self.role == 'owner'
