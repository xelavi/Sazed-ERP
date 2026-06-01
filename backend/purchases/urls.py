from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PurchaseSeriesViewSet, PurchaseInvoiceViewSet,
    PurchaseQuoteViewSet, PurchaseQuoteDocViewSet,
    RecurringPurchaseInvoiceViewSet,
)

router = DefaultRouter()
router.register(r'series', PurchaseSeriesViewSet)
router.register(r'quote-docs', PurchaseQuoteDocViewSet)
router.register(r'quotes', PurchaseQuoteViewSet)
router.register(r'recurring', RecurringPurchaseInvoiceViewSet)
router.register(r'', PurchaseInvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
