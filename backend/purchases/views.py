from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from accounts.mixins import CompanyMixin
from .models import (
    PurchaseInvoice, PurchasePayment, PurchaseQuoteDoc,
    PurchaseInvoiceLine, PurchaseInvoiceLineTax,
    PurchaseInvoiceTimeline, RecurringPurchaseInvoice,
)
from .serializers import (
    PurchaseInvoiceListSerializer, PurchaseInvoiceDetailSerializer,
    PurchaseInvoiceWriteSerializer,
    PurchasePaymentSerializer,
    PurchaseQuoteDocListSerializer, PurchaseQuoteDocDetailSerializer,
    PurchaseQuoteDocWriteSerializer,
    RecurringPurchaseInvoiceSerializer, RecurringPurchaseInvoiceCreateSerializer,
)
from .filters import PurchaseInvoiceFilter
from .services import PurchaseInvoiceService, RecurringPurchaseInvoiceService
from core.excel import build_xlsx_response


class PurchaseInvoiceViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = PurchaseInvoice.objects.select_related(
        'provider',
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
            'provider',
        ).prefetch_related(
            'lines', 'lines__taxes', 'payments', 'timeline',
        ).filter(is_template=False)
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(company=self.request.company)
        return qs.none()

    def perform_create(self, serializer):
        company = getattr(self.request, 'company', None)
        serializer.save(company=company)

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
                {'error': 'Només es poden editar factures en estat esborrany.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Només es poden editar factures en estat esborrany.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Només es poden eliminar esborranys.'},
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

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.filter_queryset(self.get_queryset())
        ids_param = request.query_params.get('ids')
        if ids_param:
            try:
                ids = [int(x) for x in ids_param.split(',') if x.strip()]
                qs = qs.filter(id__in=ids)
            except ValueError:
                pass

        headers = [
            'Número', 'Estat',
            'Proveïdor', 'NIF Proveïdor',
            'Data emissió', 'Data venciment',
            'Subtotal', 'IVA', 'Retenció', 'Total',
            'Pagat', 'Pendent', 'Moneda',
        ]
        rows = []
        for inv in qs:
            provider_name = (
                inv.provider.name if inv.provider_id else ''
            ) or inv.provider_name_snapshot
            provider_vat = inv.provider_vat_snapshot or (
                inv.provider.vat_id if inv.provider_id else ''
            )
            rows.append([
                inv.number or f'(Esborrany #{inv.pk})',
                inv.get_status_display() if inv.status else '',
                provider_name,
                provider_vat,
                inv.issue_date,
                inv.due_date,
                inv.subtotal,
                inv.total_tax,
                inv.total_retention,
                inv.total_amount,
                inv.paid_amount,
                inv.balance_due,
                inv.currency,
            ])
        return build_xlsx_response(
            'factures-compra', 'Factures compra', headers, rows,
        )


class RecurringPurchaseInvoiceViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = RecurringPurchaseInvoice.objects.select_related(
        'template', 'template__provider',
    ).all()
    serializer_class = RecurringPurchaseInvoiceSerializer
    pagination_class = None

    def get_queryset(self):
        qs = RecurringPurchaseInvoice.objects.select_related(
            'template', 'template__provider',
        ).all()
        if hasattr(self.request, 'company') and self.request.company:
            return qs.filter(company=self.request.company)
        return qs.none()

    def create(self, request, *args, **kwargs):
        ser = RecurringPurchaseInvoiceCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        source = data.pop('source_invoice')
        plan = RecurringPurchaseInvoiceService.create_plan(
            source, data, created_by=getattr(request.user, 'email', ''),
        )
        return Response(
            RecurringPurchaseInvoiceSerializer(plan).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        plan = self.get_object()
        template = plan.template
        plan.delete()
        if template and template.is_template:
            template.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        plan = self.get_object()
        if not plan.active:
            return Response(
                {'error': 'Aquest pla de recurrència no està actiu.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice = RecurringPurchaseInvoiceService.generate_one(plan)
        return Response({
            'plan': RecurringPurchaseInvoiceSerializer(plan).data,
            'invoice': PurchaseInvoiceDetailSerializer(invoice).data,
        }, status=status.HTTP_201_CREATED)


class PurchaseQuoteDocViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = PurchaseQuoteDoc.objects.select_related('provider').prefetch_related(
        'lines', 'lines__taxes',
    ).all()
    pagination_class = None

    def get_queryset(self):
        qs = PurchaseQuoteDoc.objects.select_related('provider').prefetch_related(
            'lines', 'lines__taxes',
        ).all()
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
                {'error': 'Aquest pressupost ja s\'ha convertit en factura.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.now().date()
        company = getattr(request, 'company', None)
        invoice = PurchaseInvoice.objects.create(
            invoice_type='Standard',
            status='Draft',
            company=company,
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
            for lt in ln.taxes.all():
                PurchaseInvoiceLineTax.objects.create(
                    invoice_line=new_line,
                    tax_rate=lt.tax_rate,
                    tax_name=lt.tax_name,
                    tax_percent=lt.tax_percent,
                    is_retention=lt.is_retention,
                    tax_amount=lt.tax_amount,
                )

        invoice.recalculate_totals()

        PurchaseInvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='created',
            action=f'Factura de compra creada des del pressupost «{quote.name}» (PQ-{quote.id})',
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
