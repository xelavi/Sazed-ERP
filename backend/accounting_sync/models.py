"""
Modelos del módulo `accounting_sync`.

- OdooConnection: credenciales (una por Company).
- OdooTaxMapping: enlace explícito entre TaxRate del ERP y account.tax de Odoo.
- SyncLog: auditoría de cada operación push/pull.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models

from .fields import EncryptedTextField


class OdooConnection(models.Model):
    """Credenciales y estado de la conexión a una instancia de Odoo."""

    class SyncStatus(models.TextChoices):
        OK = 'ok', 'OK'
        ERROR = 'error', 'Error'
        NEVER = 'never', 'Nunca ejecutada'

    company = models.OneToOneField(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='odoo_connection',
    )
    base_url = models.URLField(default='http://localhost:8069')
    database = models.CharField(max_length=100)
    username = models.CharField(max_length=200)
    password = EncryptedTextField()

    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(
        max_length=10, choices=SyncStatus.choices, default='never',
    )
    last_sync_error = models.TextField(blank=True, default='')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='odoo_connections_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conexión Odoo'
        verbose_name_plural = 'Conexiones Odoo'

    def __str__(self) -> str:
        return f'{self.company} → {self.base_url}/{self.database}'


class OdooTaxMapping(models.Model):
    """Mapeo explícito de TaxRate (ERP) ↔ account.tax (Odoo)."""

    class Direction(models.TextChoices):
        SALE = 'sale', 'Venta'
        PURCHASE = 'purchase', 'Compra'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='odoo_tax_mappings',
    )
    tax_rate = models.ForeignKey(
        'core.TaxRate', on_delete=models.CASCADE,
        related_name='odoo_mappings',
    )
    direction = models.CharField(max_length=10, choices=Direction.choices)
    odoo_tax_id = models.PositiveIntegerField()
    odoo_tax_name = models.CharField(max_length=200, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mapeo de impuesto Odoo'
        verbose_name_plural = 'Mapeos de impuestos Odoo'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'tax_rate', 'direction'],
                name='unique_tax_mapping_per_company_direction',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.tax_rate} ({self.direction}) → Odoo #{self.odoo_tax_id}'


class OdooProvisioningJob(models.Model):
    """Trabajo de aprovisionamiento automático de una BD Odoo para una Company.

    El flujo lo crea automáticamente el serializer al crear una Company.
    Un management command (`process_odoo_provisioning`) lo recoge y ejecuta:
    crear BD, instalar módulos, crear usuario API, mapear impuestos y
    registrar el OdooConnection asociado.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        RUNNING = 'running', 'Procesando'
        DONE = 'done', 'Completado'
        FAILED = 'failed', 'Fallido'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='odoo_provisioning_jobs',
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING,
    )
    database_name = models.CharField(max_length=100)
    admin_password = EncryptedTextField(blank=True, default='')
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=3)

    logs = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Job de aprovisionamiento Odoo'
        verbose_name_plural = 'Jobs de aprovisionamiento Odoo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'Provisioning {self.company} → {self.database_name} [{self.status}]'

    def append_log(self, line: str) -> None:
        from django.utils import timezone as _tz
        ts = _tz.now().strftime('%H:%M:%S')
        self.logs = (self.logs + f'[{ts}] {line}\n')[-10_000:]


class SyncLog(models.Model):
    """Registro de auditoría de cada operación con Odoo."""

    class Operation(models.TextChoices):
        PUSH = 'PUSH', 'Push (ERP → Odoo)'
        PULL = 'PULL', 'Pull (Odoo → ERP)'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='odoo_sync_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='odoo_sync_logs',
    )
    entity_type = models.CharField(
        max_length=50,
        help_text='Tipo de entidad ERP (ej: customer, product, invoice).',
    )
    entity_id = models.CharField(
        max_length=64, blank=True, default='',
        help_text='ID interno de la entidad (int o UUID en formato string).',
    )
    odoo_id = models.PositiveIntegerField(null=True, blank=True)

    operation = models.CharField(max_length=10, choices=Operation.choices)
    odoo_method = models.CharField(
        max_length=50,
        help_text="Método Odoo invocado (ej: 'create', 'write', 'action_post').",
    )

    success = models.BooleanField(default=False)
    request_payload_hash = models.CharField(
        max_length=64, blank=True, default='',
        help_text='SHA-256 del payload enviado para diagnóstico.',
    )
    response_excerpt = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    duration_ms = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de sincronización Odoo'
        verbose_name_plural = 'Logs de sincronización Odoo'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['company', 'entity_type', '-created_at'],
                name='synclog_co_entity_created_idx',
            ),
        ]

    def __str__(self) -> str:
        status = 'OK' if self.success else 'ERROR'
        return f'[{status}] {self.operation} {self.entity_type} {self.entity_id}'
