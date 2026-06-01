"""Adaptador `Product` ↔ `product.product`."""
from __future__ import annotations

import logging
from typing import Any

from ..models import OdooTaxMapping
from ..odoo_client import OdooClient
from .base import to_odoo_float

logger = logging.getLogger(__name__)


class ProductAdapter:
    """Mapea `products.Product` con `product.product` de Odoo."""

    odoo_model = 'product.product'
    internal_id_field = 'odoo_id'

    def __init__(self, client: OdooClient) -> None:
        self.client = client
        self._storable_type_cache: str | None = None

    # ── Helpers ─────────────────────────────────────────

    def _storable_type(self) -> str:
        """Devuelve `'product'` si Odoo tiene Inventory (`stock`) instalado,
        o `'consu'` (consumible) en caso contrario.

        Cacheado para no preguntar a Odoo en cada producto.
        """
        if self._storable_type_cache is None:
            try:
                installed = self.client.list_modules_installed(['stock'])
                self._storable_type_cache = (
                    'product' if installed.get('stock') else 'consu'
                )
            except Exception:  # noqa: BLE001
                # Si falla la consulta, jugamos seguro: 'consu' funciona siempre.
                logger.warning(
                    'No se pudo verificar el módulo "stock"; usando type=consu.'
                )
                self._storable_type_cache = 'consu'
        return self._storable_type_cache

    def _odoo_type(self, product_type: str) -> str:
        """Mapea `Product.product_type` a `product.product.type`."""
        if product_type == 'Service':
            return 'service'
        return self._storable_type()

    def _resolve_sale_taxes(self, product: Any, company: Any) -> list[int]:
        """Devuelve los IDs de account.tax (venta) mapeados al TaxRate del producto."""
        if not product.tax_rate_id or not company:
            return []
        mapping = OdooTaxMapping.objects.filter(
            company=company,
            tax_rate_id=product.tax_rate_id,
            direction='sale',
        ).first()
        if not mapping:
            logger.warning(
                'Producto %s sin OdooTaxMapping (sale) para tax_rate=%s; '
                'se enviará sin taxes_id.',
                product.sku, product.tax_rate_id,
            )
            return []
        return [mapping.odoo_tax_id]

    # ── Conversión ──────────────────────────────────────

    def to_odoo(self, product: Any, *, company: Any = None) -> dict[str, Any]:
        """Construye el payload `product.product` desde un Product del ERP."""
        data: dict[str, Any] = {
            'name': product.name,
            'default_code': product.sku,
            'type': self._odoo_type(product.product_type),
            'sale_ok': bool(product.sellable),
            'purchase_ok': bool(product.purchasable),
            'description_sale': product.description or False,
            'active': product.status == 'Active',
        }

        if product.price is not None:
            data['list_price'] = to_odoo_float(product.price)
        if product.cost is not None:
            data['standard_price'] = to_odoo_float(product.cost)

        tax_ids = self._resolve_sale_taxes(product, company)
        if tax_ids:
            # Sintaxis Odoo: (6, 0, [ids]) → reemplazar conjunto M2M
            data['taxes_id'] = [(6, 0, tax_ids)]

        return data

    def from_odoo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae campos útiles de un `product.product` para crear un Product."""
        return {
            'sku': data.get('default_code') or '',
            'name': data.get('name') or '',
            'description': data.get('description_sale') or '',
            'product_type': 'Service' if data.get('type') == 'service' else 'Product',
            'sellable': bool(data.get('sale_ok', True)),
            'purchasable': bool(data.get('purchase_ok', True)),
            'price': data.get('list_price') or 0,
            'cost': data.get('standard_price') or 0,
            'status': 'Active' if data.get('active', True) else 'Inactive',
        }
