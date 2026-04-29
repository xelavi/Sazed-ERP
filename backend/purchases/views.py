from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from .models import PurchaseInvoice, PurchaseSeries, PurchasePayment, PurchaseQuote
from .serializers import (
    PurchaseInvoiceListSerializer, PurchaseInvoiceDetailSerializer,
    PurchaseInvoiceWriteSerializer, PurchaseSeriesSerializer,
    PurchasePaymentSerializer, PurchaseQuoteSerializer,
)
from .filters import PurchaseInvoiceFilter
from .services import PurchaseInvoiceService


class PurchaseSeriesViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = PurchaseSeries.objects.all()
    serializer_class = PurchaseSeriesSerializer
    pagination_class = None


class PurchaseInvoiceViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.select_related(
        'provider', 'series',
    ).prefetch_related(
        'lines', 'lines__taxes', 'payments', 'timeline',
    ).all()
    filterset_class = PurchaseInvoiceFilter
    ordering_fields = [
        'issue_date', 'due_date', 'total_amount',
        'status', 'created_at', 'number',
    ]
    ordering = ['-issue_date', '-id']

    def get_queryset(self):
        qs = PurchaseInvoice.objects.select_related(
            'provider', 'series',
        ).prefetch_related(
            'lines', 'lines__taxes', 'payments', 'timeline',
        ).all()
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(series__company=self.request.company)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseInvoiceListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return PurchaseInvoiceWriteSerializer
        return PurchaseInvoiceDetailSerializer

    def update(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Solo se pueden editar facturas en estado borrador.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Solo se pueden editar facturas en estado borrador.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Solo se pueden eliminar borradores.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        invoice = self.get_object()
        invoice = PurchaseInvoiceService.approve(invoice)
        serializer = PurchaseInvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        invoice = self.get_object()
        PurchaseInvoiceService.void(invoice)
        serializer = PurchaseInvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        invoice = self.get_object()
        new_invoice = PurchaseInvoiceService.duplicate(invoice)
        serializer = PurchaseInvoiceDetailSerializer(new_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def rectify(self, request, pk=None):
        invoice = self.get_object()
        credit_note = PurchaseInvoiceService.create_credit_note(invoice)
        serializer = PurchaseInvoiceDetailSerializer(credit_note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def payments(self, request, pk=None):
        invoice = self.get_object()
        if request.method == 'GET':
            payments = invoice.payments.all()
            serializer = PurchasePaymentSerializer(payments, many=True)
            return Response(serializer.data)
        payment = PurchaseInvoiceService.record_payment(invoice, request.data)
        serializer = PurchasePaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='bulk-approve')
    def bulk_approve(self, request):
        ids = request.data.get('ids', [])
        results = {'approved': [], 'errors': []}
        for invoice_id in ids:
            try:
                invoice = PurchaseInvoice.objects.get(id=invoice_id)
                PurchaseInvoiceService.approve(invoice)
                results['approved'].append(invoice_id)
            except Exception as e:
                results['errors'].append({'id': invoice_id, 'error': str(e)})
        return Response(results)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        deleted = PurchaseInvoice.objects.filter(id__in=ids, status='Draft').delete()
        return Response({
            'deleted': deleted[0],
            'skipped': len(ids) - deleted[0],
        })


class PurchaseQuoteViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = PurchaseQuote.objects.all()
    serializer_class = PurchaseQuoteSerializer
    pagination_class = None

    def get_queryset(self):
        qs = PurchaseQuote.objects.all()
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            qs = qs.filter(provider_id=provider_id)
        return qs
