from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.mixins import CompanyMixin
from .models import TaxRate, Tag, Warehouse, SalesChannel
from .serializers import (
    TaxRateSerializer, TagSerializer,
    WarehouseSerializer, SalesChannelSerializer,
)


class TaxRateViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    filterset_fields = ['active', 'tax_type']
    search_fields = ['name']


class TagViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    search_fields = ['name']
    pagination_class = None  # Return all tags without pagination


class WarehouseViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filterset_fields = ['active']
    pagination_class = None

    def _check_admin(self):
        membership = getattr(self.request, 'membership', None)
        if not membership or membership.role not in ('owner', 'admin'):
            raise PermissionDenied('Only administrators can manage warehouses.')

    def perform_create(self, serializer):
        self._check_admin()
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self._check_admin()
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._check_admin()
        super().perform_destroy(instance)


class SalesChannelViewSet(CompanyMixin, viewsets.ModelViewSet):
    queryset = SalesChannel.objects.all()
    serializer_class = SalesChannelSerializer
    filterset_fields = ['active']
    pagination_class = None
