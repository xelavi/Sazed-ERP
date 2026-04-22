from django.contrib import admin

from .models import Customer, CustomerNote, CustomerActivity, Quote


class CustomerNoteInline(admin.TabularInline):
    model = CustomerNote
    extra = 0


class CustomerActivityInline(admin.TabularInline):
    model = CustomerActivity
    extra = 0


class QuoteInline(admin.TabularInline):
    model = Quote
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'contact_type', 'email', 'city', 'status',
        'is_customer', 'is_supplier',
    ]
    list_filter = ['contact_type', 'status', 'is_customer', 'is_supplier']
    search_fields = ['name', 'email', 'vat_id']
    inlines = [CustomerNoteInline, CustomerActivityInline, QuoteInline]


@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ['customer', 'author', 'created_at']


@admin.register(CustomerActivity)
class CustomerActivityAdmin(admin.ModelAdmin):
    list_display = ['customer', 'activity_type', 'subject', 'date']
    list_filter = ['activity_type']


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer', 'concept', 'amount', 'status', 'date']
    list_filter = ['status']
    search_fields = ['number', 'concept']
