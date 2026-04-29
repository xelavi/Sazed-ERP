from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PurchaseSeriesViewSet, PurchaseInvoiceViewSet, PurchaseQuoteViewSet

router = DefaultRouter()
router.register(r'series', PurchaseSeriesViewSet)
router.register(r'quotes', PurchaseQuoteViewSet)
router.register(r'', PurchaseInvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
