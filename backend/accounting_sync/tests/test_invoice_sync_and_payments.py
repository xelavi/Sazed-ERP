"""Tests de push de facturas, push de provider y pull_invoice_payments."""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from accounting_sync import sync_service
from accounting_sync.models import SyncLog


@pytest.fixture
def patched_client(monkeypatch, fake_client):
    monkeypatch.setattr(sync_service, 'get_client_for', lambda conn: fake_client)
    return fake_client


# ── push_provider ───────────────────────────────────────


@pytest.mark.django_db
def test_push_provider_creates_with_supplier_rank(odoo_connection, company, patched_client):
    from providers.models import Provider

    provider = Provider.objects.create(
        company=company, name='Proveedor Nuevo', contact_type='Company',
        vat_id='B11112222', email='nuevo@example.com',
    )
    patched_client._search.return_value = []
    patched_client._create.return_value = 555

    odoo_id = sync_service.push_provider(provider, company)
    assert odoo_id == 555
    provider.refresh_from_db()
    assert provider.odoo_id == 555

    # Verifica que se envió como supplier_rank=1
    create_args = patched_client._create.call_args
    payload = create_args[0][1]
    assert payload['supplier_rank'] == 1
    assert payload['customer_rank'] == 0


# ── push_sales_invoice ──────────────────────────────────


@pytest.fixture
def approved_sale_invoice(db, company):
    from core.models import TaxRate
    from customers.models import Customer
    from invoices.models import Invoice, InvoiceLine, InvoiceSeries

    series = InvoiceSeries.objects.create(
        company=company, name='Default', prefix='FAC',
    )
    customer = Customer.objects.create(
        company=company, name='Cliente Aprob', contact_type='Company',
        vat_id='B22223333', is_customer=True, odoo_id=100,
    )
    invoice = Invoice.objects.create(
        company=company, series=series, customer=customer,
        issue_date=date(2026, 1, 5), due_date=date(2026, 2, 5),
        status='Approved', number='FAC-2026-0010',
    )
    InvoiceLine.objects.create(
        invoice=invoice, position=0, description='Servicio consultoría',
        quantity=Decimal('1'), unit_price=Decimal('100.00'),
    )
    return invoice


@pytest.mark.django_db
def test_push_sales_invoice_creates_and_posts(
    odoo_connection, company, patched_client, approved_sale_invoice,
):
    patched_client._create.return_value = 401
    patched_client.post_invoice = MagicMock(return_value=True)

    odoo_id = sync_service.push_sales_invoice(approved_sale_invoice, company)
    assert odoo_id == 401
    approved_sale_invoice.refresh_from_db()
    assert approved_sale_invoice.odoo_id == 401

    # Hubo un create + un action_post
    patched_client._create.assert_called_once()
    patched_client.post_invoice.assert_called_once_with(401)

    # Dos logs: create + action_post
    logs = SyncLog.objects.filter(
        entity_type='sales_invoice', entity_id=str(approved_sale_invoice.pk),
    ).order_by('id')
    assert logs.count() == 2
    assert {l.odoo_method for l in logs} == {'create', 'action_post'}


@pytest.mark.django_db
def test_push_sales_invoice_draft_does_not_post(
    odoo_connection, company, patched_client, approved_sale_invoice,
):
    approved_sale_invoice.status = 'Draft'
    approved_sale_invoice.save()
    patched_client._create.return_value = 402
    patched_client.post_invoice = MagicMock()

    sync_service.push_sales_invoice(approved_sale_invoice, company)
    patched_client.post_invoice.assert_not_called()


@pytest.mark.django_db
def test_push_sales_invoice_post_failure_is_logged_not_raised(
    odoo_connection, company, patched_client, approved_sale_invoice,
):
    patched_client._create.return_value = 403
    patched_client.post_invoice = MagicMock(side_effect=RuntimeError('not ready'))

    odoo_id = sync_service.push_sales_invoice(approved_sale_invoice, company)
    assert odoo_id == 403  # creación OK pese al fallo de post

    log = SyncLog.objects.get(
        entity_type='sales_invoice', odoo_method='action_post',
    )
    assert log.success is False
    assert 'not ready' in log.error_message


# ── push_purchase_invoice ───────────────────────────────


@pytest.fixture
def approved_purchase_invoice(db, company):
    from providers.models import Provider
    from purchases.models import PurchaseInvoice, PurchaseInvoiceLine, PurchaseSeries

    series = PurchaseSeries.objects.create(
        company=company, name='Default', prefix='PUR',
    )
    provider = Provider.objects.create(
        company=company, name='Prov X', contact_type='Company',
        vat_id='B33334444', odoo_id=300, email='x@e.com',
    )
    invoice = PurchaseInvoice.objects.create(
        series=series, provider=provider,
        issue_date=date(2026, 1, 8), due_date=date(2026, 2, 8),
        status='Approved', number='PUR-2026-0001',
    )
    PurchaseInvoiceLine.objects.create(
        invoice=invoice, position=0, description='Material',
        quantity=Decimal('2'), unit_price=Decimal('25.00'),
    )
    return invoice


@pytest.mark.django_db
def test_push_purchase_invoice_default_draft(
    odoo_connection, company, patched_client, approved_purchase_invoice,
):
    patched_client._create.return_value = 501
    patched_client.post_invoice = MagicMock()

    odoo_id = sync_service.push_purchase_invoice(approved_purchase_invoice, company)
    assert odoo_id == 501
    # Default post=False → no action_post
    patched_client.post_invoice.assert_not_called()


# ── pull_invoice_payments ───────────────────────────────


@pytest.mark.django_db
def test_pull_invoice_payments_updates_sales(
    odoo_connection, company, patched_client, approved_sale_invoice,
):
    approved_sale_invoice.odoo_id = 401
    approved_sale_invoice.total_amount = Decimal('100.00')
    approved_sale_invoice.balance_due = Decimal('100.00')
    approved_sale_invoice.save()

    patched_client.list_invoices_since = MagicMock(return_value=[{
        'id': 401, 'move_type': 'out_invoice', 'state': 'posted',
        'payment_state': 'paid',
        'amount_total': 100.0, 'amount_residual': 0.0,
    }])

    result = sync_service.pull_invoice_payments(company)
    assert result == {
        'sales_updated': 1, 'purchases_updated': 0, 'errors': 0, 'rows': 1,
    }
    approved_sale_invoice.refresh_from_db()
    assert approved_sale_invoice.status == 'Paid'
    assert approved_sale_invoice.balance_due == Decimal('0.00')
    assert approved_sale_invoice.paid_amount == Decimal('100.00')


@pytest.mark.django_db
def test_pull_invoice_payments_ignores_external(
    odoo_connection, company, patched_client,
):
    patched_client.list_invoices_since = MagicMock(return_value=[{
        'id': 9999, 'move_type': 'out_invoice', 'state': 'posted',
        'payment_state': 'paid',
        'amount_total': 50.0, 'amount_residual': 0.0,
    }])

    result = sync_service.pull_invoice_payments(company)
    # Factura externa (no existe en ERP con ese odoo_id) → ignorada
    assert result['sales_updated'] == 0


@pytest.mark.django_db
def test_pull_invoice_payments_partial_state(
    odoo_connection, company, patched_client, approved_sale_invoice,
):
    approved_sale_invoice.odoo_id = 401
    approved_sale_invoice.total_amount = Decimal('100.00')
    approved_sale_invoice.balance_due = Decimal('100.00')
    approved_sale_invoice.save()

    patched_client.list_invoices_since = MagicMock(return_value=[{
        'id': 401, 'move_type': 'out_invoice', 'state': 'posted',
        'payment_state': 'partial',
        'amount_total': 100.0, 'amount_residual': 40.0,
    }])

    sync_service.pull_invoice_payments(company)
    approved_sale_invoice.refresh_from_db()
    assert approved_sale_invoice.status == 'PartiallyPaid'
    assert approved_sale_invoice.paid_amount == Decimal('60.00')
    assert approved_sale_invoice.balance_due == Decimal('40.00')


@pytest.mark.django_db
def test_pull_uses_last_sync_at(
    odoo_connection, company, patched_client,
):
    odoo_connection.last_sync_at = timezone.now() - timedelta(hours=2)
    odoo_connection.save()
    patched_client.list_invoices_since = MagicMock(return_value=[])

    sync_service.pull_invoice_payments(company)
    args, _ = patched_client.list_invoices_since.call_args
    # primer arg = since
    assert args[0] == odoo_connection.last_sync_at


# ── Comando management ──────────────────────────────────


@pytest.mark.django_db
def test_pull_odoo_payments_command(
    odoo_connection, company, patched_client, monkeypatch, capsys,
):
    from django.core.management import call_command

    patched_client.list_invoices_since = MagicMock(return_value=[])
    call_command('pull_odoo_payments', f'--company={company.id}')
    out = capsys.readouterr().out
    assert 'pulling pagos' in out
    assert 'Total facturas actualizadas: 0' in out
