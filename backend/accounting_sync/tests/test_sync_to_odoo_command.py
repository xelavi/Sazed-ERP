"""Tests del comando sync_to_odoo."""
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.core.management import CommandError, call_command


@pytest.fixture
def patched_sync(monkeypatch):
    """Mockea sync_service.push_* y get_client_for para no tocar red."""
    from accounting_sync import sync_service

    calls = {'contact': 0, 'product': 0, 'provider': 0, 'sales': 0, 'purchase': 0}

    def fake_push_contact(c, comp, **kw):
        calls['contact'] += 1
        return 1
    def fake_push_provider(p, comp, **kw):
        calls['provider'] += 1
        return 2
    def fake_push_product(p, comp, **kw):
        calls['product'] += 1
        return 3
    def fake_push_sales(i, comp, **kw):
        calls['sales'] += 1
        return 4
    def fake_push_purchase(i, comp, **kw):
        calls['purchase'] += 1
        return 5

    monkeypatch.setattr(sync_service, 'push_contact', fake_push_contact)
    monkeypatch.setattr(sync_service, 'push_provider', fake_push_provider)
    monkeypatch.setattr(sync_service, 'push_product', fake_push_product)
    monkeypatch.setattr(sync_service, 'push_sales_invoice', fake_push_sales)
    monkeypatch.setattr(sync_service, 'push_purchase_invoice', fake_push_purchase)

    fake_client = MagicMock()
    fake_client.connect.return_value = 1
    fake_client.list_modules_installed.return_value = {
        'l10n_es': True, 'l10n_es_aeat': False,
    }
    monkeypatch.setattr(sync_service, 'get_client_for', lambda conn: fake_client)
    return calls


@pytest.mark.django_db
def test_sync_to_odoo_fails_without_connection(company):
    with pytest.raises(CommandError, match='OdooConnection'):
        call_command('sync_to_odoo', f'--company={company.id}')


@pytest.mark.django_db
def test_sync_to_odoo_processes_all_entities(
    odoo_connection, company, patched_sync, capsys,
):
    from customers.models import Customer
    from providers.models import Provider
    from products.models import Product

    Customer.objects.create(
        company=company, name='C1', contact_type='Company',
        vat_id='B1', is_customer=True,
    )
    Customer.objects.create(
        company=company, name='C2', contact_type='Person',
        is_customer=True,
    )
    Provider.objects.create(
        company=company, name='P1', contact_type='Company',
        vat_id='B2', email='p@e.com',
    )
    Product.objects.create(
        company=company, sku='SKU-A', name='A', product_type='Product',
    )

    call_command('sync_to_odoo', f'--company={company.id}', '--skip-invoices')

    assert patched_sync['contact'] == 2
    assert patched_sync['provider'] == 1
    assert patched_sync['product'] == 1
    out = capsys.readouterr().out
    assert 'Resumen' in out
    assert 'clientes:        2' in out


@pytest.mark.django_db
def test_sync_to_odoo_dry_run(odoo_connection, company, patched_sync):
    from customers.models import Customer

    Customer.objects.create(
        company=company, name='C-dry', contact_type='Company',
        vat_id='B-dry', is_customer=True,
    )

    call_command('sync_to_odoo', f'--company={company.id}', '--dry-run', '--skip-invoices')
    # En dry-run NO debe llamar a ningún push_*
    assert patched_sync['contact'] == 0
    assert patched_sync['provider'] == 0
    assert patched_sync['product'] == 0
