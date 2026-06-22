from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PurchaseInvoiceViewSet,
    PurchaseQuoteDocViewSet,
    RecurringPurchaseInvoiceViewSet,
)

router = DefaultRouter()
router.register(r'quote-docs', PurchaseQuoteDocViewSet)
router.register(r'recurring', RecurringPurchaseInvoiceViewSet)
router.register(r'', PurchaseInvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
