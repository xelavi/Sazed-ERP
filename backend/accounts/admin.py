from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Company, Membership


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
    list_display = ['user', 'company', 'role', 'is_default', 'joined_at']
    list_filter = ['role', 'is_default']
    search_fields = ['user__email', 'company__name']
