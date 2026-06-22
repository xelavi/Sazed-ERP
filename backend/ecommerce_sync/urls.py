"""URLs de la integración e-commerce."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EcommerceSyncLogViewSet,
    StoreFulSyncView,
    StoreConnectionViewSet,
    StoreTaxMappingViewSet,
    StoreTestConnectionView,
)

router = DefaultRouter()
router.register(r'store/connections', StoreConnectionViewSet, basename='store-connection')
router.register(r'store/tax-mappings', StoreTaxMappingViewSet, basename='store-tax-mapping')
router.register(r'store/sync-logs', EcommerceSyncLogViewSet, basename='store-sync-log')

urlpatterns = [
    path('store/test-connection/', StoreTestConnectionView.as_view(), name='store-test-connection'),
    path('store/full-sync/', StoreFulSyncView.as_view(), name='store-full-sync'),
    path('', include(router.urls)),
]
