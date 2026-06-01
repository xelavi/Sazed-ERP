from django.contrib import admin

from .models import EcommerceSyncLog, StoreConnection, StoreTaxMapping


@admin.register(StoreConnection)
class StoreConnectionAdmin(admin.ModelAdmin):
    list_display = ('company', 'platform', 'base_url', 'is_active', 'last_sync_status', 'last_sync_at')
    list_filter = ('platform', 'is_active', 'last_sync_status')
    search_fields = ('company__name', 'base_url')
    exclude = ('api_key',)  # nunca mostrar la key cifrada en el admin


@admin.register(StoreTaxMapping)
class StoreTaxMappingAdmin(admin.ModelAdmin):
    list_display = ('company', 'tax_rate', 'store_tax_id', 'store_tax_name')
    list_filter = ('company',)


@admin.register(EcommerceSyncLog)
class EcommerceSyncLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'operation', 'entity_type', 'entity_id', 'success', 'duration_ms')
    list_filter = ('operation', 'entity_type', 'success', 'company')
    search_fields = ('entity_id', 'error_message')
    readonly_fields = [f.name for f in EcommerceSyncLog._meta.fields]
