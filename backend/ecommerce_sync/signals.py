"""
Sincronización en tiempo real ERP → tienda vía signals post_save.

Al guardar un Product/Customer, si su Company tiene una StoreConnection
activa, se hace push a la tienda tras confirmar la transacción
(`transaction.on_commit`).

Decisiones (calcadas de accounting_sync):
- El push se ejecuta tras commit y captura cualquier error para NO romper
  el guardado del ERP (tienda caída ≠ no poder guardar un producto).
- Anti-recursión: el push escribe de vuelta `prestashop_id`; detectamos ese
  caso (`update_fields == {'prestashop_id'}`) y lo ignoramos.

La dirección tienda → ERP (pedidos) NO usa signals: PrestaShop no emite
webhooks, así que se hace por polling (`pull_prestashop`).
"""
from __future__ import annotations

import logging

from django.db import transaction
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)


def _has_active_connection(company) -> bool:
    from .models import StoreConnection
    if company is None:
        return False
    return StoreConnection.objects.filter(company=company, is_active=True).exists()


def _only_link_field(update_fields) -> bool:
    return update_fields is not None and set(update_fields) == {'prestashop_id'}


def _push_after_commit(label: str, fn) -> None:
    def _run():
        try:
            fn()
            logger.info('Sync %s -> tienda OK', label)
        except Exception:  # noqa: BLE001
            logger.exception('Sync %s -> tienda falló (no afecta al guardado)', label)

    transaction.on_commit(_run)


# ── Receivers ───────────────────────────────────────────


def sync_product(sender, instance, created, update_fields=None, **kwargs):
    if _only_link_field(update_fields):
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service
    if not company.store_connection.push_products:
        return
    _push_after_commit(
        f'product:{instance.pk}',
        lambda: sync_service.push_product(instance, company),
    )


def sync_customer(sender, instance, created, update_fields=None, **kwargs):
    if _only_link_field(update_fields):
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service
    if not company.store_connection.push_customers:
        return
    _push_after_commit(
        f'customer:{instance.pk}',
        lambda: sync_service.push_customer(instance, company),
    )


def connect_signals() -> None:
    """Conecta los receivers. Se llama desde AppConfig.ready()."""
    from customers.models import Customer
    from products.models import Product

    post_save.connect(sync_product, sender=Product, dispatch_uid='ecom_sync_product')
    post_save.connect(sync_customer, sender=Customer, dispatch_uid='ecom_sync_customer')
