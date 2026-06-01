"""Adaptador `customers.Customer` ↔ `customer` de PrestaShop.

PrestaShop separa el cliente (`customer`: nombre/email) de su dirección
(`address`). Este adaptador cubre el `customer`; la sincronización de la
dirección fiscal se añadirá junto al flujo de pedidos.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CustomerAdapter:
    """Mapea `customers.Customer` con el recurso `customer` de PrestaShop."""

    store_resource = 'customers'
    internal_id_field = 'prestashop_id'

    @staticmethod
    def _split_name(full_name: str) -> tuple[str, str]:
        parts = (full_name or '').strip().split(' ', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return (parts[0] if parts else 'Cliente'), '.'

    def to_store(self, customer: Any, *, company: Any = None) -> dict[str, Any]:
        firstname, lastname = self._split_name(customer.name)
        payload: dict[str, Any] = {
            'firstname': firstname,
            'lastname': lastname,
            'email': customer.email or f'sin-email-{customer.pk}@local.invalid',
            'active': '1' if customer.status == 'Active' else '0',
        }
        return payload

    def from_store(self, data: dict[str, Any]) -> dict[str, Any]:
        firstname = (data.get('firstname') or '').strip()
        lastname = (data.get('lastname') or '').strip()
        name = ' '.join(p for p in (firstname, lastname) if p) or 'Cliente'
        return {
            'name': name,
            'email': data.get('email') or '',
            'contact_type': 'Person',
            'status': 'Active' if str(data.get('active')) == '1' else 'Inactive',
        }
