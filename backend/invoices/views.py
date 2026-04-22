from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from .models import Invoice, InvoiceSeries, Payment, EventLog
from .serializers import (
    InvoiceListSerializer, InvoiceDetailSerializer, InvoiceWriteSerializer,
    InvoiceSeriesSerializer, PaymentSerializer,
)
from .filters import InvoiceFilter
from .services import InvoiceService
from .verifactu import MockAeatService, VeriFactuXmlGenerator, generate_invoice_pdf


def _get_client_ip(request) -> str:
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class InvoiceSeriesViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = InvoiceSeries.objects.all()
    serializer_class = InvoiceSeriesSerializer
    pagination_class = None


class InvoiceViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related(
        'customer', 'series',
    ).prefetch_related(
        'lines', 'lines__taxes', 'payments', 'timeline',
    ).all()
    filterset_class = InvoiceFilter
    ordering_fields = [
        'issue_date', 'due_date', 'total_amount',
        'status', 'created_at', 'number',
    ]
    ordering = ['-issue_date', '-id']

    def get_queryset(self):
        qs = Invoice.objects.select_related(
            'customer', 'series',
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
            return InvoiceListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return InvoiceWriteSerializer
        return InvoiceDetailSerializer

    # ── Regla de inalterabilidad (VeriFactu) ────────────
    def _check_immutable(self, invoice, action_label: str):
        """
        Si la factura ya tiene hash_actual bloquea la mutación y
        registra el intento en EventLog. Devuelve Response 403 o None.
        """
        if invoice.hash_actual:
            ip = _get_client_ip(self.request)
            usuario = getattr(self.request.user, 'email', 'anonymous')
            EventLog.objects.create(
                invoice=invoice,
                accion=action_label,
                detalles=(
                    f'Intento rechazado sobre factura sellada {invoice.number}. '
                    f'Acción: {action_label}'
                ),
                usuario=usuario,
                ip=ip,
            )
            return Response(
                {
                    'error': (
                        'Esta factura ya ha sido registrada en AEAT (VeriFactu) '
                        'y no puede modificarse. Para corregirla emite una '
                        'factura rectificativa (R1).'
                    ),
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def update(self, request, *args, **kwargs):
        invoice = self.get_object()
        blocked = self._check_immutable(invoice, 'Intento_Modificacion')
        if blocked:
            return blocked
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        invoice = self.get_object()
        blocked = self._check_immutable(invoice, 'Intento_Modificacion')
        if blocked:
            return blocked
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Solo se pueden eliminar borradores sin hash."""
        invoice = self.get_object()
        blocked = self._check_immutable(invoice, 'Intento_Borrado')
        if blocked:
            return blocked
        if invoice.status != 'Draft':
            return Response(
                {'error': 'Solo se pueden eliminar borradores.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- Business actions ----------

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        invoice = self.get_object()
        invoice = InvoiceService.approve(invoice)
        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def void(self, request, pk=None):
        invoice = self.get_object()
        InvoiceService.void(invoice)
        serializer = InvoiceDetailSerializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        invoice = self.get_object()
        new_invoice = InvoiceService.duplicate(invoice)
        serializer = InvoiceDetailSerializer(new_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def rectify(self, request, pk=None):
        invoice = self.get_object()
        credit_note = InvoiceService.create_credit_note(invoice)
        serializer = InvoiceDetailSerializer(credit_note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Marcar factura como enviada por email."""
        invoice = self.get_object()
        from .models import InvoiceTimeline
        from django.utils import timezone
        InvoiceTimeline.objects.create(
            invoice=invoice,
            event_type='sent',
            action='Factura enviada por email',
            actor='System',
            date=timezone.now().date(),
        )
        return Response({'status': 'sent'})

    # ── VeriFactu ────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='verifactu-submit')
    def verifactu_submit(self, request, pk=None):
        """
        Envía la factura al mock AEAT (VeriFactu).
        La factura debe estar aprobada y tener hash_actual.
        """
        invoice = self.get_object()
        if not invoice.hash_actual:
            return Response(
                {'error': 'La factura no está sellada. Apruébala primero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if invoice.estado_aeat == 'Aceptado':
            return Response(
                {'error': 'Esta factura ya fue aceptada por la AEAT.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = MockAeatService.submit(invoice)
        serializer = InvoiceDetailSerializer(invoice)
        return Response({**result, 'invoice': serializer.data})

    @action(detail=True, methods=['get'], url_path='verifactu-xml')
    def verifactu_xml(self, request, pk=None):
        """Devuelve el XML VeriFactu de la factura."""
        invoice = self.get_object()
        if not invoice.hash_actual:
            return Response(
                {'error': 'La factura no está sellada. Apruébala primero.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        xml_str = VeriFactuXmlGenerator.generate(invoice)
        return HttpResponse(xml_str, content_type='application/xml; charset=utf-8')

    # ── PDF ─────────────────────────────────────────────

    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Genera y descarga el PDF de la factura con QR VeriFactu."""
        invoice = self.get_object()
        try:
            pdf_bytes = generate_invoice_pdf(invoice)
        except ImportError as exc:
            return Response(
                {'error': str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        EventLog.objects.create(
            invoice=invoice,
            accion='Generacion_PDF',
            detalles=f'PDF generado para factura {invoice.number}',
            usuario=getattr(request.user, 'email', 'anonymous'),
            ip=_get_client_ip(request),
        )
        filename = f'factura-{invoice.number or invoice.pk}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # ---------- Nested: payments ----------

    @action(detail=True, methods=['get', 'post'])
    def payments(self, request, pk=None):
        invoice = self.get_object()
        if request.method == 'GET':
            payments = invoice.payments.all()
            serializer = PaymentSerializer(payments, many=True)
            return Response(serializer.data)
        payment = InvoiceService.record_payment(invoice, request.data)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------- Bulk actions ----------

    @action(detail=False, methods=['post'], url_path='bulk-approve')
    def bulk_approve(self, request):
        ids = request.data.get('ids', [])
        results = {'approved': [], 'errors': []}
        for invoice_id in ids:
            try:
                invoice = Invoice.objects.get(id=invoice_id)
                InvoiceService.approve(invoice)
                results['approved'].append(invoice_id)
            except Exception as e:
                results['errors'].append({'id': invoice_id, 'error': str(e)})
        return Response(results)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        deleted = Invoice.objects.filter(id__in=ids, status='Draft').delete()
        return Response({
            'deleted': deleted[0],
            'skipped': len(ids) - deleted[0],
        })


# ──────────────────────────────────────────────────────────────────────────────
#  FASE 4 — Mock AEAT endpoint (POST /api/mock-aeat/verifactu/alta)
# ──────────────────────────────────────────────────────────────────────────────

@api_view(['POST'])
def mock_aeat_alta(request):
    """
    Simula el endpoint de registro de facturas de la AEAT (VeriFactu).

    Acepta JSON o XML (text/xml, application/xml).
    Valida que existan los campos 'Huella' e 'ImporteTotal'.
    Devuelve siempre 200 OK simulando éxito.
    """
    import uuid

    content_type = request.content_type or ''
    if 'xml' in content_type:
        body = request.body.decode('utf-8', errors='replace')
    else:
        # Aceptar JSON con campo 'xml' o directamente el payload completo
        body = request.data.get('xml', str(request.data))

    if '<Huella>' not in body or '<ImporteTotal>' not in body:
        return Response(
            {
                'estado': 'Rechazado',
                'csv': None,
                'mensaje': 'Validación fallida: faltan campos Huella o ImporteTotal.',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    csv_mock = f'MOCK-CSV-{uuid.uuid4().hex[:9].upper()}'
    return Response({
        'estado': 'Aceptado',
        'csv': csv_mock,
        'mensaje': 'Registro procesado correctamente (Simulación)',
    })

