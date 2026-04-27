from django.contrib import admin

from .models import Provider, ProviderNote, ProviderActivity, PurchaseOrder


class ProviderNoteInline(admin.TabularInline):
    model = ProviderNote
    extra = 0


class ProviderActivityInline(admin.TabularInline):
    model = ProviderActivity
    extra = 0


class PurchaseOrderInline(admin.TabularInline):
    model = PurchaseOrder
    extra = 0


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contact_type', 'email', 'city', 'status',
    ]
    list_filter = ['contact_type', 'status']
    search_fields = ['name', 'email', 'vat_id']
    inlines = [ProviderNoteInline, ProviderActivityInline, PurchaseOrderInline]


@admin.register(ProviderNote)
class ProviderNoteAdmin(admin.ModelAdmin):
    list_display = ['provider', 'author', 'created_at']


@admin.register(ProviderActivity)
class ProviderActivityAdmin(admin.ModelAdmin):
    list_display = ['provider', 'activity_type', 'subject', 'date']
    list_filter = ['activity_type']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'provider', 'concept', 'total_amount', 'status', 'date']
    list_filter = ['status']
    search_fields = ['number', 'concept']
