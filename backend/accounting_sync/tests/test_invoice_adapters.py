"""Tests de adaptadores de facturas (Fase 2)."""
from datetime import date
from decimal import Decimal

import pytest

from accounting_sync.adapters import PurchaseInvoiceAdapter, SalesInvoiceAdapter


@pytest.fixture
def sale_invoice(db, company):
    from core.models import TaxRate
    from customers.models import Customer
    from invoices.models import Invoice, InvoiceLine, InvoiceLineTax, InvoiceSeries
    from products.models import Product
    from accounting_sync.models import OdooTaxMapping

    series = InvoiceSeries.objects.create(
        company=company, name='Default', prefix='FAC', is_default=True,
    )
    customer = Customer.objects.create(
        company=company, name='Cliente Demo', contact_type='Company',
        vat_id='B12345678', is_customer=True, odoo_id=42,
    )
    product = Product.objects.create(
        company=company, sku='SKU-1', name='Producto X',
        product_type='Product', status='Active', odoo_id=200,
    )
    tax = TaxRate.objects.create(
        company=company, name='IVA 21%', percent=Decimal('21'), tax_type='VAT',
    )
    OdooTaxMapping.objects.create(
        company=company, tax_rate=tax, direction='sale',
        odoo_tax_id=77, odoo_tax_name='IVA 21% (Venta)',
    )

    invoice = Invoice.objects.create(
        company=company, series=series, customer=customer,
        issue_date=date(2026, 1, 15), due_date=date(2026, 2, 15),
        status='Approved', number='FAC-2026-0001',
    )
    line = InvoiceLine.objects.create(
        invoice=invoice, position=0, product=product,
        description='Producto X', quantity=Decimal('2'),
        unit_price=Decimal('50.00'),
    )
    InvoiceLineTax.objects.create(
        invoice_line=line, tax_rate=tax, tax_name='IVA 21%',
        tax_percent=Decimal('21'), is_retention=False,
        tax_amount=Decimal('21.00'),
    )
    return invoice


@pytest.mark.django_db
def test_sales_adapter_basic(sale_invoice, fake_client, company):
    adapter = SalesInvoiceAdapter(fake_client)
    payload = adapter.to_odoo(sale_invoice, company=company)

    assert payload['move_type'] == 'out_invoice'
    assert payload['partner_id'] == 42
    assert payload['invoice_date'] == '2026-01-15'
    assert payload['invoice_date_due'] == '2026-02-15'
    assert payload['ref'] == 'FAC-2026-0001'

    # 1 línea, formato (0, 0, {...})
    assert len(payload['invoice_line_ids']) == 1
    cmd, _, line_data = payload['invoice_line_ids'][0]
    assert cmd == 0
    assert line_data['name'] == 'Producto X'
    assert line_data['quantity'] == 2.0
    assert line_data['price_unit'] == 50.0
    assert line_data['product_id'] == 200
    assert line_data['tax_ids'] == [(6, 0, [77])]


@pytest.mark.django_db
def test_sales_adapter_credit_note(sale_invoice, fake_client, company):
    sale_invoice.invoice_type = 'CreditNote'
    sale_invoice.save(update_fields=['invoice_type'])
    adapter = SalesInvoiceAdapter(fake_client)
    payload = adapter.to_odoo(sale_invoice, company=company)
    assert payload['move_type'] == 'out_refund'


@pytest.mark.django_db
def test_sales_adapter_requires_customer_odoo_id(sale_invoice, fake_client, company):
    sale_invoice.customer.odoo_id = None
    sale_invoice.customer.save(update_fields=['odoo_id'])
    adapter = SalesInvoiceAdapter(fake_client)
    with pytest.raises(ValueError, match='odoo_id'):
        adapter.to_odoo(sale_invoice, company=company)


@pytest.mark.django_db
def test_sales_adapter_skips_unmapped_tax(sale_invoice, fake_client, company, caplog):
    from accounting_sync.models import OdooTaxMapping
    OdooTaxMapping.objects.all().delete()

    adapter = SalesInvoiceAdapter(fake_client)
    with caplog.at_level('WARNING'):
        payload = adapter.to_odoo(sale_invoice, company=company)

    cmd, _, line_data = payload['invoice_line_ids'][0]
    assert 'tax_ids' not in line_data
    assert any('OdooTaxMapping' in r.message for r in caplog.records)


# ── PurchaseInvoiceAdapter ──────────────────────────────


@pytest.fixture
def purchase_invoice(db, company):
    from core.models import TaxRate
    from providers.models import Provider
    from purchases.models import (
        PurchaseInvoice, PurchaseInvoiceLine, PurchaseInvoiceLineTax, PurchaseSeries,
    )
    from accounting_sync.models import OdooTaxMapping

    series = PurchaseSeries.objects.create(
        company=company, name='Default', prefix='PUR', is_default=True,
    )
    provider = Provider.objects.create(
        company=company, name='Proveedor X', contact_type='Company',
        vat_id='B99999999', odoo_id=88, email='prov@example.com',
    )
    tax = TaxRate.objects.create(
        company=company, name='IVA 21% Compra', percent=Decimal('21'), tax_type='VAT',
    )
    OdooTaxMapping.objects.create(
        company=company, tax_rate=tax, direction='purchase',
        odoo_tax_id=99, odoo_tax_name='IVA 21% (Compra)',
    )

    invoice = PurchaseInvoice.objects.create(
        series=series, provider=provider,
        issue_date=date(2026, 1, 10), due_date=date(2026, 2, 10),
        status='Approved', number='PUR-2026-0001',
    )
    line = PurchaseInvoiceLine.objects.create(
        invoice=invoice, position=0, description='Material',
        quantity=Decimal('3'), unit_price=Decimal('15.50'),
    )
    PurchaseInvoiceLineTax.objects.create(
        invoice_line=line, tax_rate=tax, tax_name='IVA 21%',
        tax_percent=Decimal('21'), is_retention=False,
        tax_amount=Decimal('9.77'),
    )
    return invoice


@pytest.mark.django_db
def test_purchase_adapter_basic(purchase_invoice, fake_client, company):
    adapter = PurchaseInvoiceAdapter(fake_client)
    payload = adapter.to_odoo(purchase_invoice, company=company)

    assert payload['move_type'] == 'in_invoice'
    assert payload['partner_id'] == 88
    cmd, _, line_data = payload['invoice_line_ids'][0]
    assert line_data['quantity'] == 3.0
    assert line_data['price_unit'] == 15.50
    assert line_data['tax_ids'] == [(6, 0, [99])]


@pytest.mark.django_db
def test_purchase_adapter_requires_provider_odoo_id(purchase_invoice, fake_client, company):
    purchase_invoice.provider.odoo_id = None
    purchase_invoice.provider.save(update_fields=['odoo_id'])
    adapter = PurchaseInvoiceAdapter(fake_client)
    with pytest.raises(ValueError, match='odoo_id'):
        adapter.to_odoo(purchase_invoice, company=company)
