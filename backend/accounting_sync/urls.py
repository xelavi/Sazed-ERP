"""URLs de la integración Odoo."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OdooConnectionViewSet,
    OdooProvisioningJobViewSet,
    OdooSsoLoginView,
    OdooTaxMappingViewSet,
    OdooTestConnectionView,
    SyncLogViewSet,
)

router = DefaultRouter()
router.register(r'odoo/connections', OdooConnectionViewSet, basename='odoo-connection')
router.register(r'odoo/tax-mappings', OdooTaxMappingViewSet, basename='odoo-tax-mapping')
router.register(r'odoo/sync-logs', SyncLogViewSet, basename='odoo-sync-log')
router.register(r'odoo/provisioning', OdooProvisioningJobViewSet, basename='odoo-provisioning')

urlpatterns = [
    path('odoo/test-connection/', OdooTestConnectionView.as_view(), name='odoo-test-connection'),
    path('odoo/sso-login/', OdooSsoLoginView.as_view(), name='odoo-sso-login'),
    path('', include(router.urls)),
]
