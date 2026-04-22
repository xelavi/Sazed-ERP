from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.dashboard import dashboard_summary, dashboard_wallet
from core.inventory import (
    inventory_overview, warehouse_stock, reorder_rules,
    create_reorder_rule, restock_product, movement_history,
    adjust_stock, transfer_stock, all_stock,
)
from invoices.views import mock_aeat_alta

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('core.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/products/', include('products.urls')),
    path('api/invoices/', include('invoices.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/dashboard/summary/', dashboard_summary, name='dashboard-summary'),
    path('api/dashboard/wallet/', dashboard_wallet, name='dashboard-wallet'),
    # Mock AEAT — VeriFactu
    path('api/mock-aeat/verifactu/alta', mock_aeat_alta, name='mock-aeat-alta'),
    # Inventory
    path('api/inventory/overview/', inventory_overview, name='inventory-overview'),
    path('api/inventory/warehouses/<int:warehouse_id>/stock/', warehouse_stock, name='warehouse-stock'),
    path('api/inventory/reorder-rules/', reorder_rules, name='reorder-rules'),
    path('api/inventory/reorder-rules/create/', create_reorder_rule, name='reorder-rule-create'),
    path('api/inventory/restock/', restock_product, name='restock-product'),
    path('api/inventory/adjust/', adjust_stock, name='inventory-adjust'),
    path('api/inventory/transfer/', transfer_stock, name='inventory-transfer'),
    path('api/inventory/stock/', all_stock, name='inventory-stock'),
    path('api/inventory/movements/', movement_history, name='movement-history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
