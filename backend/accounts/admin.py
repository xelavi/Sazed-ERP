from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Company, Membership, Role, SystemSettings


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    fk_name = 'user'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    inlines = [MembershipInline]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2'),
        }),
    )


class MembershipCompanyInline(admin.TabularInline):
    model = Membership
    extra = 0
    fk_name = 'company'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'tax_id', 'plan', 'created_at']
    list_filter = ['plan']
    search_fields = ['name', 'slug', 'tax_id']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MembershipCompanyInline]


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'role', 'custom_role', 'is_default', 'joined_at']
    list_filter = ['role', 'is_default']
    search_fields = ['user__email', 'company__name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'created_at']
    list_filter = ['company']
    search_fields = ['name', 'company__name']


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', '__str__', 'updated_at']
    search_fields = ['key']
    readonly_fields = ['updated_at']

    fieldsets = (
        (None, {
            'fields': ('key', 'value'),
            'description': 'Configuración del sistema. Cambios sin necesidad de reiniciar.'
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )
