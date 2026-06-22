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


class StoreFulSyncView(APIView):
    """`POST /api/integrations/store/full-sync/`.

    Sincronización completa ERP → PrestaShop para la empresa activa del usuario:
    1. Purga productos huérfanos de la tienda (no enlazados al ERP).
    2. Sube (crea o actualiza) todos los productos de la empresa, con imagen.
    3. Sube (crea o actualiza) todos los clientes de la empresa.

    Devuelve un resumen JSON: { purged, products_ok, products_err,
                                customers_ok, customers_err }.
    """

    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        from accounts.models import Company
        from .sync_service import full_sync_to_store
        from .models import StoreConnection

        # Determinar la empresa del usuario (la primera en la que es admin).
        admin_ids = _admin_company_ids(request.user)
        if not admin_ids:
            return Response(
                {'error': 'No ets administrador de cap empresa.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Permitir especificar company_id en el body; si no, usar la primera.
        company_id = request.data.get('company_id') or next(iter(admin_ids))
        if int(company_id) not in admin_ids:
            return Response(
                {'error': 'No tens permisos sobre aquesta empresa.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Empresa no trobada.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            result = full_sync_to_store(company, user=request.user)
            return Response(result)
        except StoreConnection.DoesNotExist:
            return Response(
                {'error': 'Aquesta empresa no té una botiga PrestaShop connectada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EcommerceConnectionError as exc:
            logger.warning('full-sync connection error: %s', exc)
            return Response({'error': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as exc:  # noqa: BLE001
            logger.exception('full-sync inesperat')
            return Response(
                {'error': f'{type(exc).__name__}: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

