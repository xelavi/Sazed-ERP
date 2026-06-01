"""ViewSets de la API de integración e-commerce."""
from __future__ import annotations

import logging

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Membership

from .clients import PrestaShopClient
from .clients.base import EcommerceConnectionError
from .models import EcommerceSyncLog, StoreConnection, StoreTaxMapping
from .permissions import IsCompanyAdmin
from .serializers import (
    EcommerceSyncLogSerializer,
    StoreConnectionSerializer,
    StoreConnectionUpdateSerializer,
    StoreTaxMappingSerializer,
    TestConnectionSerializer,
)

logger = logging.getLogger(__name__)


def _admin_company_ids(user) -> set[int]:
    return set(
        Membership.objects.filter(
            user=user, role__in=('owner', 'admin'),
        ).values_list('company_id', flat=True)
    )


class StoreConnectionViewSet(viewsets.ModelViewSet):
    """CRUD de StoreConnection (una por Company, gestionada por admins)."""

    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return StoreConnection.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return StoreConnectionUpdateSerializer
        return StoreConnectionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StoreTaxMappingViewSet(viewsets.ModelViewSet):
    serializer_class = StoreTaxMappingSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return StoreTaxMapping.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company', 'tax_rate')


class EcommerceSyncLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    serializer_class = EcommerceSyncLogSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return EcommerceSyncLog.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company', 'user')


class StoreTestConnectionView(APIView):
    """`POST /api/integrations/store/test-connection/`.

    Verifica credenciales SIN persistirlas. Devuelve el nombre de la tienda
    y los recursos accesibles con la API key.
    """

    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        serializer = TestConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data['platform'] != 'prestashop':
            return Response(
                {'ok': False, 'error': f"Plataforma '{data['platform']}' aún no soportada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = PrestaShopClient(base_url=data['base_url'], api_key=data['api_key'])
        try:
            result = client.test_connection()
            return Response(result)
        except EcommerceConnectionError as exc:
            return Response(
                {'ok': False, 'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('test-connection (store) inesperado')
            return Response(
                {'ok': False, 'error': f'{type(exc).__name__}: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
