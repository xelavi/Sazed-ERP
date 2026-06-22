"""
Sincronización en tiempo real ERP → Odoo vía signals post_save.

Al guardar un Customer/Provider/Product/Invoice/PurchaseInvoice, si su
Company tiene una OdooConnection activa, se hace push a Odoo justo
después de confirmar la transacción (`transaction.on_commit`).

Decisiones:
- El push se ejecuta tras commit para no enviar datos que luego hagan
  rollback, y captura cualquier error para NO romper el guardado del ERP
  (Odoo caído ≠ no poder guardar un cliente).
- Anti-recursión: los push escriben de vuelta `odoo_id` en la entidad con
  `save(update_fields=['odoo_id'])`; detectamos ese caso y lo ignoramos.
- Facturas: solo se sincronizan cuando NO están en Draft (al aprobarse),
  porque antes no tienen líneas/importes definitivos.
"""
from __future__ import annotations

import logging

from django.db import transaction
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)


def _has_active_connection(company) -> bool:
    from .models import OdooConnection
    if company is None:
        return False
    return OdooConnection.objects.filter(company=company, is_active=True).exists()


def _only_odoo_id(update_fields) -> bool:
    """True si el save solo tocó `odoo_id` (el write-back del propio push)."""
    return update_fields is not None and set(update_fields) == {'odoo_id'}


def _push_after_commit(label: str, fn) -> None:
    """Programa el push tras commit, blindado contra errores."""
    def _run():
        try:
            fn()
            logger.info('Sync %s -> Odoo OK', label)
        except Exception:  # noqa: BLE001
            logger.exception('Sync %s -> Odoo falló (no afecta al guardado)', label)

    transaction.on_commit(_run)


# ── Receivers ───────────────────────────────────────────


def sync_customer(sender, instance, created, update_fields=None, **kwargs):
    if _only_odoo_id(update_fields):
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service
    _push_after_commit(
        f'customer:{instance.pk}',
        lambda: sync_service.push_contact(instance, company),
    )


def sync_provider(sender, instance, created, update_fields=None, **kwargs):
    if _only_odoo_id(update_fields):
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service
    _push_after_commit(
        f'provider:{instance.pk}',
        lambda: sync_service.push_provider(instance, company),
    )


def sync_product(sender, instance, created, update_fields=None, **kwargs):
    if _only_odoo_id(update_fields):
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service
    _push_after_commit(
        f'product:{instance.pk}',
        lambda: sync_service.push_product(instance, company),
    )


def sync_invoice(sender, instance, created, update_fields=None, **kwargs):
    if _only_odoo_id(update_fields):
        return
    if getattr(instance, 'is_template', False):
        return
    if instance.status == 'Draft':
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service

    def _push():
        # La factura necesita que su cliente exista ya en Odoo.
        if not instance.customer.odoo_id:
            sync_service.push_contact(instance.customer, company)
        sync_service.push_sales_invoice(instance, company, post=True)

    _push_after_commit(f'invoice:{instance.pk}', _push)


def sync_purchase_invoice(sender, instance, created, update_fields=None, **kwargs):
    if _only_odoo_id(update_fields):
        return
    if getattr(instance, 'is_template', False):
        return
    if instance.status == 'Draft':
        return
    company = instance.company
    if not _has_active_connection(company):
        return
    from . import sync_service

    def _push():
        if not instance.provider.odoo_id:
            sync_service.push_provider(instance.provider, company)
        sync_service.push_purchase_invoice(instance, company, post=True)

    _push_after_commit(f'purchase:{instance.pk}', _push)


def connect_signals() -> None:
    """Conecta los receivers. Se llama desde AppConfig.ready()."""
    from customers.models import Customer
    from products.models import Product
    from invoices.models import Invoice
    from purchases.models import PurchaseInvoice

    # Clients i proveïdors (ara unificats com a Customer)
    post_save.connect(sync_customer, sender=Customer, dispatch_uid='odoo_sync_customer')
    post_save.connect(sync_product, sender=Product, dispatch_uid='odoo_sync_product')
    post_save.connect(sync_invoice, sender=Invoice, dispatch_uid='odoo_sync_invoice')
    post_save.connect(
        sync_purchase_invoice, sender=PurchaseInvoice,
        dispatch_uid='odoo_sync_purchase_invoice',
    )
