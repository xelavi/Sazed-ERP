from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from core.excel import build_xlsx_response
from .models import Customer, CustomerNote, CustomerActivity, Quote
from .serializers import (
    CustomerListSerializer, CustomerDetailSerializer, CustomerWriteSerializer,
    CustomerNoteSerializer, CustomerActivitySerializer, QuoteSerializer,
)
from .filters import CustomerFilter


class CustomerViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    filterset_class = CustomerFilter
    ordering_fields = ['name', 'created_at', 'updated_at', 'city']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return CustomerWriteSerializer
        return CustomerDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete: marcar como Inactive en lugar de borrar."""
        customer = self.get_object()
        customer.status = 'Inactive'
        customer.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------- Export ----------

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Descarga el listado de clientes en XLSX."""
        qs = self.filter_queryset(self.get_queryset())
        headers = [
            'Nombre', 'Tipo', 'Estado', 'Email', 'Teléfono', 'Web',
            'NIF/CIF', 'Razón social', 'Dirección', 'Ciudad', 'Provincia',
            'Código postal', 'País', 'Método de pago', 'IBAN',
            'Total facturado', 'Creado', 'Actualizado',
        ]
        rows = []
        for c in qs:
            rows.append([
                c.name,
                c.get_contact_type_display() if c.contact_type else '',
                c.get_status_display() if c.status else '',
                c.email,
                c.phone,
                c.website,
                c.vat_id,
                c.legal_name,
                c.address,
                c.city,
                c.province,
                c.postal_code,
                c.country,
                c.payment_method,
                c.bank_account,
                c.total_invoiced,
                c.created_at.replace(tzinfo=None) if c.created_at else None,
                c.updated_at.replace(tzinfo=None) if c.updated_at else None,
            ])
        return build_xlsx_response('clientes', 'Clientes', headers, rows)

    # ---------- Nested routes ----------

    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        customer = self.get_object()
        if request.method == 'GET':
            notes = customer.notes.all()
            serializer = CustomerNoteSerializer(notes, many=True)
            return Response(serializer.data)
        # POST
        serializer = CustomerNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def activities(self, request, pk=None):
        customer = self.get_object()
        if request.method == 'GET':
            activities = customer.activities.all()
            serializer = CustomerActivitySerializer(activities, many=True)
            return Response(serializer.data)
        # POST
        serializer = CustomerActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def quotes(self, request, pk=None):
        customer = self.get_object()
        if request.method == 'GET':
            quotes = customer.quotes.all()
            serializer = QuoteSerializer(quotes, many=True)
            return Response(serializer.data)
        # POST
        serializer = QuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Devuelve las facturas del cliente (delegada a invoices app)."""
        customer = self.get_object()
        from invoices.serializers import InvoiceListSerializer
        invoices = customer.invoices.all()
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)
