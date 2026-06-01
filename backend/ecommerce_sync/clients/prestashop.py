"""
Cliente del Webservice de PrestaShop (REST/XML).

Autenticación: HTTP Basic con la API key como usuario y password vacío
(validado contra PrestaShop 8.1). Devuelve y consume XML; las rutas de
lectura están operativas, las de escritura construyen el XML del recurso
a partir de un dict (la traducción fina de campos vive en los adapters).
"""
from __future__ import annotations

import logging
import secrets
import xml.etree.ElementTree as ET
from typing import Any

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .base import EcommerceClient, EcommerceConnectionError

logger = logging.getLogger(__name__)

#: namespace xlink que PrestaShop usa en sus respuestas
_XLINK = '{http://www.w3.org/1999/xlink}'
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

#: campos de solo-lectura que PrestaShop rechaza en un PUT y hay que quitar
#: del documento antes de reenviarlo (read-modify-write).
_READONLY_FIELDS = {
    'manufacturer_name', 'quantity', 'position_in_category',
    'id_default_image', 'id_default_combination', 'new', 'cache_default_attribute',
    'date_add', 'date_upd', 'pack_stock_type', 'nb_downloadable',
}


class PrestaShopClient(EcommerceClient):
    """Cliente del Webservice de PrestaShop."""

    platform = 'prestashop'

    def __init__(self, base_url: str, api_key: str, timeout: int | None = None) -> None:
        self.base_url = base_url.rstrip('/')
        self.api_base = f'{self.base_url}/api'
        self._auth = HTTPBasicAuth(api_key, '')
        self.timeout = timeout or getattr(settings, 'ECOMMERCE_HTTP_TIMEOUT', 30)

    # ── Núcleo HTTP ─────────────────────────────────────

    @retry(
        retry=retry_if_exception_type(requests.exceptions.ConnectionError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, max=4),
        reraise=True,
    )
    def _request(
        self, method: str, path: str, *,
        params: dict | None = None, data: str | None = None,
    ) -> ET.Element | None:
        url = f'{self.api_base}/{path.lstrip("/")}' if path else f'{self.api_base}/'
        headers = {'Content-Type': 'text/xml', 'Accept': 'text/xml'}
        try:
            resp = requests.request(
                method, url, auth=self._auth, params=params,
                data=data.encode('utf-8') if data else None,
                headers=headers, timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise EcommerceConnectionError(f'Error de red con PrestaShop: {exc}') from exc

        if resp.status_code in (401, 403):
            raise EcommerceConnectionError(
                f'Autenticación rechazada por PrestaShop (HTTP {resp.status_code}). '
                'Revisa la API key y sus permisos.'
            )
        if resp.status_code == 404:
            return None
        if resp.status_code >= 400:
            raise EcommerceConnectionError(
                f'PrestaShop devolvió HTTP {resp.status_code}: {resp.text[:300]}'
            )
        if not resp.content:
            return None
        try:
            return ET.fromstring(resp.content)
        except ET.ParseError as exc:
            raise EcommerceConnectionError(
                f'Respuesta XML no parseable de PrestaShop: {exc}'
            ) from exc

    # ── Conexión ────────────────────────────────────────

    def test_connection(self) -> dict[str, Any]:
        root = self._request('GET', '')
        if root is None:
            raise EcommerceConnectionError('PrestaShop no devolvió la lista de recursos.')
        api = root.find('api')
        shop_name = api.get('shopName') if api is not None else None
        resources = [child.tag for child in api] if api is not None else []
        return {'ok': True, 'shop_name': shop_name, 'resources': resources}

    # ── Helpers XML ─────────────────────────────────────

    @staticmethod
    def _ids_from_list(root: ET.Element | None, tag: str) -> list[int]:
        if root is None:
            return []
        return [int(el.get('id')) for el in root.iter(tag) if el.get('id')]

    @staticmethod
    def _created_id(root: ET.Element | None, singular: str) -> int | None:
        """Lee el id de la respuesta de un POST.

        Al crear, PrestaShop devuelve el recurso completo con el id como
        elemento hijo (`<product><id>20</id>…`), no como atributo.
        """
        if root is None:
            return None
        el = root.find(singular)
        if el is None:
            return None
        id_el = el.find('id')
        if id_el is not None and id_el.text and id_el.text.isdigit():
            return int(id_el.text)
        if el.get('id'):
            return int(el.get('id'))
        return None

    @staticmethod
    def _element_to_dict(el: ET.Element) -> dict[str, Any]:
        """Aplana un elemento de recurso PrestaShop a dict.

        Los campos multilenguaje (con <language>) se reducen al primer idioma.
        """
        out: dict[str, Any] = {}
        for child in el:
            lang = child.find('language')
            if lang is not None:
                out[child.tag] = lang.text
            elif len(child) == 0:
                out[child.tag] = child.text
            # asociaciones anidadas se ignoran en este helper base
        return out

    @staticmethod
    def _set_categories(el: ET.Element, category_ids: list[int]) -> None:
        """Fija las categorías asociadas del recurso (associations/categories).

        Un producto sin categoría no aparece en el front office de PrestaShop.
        """
        assoc = el.find('associations')
        if assoc is None:
            assoc = ET.SubElement(el, 'associations')
        old = assoc.find('categories')
        if old is not None:
            assoc.remove(old)
        cats = ET.SubElement(assoc, 'categories')
        for cid in category_ids:
            cat = ET.SubElement(cats, 'category')
            ET.SubElement(cat, 'id').text = str(cid)

    @staticmethod
    def _apply_changes(el: ET.Element, changes: dict[str, Any]) -> None:
        """Aplica cambios sobre un elemento de recurso ya existente (in-place).

        Soporta valores escalares, la convención multilenguaje {id_lang: texto}
        y la clave especial `category_ids` (lista) para las asociaciones.
        """
        for key, value in changes.items():
            if key == 'id' or value is None:
                continue
            if key == 'category_ids':
                PrestaShopClient._set_categories(el, value)
                continue
            child = el.find(key)
            if child is None:
                child = ET.SubElement(el, key)
            for sub in list(child):
                child.remove(sub)
            if isinstance(value, dict):
                child.text = None
                for lid, v in value.items():
                    lang_el = ET.SubElement(child, 'language')
                    lang_el.set('id', str(lid))
                    lang_el.text = str(v)
            else:
                child.text = str(value)

    def _read_modify_write(
        self, resource: str, singular: str, store_id: int, changes: dict[str, Any],
    ) -> None:
        """Patrón canónico de update en PrestaShop: GET completo → editar → PUT.

        Evita los errores "parameter X required" en PUT (PrestaShop espera el
        recurso completo) y preserva campos como `passwd`.
        """
        root = self._request('GET', f'{resource}/{store_id}')
        if root is None:
            raise EcommerceConnectionError(
                f'No existe {singular} #{store_id} en PrestaShop para actualizar.'
            )
        el = root.find(singular)
        if el is None:
            raise EcommerceConnectionError(f'Respuesta inesperada al leer {singular}.')
        # Quitar campos de solo-lectura que el PUT rechazaría.
        for ro in _READONLY_FIELDS:
            ro_el = el.find(ro)
            if ro_el is not None:
                el.remove(ro_el)
        self._apply_changes(el, changes)
        xml = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding='unicode')
        self._request('PUT', f'{resource}/{store_id}', data=xml)

    def _build_resource_xml(self, singular: str, payload: dict[str, Any]) -> str:
        """Convierte un dict en el XML de un recurso PrestaShop (vía ElementTree).

        Reutiliza `_apply_changes`, por lo que soporta escalares, multilenguaje
        ({id_lang: texto}) y `category_ids`. ElementTree se encarga del escape.
        """
        root = ET.Element('prestashop')
        el = ET.SubElement(root, singular)
        self._apply_changes(el, payload)
        return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding='unicode')

    # ── Productos ───────────────────────────────────────

    def list_products(self, **filters) -> list[dict[str, Any]]:
        params = {'display': 'full', **self._as_ps_filters(filters)}
        root = self._request('GET', 'products', params=params)
        if root is None:
            return []
        return [self._element_to_dict(p) for p in root.iter('product')]

    def get_product(self, store_id: int) -> dict[str, Any]:
        root = self._request('GET', f'products/{store_id}')
        if root is None:
            return {}
        prod = root.find('product')
        return self._element_to_dict(prod) if prod is not None else {}

    def find_product_by_reference(self, reference: str) -> int | None:
        root = self._request(
            'GET', 'products', params={'filter[reference]': f'[{reference}]'},
        )
        ids = self._ids_from_list(root, 'product')
        return ids[0] if ids else None

    def create_product(self, payload: dict[str, Any]) -> int:
        xml = self._build_resource_xml('product', payload)
        root = self._request('POST', 'products', data=xml)
        new_id = self._created_id(root, 'product')
        if new_id is None:
            raise EcommerceConnectionError('PrestaShop no devolvió id al crear el producto.')
        return new_id

    def update_product(self, store_id: int, payload: dict[str, Any]) -> None:
        self._read_modify_write('products', 'product', store_id, payload)

    def set_stock(self, store_id: int, quantity: int) -> None:
        root = self._request(
            'GET', 'stock_availables',
            params={'filter[id_product]': str(store_id)},
        )
        ids = self._ids_from_list(root, 'stock_available')
        if not ids:
            logger.warning('Sin stock_available para producto %s', store_id)
            return
        sa_id = ids[0]
        self._read_modify_write(
            'stock_availables', 'stock_available', sa_id, {'quantity': quantity},
        )

    # ── Imágenes ────────────────────────────────────────

    def list_product_image_ids(self, store_id: int) -> list[int]:
        """IDs de las imágenes (declinations) de un producto en PrestaShop."""
        root = self._request('GET', f'images/products/{store_id}')
        if root is None:
            return []
        # La respuesta lista <image ...> con hijos <declination id=".."/>; en
        # productos con una sola imagen puede venir como <image id=".."/>.
        ids = [int(d.get('id')) for d in root.iter('declination') if d.get('id')]
        if ids:
            return ids
        img = root.find('image')
        if img is not None and img.get('id'):
            return [int(img.get('id'))]
        return []

    def upload_product_image(
        self, store_id: int, image_bytes: bytes, filename: str,
        content_type: str = 'image/jpeg',
    ) -> int | None:
        """Sube una imagen al producto (multipart) y devuelve su id si lo informa.

        No usa `_request` porque la subida es binaria (multipart/form-data),
        no XML. El campo del formulario debe llamarse `image`.
        """
        url = f'{self.api_base}/images/products/{store_id}'
        try:
            resp = requests.post(
                url, auth=self._auth,
                files={'image': (filename, image_bytes, content_type)},
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            raise EcommerceConnectionError(f'Error subiendo imagen: {exc}') from exc

        if resp.status_code in (401, 403):
            raise EcommerceConnectionError(
                f'Autenticación rechazada al subir imagen (HTTP {resp.status_code}).'
            )
        if resp.status_code >= 400:
            raise EcommerceConnectionError(
                f'PrestaShop rechazó la imagen (HTTP {resp.status_code}): {resp.text[:300]}'
            )
        try:
            root = ET.fromstring(resp.content)
            return self._created_id(root, 'image')
        except ET.ParseError:
            return None

    def delete_product_image(self, store_id: int, image_id: int) -> None:
        self._request('DELETE', f'images/products/{store_id}/{image_id}')

    # ── Clientes ────────────────────────────────────────

    def find_customer_by_email(self, email: str) -> int | None:
        root = self._request(
            'GET', 'customers', params={'filter[email]': f'[{email}]'},
        )
        ids = self._ids_from_list(root, 'customer')
        return ids[0] if ids else None

    def create_customer(self, payload: dict[str, Any]) -> int:
        # PrestaShop exige `passwd` al crear. Los clientes sincronizados desde
        # el ERP no usan el storefront, así que generamos una contraseña
        # aleatoria; solo se fija en el alta, no en cada update.
        payload = {**payload, 'passwd': secrets.token_urlsafe(16)}
        xml = self._build_resource_xml('customer', payload)
        root = self._request('POST', 'customers', data=xml)
        new_id = self._created_id(root, 'customer')
        if new_id is None:
            raise EcommerceConnectionError('PrestaShop no devolvió id al crear el cliente.')
        return new_id

    def update_customer(self, store_id: int, payload: dict[str, Any]) -> None:
        self._read_modify_write('customers', 'customer', store_id, payload)

    # ── Pedidos (tienda → ERP) ──────────────────────────

    def list_orders_since(self, since, **filters) -> list[dict[str, Any]]:
        params = {
            'display': 'full',
            'date': '1',
            'filter[date_upd]': f'[{since:%Y-%m-%d %H:%M:%S},{self._now()}]',
            'sort': '[date_upd_ASC]',
            **self._as_ps_filters(filters),
        }
        root = self._request('GET', 'orders', params=params)
        if root is None:
            return []
        return [self._element_to_dict(o) for o in root.iter('order')]

    def get_order(self, store_id: int) -> dict[str, Any]:
        root = self._request('GET', f'orders/{store_id}')
        if root is None:
            return {}
        order = root.find('order')
        return self._element_to_dict(order) if order is not None else {}

    def get_order_rows(self, store_id: int) -> list[dict[str, Any]]:
        """Líneas de un pedido (associations/order_rows)."""
        root = self._request('GET', f'orders/{store_id}')
        if root is None:
            return []
        rows = []
        for r in root.iter('order_row'):
            def _t(tag):
                node = r.find(tag)
                return node.text if node is not None else None
            rows.append({
                'product_id': _t('product_id'),
                'product_name': _t('product_name'),
                'product_reference': _t('product_reference'),
                'quantity': _t('product_quantity'),
                'unit_price_tax_excl': _t('unit_price_tax_excl'),
                'unit_price_tax_incl': _t('unit_price_tax_incl'),
            })
        return rows

    # ── Listados para pull (tienda → ERP) ───────────────

    def list_customers(self, **filters) -> list[dict[str, Any]]:
        params = {'display': 'full', **self._as_ps_filters(filters)}
        root = self._request('GET', 'customers', params=params)
        if root is None:
            return []
        out = []
        for c in root.iter('customer'):
            data = self._element_to_dict(c)
            data['id'] = c.findtext('id') or c.get('id')
            out.append(data)
        return out

    def list_products_full(self, **filters) -> list[dict[str, Any]]:
        """Como list_products pero garantizando el id en cada dict."""
        params = {'display': 'full', **self._as_ps_filters(filters)}
        root = self._request('GET', 'products', params=params)
        if root is None:
            return []
        out = []
        for p in root.iter('product'):
            data = self._element_to_dict(p)
            data['id'] = p.findtext('id') or p.get('id')
            out.append(data)
        return out

    def list_all_product_ids(self) -> list[int]:
        """Todos los ids de producto de la tienda (para limpieza/diagnóstico)."""
        root = self._request('GET', 'products')
        return self._ids_from_list(root, 'product')

    def delete_product(self, store_id: int) -> None:
        self._request('DELETE', f'products/{store_id}')

    # ── Utilidades ──────────────────────────────────────

    @staticmethod
    def _as_ps_filters(filters: dict) -> dict:
        """Traduce kwargs simples a la sintaxis filter[campo]=[valor]."""
        out = {}
        for key, value in filters.items():
            if key in ('limit', 'sort', 'display'):
                out[key] = value
            else:
                out[f'filter[{key}]'] = f'[{value}]'
        return out

    @staticmethod
    def _now() -> str:
        from django.utils import timezone
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')
