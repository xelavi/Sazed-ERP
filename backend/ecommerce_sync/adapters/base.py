"""Helpers y contrato común de los adaptadores ERP ↔ tienda."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Protocol

TWO_DECIMALS = Decimal('0.01')

#: id del idioma por defecto en PrestaShop (Español tras la instalación).
DEFAULT_LANG_ID = 1


def to_store_price(value: Decimal | float | int | None) -> str:
    """Formatea un importe a string con 6 decimales (formato precio PrestaShop)."""
    if value is None:
        return '0.000000'
    dec = value if isinstance(value, Decimal) else Decimal(str(value))
    return f'{dec.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN)}'


def from_store_decimal(value: Any) -> Decimal:
    """Convierte un numérico de la tienda a Decimal con 2 decimales."""
    if value in (None, False, ''):
        return Decimal('0.00')
    return Decimal(str(value)).quantize(TWO_DECIMALS, rounding=ROUND_HALF_EVEN)


def lang(text: str | None) -> dict[int, str]:
    """Envuelve un texto en la convención multilenguaje del cliente."""
    return {DEFAULT_LANG_ID: text or ''}


class Adapter(Protocol):
    """Contrato común de los adaptadores."""

    store_resource: str
    internal_id_field: str

    def to_store(self, obj: Any, *, company: Any) -> dict[str, Any]:
        """Construye el payload de la tienda a partir de la entidad ERP."""

    def from_store(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae los campos relevantes del payload de la tienda."""
