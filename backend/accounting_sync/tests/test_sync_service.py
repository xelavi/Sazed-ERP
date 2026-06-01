"""Tests del servicio de sincronización: idempotencia, SyncLog, errores."""
from unittest.mock import MagicMock, patch

import pytest

from accounting_sync import sync_service
from accounting_sync.models import SyncLog


@pytest.fixture
def patched_client(monkeypatch, fake_client):
    """Hace que sync_service.get_client_for devuelva siempre fake_client."""
    monkeypatch.setattr(sync_service, 'get_client_for', lambda conn: fake_client)
    return fake_client


# ── push_contact ────────────────────────────────────────


@pytest.mark.django_db
def test_push_contact_creates_when_no_vat_match(odoo_connection, company, patched_client):
    from customers.models import Customer

    customer = Customer.objects.create(
        company=company, name='Nuevo cliente', contact_type='Company',
        vat_id='B11111111', is_customer=True,
    )
    patched_client._search.return_value = []  # no existe
    patched_client._create.return_value = 555

    odoo_id = sync_service.push_contact(customer, company)
    assert odoo_id == 555
    customer.refresh_from_db()
    assert customer.odoo_id == 555

    log = SyncLog.objects.get(entity_type='customer', entity_id=str(customer.pk))
    assert log.success is True
    assert log.odoo_method == 'create'
    assert log.odoo_id == 555


@pytest.mark.django_db
def test_push_contact_links_existing_by_vat(odoo_connection, company, patched_client):
    from customers.models import Customer
    customer = Customer.objects.create(
        company=company, name='Existente', contact_type='Company',
        vat_id='A12345674', is_customer=True,  # CIF válido (checksum OK)
    )
    # find_partner_by_vat → encuentra id 77
    patched_client._search.return_value = [77]

    odoo_id = sync_service.push_contact(customer, company)
    assert odoo_id == 77
    customer.refresh_from_db()
    assert customer.odoo_id == 77

    log = SyncLog.objects.get(entity_type='customer', entity_id=str(customer.pk))
    assert log.odoo_method == 'write'
    patched_client._write.assert_called_once()


@pytest.mark.django_db
def test_push_contact_updates_when_odoo_id_set(odoo_connection, company, patched_client):
    from customers.models import Customer
    customer = Customer.objects.create(
        company=company, name='Vinculado', contact_type='Company',
        vat_id='B33333333', is_customer=True, odoo_id=999,
    )

    odoo_id = sync_service.push_contact(customer, company)
    assert odoo_id == 999
    patched_client._write.assert_called_once()
    patched_client._search.assert_not_called()  # no busca, ya tiene id


@pytest.mark.django_db
def test_push_contact_logs_failure(odoo_connection, company, patched_client):
    from customers.models import Customer
    customer = Customer.objects.create(
        company=company, name='Fallido', contact_type='Company',
        vat_id='B44444444', is_customer=True,
    )
    patched_client._search.return_value = []
    patched_client._create.side_effect = RuntimeError('network down')

    with pytest.raises(RuntimeError):
        sync_service.push_contact(customer, company)

    log = SyncLog.objects.get(entity_type='customer', entity_id=str(customer.pk))
    assert log.success is False
    assert 'network down' in log.error_message


# ── push_product ────────────────────────────────────────


@pytest.mark.django_db
def test_push_product_links_by_sku(odoo_connection, company, patched_client):
    from products.models import Product
    product = Product.objects.create(
        company=company, sku='SKU-XYZ', name='Demo',
        product_type='Product', status='Active',
    )
    patched_client._search.return_value = [123]

    odoo_id = sync_service.push_product(product, company)
    assert odoo_id == 123
    product.refresh_from_db()
    assert product.odoo_id == 123


@pytest.mark.django_db
def test_push_product_creates_when_not_found(odoo_connection, company, patched_client):
    from products.models import Product
    product = Product.objects.create(
        company=company, sku='SKU-NEW', name='Nuevo',
        product_type='Product', status='Active',
    )
    patched_client._search.return_value = []
    patched_client._create.return_value = 321

    odoo_id = sync_service.push_product(product, company)
    assert odoo_id == 321
    product.refresh_from_db()
    assert product.odoo_id == 321
    log = SyncLog.objects.get(entity_type='product', entity_id=str(product.pk))
    assert log.odoo_method == 'create'


# ── Conexión inactiva ───────────────────────────────────


@pytest.mark.django_db
def test_push_contact_fails_without_active_connection(company, patched_client):
    from customers.models import Customer
    customer = Customer.objects.create(
        company=company, name='Sin conexión', contact_type='Person',
        is_customer=True,
    )
    with pytest.raises(Exception):  # OdooConnection.DoesNotExist
        sync_service.push_contact(customer, company)
