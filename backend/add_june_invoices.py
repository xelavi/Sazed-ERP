"""
Afegir factures de venda i compra al juny 2026 per simular un mes en curs
realista (som a dia 9, ~30% del mes).

Objectiu:
  - Venda juny: ~15.000 EUR (30% de ~47.000 que fa un mes normal)
  - Compra juny: ~10.000 EUR (mantenint ~30% marge)
  - Ja tenim: venda 4.990 + compra 3.200
  - Cal afegir: ~10.000 venda + ~6.800 compra
"""
from decimal import Decimal
from datetime import date, timedelta
from invoices.models import Invoice, InvoiceSeries
from purchases.models import PurchaseInvoice
from customers.models import Customer
from accounts.models import Company

sazed = Company.objects.get(name='Sazed')
serie = InvoiceSeries.objects.get(company=sazed, prefix='FAC')

# Clients i proveïdors reals
clients = list(Customer.objects.filter(company=sazed, is_supplier=False).order_by('?')[:6])
provs = list(Customer.objects.filter(company=sazed, is_supplier=True).order_by('?')[:4])

# ---------- FACTURES DE VENDA ----------
sales_data = [
    # (client_idx, number, status, subtotal, issue_day, paid)
    (0, 'FAC-2026-0093', 'Paid',    Decimal('2150.00'), 2, True),
    (1, 'FAC-2026-0094', 'Paid',    Decimal('1875.50'), 3, True),
    (2, 'FAC-2026-0095', 'Approved', Decimal('1420.00'), 5, False),
    (3, 'FAC-2026-0096', 'Approved', Decimal('980.75'),  6, False),
    (4, 'FAC-2026-0097', 'Paid',    Decimal('2340.00'), 7, True),
    (5, 'FAC-2026-0098', 'Approved', Decimal('1650.00'), 9, False),
]

created_sales = 0
for ci, number, status, subtotal, day, paid in sales_data:
    client = clients[ci % len(clients)]
    tax = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    total = subtotal + tax
    issue = date(2026, 6, day)
    due = issue + timedelta(days=30)

    Invoice.objects.create(
        company=sazed,
        series=serie,
        number=number,
        customer=client,
        customer_name_snapshot=client.name,
        status=status,
        issue_date=issue,
        due_date=due,
        subtotal=subtotal,
        tax_base=subtotal,
        total_tax=tax,
        total_amount=total,
        paid_amount=total if paid else Decimal('0'),
        balance_due=Decimal('0') if paid else total,
        is_template=False,
        currency='EUR',
    )
    created_sales += 1

# ---------- FACTURES DE COMPRA ----------
purch_data = [
    # (prov_idx, number, status, subtotal, issue_day, paid)
    (0, 'PC-2026-0141', 'Paid',     Decimal('1580.00'), 2, True),
    (1, 'PC-2026-0142', 'Approved', Decimal('1230.00'), 4, False),
    (2, 'PC-2026-0143', 'Approved', Decimal('890.50'),  6, False),
    (3, 'PC-2026-0144', 'Paid',     Decimal('1720.00'), 8, True),
    (0, 'PC-2026-0145', 'Approved', Decimal('960.00'),  9, False),
]

created_purch = 0
for pi, number, status, subtotal, day, paid in purch_data:
    prov = provs[pi % len(provs)]
    tax = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    total = subtotal + tax
    issue = date(2026, 6, day)
    due = issue + timedelta(days=30)

    PurchaseInvoice.objects.create(
        company=sazed,
        number=number,
        provider=prov,
        provider_name_snapshot=prov.name,
        status=status,
        issue_date=issue,
        due_date=due,
        subtotal=subtotal,
        tax_base=subtotal,
        total_tax=tax,
        total_amount=total,
        paid_amount=total if paid else Decimal('0'),
        balance_due=Decimal('0') if paid else total,
        is_template=False,
        currency='EUR',
    )
    created_purch += 1

# ---------- RESUM ----------
from django.db.models import Sum

total_venda_juny = Invoice.objects.filter(
    company=sazed, issue_date__year=2026, issue_date__month=6
).exclude(status='Voided').aggregate(t=Sum('total_amount'))['t'] or 0

total_compra_juny = PurchaseInvoice.objects.filter(
    company=sazed, issue_date__year=2026, issue_date__month=6
).exclude(status='Voided').aggregate(t=Sum('total_amount'))['t'] or 0

benefici = float(total_venda_juny) - float(total_compra_juny)
marge = benefici / float(total_venda_juny) * 100 if total_venda_juny else 0

print(f"Creades {created_sales} factures de venda i {created_purch} de compra al juny")
print(f"  Venda juny:  {float(total_venda_juny):>10.2f} EUR")
print(f"  Compra juny: {float(total_compra_juny):>10.2f} EUR")
print(f"  Benefici:    {benefici:>10.2f} EUR ({marge:.1f}% marge)")
