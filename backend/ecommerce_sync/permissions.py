"""Permisos DRF para ecommerce_sync (idéntico criterio que accounting_sync)."""
from __future__ import annotations

from rest_framework.permissions import BasePermission

from accounts.models import Membership


class IsCompanyAdmin(BasePermission):
    """Permite la acción si el usuario es owner/admin de alguna company."""

    message = 'Necesitas rol de propietario o administrador en la empresa.'

    def _admin_company_ids(self, user) -> set[int]:
        return set(
            Membership.objects.filter(
                user=user, role__in=('owner', 'admin'),
            ).values_list('company_id', flat=True)
        )

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(self._admin_company_ids(request.user))

    def has_object_permission(self, request, view, obj) -> bool:
        company_id = getattr(obj, 'company_id', None) or getattr(
            getattr(obj, 'company', None), 'id', None,
        )
        if company_id is None:
            return False
        return company_id in self._admin_company_ids(request.user)
