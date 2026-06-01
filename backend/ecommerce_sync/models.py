"""
Modelos del módulo `ecommerce_sync`.

- StoreConnection: credenciales de la tienda online (una por Company).
- StoreTaxMapping: enlace TaxRate del ERP ↔ tax_rules_group de la tienda.
- EcommerceSyncLog: auditoría de cada operación push/pull.

Pensado para ser multiplataforma (PrestaShop hoy; Shopify/WooCommerce
después) mediante el campo `platform` y la capa de clientes en `clients/`.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models

from .fields import EncryptedTextField


class StoreConnection(models.Model):
    """Credenciales y estado de la conexión a una tienda e-commerce."""

    class Platform(models.TextChoices):
        PRESTASHOP = 'prestashop', 'PrestaShop'
        SHOPIFY = 'shopify', 'Shopify'
        WOOCOMMERCE = 'woocommerce', 'WooCommerce'

    class SyncStatus(models.TextChoices):
        OK = 'ok', 'OK'
        ERROR = 'error', 'Error'
        NEVER = 'never', 'Nunca ejecutada'

    company = models.OneToOneField(
        'accounts.Company',
        on_delete=models.CASCADE,
        related_name='store_connection',
    )
    platform = models.CharField(
        max_length=20, choices=Platform.choices, default=Platform.PRESTASHOP,
    )
    base_url = models.URLField(
        default='http://localhost:8080',
        help_text='URL base de la tienda (sin /api).',
    )
    # En PrestaShop la autenticación es Basic con la API key como usuario.
    api_key = EncryptedTextField()

    is_active = models.BooleanField(default=True)

    # Qué entidades y en qué dirección se sincronizan.
    push_products = models.BooleanField(default=True)
    push_customers = models.BooleanField(default=True)
    pull_orders = models.BooleanField(default=True)

    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(
        max_length=10, choices=SyncStatus.choices, default='never',
    )
    last_sync_error = models.TextField(blank=True, default='')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='store_connections_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conexión e-commerce'
        verbose_name_plural = 'Conexiones e-commerce'

    def __str__(self) -> str:
        return f'{self.company} → {self.get_platform_display()} ({self.base_url})'


class StoreTaxMapping(models.Model):
    """Mapeo explícito de TaxRate (ERP) ↔ tax_rules_group (tienda)."""

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='store_tax_mappings',
    )
    tax_rate = models.ForeignKey(
        'core.TaxRate', on_delete=models.CASCADE,
        related_name='store_mappings',
    )
    store_tax_id = models.PositiveIntegerField(
        help_text='id del tax_rules_group en la tienda.',
    )
    store_tax_name = models.CharField(max_length=200, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mapeo de impuesto e-commerce'
        verbose_name_plural = 'Mapeos de impuestos e-commerce'
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'tax_rate'],
                name='unique_store_tax_mapping_per_company',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.tax_rate} → tienda #{self.store_tax_id}'


class EcommerceSyncLog(models.Model):
    """Registro de auditoría de cada operación con la tienda."""

    class Operation(models.TextChoices):
        PUSH = 'PUSH', 'Push (ERP → tienda)'
        PULL = 'PULL', 'Pull (tienda → ERP)'

    company = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE,
        related_name='store_sync_logs',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='store_sync_logs',
    )
    entity_type = models.CharField(
        max_length=50,
        help_text='Tipo de entidad ERP (ej: product, customer, order).',
    )
    entity_id = models.CharField(max_length=64, blank=True, default='')
    store_id = models.PositiveIntegerField(null=True, blank=True)

    operation = models.CharField(max_length=10, choices=Operation.choices)
    method = models.CharField(
        max_length=50,
        help_text="Método HTTP/lógico (ej: 'GET', 'POST', 'PUT').",
    )

    success = models.BooleanField(default=False)
    request_payload_hash = models.CharField(max_length=64, blank=True, default='')
    response_excerpt = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    duration_ms = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de sincronización e-commerce'
        verbose_name_plural = 'Logs de sincronización e-commerce'
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['company', 'entity_type', '-created_at'],
                name='ecomlog_co_entity_created_idx',
            ),
        ]

    def __str__(self) -> str:
        status = 'OK' if self.success else 'ERROR'
        return f'[{status}] {self.operation} {self.entity_type} {self.entity_id}'
