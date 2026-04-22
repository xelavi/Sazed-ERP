from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaxRateViewSet, TagViewSet, WarehouseViewSet, SalesChannelViewSet

router = DefaultRouter()
router.register(r'tax-rates', TaxRateViewSet)
router.register(r'tags', TagViewSet)
router.register(r'warehouses', WarehouseViewSet)
router.register(r'sales-channels', SalesChannelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
