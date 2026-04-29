from django.contrib import admin

from .models import (
    PurchaseSeries, PurchaseInvoice, PurchaseInvoiceLine,
    PurchaseInvoiceLineTax, PurchasePayment, PurchaseInvoiceTimeline,
    PurchaseQuote,
)


@admin.register(PurchaseSeries)
class PurchaseSeriesAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'name', 'next_seq', 'is_default', 'active']
    list_filter = ['active', 'is_default']


class PurchaseInvoiceLineInline(admin.TabularInline):
    model = PurchaseInvoiceLine
    extra = 0


class PurchasePaymentInline(admin.TabularInline):
    model = PurchasePayment
    extra = 0


class PurchaseInvoiceTimelineInline(admin.TabularInline):
    model = PurchaseInvoiceTimeline
    extra = 0
    readonly_fields = ['event_type', 'action', 'actor', 'date', 'created_at']


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'number', 'invoice_type', 'status', 'provider',
        'issue_date', 'due_date', 'total_amount', 'balance_due',
    ]
    list_filter = ['status', 'invoice_type', 'series']
    search_fields = ['number', 'provider__name']
    inlines = [PurchaseInvoiceLineInline, PurchasePaymentInline, PurchaseInvoiceTimelineInline]
    readonly_fields = [
        'locked_at', 'provider_name_snapshot',
        'provider_vat_snapshot', 'provider_address_snapshot',
    ]


@admin.register(PurchasePayment)
class PurchasePaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'date', 'amount', 'method', 'reference']
    list_filter = ['method']


@admin.register(PurchaseQuote)
class PurchaseQuoteAdmin(admin.ModelAdmin):
    list_display = ['number', 'provider', 'concept', 'amount', 'status', 'date']
    list_filter = ['status']
    search_fields = ['number', 'concept']
