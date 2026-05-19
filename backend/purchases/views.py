from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from accounts.mixins import CompanyMixin
from .models import (
    PurchaseInvoice, PurchaseSeries, PurchasePayment, PurchaseQuote,
    PurchaseQuoteDoc, PurchaseInvoiceLine, PurchaseInvoiceLineTax,
    PurchaseInvoiceTimeline,
)
from .serializers import (
    PurchaseInvoiceListSerializer, PurchaseInvoiceDetailSerializer,
    PurchaseInvoiceWriteSerializer, PurchaseSeriesSerializer,
    PurchasePaymentSerializer, PurchaseQuoteSerializer,
    PurchaseQuoteDocListSerializer, PurchaseQuoteDocDetailSerializer,
    PurchaseQuoteDocWriteSerializer,
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


class PurchaseQuoteDocViewSet(CompanyMixin, viewsets.ModelViewSet):
    """Presupuestos de compra (con líneas y conversión a factura)."""

    queryset = PurchaseQuoteDoc.objects.select_related('provider').prefetch_related('lines').all()
    pagination_class = None

    def get_queryset(self):
        qs = PurchaseQuoteDoc.objects.select_related('provider').prefetch_related('lines').all()
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(company=self.request.company)
        return qs.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseQuoteDocListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return PurchaseQuoteDocWriteSerializer
        return PurchaseQuoteDocDetailSerializer

    def perform_create(self, serializer):
        company = getattr(self.request, 'company', None)
        if company:
            serializer.save(company=company)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], url_path='convert-to-invoice')
    def convert_to_invoice(self, request, pk=None):
        quote = self.get_object()
        if quote.converted_invoice_id:
            return Response(
                {'error': 'Este presupuesto ya se convirtió en factura.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        default_series = PurchaseSeries.objects.filter(
            company=getattr(request, 'company', None),
            is_default=True, active=True,
        ).first()
        if not default_series:
            default_series = PurchaseSeries.objects.filter(
                company=getattr(request, 'company', None), active=True,
            ).first()
        if not default_series:
            raise ValidationError('No hay serie de facturas de compra configurada.')

        today = timezone.now().date()
        invoice = PurchaseInvoice.objects.create(
            invoice_type='Standard',
            status='Draft',
            series=default_series,
            provider=quote.provider,
            issue_date=today,
            due_date=today + timedelta(days=30),
            currency=quote.currency,
            provider_notes=quote.provider_notes,
            internal_notes=quote.internal_notes,
        )

        for ln in quote.lines.all():
            new_line = PurchaseInvoiceLine.objects.create(
                invoice=invoice,
                position=ln.position,
                product=ln.product,
                description=ln.description,
                quantity=ln.quantity,
                unit_price=ln.unit_price,
            )
            if ln.tax_percent and ln.tax_percent > 0:
                from core.models import TaxRate
                rate = TaxRate.objects.filter(
                    rate=ln.tax_percent, is_retention=False,
                ).first()
                if rate:
                    PurchaseInvoiceLineTax.objects.create(
                        invoice_line=new_line,
                        tax_rate=rate,
                        tax_name=rate.name,
                        tax_percent=rate.rate,
                        is_retention=False,
                        tax_amount=ln.tax_amount,
                    )

        invoice.recalculate_totals()

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='created',
            action=f'Factura de compra creada desde presupuesto «{quote.name}» (PQ-{quote.id})',
            actor=getattr(request.user, 'email', 'System'),
            date=today,
        )

        quote.status = 'Converted'
        quote.converted_invoice = invoice
        quote.save(update_fields=['status', 'converted_invoice'])

        return Response(
            PurchaseQuoteDocDetailSerializer(quote).data,
            status=status.HTTP_201_CREATED,
        )
