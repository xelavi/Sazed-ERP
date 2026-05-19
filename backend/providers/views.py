from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from core.excel import build_xlsx_response
from .models import Provider, ProviderNote, ProviderActivity, PurchaseOrder
from .serializers import (
    ProviderListSerializer, ProviderDetailSerializer, ProviderWriteSerializer,
    ProviderNoteSerializer, ProviderActivitySerializer, PurchaseOrderSerializer,
)
from .filters import ProviderFilter


class ProviderViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    filterset_class = ProviderFilter
    ordering_fields = ['name', 'created_at', 'updated_at', 'city']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProviderListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProviderWriteSerializer
        return ProviderDetailSerializer

    def destroy(self, request, *args, **kwargs):
        provider = self.get_object()
        provider.status = 'Inactive'
        provider.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Descarga el listado de proveedores en XLSX."""
        qs = self.filter_queryset(self.get_queryset())
        headers = [
            'Nombre', 'Tipo', 'Estado', 'Email', 'Teléfono', 'Web',
            'NIF/CIF', 'Razón social', 'Dirección', 'Ciudad', 'Provincia',
            'Código postal', 'País', 'Método de pago', 'IBAN',
            'Total comprado', 'Saldo pendiente', 'Documentos',
            'Creado', 'Actualizado',
        ]
        rows = []
        for p in qs:
            rows.append([
                p.name,
                p.get_contact_type_display() if p.contact_type else '',
                p.get_status_display() if p.status else '',
                p.email,
                p.phone,
                p.website,
                p.vat_id,
                p.legal_name,
                p.address,
                p.city,
                p.province,
                p.postal_code,
                p.country,
                p.payment_method,
                p.bank_account,
                p.total_purchased,
                p.pending_balance,
                p.total_documents,
                p.created_at.replace(tzinfo=None) if p.created_at else None,
                p.updated_at.replace(tzinfo=None) if p.updated_at else None,
            ])
        return build_xlsx_response('proveedores', 'Proveedores', headers, rows)

    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        provider = self.get_object()
        if request.method == 'GET':
            notes = provider.notes.all()
            serializer = ProviderNoteSerializer(notes, many=True)
            return Response(serializer.data)
        serializer = ProviderNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def activities(self, request, pk=None):
        provider = self.get_object()
        if request.method == 'GET':
            activities = provider.activities.all()
            serializer = ProviderActivitySerializer(activities, many=True)
            return Response(serializer.data)
        serializer = ProviderActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='purchase-orders')
    def purchase_orders(self, request, pk=None):
        provider = self.get_object()
        if request.method == 'GET':
            orders = provider.purchase_orders.all()
            serializer = PurchaseOrderSerializer(orders, many=True)
            return Response(serializer.data)
        serializer = PurchaseOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(provider=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
