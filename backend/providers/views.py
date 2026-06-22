from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
from core.excel import build_xlsx_response
from customers.models import Customer, CustomerNote, CustomerActivity
from customers.serializers import CustomerNoteSerializer, CustomerActivitySerializer
from .serializers import ProviderListSerializer, ProviderDetailSerializer, ProviderWriteSerializer
from .filters import ProviderFilter


class ProviderViewSet(CompanyMixin, viewsets.ModelViewSet):
    """
    Proveïdors = Customer(is_supplier=True).
    El model Provider ha estat fusionat amb Customer.
    """
    queryset = Customer.objects.all()
    filterset_class = ProviderFilter
    ordering_fields = ['name', 'created_at', 'updated_at', 'city']
    ordering = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_supplier=True)

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
        qs = self.filter_queryset(self.get_queryset())
        headers = [
            'Nom', 'Tipus', 'Estat', 'Email', 'Telèfon', 'Web',
            'NIF/CIF', 'Raó social', 'Adreça', 'Ciutat', 'Província',
            'Codi postal', 'País', 'Mètode de pagament', 'IBAN',
            'Creat', 'Actualitzat',
        ]
        rows = []
        for p in qs:
            rows.append([
                p.name,
                p.get_contact_type_display() if p.contact_type else '',
                p.get_status_display() if p.status else '',
                p.email, p.phone, p.website, p.vat_id, p.legal_name,
                p.address, p.city, p.province, p.postal_code, p.country,
                p.payment_method, p.bank_account,
                p.created_at.replace(tzinfo=None) if p.created_at else None,
                p.updated_at.replace(tzinfo=None) if p.updated_at else None,
            ])
        return build_xlsx_response('proveedors', 'Proveïdors', headers, rows)

    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        provider = self.get_object()
        if request.method == 'GET':
            serializer = CustomerNoteSerializer(provider.notes.all(), many=True)
            return Response(serializer.data)
        serializer = CustomerNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def activities(self, request, pk=None):
        provider = self.get_object()
        if request.method == 'GET':
            serializer = CustomerActivitySerializer(provider.activities.all(), many=True)
            return Response(serializer.data)
        serializer = CustomerActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=provider)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
