"""Adaptador `order` de PrestaShop → `invoices.Invoice` del ERP.

Dirección única tienda → ERP: un pedido online se convierte en una
factura de venta. El detalle de líneas (`order_rows`/`order_details`) y
el matching de productos por `reference` se completará en la fase de
implementación del pull de pedidos.
"""
from __future__ import annotations

import logging
from typing import Any

from .base import from_store_decimal

logger = logging.getLogger(__name__)


class OrderAdapter:
    """Mapea un `order` de PrestaShop a los datos de una `Invoice` del ERP."""

    store_resource = 'orders'
    internal_id_field = 'prestashop_id'

    def from_store(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae la cabecera del pedido. Las líneas se procesan aparte."""
        return {
            'store_order_id': data.get('id'),
            'store_customer_id': data.get('id_customer'),
            'reference': data.get('reference') or '',
            'total_paid': from_store_decimal(data.get('total_paid')),
            'total_paid_tax_excl': from_store_decimal(data.get('total_paid_tax_excl')),
            'current_state': data.get('current_state'),
            'date_add': data.get('date_add'),
        }

    def to_store(self, obj: Any, *, company: Any = None) -> dict[str, Any]:  # pragma: no cover
        raise NotImplementedError('El ERP no crea pedidos en la tienda.')
