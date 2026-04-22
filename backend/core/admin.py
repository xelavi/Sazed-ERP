from django.contrib import admin

from .models import TaxRate, Tag, Warehouse, SalesChannel


@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'tax_type', 'percent', 'is_default', 'active']
    list_filter = ['tax_type', 'active', 'is_default']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'created_at']
    list_filter = ['active']


@admin.register(SalesChannel)
class SalesChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_filter = ['active']
