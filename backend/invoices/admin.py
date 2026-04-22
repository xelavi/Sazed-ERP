from django.contrib import admin

from .models import (
    InvoiceSeries, Invoice, InvoiceLine,
    InvoiceLineTax, Payment, InvoiceTimeline,
)


@admin.register(InvoiceSeries)
class InvoiceSeriesAdmin(admin.ModelAdmin):
    list_display = ['prefix', 'name', 'next_seq', 'is_default', 'active']
    list_filter = ['active', 'is_default']


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceTimelineInline(admin.TabularInline):
    model = InvoiceTimeline
    extra = 0
    readonly_fields = ['event_type', 'action', 'actor', 'date', 'created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'number', 'invoice_type', 'status', 'customer',
        'issue_date', 'due_date', 'total_amount', 'balance_due',
    ]
    list_filter = ['status', 'invoice_type', 'series']
    search_fields = ['number', 'customer__name']
    inlines = [InvoiceLineInline, PaymentInline, InvoiceTimelineInline]
    readonly_fields = [
        'locked_at', 'customer_name_snapshot',
        'customer_vat_snapshot', 'customer_address_snapshot',
    ]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'date', 'amount', 'method', 'reference']
    list_filter = ['method']
