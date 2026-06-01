"""Tests de adaptadores Contact y Product."""
from decimal import Decimal

import pytest

from accounting_sync.adapters import ContactAdapter, ProductAdapter
from accounting_sync.adapters.base import (
    from_odoo_decimal,
    to_odoo_float,
)


# ── Helpers ──────────────────────────────────────────────


def test_to_odoo_float_rounding():
    assert to_odoo_float(Decimal('19.995')) == 20.00  # ROUND_HALF_EVEN
    assert to_odoo_float(Decimal('19.985')) == 19.98
    assert to_odoo_float(None) == 0.0
    assert to_odoo_float(19) == 19.0


def test_from_odoo_decimal():
    assert from_odoo_decimal(19.99) == Decimal('19.99')
    assert from_odoo_decimal(None) == Decimal('0.00')
    assert from_odoo_decimal(False) == Decimal('0.00')


# ── ContactAdapter ──────────────────────────────────────


class _CustomerStub:
    def __init__(self, **kwargs):
        defaults = dict(
            name='ACME', legal_name='ACME S.L.', contact_type='Company',
            vat_id='B12345678', email='info@acme.example', phone='+34911',
            website='https://acme.example', address='Calle 1', city='Madrid',
            postal_code='28001', country='España', is_customer=True,
            is_supplier=False, status='Active',
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


@pytest.mark.django_db
def test_contact_to_odoo_adds_es_prefix(fake_client):
    """CIF válido del banco de pruebas: A12345674 (mismo ejemplo de Odoo)."""
    adapter = ContactAdapter(fake_client)
    payload = adapter.to_odoo(_CustomerStub(vat_id='A12345674'), company=None)
    assert payload['vat'] == 'ESA12345674'
    assert payload['is_company'] is True
    assert payload['customer_rank'] == 1
    assert payload['supplier_rank'] == 0
    assert payload['country_id'] == 69


@pytest.mark.django_db
def test_contact_drops_invalid_checksum(fake_client, caplog):
    """B12345678 tiene la forma de un CIF pero checksum erróneo."""
    adapter = ContactAdapter(fake_client)
    with caplog.at_level('WARNING'):
        payload = adapter.to_odoo(_CustomerStub(vat_id='B12345678'), company=None)
    assert payload['vat'] is False or payload['vat'] == ''
    assert any('NIF/NIE/CIF' in r.message for r in caplog.records)


@pytest.mark.django_db
def test_contact_keeps_existing_country_prefix(fake_client):
    """ESA12345674 es un CIF válido (mismo ejemplo que usa Odoo)."""
    adapter = ContactAdapter(fake_client)
    payload = adapter.to_odoo(_CustomerStub(vat_id='ESA12345674'), company=None)
    assert payload['vat'] == 'ESA12345674'


@pytest.mark.django_db
def test_contact_person_is_not_company(fake_client):
    adapter = ContactAdapter(fake_client)
    payload = adapter.to_odoo(_CustomerStub(contact_type='Person'), company=None)
    assert payload['is_company'] is False


@pytest.mark.django_db
def test_contact_supplier_rank(fake_client):
    adapter = ContactAdapter(fake_client)
    payload = adapter.to_odoo(
        _CustomerStub(is_customer=False, is_supplier=True), company=None,
    )
    assert payload['supplier_rank'] == 1
    assert payload['customer_rank'] == 0


@pytest.mark.django_db
def test_contact_from_odoo(fake_client):
    from accounting_sync.tests.fixtures import PARTNER_RESPONSE
    adapter = ContactAdapter(fake_client)
    parsed = adapter.from_odoo(PARTNER_RESPONSE)
    assert parsed['name'] == 'ACME S.L.'
    assert parsed['vat_id'] == 'B12345678'
    assert parsed['contact_type'] == 'Company'
    assert parsed['is_customer'] is True


# ── ProductAdapter ──────────────────────────────────────


class _ProductStub:
    def __init__(self, **kwargs):
        defaults = dict(
            sku='SKU-1', name='Producto', description='desc',
            product_type='Product', sellable=True, purchasable=True,
            price=Decimal('19.99'), cost=Decimal('12.50'),
            status='Active', tax_rate_id=None,
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


@pytest.mark.django_db
def test_product_to_odoo_basic_with_stock(fake_client):
    """Si el módulo `stock` está instalado, mandamos type='product'."""
    fake_client.list_modules_installed = lambda names: {'stock': True}
    adapter = ProductAdapter(fake_client)
    payload = adapter.to_odoo(_ProductStub(), company=None)
    assert payload['default_code'] == 'SKU-1'
    assert payload['type'] == 'product'
    assert payload['list_price'] == 19.99
    assert payload['standard_price'] == 12.50
    assert 'taxes_id' not in payload  # sin mapping


@pytest.mark.django_db
def test_product_to_odoo_falls_back_to_consu_without_stock(fake_client):
    """Si `stock` no está instalado, caemos a type='consu'."""
    fake_client.list_modules_installed = lambda names: {'stock': False}
    adapter = ProductAdapter(fake_client)
    payload = adapter.to_odoo(_ProductStub(), company=None)
    assert payload['type'] == 'consu'


@pytest.mark.django_db
def test_product_service_type(fake_client):
    """Los servicios son siempre 'service' independientemente de stock."""
    fake_client.list_modules_installed = lambda names: {'stock': True}
    adapter = ProductAdapter(fake_client)
    payload = adapter.to_odoo(_ProductStub(product_type='Service'), company=None)
    assert payload['type'] == 'service'


@pytest.mark.django_db
def test_product_taxes_id_from_mapping(fake_client, company, db):
    from core.models import TaxRate
    from accounting_sync.models import OdooTaxMapping

    rate = TaxRate.objects.create(
        company=company, name='IVA 21%', percent=21, tax_type='VAT',
    )
    OdooTaxMapping.objects.create(
        company=company, tax_rate=rate, direction='sale',
        odoo_tax_id=11, odoo_tax_name='IVA 21% (Venta)',
    )

    product = _ProductStub(tax_rate_id=rate.id)
    adapter = ProductAdapter(fake_client)
    payload = adapter.to_odoo(product, company=company)
    assert payload['taxes_id'] == [(6, 0, [11])]


@pytest.mark.django_db
def test_product_from_odoo(fake_client):
    from accounting_sync.tests.fixtures import PRODUCT_RESPONSE
    adapter = ProductAdapter(fake_client)
    parsed = adapter.from_odoo(PRODUCT_RESPONSE)
    assert parsed['sku'] == 'SKU-001'
    assert parsed['product_type'] == 'Product'
    assert parsed['price'] == 19.99
