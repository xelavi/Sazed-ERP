"""Adaptador `products.Product` ↔ `product` de PrestaShop."""
from __future__ import annotations

import logging
from typing import Any

from django.utils.text import slugify

from .base import from_store_decimal, lang, to_store_price

logger = logging.getLogger(__name__)

#: categoría por defecto (Inicio/Home) a la que se asocia todo producto
#: para que sea visible en el escaparate de PrestaShop.
DEFAULT_CATEGORY_ID = 2


class ProductAdapter:
    """Mapea `products.Product` con el recurso `product` de PrestaShop."""

    store_resource = 'products'
    internal_id_field = 'prestashop_id'

    def to_store(self, product: Any, *, company: Any = None) -> dict[str, Any]:
        """Construye el payload `product` desde un Product del ERP.

        Nota: el precio en PrestaShop (`price`) es SIN impuestos. Si el ERP
        guarda precio con IVA, usar `price_excl_tax` cuando esté disponible.
        """
        price = product.price_excl_tax if product.price_excl_tax is not None else product.price
        # `link_rewrite` (slug multilenguaje) es obligatorio al crear un
        # producto en PrestaShop; si falta, el POST es rechazado.
        slug = slugify(product.name) or f'producto-{product.sku}'.lower()
        payload: dict[str, Any] = {
            'reference': product.sku,
            'name': lang(product.name),
            'description': lang(product.description or ''),
            'link_rewrite': lang(slug),
            'price': to_store_price(price),
            'active': '1' if product.status == 'Active' else '0',
            'state': '1',
            # Visibilidad en el escaparate: sin categoría asociada un producto
            # no aparece en el front office, y debe poder mostrarse/comprarse.
            'id_category_default': str(DEFAULT_CATEGORY_ID),
            'category_ids': [DEFAULT_CATEGORY_ID],
            'available_for_order': '1',
            'show_price': '1',
            'visibility': 'both',
        }
        return payload

    def from_store(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae campos útiles de un `product` de PrestaShop para el ERP."""
        return {
            'sku': data.get('reference') or '',
            'name': data.get('name') or '',
            'description': data.get('description') or '',
            'price': from_store_decimal(data.get('price')),
            'status': 'Active' if str(data.get('active')) == '1' else 'Inactive',
        }
