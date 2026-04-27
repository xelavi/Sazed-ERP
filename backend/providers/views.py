from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.mixins import CompanyMixin
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
