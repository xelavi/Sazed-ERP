"""
Servicio de sincronización ERP ↔ tienda e-commerce.

Push (ERP → tienda): productos y clientes, idempotente con `prestashop_id`
(si está vacío, se intenta enlazar por identificador natural — SKU/email —
antes de crear). Cada operación se audita en `EcommerceSyncLog`.

Pull (tienda → ERP): clientes y productos creados en la tienda, y pedidos
→ facturas (en estado Borrador para revisión antes de aprobar).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Callable

from django.db.models.signals import post_save
from django.utils import timezone

from .adapters import CustomerAdapter, ProductAdapter
from .clients import EcommerceClient, get_client_for
from .models import EcommerceSyncLog, StoreConnection

logger = logging.getLogger(__name__)


# ── Helpers ─────────────────────────────────────────────


def _payload_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def _excerpt(value: Any, limit: int = 500) -> str:
    text = repr(value) if not isinstance(value, str) else value
    return text[:limit]


def _log_operation(
    *, company, user, entity_type, entity_id, operation,
    method, payload, store_id, success, response, error, duration_ms,
) -> EcommerceSyncLog:
    return EcommerceSyncLog.objects.create(
        company=company, user=user,
        entity_type=entity_type, entity_id=str(entity_id),
        store_id=store_id, operation=operation, method=method,
        success=success,
        request_payload_hash=_payload_hash(payload) if payload else '',
        response_excerpt=_excerpt(response) if response else '',
        error_message=error, duration_ms=duration_ms,
    )


def _touch_connection(connection: StoreConnection, *, success: bool, error: str = '') -> None:
    connection.last_sync_at = timezone.now()
    connection.last_sync_status = 'ok' if success else 'error'
    connection.last_sync_error = '' if success else error
    connection.save(update_fields=['last_sync_at', 'last_sync_status', 'last_sync_error'])


def _run_push(
    *, company, user, entity_type, entity_id, payload,
    find_existing: Callable[[], int | None],
    write: Callable[[int, dict], None],
    create: Callable[[dict], int],
    current_store_id: int | None,
) -> int:
    """Lógica genérica de push idempotente con logging."""
    start = time.monotonic()
    store_id = current_store_id
    method = 'PUT' if current_store_id else 'POST'
    error = ''
    success = False
    response: Any = None
    try:
        if store_id:
            write(store_id, payload)
            response = {'id': store_id, 'written': True}
        else:
            existing = find_existing()
            if existing:
                method = 'PUT'
                write(existing, payload)
                store_id = existing
                response = {'id': existing, 'linked': True}
            else:
                method = 'POST'
                store_id = create(payload)
                response = {'id': store_id, 'created': True}
        success = True
        return store_id
    except Exception as exc:  # noqa: BLE001
        error = f'{type(exc).__name__}: {exc}'
        logger.exception('Push %s id=%s falló: %s', entity_type, entity_id, error)
        raise
    finally:
        _log_operation(
            company=company, user=user,
            entity_type=entity_type, entity_id=entity_id,
            operation='PUSH', method=method, payload=payload,
            store_id=store_id, success=success, response=response,
            error=error, duration_ms=int((time.monotonic() - start) * 1000),
        )


def _connection_for(company) -> StoreConnection:
    return StoreConnection.objects.get(company=company, is_active=True)


# ── Push: productos ─────────────────────────────────────


def push_product(product, company, *, user=None) -> int:
    """Sincroniza un `products.Product` con la tienda. Devuelve el id en la tienda."""
    connection = _connection_for(company)
    client: EcommerceClient = get_client_for(connection)
    adapter = ProductAdapter()
    payload = adapter.to_store(product, company=company)

    store_id = _run_push(
        company=company, user=user,
        entity_type='product', entity_id=str(product.pk), payload=payload,
        find_existing=lambda: client.find_product_by_reference(product.sku),
        write=lambda sid, data: client.update_product(sid, data),
        create=lambda data: client.create_product(data),
        current_store_id=product.prestashop_id,
    )

    if product.prestashop_id != store_id:
        product.prestashop_id = store_id
        product.save(update_fields=['prestashop_id'])

    # Stock (la tienda lo gestiona en stock_availables, no en el producto).
    if product.stock is not None:
        try:
            client.set_stock(store_id, int(product.stock))
        except Exception:  # noqa: BLE001
            logger.warning('No se pudo fijar stock del producto %s', product.pk)

    # Imagen principal (subida binaria, idempotente).
    _sync_product_image(client, product, store_id)

    _touch_connection(connection, success=True)
    return store_id


def _sync_product_image(client, product, store_id: int) -> None:
    """Sube la imagen principal del producto a PrestaShop si aún no la tiene.

    Idempotente: si el producto ya tiene imágenes en la tienda, no hace nada
    (evita re-subir en cada guardado). Cualquier fallo se registra sin romper
    la sincronización del producto.
    """
    image_field = getattr(product, 'image', None)
    if not image_field:
        return
    try:
        if client.list_product_image_ids(store_id):
            return  # ya tiene imagen en la tienda
        import mimetypes
        import os

        image_field.open('rb')
        try:
            data = image_field.read()
        finally:
            image_field.close()
        filename = os.path.basename(image_field.name) or f'product-{product.pk}.jpg'
        content_type = mimetypes.guess_type(filename)[0] or 'image/jpeg'
        client.upload_product_image(store_id, data, filename, content_type)
        logger.info('Imagen del producto %s subida a tienda (store#%s)', product.pk, store_id)
    except Exception:  # noqa: BLE001
        logger.warning('No se pudo subir la imagen del producto %s', product.pk)


# ── Push: clientes ──────────────────────────────────────


def push_customer(customer, company, *, user=None) -> int:
    """Sincroniza un `customers.Customer` con la tienda. Devuelve el id en la tienda."""
    connection = _connection_for(company)
    client: EcommerceClient = get_client_for(connection)
    adapter = CustomerAdapter()
    payload = adapter.to_store(customer, company=company)

    store_id = _run_push(
        company=company, user=user,
        entity_type='customer', entity_id=str(customer.pk), payload=payload,
        find_existing=lambda: (
            client.find_customer_by_email(customer.email) if customer.email else None
        ),
        write=lambda sid, data: client.update_customer(sid, data),
        create=lambda data: client.create_customer(data),
        current_store_id=customer.prestashop_id,
    )

    if customer.prestashop_id != store_id:
        customer.prestashop_id = store_id
        customer.save(update_fields=['prestashop_id'])

    _touch_connection(connection, success=True)
    return store_id


# ── Pull: pedidos → facturas (esqueleto) ────────────────


@contextmanager
def _suppress_push_signals():
    """Desconecta los signals de push mientras se importa desde la tienda.

    Sin esto, crear un Product/Customer en el ERP durante el pull dispararía
    el push de vuelta a la tienda (bucle / duplicados).
    """
    from customers.models import Customer
    from products.models import Product
    from .signals import sync_customer, sync_product

    post_save.disconnect(sync_product, sender=Product, dispatch_uid='ecom_sync_product')
    post_save.disconnect(sync_customer, sender=Customer, dispatch_uid='ecom_sync_customer')
    try:
        yield
    finally:
        post_save.connect(sync_product, sender=Product, dispatch_uid='ecom_sync_product')
        post_save.connect(sync_customer, sender=Customer, dispatch_uid='ecom_sync_customer')


def pull_customers(company, *, user=None) -> dict:
    """Importa al ERP los clientes de la tienda que aún no estén enlazados."""
    from customers.models import Customer

    connection = _connection_for(company)
    client = get_client_for(connection)
    adapter = CustomerAdapter()

    created = linked = 0
    with _suppress_push_signals():
        for data in client.list_customers():
            store_id = int(data.get('id'))
            if Customer.objects.filter(company=company, prestashop_id=store_id).exists():
                continue
            fields = adapter.from_store(data)
            email = fields.get('email')
            existing = (
                Customer.objects.filter(company=company, email=email).first()
                if email else None
            )
            if existing:
                existing.prestashop_id = store_id
                existing.save(update_fields=['prestashop_id'])
                linked += 1
            else:
                Customer.objects.create(
                    company=company, prestashop_id=store_id, **fields,
                )
                created += 1
    return {'created': created, 'linked': linked}


def pull_products(company, *, user=None) -> dict:
    """Importa al ERP los productos de la tienda que aún no estén enlazados."""
    from products.models import Product

    connection = _connection_for(company)
    client = get_client_for(connection)
    adapter = ProductAdapter()

    created = linked = 0
    with _suppress_push_signals():
        for data in client.list_products_full():
            store_id = int(data.get('id'))
            if Product.objects.filter(prestashop_id=store_id).exists():
                continue
            fields = adapter.from_store(data)
            sku = fields.get('sku') or f'PS-{store_id}'
            fields['sku'] = sku
            existing = Product.objects.filter(sku=sku).first()
            if existing:
                existing.prestashop_id = store_id
                existing.save(update_fields=['prestashop_id'])
                linked += 1
            else:
                Product.objects.create(
                    company=company, prestashop_id=store_id, **fields,
                )
                created += 1
    return {'created': created, 'linked': linked}


def pull_orders(company, *, since=None, user=None) -> dict:
    """Convierte los pedidos de la tienda en facturas (Borrador) del ERP.

    - Idempotente: ignora pedidos que ya tengan una `Invoice` con ese
      `prestashop_id`.
    - Resuelve el cliente por `prestashop_id` (lo crea si hace falta).
    - Mapea las líneas a productos del ERP por `prestashop_id`.
    - Crea la factura en estado **Borrador**: aprobarla (acto deliberado) es
      lo que dispara numeración fiscal / VeriFactu / push contable a Odoo.
    """
    from customers.models import Customer
    from invoices.models import Invoice, InvoiceLine, InvoiceSeries
    from products.models import Product

    connection = _connection_for(company)
    client = get_client_for(connection)

    if since is None:
        since = connection.last_sync_at or (timezone.now() - timedelta(days=365))

    series = (
        InvoiceSeries.objects.filter(company=company, is_default=True).first()
        or InvoiceSeries.objects.filter(company=company, active=True).first()
        or InvoiceSeries.objects.filter(company=company).first()
    )
    if series is None:
        raise ValueError(
            f'La empresa {company} no tiene ninguna serie de facturación; '
            'no se pueden crear facturas desde pedidos.'
        )

    orders = client.list_orders_since(since)
    created = skipped = 0
    errors = 0

    with _suppress_push_signals():
        for order in orders:
            store_id = int(order.get('id'))
            if Invoice.objects.filter(company=company, prestashop_id=store_id).exists():
                skipped += 1
                continue
            try:
                _create_invoice_from_order(
                    company, client, series, order, store_id,
                    Customer, Invoice, InvoiceLine, Product,
                )
                created += 1
            except Exception:  # noqa: BLE001
                errors += 1
                logger.exception('Fallo importando pedido PrestaShop %s', store_id)

    _touch_connection(connection, success=errors == 0)
    return {'created': created, 'skipped': skipped, 'errors': errors, 'orders': len(orders)}


def _create_invoice_from_order(
    company, client, series, order, store_id,
    Customer, Invoice, InvoiceLine, Product,
):
    """Crea una factura Borrador a partir de un pedido de la tienda."""
    # 1. Cliente: por prestashop_id; si no existe, importarlo.
    ps_customer_id = order.get('id_customer')
    customer = None
    if ps_customer_id:
        customer = Customer.objects.filter(
            company=company, prestashop_id=int(ps_customer_id),
        ).first()
    if customer is None:
        cust_data = client._request('GET', f'customers/{ps_customer_id}') if ps_customer_id else None
        adapter = CustomerAdapter()
        if cust_data is not None and cust_data.find('customer') is not None:
            fields = adapter.from_store(
                client._element_to_dict(cust_data.find('customer'))
            )
            customer = Customer.objects.create(
                company=company, prestashop_id=int(ps_customer_id), **fields,
            )
        else:
            customer, _ = Customer.objects.get_or_create(
                company=company, name='Cliente tienda online',
                defaults={'contact_type': 'Person'},
            )

    # 2. Fechas
    raw_date = (order.get('date_add') or '')[:10]
    try:
        issue = date.fromisoformat(raw_date) if raw_date else date.today()
    except ValueError:
        issue = date.today()

    # 3. Cabecera (Borrador, sin número aún)
    invoice = Invoice.objects.create(
        company=company, series=series, customer=customer,
        status='Draft', issue_date=issue, due_date=issue,
        payment_method='Card', currency=order.get('id_currency') and 'EUR' or 'EUR',
        prestashop_id=store_id,
        customer_notes=f'Pedido PrestaShop #{order.get("reference") or store_id}',
    )

    # 4. Líneas
    for i, row in enumerate(client.get_order_rows(store_id)):
        product = None
        if row.get('product_id'):
            product = Product.objects.filter(
                prestashop_id=int(row['product_id']),
            ).first()
        qty = Decimal(str(row.get('quantity') or '1'))
        unit = Decimal(str(row.get('unit_price_tax_excl') or '0'))
        InvoiceLine.objects.create(
            invoice=invoice, position=i, product=product,
            description=row.get('product_name') or (product.name if product else 'Artículo'),
            quantity=qty, unit_price=unit,
        )

    invoice.recalculate_totals()
    return invoice


def pull_all(company, *, user=None) -> dict:
    """Ejecuta el pull completo tienda → ERP: clientes, productos y pedidos."""
    return {
        'customers': pull_customers(company, user=user),
        'products': pull_products(company, user=user),
        'orders': pull_orders(company, user=user),
    }
