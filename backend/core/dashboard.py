"""Dashboard API views — summary KPIs and wallet data."""

from datetime import date
from decimal import Decimal

from django.db.models import Sum, Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from customers.models import Customer
from invoices.models import Invoice, Payment


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
