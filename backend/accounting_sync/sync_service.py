"""
Servicio de sincronización ERP ↔ Odoo (Fase 1: contacts + products).

Cada operación:
- Verifica idempotencia: si `odoo_id` está poblado → write(); si no,
  intenta encontrar el registro en Odoo por identificador natural
  (VAT para contactos, SKU para productos) y enlaza; si no, crea.
- Persiste el `odoo_id` en la entidad ERP.
- Registra la operación en `SyncLog`.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Callable

from decimal import Decimal

from django.utils import timezone

from .adapters import (
    ContactAdapter,
    ProductAdapter,
    PurchaseInvoiceAdapter,
    SalesInvoiceAdapter,
)
from .adapters.base import from_odoo_decimal
from .models import OdooConnection, SyncLog
from .odoo_client import OdooClient

logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────


def _payload_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _excerpt(value: Any, limit: int = 500) -> str:
    text = repr(value) if not isinstance(value, str) else value
    return text[:limit]


def get_client_for(connection: OdooConnection) -> OdooClient:
    """Construye un `OdooClient` desde una `OdooConnection` activa."""
    return OdooClient(
        base_url=connection.base_url,
        database=connection.database,
        username=connection.username,
        password=connection.password,
    )


def _log_operation(
    *,
    company,
    user,
    entity_type: str,
    entity_id: str,
    operation: str,
    odoo_method: str,
    payload: dict,
    odoo_id: int | None,
    success: bool,
    response: Any,
    error: str,
    duration_ms: int,
) -> SyncLog:
    return SyncLog.objects.create(
        company=company,
        user=user,
        entity_type=entity_type,
        entity_id=str(entity_id),
        odoo_id=odoo_id,
        operation=operation,
        odoo_method=odoo_method,
        success=success,
        request_payload_hash=_payload_hash(payload) if payload else '',
        response_excerpt=_excerpt(response) if response else '',
        error_message=error,
        duration_ms=duration_ms,
    )


def _run_push(
    *,
    company,
    user,
    entity_type: str,
    entity_id: str,
    payload: dict,
    find_existing: Callable[[], int | None],
    write: Callable[[int, dict], None],
    create: Callable[[dict], int],
    current_odoo_id: int | None,
) -> int:
    """Lógica genérica de push idempotente con logging."""
    start = time.monotonic()
    odoo_id: int | None = current_odoo_id
    method = 'write' if current_odoo_id else 'create'
    error = ''
    success = False
    response: Any = None

    try:
        if odoo_id:
            write(odoo_id, payload)
            response = {'id': odoo_id, 'written': True}
        else:
            existing = find_existing()
            if existing:
                method = 'write'
                write(existing, payload)
                odoo_id = existing
                response = {'id': existing, 'linked': True}
            else:
                method = 'create'
                odoo_id = create(payload)
                response = {'id': odoo_id, 'created': True}
        success = True
        return odoo_id
    except Exception as exc:  # noqa: BLE001
        error = f'{type(exc).__name__}: {exc}'
        logger.exception('Push %s id=%s falló: %s', entity_type, entity_id, error)
        raise
    finally:
        duration_ms = int((time.monotonic() - start) * 1000)
        _log_operation(
            company=company, user=user,
            entity_type=entity_type, entity_id=entity_id,
            operation='PUSH', odoo_method=method,
            payload=payload, odoo_id=odoo_id,
            success=success, response=response, error=error,
            duration_ms=duration_ms,
        )


# ── API pública ─────────────────────────────────────────


def push_contact(customer, company, *, user=None) -> int:
    """Sincroniza un `customers.Customer` con Odoo.

    Returns:
        ID del partner en Odoo.

    Raises:
        OdooConnection.DoesNotExist: si la company no tiene conexión activa.
        OdooConnectionError: si falla la autenticación.
    """
    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)
    adapter = ContactAdapter(client)
    payload = adapter.to_odoo(customer, company=company)

    odoo_id = _run_push(
        company=company, user=user,
        entity_type='customer', entity_id=str(customer.pk),
        payload=payload,
        find_existing=lambda: (
            client.find_partner_by_vat(payload['vat']) if payload.get('vat') else None
        ),
        write=lambda oid, data: client.update_partner(oid, data),
        create=lambda data: client.create_partner(data),
        current_odoo_id=customer.odoo_id,
    )

    if customer.odoo_id != odoo_id:
        customer.odoo_id = odoo_id
        customer.save(update_fields=['odoo_id'])

    _touch_connection(connection, success=True)
    return odoo_id


def push_product(product, company, *, user=None) -> int:
    """Sincroniza un `products.Product` con Odoo."""
    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)
    adapter = ProductAdapter(client)
    payload = adapter.to_odoo(product, company=company)

    odoo_id = _run_push(
        company=company, user=user,
        entity_type='product', entity_id=str(product.pk),
        payload=payload,
        find_existing=lambda: (
            client.find_product_by_default_code(payload['default_code'])
            if payload.get('default_code') else None
        ),
        write=lambda oid, data: client.update_product(oid, data),
        create=lambda data: client.create_product(data),
        current_odoo_id=product.odoo_id,
    )

    if product.odoo_id != odoo_id:
        product.odoo_id = odoo_id
        product.save(update_fields=['odoo_id'])

    _touch_connection(connection, success=True)
    return odoo_id


def _touch_connection(connection: OdooConnection, *, success: bool, error: str = '') -> None:
    connection.last_sync_at = timezone.now()
    connection.last_sync_status = 'ok' if success else 'error'
    connection.last_sync_error = '' if success else error
    connection.save(update_fields=['last_sync_at', 'last_sync_status', 'last_sync_error'])


# ── Provider (proveedor del módulo providers) ───────────


def push_provider(provider, company, *, user=None) -> int:
    """Sincroniza un `providers.Provider` con Odoo (res.partner, supplier_rank=1).

    Reutiliza `ContactAdapter` mediante un proxy ligero que expone los
    campos compatibles.
    """
    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)
    adapter = ContactAdapter(client)

    proxy = _ProviderAsCustomer(provider)
    payload = adapter.to_odoo(proxy, company=company)

    odoo_id = _run_push(
        company=company, user=user,
        entity_type='provider', entity_id=str(provider.pk),
        payload=payload,
        find_existing=lambda: (
            client.find_partner_by_vat(payload['vat']) if payload.get('vat') else None
        ),
        write=lambda oid, data: client.update_partner(oid, data),
        create=lambda data: client.create_partner(data),
        current_odoo_id=provider.odoo_id,
    )

    if provider.odoo_id != odoo_id:
        provider.odoo_id = odoo_id
        provider.save(update_fields=['odoo_id'])

    _touch_connection(connection, success=True)
    return odoo_id


class _ProviderAsCustomer:
    """Proxy fino: presenta un Provider como si fuera un Customer (is_supplier=True)."""

    def __init__(self, provider):
        self._provider = provider

    def __getattr__(self, name):
        return getattr(self._provider, name)

    @property
    def is_customer(self):
        return False

    @property
    def is_supplier(self):
        return True


# ── Facturas de venta ────────────────────────────────────


def push_sales_invoice(invoice, company, *, post: bool = True, user=None) -> int:
    """Sincroniza una `invoices.Invoice` con Odoo.

    Args:
        invoice: instancia de `invoices.Invoice`.
        company: empresa propietaria.
        post: si True, confirma la factura en Odoo (state=posted) tras crearla.
              Solo se confirma si la factura del ERP está aprobada o más allá.
        user: usuario que dispara la operación (opcional, para SyncLog).

    Returns:
        ID en Odoo (`account.move.id`).

    Notas:
        - Idempotencia: si `invoice.odoo_id` está poblado y ya está posted
          en Odoo, se salta el write (las facturas conciliadas no se pueden
          modificar). Solo se crea si no tiene odoo_id.
    """
    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)
    adapter = SalesInvoiceAdapter(client)
    payload = adapter.to_odoo(invoice, company=company)

    # Si ya existe en Odoo y está confirmada, no intentamos write (daría RPCError)
    if invoice.odoo_id and _is_invoice_posted(client, invoice.odoo_id):
        odoo_id = invoice.odoo_id
        logger.debug('sales_invoice %s ya está posted en Odoo (%s); se salta write.', invoice.pk, odoo_id)
    else:
        odoo_id = _run_push(
            company=company, user=user,
            entity_type='sales_invoice', entity_id=str(invoice.pk),
            payload=payload,
            find_existing=lambda: None,
            write=lambda oid, data: client.update_invoice(oid, data),
            create=lambda data: client.create_invoice(data),
            current_odoo_id=invoice.odoo_id,
        )

    if invoice.odoo_id != odoo_id:
        invoice.odoo_id = odoo_id
        invoice.save(update_fields=['odoo_id'])

    # Confirmación: solo si el ERP la marcó como aprobada (o más allá)
    if post and invoice.status in ('Approved', 'PartiallyPaid', 'Paid'):
        posted = _post_invoice_safely(
            client, company, user,
            entity_type='sales_invoice', entity_id=str(invoice.pk),
            odoo_id=odoo_id,
        )
        # Tesorería simulada: cobro inmediato → el banco sube.
        if posted:
            _register_payment_safely(
                client, company, user,
                entity_type='sales_invoice', entity_id=str(invoice.pk),
                odoo_id=odoo_id,
            )

    _touch_connection(connection, success=True)
    return odoo_id


# ── Facturas de compra ───────────────────────────────────


def push_purchase_invoice(invoice, company, *, post: bool = False, user=None) -> int:
    """Sincroniza una `purchases.PurchaseInvoice` con Odoo (en draft por defecto)."""
    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)
    adapter = PurchaseInvoiceAdapter(client)
    payload = adapter.to_odoo(invoice, company=company)

    # Si ya existe en Odoo y está confirmada, no intentamos write (daría RPCError)
    if invoice.odoo_id and _is_invoice_posted(client, invoice.odoo_id):
        odoo_id = invoice.odoo_id
        logger.debug('purchase_invoice %s ya está posted en Odoo (%s); se salta write.', invoice.pk, odoo_id)
    else:
        odoo_id = _run_push(
            company=company, user=user,
            entity_type='purchase_invoice', entity_id=str(invoice.pk),
            payload=payload,
            find_existing=lambda: None,
            write=lambda oid, data: client.update_invoice(oid, data),
            create=lambda data: client.create_invoice(data),
            current_odoo_id=invoice.odoo_id,
        )

    if invoice.odoo_id != odoo_id:
        invoice.odoo_id = odoo_id
        invoice.save(update_fields=['odoo_id'])

    if post and invoice.status in ('Approved', 'PartiallyPaid', 'Paid'):
        posted = _post_invoice_safely(
            client, company, user,
            entity_type='purchase_invoice', entity_id=str(invoice.pk),
            odoo_id=odoo_id,
        )
        # Tesorería simulada: pago inmediato → el banco baja.
        if posted:
            _register_payment_safely(
                client, company, user,
                entity_type='purchase_invoice', entity_id=str(invoice.pk),
                odoo_id=odoo_id,
            )

    _touch_connection(connection, success=True)
    return odoo_id


def _is_invoice_posted(client: OdooClient, odoo_id: int) -> bool:
    """Comprova si una factura a Odoo ja està en estat 'posted' (confirmada).

    Retorna True si està posted o cancel (qualsevol estat que ja no es pot modificar).
    Retorna False si està en draft o si no es pot determinar (safe fallback).
    """
    try:
        invoice = client.get_invoice(odoo_id, ['state'])
        if invoice:
            return invoice.get('state') in ('posted', 'cancel')
    except Exception:  # noqa: BLE001
        pass
    return False


def _post_invoice_safely(
    client: OdooClient, company, user, *,
    entity_type: str, entity_id: str, odoo_id: int,
) -> bool:
    """Llama a `action_post` y registra el resultado, sin propagar fallos.

    Devuelve True si la factura quedó contabilizada.
    """
    start = time.monotonic()
    error = ''
    success = False
    response = None
    try:
        response = client.post_invoice(odoo_id)
        success = True
    except Exception as exc:  # noqa: BLE001
        error = f'{type(exc).__name__}: {exc}'
        logger.warning(
            'No se pudo confirmar la factura odoo_id=%s: %s', odoo_id, error,
        )
    finally:
        _log_operation(
            company=company, user=user,
            entity_type=entity_type, entity_id=entity_id,
            operation='PUSH', odoo_method='action_post',
            payload={}, odoo_id=odoo_id,
            success=success, response=response, error=error,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
    return success


def _register_payment_safely(
    client: OdooClient, company, user, *,
    entity_type: str, entity_id: str, odoo_id: int,
) -> None:
    """Registra el pago/cobro total de la factura (tesorería simulada).

    Mueve la cuenta de banco al instante. No propaga fallos.
    """
    bank = client.find_bank_journal()
    if not bank:
        logger.warning('Sin diario de banco; no se registra pago de odoo_id=%s', odoo_id)
        return

    start = time.monotonic()
    error = ''
    success = False
    response = None
    try:
        paid = client.register_invoice_payment(odoo_id, bank['id'])
        response = {'paid': paid}
        success = True
    except Exception as exc:  # noqa: BLE001
        error = f'{type(exc).__name__}: {exc}'
        logger.warning(
            'No se pudo registrar el pago de odoo_id=%s: %s', odoo_id, error,
        )
    finally:
        _log_operation(
            company=company, user=user,
            entity_type=entity_type, entity_id=entity_id,
            operation='PUSH', odoo_method='register_payment',
            payload={}, odoo_id=odoo_id,
            success=success, response=response, error=error,
            duration_ms=int((time.monotonic() - start) * 1000),
        )


# ── Pull de pagos / estado de cobros ────────────────────


PAYMENT_STATE_TO_STATUS = {
    'paid': 'Paid',
    'partial': 'PartiallyPaid',
    'in_payment': 'PartiallyPaid',
    'reversed': 'Voided',
    'not_paid': 'Approved',
}


def pull_invoice_payments(company, *, since=None, user=None) -> dict:
    """Actualiza el estado de cobro de facturas sincronizadas desde Odoo.

    Args:
        company: empresa.
        since: datetime mínimo. Si None, usa `connection.last_sync_at` o
               las últimas 24 h como fallback.

    Returns:
        dict con contadores: `{sales_updated, purchases_updated, errors}`.
    """
    from invoices.models import Invoice
    from purchases.models import PurchaseInvoice

    connection = OdooConnection.objects.get(company=company, is_active=True)
    client = get_client_for(connection)

    if since is None:
        since = connection.last_sync_at or (
            timezone.now() - timezone.timedelta(days=1)
        )

    start = time.monotonic()
    sales_updated = 0
    purchases_updated = 0
    errors = 0

    try:
        rows = client.list_invoices_since(
            since,
            move_types=['out_invoice', 'in_invoice', 'out_refund', 'in_refund'],
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception('pull_invoice_payments: list_invoices_since falló')
        _touch_connection(connection, success=False, error=str(exc))
        raise

    for row in rows:
        move_type = row.get('move_type')
        odoo_id = row.get('id')
        if move_type in ('out_invoice', 'out_refund'):
            invoice = Invoice.objects.filter(
                company=company, odoo_id=odoo_id,
            ).first()
            if invoice is None:
                continue  # ignoramos facturas externas (decisión Fase 1)
            try:
                if _apply_payment_state(invoice, row):
                    sales_updated += 1
            except Exception:  # noqa: BLE001
                errors += 1
                logger.exception('Fallo actualizando Invoice %s', invoice.pk)
        elif move_type in ('in_invoice', 'in_refund'):
            pinvoice = PurchaseInvoice.objects.filter(
                company=company, odoo_id=odoo_id,
            ).first()
            if pinvoice is None:
                continue
            try:
                if _apply_payment_state(pinvoice, row):
                    purchases_updated += 1
            except Exception:  # noqa: BLE001
                errors += 1
                logger.exception('Fallo actualizando PurchaseInvoice %s', pinvoice.pk)

    duration_ms = int((time.monotonic() - start) * 1000)
    _log_operation(
        company=company, user=user,
        entity_type='payments_pull', entity_id='',
        operation='PULL', odoo_method='search_read',
        payload={'since': since.isoformat()},
        odoo_id=None,
        success=errors == 0,
        response={
            'rows': len(rows),
            'sales_updated': sales_updated,
            'purchases_updated': purchases_updated,
            'errors': errors,
        },
        error='' if errors == 0 else f'{errors} fallos parciales',
        duration_ms=duration_ms,
    )

    _touch_connection(connection, success=errors == 0)
    return {
        'sales_updated': sales_updated,
        'purchases_updated': purchases_updated,
        'errors': errors,
        'rows': len(rows),
    }


def _apply_payment_state(invoice, row: dict) -> bool:
    """Actualiza paid_amount/balance_due/status de la factura. Devuelve True si cambió."""
    payment_state = row.get('payment_state') or 'not_paid'
    amount_total = from_odoo_decimal(row.get('amount_total'))
    amount_residual = from_odoo_decimal(row.get('amount_residual'))
    paid_amount = amount_total - amount_residual
    if paid_amount < Decimal('0'):
        paid_amount = Decimal('0')

    new_status = PAYMENT_STATE_TO_STATUS.get(payment_state)

    fields_to_update: list[str] = []
    if invoice.paid_amount != paid_amount:
        invoice.paid_amount = paid_amount
        fields_to_update.append('paid_amount')
    if invoice.balance_due != amount_residual:
        invoice.balance_due = amount_residual
        fields_to_update.append('balance_due')
    if new_status and invoice.status != new_status:
        invoice.status = new_status
        fields_to_update.append('status')

    if fields_to_update:
        invoice.save(update_fields=fields_to_update)
        return True
    return False
