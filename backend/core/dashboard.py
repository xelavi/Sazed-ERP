"""Dashboard API views — summary KPIs, wallet and analytics."""

from datetime import date
from decimal import Decimal

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import Customer
from invoices.models import Invoice, InvoiceLine, Payment
from purchases.models import PurchaseInvoice


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """KPIs: total facturado, pendiente, nº facturas, nº clientes activos."""
    company = getattr(request, 'company', None)
    invoices = Invoice.objects.exclude(status__in=['Draft', 'Voided'])
    customers_qs = Customer.objects.all()
    if company:
        invoices = invoices.filter(company=company)
        customers_qs = customers_qs.filter(company=company)

    total_invoiced = invoices.aggregate(
        total=Sum('total_amount'),
    )['total'] or Decimal('0.00')

    pending = invoices.filter(
        status__in=['Approved', 'PartiallyPaid'],
    ).aggregate(
        total=Sum('balance_due'),
    )['total'] or Decimal('0.00')

    overdue = invoices.filter(
        status__in=['Approved', 'PartiallyPaid'],
        due_date__lt=date.today(),
    ).aggregate(
        total=Sum('balance_due'),
    )['total'] or Decimal('0.00')

    invoice_count = invoices.count()
    active_customers = customers_qs.filter(status='Active').count()

    return Response({
        'total_invoiced': total_invoiced,
        'pending_balance': pending,
        'overdue_balance': overdue,
        'invoice_count': invoice_count,
        'active_customers': active_customers,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_wallet(request):
    """Wallet: saldo disponible, pendiente, pagos recientes."""
    company = getattr(request, 'company', None)
    invoices_qs = Invoice.objects.all()
    payments_qs = Payment.objects.all()
    if company:
        invoices_qs = invoices_qs.filter(company=company)
        payments_qs = payments_qs.filter(invoice__company=company)

    paid = invoices_qs.filter(
        status='Paid',
    ).aggregate(
        total=Sum('total_amount'),
    )['total'] or Decimal('0.00')

    pending = invoices_qs.filter(
        status__in=['Approved', 'PartiallyPaid'],
    ).aggregate(
        total=Sum('balance_due'),
    )['total'] or Decimal('0.00')

    recent_payments = payments_qs.select_related(
        'invoice', 'invoice__customer',
    ).order_by('-date', '-created_at')[:10]

    payments_data = [
        {
            'id': p.id,
            'date': p.date,
            'amount': p.amount,
            'method': p.method,
            'reference': p.reference,
            'invoice_number': p.invoice.number,
            'customer_name': p.invoice.customer.name,
        }
        for p in recent_payments
    ]

    return Response({
        'available_balance': paid,
        'pending_balance': pending,
        'recent_payments': payments_data,
    })


# ── Analytics (for the Dashboards module) ────────────────────────────
MONTH_ABBR = ['', 'Gen', 'Feb', 'Mar', 'Abr', 'Mai', 'Jun',
              'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Des']


def _last_12_months():
    """Returns (labels, index_map, start_date) for the trailing 12 months."""
    today = date.today()
    seq = []
    for i in range(11, -1, -1):
        mm, yy = today.month - i, today.year
        while mm <= 0:
            mm += 12
            yy -= 1
        seq.append((yy, mm))
    labels = [MONTH_ABBR[mm] for _, mm in seq]
    index = {key: idx for idx, key in enumerate(seq)}
    start = date(seq[0][0], seq[0][1], 1)
    return labels, index, start


def _series_from(qs, date_field, value_field, index):
    """Buckets a queryset into a 12-slot monthly series."""
    out = [0.0] * 12
    rows = (
        qs.annotate(_m=TruncMonth(date_field))
        .values('_m')
        .annotate(_v=value_field)
        .order_by('_m')
    )
    for row in rows:
        m = row['_m']
        if m is None:
            continue
        key = (m.year, m.month)
        if key in index:
            out[index[key]] = round(float(row['_v'] or 0), 2)
    return out


def _breakdown(qs, group_field, value_field, label_empty='Sense assignar', top=6):
    """Top-N grouped breakdown with the remainder folded into 'Altres'."""
    rows = (
        qs.values(group_field)
        .annotate(_v=value_field)
        .order_by('-_v')
    )
    items = []
    for row in rows:
        val = round(float(row['_v'] or 0), 2)
        if val <= 0:
            continue
        label = row[group_field] or label_empty
        items.append({'label': str(label), 'value': val})
    if len(items) > top:
        head = items[:top]
        rest = sum(i['value'] for i in items[top:])
        if rest > 0:
            head.append({'label': 'Altres', 'value': round(rest, 2)})
        return head
    return items


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_analytics(request):
    """Real per-company analytics: 12-month series + breakdowns per metric."""
    company = getattr(request, 'company', None)
    labels, index, start = _last_12_months()

    # DEBUG — remove after fixing
    print(f'[DASHBOARD DEBUG] company={company} (id={company.id if company else None})')

    def scoped(qs):
        return qs.filter(company=company) if company else qs

    # Sales invoices (exclude drafts, voided and recurring templates)
    inv = scoped(Invoice.objects).filter(is_template=False).exclude(
        status__in=['Draft', 'Voided'],
    )
    inv_window = inv.filter(issue_date__gte=start)

    # Purchase invoices (expenses). Scoped by direct company FK.
    pur = PurchaseInvoice.objects.filter(is_template=False).exclude(
        status__in=['Draft', 'Voided'],
    )
    if company:
        pur = pur.filter(company=company)
    pur_window = pur.filter(issue_date__gte=start)

    # DEBUG — remove after fixing
    print(f'[DASHBOARD DEBUG] inv_window={inv_window.count()}, pur_window={pur_window.count()}')

    # Customers
    cust = scoped(Customer.objects)
    cust_window = cust.filter(created_at__date__gte=start)

    # Invoice lines within the sales window (for category / product breakdowns)
    lines = InvoiceLine.objects.filter(invoice__in=inv_window)

    # ── Monthly series ───────────────────────────────────────────────
    revenue = _series_from(inv_window, 'issue_date', Sum('total_amount'), index)
    inv_count = _series_from(inv_window, 'issue_date', Count('id'), index)
    expenses = _series_from(pur_window, 'issue_date', Sum('total_amount'), index)
    new_cust = _series_from(cust_window, 'created_at', Count('id'), index)
    units = _series_from(lines, 'invoice__issue_date', Sum('quantity'), index)

    profit = [round(revenue[i] - expenses[i], 2) for i in range(12)]
    avg_ticket = [
        round(revenue[i] / inv_count[i], 2) if inv_count[i] else 0.0
        for i in range(12)
    ]

    metrics = {
        'revenue': {
            'unit': 'currency', 'series': revenue,
            'breakdowns': {
                'category': _breakdown(lines, 'product__category__name', Sum('subtotal'), 'Sense categoria'),
                'product': _breakdown(lines, 'product__name', Sum('subtotal'), 'Sense producte', top=8),
                'region': _breakdown(inv_window, 'customer__province', Sum('total_amount'), 'Sense regió'),
                'customer': _breakdown(inv_window, 'customer__name', Sum('total_amount'), 'Sense client'),
            },
        },
        'expenses': {
            'unit': 'currency', 'series': expenses,
            'breakdowns': {
                'provider': _breakdown(pur_window, 'provider__name', Sum('total_amount'), 'Sense proveïdor'),
            },
        },
        'profit': {'unit': 'currency', 'series': profit, 'breakdowns': {}},
        'invoices': {
            'unit': 'number', 'series': inv_count,
            'breakdowns': {
                'status': _breakdown(inv_window, 'status', Count('id'), 'Sense estat', top=8),
            },
        },
        'new_customers': {
            'unit': 'number', 'series': new_cust,
            'breakdowns': {
                'region': _breakdown(cust, 'province', Count('id'), 'Sense regió'),
                'type': _breakdown(cust, 'contact_type', Count('id'), 'Altre', top=8),
            },
        },
        'avg_ticket': {'unit': 'currency', 'series': avg_ticket, 'breakdowns': {}},
        'units_sold': {
            'unit': 'number', 'series': units,
            'breakdowns': {
                'product': _breakdown(lines, 'product__name', Sum('quantity'), 'Sense producte', top=8),
                'category': _breakdown(lines, 'product__category__name', Sum('quantity'), 'Sense categoria'),
            },
        },
    }

    return Response({'months': labels, 'metrics': metrics})
