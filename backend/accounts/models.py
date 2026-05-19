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
    phone = models.CharField(max_length=30, blank=True, default='')
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


# ── Inbox: Notifications, Messages, Invitations ───────


class Notification(models.Model):
    """System-generated notification for a single user."""

    class Kind(models.TextChoices):
        SYSTEM = 'system', 'Sistema'
        ALERT = 'alert', 'Aviso'
        ACTIVITY = 'activity', 'Actividad'

    recipient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='notifications',
    )
    kind = models.CharField(max_length=10, choices=Kind.choices, default='system')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True, default='')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.kind}] {self.title} → {self.recipient.email}'


class Message(models.Model):
    """User-to-user message scoped to a company. Supports replies via parent."""

    sender = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='sent_messages',
    )
    recipient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='received_messages',
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='messages',
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='replies',
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender.email} → {self.recipient.email}: {self.subject}'


class Invitation(models.Model):
    """Pending invitation for a user to join a company."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        ACCEPTED = 'accepted', 'Aceptada'
        REJECTED = 'rejected', 'Rechazada'

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='invitations',
    )
    inviter = models.ForeignKey(
        'User', on_delete=models.SET_NULL,
        null=True, related_name='sent_company_invitations',
    )
    invitee = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='received_invitations',
    )
    role = models.CharField(
        max_length=10, choices=Membership.Role.choices, default='editor',
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'invitee'],
                condition=models.Q(status='pending'),
                name='unique_pending_invitation',
            ),
        ]

    def __str__(self):
        return f'{self.invitee.email} → {self.company.name} ({self.status})'


# ── Social Auth ────────────────────────────────────────


class SocialAccount(models.Model):
    """
    External identity (Facebook, etc.) linked to a User.
    Stores the long-lived access token used to call provider APIs
    (e.g. Facebook Graph API for Pages and Instagram Business).
    """

    PROVIDER_FACEBOOK = 'facebook'
    PROVIDER_CHOICES = [
        (PROVIDER_FACEBOOK, 'Facebook'),
    ]

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='social_accounts',
    )
    provider = models.CharField(max_length=32, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=128)
    # TODO: cifrar en producción (django-fernet-fields o equivalente)
    access_token = models.TextField()
    token_expires_at = models.DateTimeField(null=True, blank=True)
    scopes = models.JSONField(default=list, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('provider', 'provider_user_id')]
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user.email} · {self.provider}:{self.provider_user_id}'


# ── System Settings ────────────────────────────────────


class SystemSettings(models.Model):
    """
    Key-value store for system configuration that admins can edit
    without touching code or .env files.

    Usage:
        >>> SystemSettings.get('facebook_app_id')
        '123456789'
    """

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['key']

    def __str__(self):
        # Truncate sensitive values for display
        display = self.value[:30] + '…' if len(self.value) > 30 else self.value
        is_secret = 'secret' in self.key.lower() or 'token' in self.key.lower()
        if is_secret:
            display = '***hidden***'
        return f'{self.key} = {display}'

    @classmethod
    def get(cls, key, default=None):
        """Get a setting value by key. Returns default if not found."""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value):
        """Create or update a setting."""
        obj, created = cls.objects.get_or_create(key=key)
        obj.value = str(value)
        obj.save(update_fields=['value'])
        return obj
