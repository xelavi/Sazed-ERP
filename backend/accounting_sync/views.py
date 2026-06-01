"""ViewSets de la API de integración Odoo."""
from __future__ import annotations

import logging

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Membership

from .models import OdooConnection, OdooProvisioningJob, OdooTaxMapping, SyncLog
from .odoo_client import OdooClient, OdooConnectionError
from .permissions import IsCompanyAdmin
from .serializers import (
    OdooConnectionSerializer,
    OdooConnectionUpdateSerializer,
    OdooProvisioningJobSerializer,
    OdooTaxMappingSerializer,
    SyncLogSerializer,
    TestConnectionSerializer,
)

logger = logging.getLogger(__name__)


def _admin_company_ids(user) -> set[int]:
    return set(
        Membership.objects.filter(
            user=user, role__in=('owner', 'admin'),
        ).values_list('company_id', flat=True)
    )


class OdooConnectionViewSet(viewsets.ModelViewSet):
    """CRUD de OdooConnection (una por Company, gestionada por admins)."""

    serializer_class = OdooConnectionSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return OdooConnection.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company')

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return OdooConnectionUpdateSerializer
        return OdooConnectionSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OdooTaxMappingViewSet(viewsets.ModelViewSet):
    """CRUD del mapeo de impuestos."""

    serializer_class = OdooTaxMappingSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return OdooTaxMapping.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company', 'tax_rate')


class SyncLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """Logs de sincronización (solo lectura)."""

    serializer_class = SyncLogSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        return SyncLog.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company', 'user')


class OdooProvisioningJobViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet,
):
    """Estado del provisioning automático (polling desde el frontend).

    GET /api/integrations/odoo/provisioning/?company_id=X
        Devuelve el job más reciente para esa company (cualquier estado).

    GET /api/integrations/odoo/provisioning/<id>/
        Detalle de un job concreto.
    """

    serializer_class = OdooProvisioningJobSerializer
    permission_classes = [IsCompanyAdmin]

    def get_queryset(self):
        qs = OdooProvisioningJob.objects.filter(
            company_id__in=_admin_company_ids(self.request.user),
        ).select_related('company').order_by('-created_at')
        company_id = self.request.query_params.get('company_id')
        if company_id:
            qs = qs.filter(company_id=company_id)
        return qs

    def list(self, request, *args, **kwargs):
        """Versión simplificada: devuelve solo el job más reciente."""
        qs = self.get_queryset()
        job = qs.first()
        if job is None:
            return Response(None)
        return Response(self.get_serializer(job).data)


class OdooSsoLoginView(APIView):
    """`POST /api/integrations/odoo/sso-login/`.

    Autentica del lado servidor contra `/web/session/authenticate` de Odoo
    (JSON-RPC, sin CSRF) y devuelve el `session_id` resultante. El frontend
    coloca esa cookie para `localhost` y abre Odoo ya autenticado, sin pasar
    por el formulario de login (que exigiría csrf_token).

    Las credenciales nunca salen del backend; solo viaja el session_id.
    """

    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        company_id = request.data.get('company_id')
        if not company_id:
            return Response(
                {'error': 'company_id requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if int(company_id) not in _admin_company_ids(request.user):
            return Response(
                {'error': 'No tienes permiso de admin en esa empresa.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            conn = OdooConnection.objects.get(company_id=company_id, is_active=True)
        except OdooConnection.DoesNotExist:
            return Response(
                {'error': 'No hay conexión Odoo activa para esa empresa. '
                          'Espera a que termine el aprovisionamiento.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        client = OdooClient(
            base_url=conn.base_url,
            database=conn.database,
            username=conn.username,
            password=conn.password,
        )
        try:
            session_id = client.web_session_id()
        except OdooConnectionError as exc:
            return Response(
                {'error': f'No se pudo iniciar sesión en Odoo: {exc}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        resp = Response({
            'base_url': conn.base_url.rstrip('/'),
            'redirect': '/web',
        })
        # Seteamos la cookie de sesión desde el servidor: a diferencia de
        # document.cookie (JS), un Set-Cookie de servidor SÍ sobrescribe la
        # cookie `session_id` HttpOnly que deja Odoo. Como Django y Odoo
        # comparten host (localhost, host-only sin domain), la cookie viaja
        # también a :8069 y el navegador entra autenticado.
        resp.set_cookie(
            'session_id', session_id,
            path='/', samesite='Lax', httponly=True, secure=False,
        )
        return resp


class OdooTestConnectionView(APIView):
    """`POST /api/integrations/odoo/test-connection/`.

    Verifica credenciales SIN persistirlas. Devuelve versión del servidor
    y si están instalados los módulos `l10n_es` / `l10n_es_aeat`.
    """

    permission_classes = [IsCompanyAdmin]

    def post(self, request):
        serializer = TestConnectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        client = OdooClient(
            base_url=data['base_url'],
            database=data['database'],
            username=data['username'],
            password=data['password'],
        )

        try:
            uid = client.connect()
            modules = client.list_modules_installed(['l10n_es', 'l10n_es_aeat'])
            return Response({
                'ok': True,
                'uid': uid,
                'server_version': client.server_version(),
                'modules': modules,
            })
        except OdooConnectionError as exc:
            return Response(
                {'ok': False, 'error': str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('test-connection inesperado')
            return Response(
                {'ok': False, 'error': f'{type(exc).__name__}: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
