from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    InvoiceSeriesViewSet, InvoiceViewSet, QuoteViewSet, mock_aeat_alta,
)

router = DefaultRouter()
router.register(r'series', InvoiceSeriesViewSet)
router.register(r'quotes', QuoteViewSet)
router.register(r'', InvoiceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
