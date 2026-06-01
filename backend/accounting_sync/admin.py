"""Configuración del admin para accounting_sync."""
from django.contrib import admin

from .models import OdooConnection, OdooProvisioningJob, OdooTaxMapping, SyncLog


@admin.register(OdooConnection)
class OdooConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'base_url', 'database', 'username',
        'is_active', 'last_sync_status', 'last_sync_at',
    )
    list_filter = ('is_active', 'last_sync_status')
    search_fields = ('company__name', 'base_url', 'database', 'username')
    readonly_fields = (
        'last_sync_at', 'last_sync_status', 'last_sync_error',
        'created_at', 'updated_at', 'created_by',
    )
    # Nunca exponer la contraseña en list/detail más allá del campo de edición
    fields = (
        'company', 'base_url', 'database', 'username', 'password',
        'is_active',
        'last_sync_at', 'last_sync_status', 'last_sync_error',
        'created_by', 'created_at', 'updated_at',
    )


@admin.register(OdooTaxMapping)
class OdooTaxMappingAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'tax_rate', 'direction', 'odoo_tax_id', 'odoo_tax_name',
    )
    list_filter = ('direction', 'company')
    search_fields = (
        'company__name', 'tax_rate__name', 'odoo_tax_name',
    )


@admin.register(OdooProvisioningJob)
class OdooProvisioningJobAdmin(admin.ModelAdmin):
    list_display = (
        'company', 'status', 'database_name', 'attempts',
        'created_at', 'finished_at',
    )
    list_filter = ('status',)
    search_fields = ('company__name', 'database_name', 'error_message')
    readonly_fields = (
        'created_at', 'started_at', 'finished_at',
        'attempts', 'logs',
    )
    fields = (
        'company', 'status', 'database_name', 'admin_password',
        'attempts', 'max_attempts',
        'logs', 'error_message',
        'created_at', 'started_at', 'finished_at',
    )
    actions = ['requeue']

    @admin.action(description='Re-encolar como pending')
    def requeue(self, request, queryset):
        updated = queryset.update(
            status=OdooProvisioningJob.Status.PENDING,
            error_message='',
            attempts=0,
        )
        self.message_user(request, f'{updated} job(s) re-encolados.')


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'company', 'operation', 'entity_type', 'entity_id',
        'odoo_method', 'success', 'duration_ms',
    )
    list_filter = ('operation', 'success', 'entity_type', 'company')
    search_fields = ('entity_id', 'odoo_method', 'error_message')
    readonly_fields = tuple(
        f.name for f in SyncLog._meta.fields  # solo lectura: log inmutable
    )
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Permitir purgas manuales en admin
        return request.user.is_superuser
