"""Adaptador `Customer` ↔ `res.partner`."""
from __future__ import annotations

import logging
import re
from typing import Any

from ..odoo_client import OdooClient

logger = logging.getLogger(__name__)

# Algoritmos de validación NIF/NIE/CIF (l10n_es de Odoo aplica los mismos)
_NIF_LETTERS = 'TRWAGMYFPDXBNJZSQVHLCKE'
_CIF_CONTROL_LETTERS = 'JABCDEFGHI'
_NIE_PREFIX_MAP = {'X': '0', 'Y': '1', 'Z': '2'}

_RE_NIF = re.compile(r'^(\d{8})([A-Z])$')
_RE_NIE = re.compile(r'^([XYZ])(\d{7})([A-Z])$')
_RE_CIF = re.compile(r'^([ABCDEFGHJNPQRSUVW])(\d{7})([A-J0-9])$')


def _is_valid_es_vat(raw: str) -> bool:
    """Valida un NIF, NIE o CIF español comprobando el dígito de control."""
    vat = raw.upper().removeprefix('ES')

    if m := _RE_NIF.match(vat):
        digits, letter = m.group(1), m.group(2)
        return letter == _NIF_LETTERS[int(digits) % 23]

    if m := _RE_NIE.match(vat):
        prefix, rest, letter = m.groups()
        num = int(_NIE_PREFIX_MAP[prefix] + rest)
        return letter == _NIF_LETTERS[num % 23]

    if m := _RE_CIF.match(vat):
        _entity, digits, control = m.groups()
        # Posiciones pares (2ª, 4ª, 6ª) → suma directa
        even_sum = sum(int(d) for d in digits[1::2])
        # Posiciones impares (1ª, 3ª, 5ª, 7ª) → duplica y suma cifras
        odd_sum = 0
        for d in digits[::2]:
            doubled = int(d) * 2
            odd_sum += doubled // 10 + doubled % 10
        check_digit = (10 - (even_sum + odd_sum) % 10) % 10
        if control.isdigit():
            return int(control) == check_digit
        return control == _CIF_CONTROL_LETTERS[check_digit]

    return False


class ContactAdapter:
    """Mapea `customers.Customer` con `res.partner` de Odoo."""

    odoo_model = 'res.partner'
    internal_id_field = 'odoo_id'

    def __init__(self, client: OdooClient) -> None:
        self.client = client
        self._country_id_cache: int | None = None

    # ── Helpers ─────────────────────────────────────────

    def _country_id(self) -> int | None:
        if self._country_id_cache is None:
            self._country_id_cache = self.client.find_country_id('ES')
        return self._country_id_cache

    @staticmethod
    def _vat_with_prefix(vat: str | None) -> str:
        """Devuelve el VAT con prefijo ES si pasa la validación; '' si no.

        Aplica la misma validación de checksum que `l10n_es` en Odoo
        (NIF/NIE/CIF). Si falla, se envía '' (False en el payload) y
        se registra un warning para que el usuario corrija el dato.
        """
        if not vat:
            return ''
        vat_clean = vat.strip().upper().replace(' ', '').replace('-', '')
        if not _is_valid_es_vat(vat_clean):
            logger.warning(
                'VAT %r no pasa validacion NIF/NIE/CIF; se enviara sin VAT.',
                vat,
            )
            return ''
        if vat_clean.startswith('ES'):
            return vat_clean
        return f'ES{vat_clean}'

    # ── Conversión ──────────────────────────────────────

    def to_odoo(self, customer: Any, *, company: Any = None) -> dict[str, Any]:
        """Construye el payload `res.partner` desde un Customer del ERP."""
        data: dict[str, Any] = {
            'name': customer.name or customer.legal_name or 'Sin nombre',
            'is_company': customer.contact_type == 'Company',
            'vat': self._vat_with_prefix(customer.vat_id) or False,
            'email': customer.email or False,
            'phone': customer.phone or False,
            'website': customer.website or False,
            'street': customer.address or False,
            'city': customer.city or False,
            'zip': customer.postal_code or False,
            'customer_rank': 1 if customer.is_customer else 0,
            'supplier_rank': 1 if customer.is_supplier else 0,
            'active': customer.status == 'Active',
        }

        country_id = self._country_id()
        if country_id:
            data['country_id'] = country_id

        # Eliminamos False vacíos: Odoo prefiere ausencia de campo a False
        # en strings, pero `False` es válido para "limpiar" un valor.
        # Para create() conviene quitar los False de strings opcionales.
        return data

    def from_odoo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae campos útiles de un `res.partner` para crear un Customer.

        El ERP solo hace push en Fase 1; este método se reserva para
        futuros flujos de reconciliación o importación manual.
        """
        return {
            'name': data.get('name', ''),
            'legal_name': data.get('name', ''),
            'vat_id': (data.get('vat') or '').removeprefix('ES'),
            'email': data.get('email') or '',
            'phone': data.get('phone') or '',
            'website': data.get('website') or '',
            'address': data.get('street') or '',
            'city': data.get('city') or '',
            'postal_code': data.get('zip') or '',
            'is_customer': bool(data.get('customer_rank')),
            'is_supplier': bool(data.get('supplier_rank')),
            'status': 'Active' if data.get('active', True) else 'Inactive',
            'contact_type': 'Company' if data.get('is_company') else 'Person',
        }
