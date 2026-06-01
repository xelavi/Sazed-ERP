"""Protocolo común para adaptadores de dominio ERP ↔ Odoo."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any, Protocol


TWO_DECIMALS = Decimal('0.01')


def to_odoo_float(value: Decimal | float | int | None) -> float:
    """Convierte Decimal a float con redondeo bancario y 2 decimales.

    Odoo XML-RPC trabaja con floats. Toda salida monetaria pasa por aquí
    para evitar discrepancias por precisión.
    """
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value.quantize(TWO_DECIMALS, rounding=ROUND_HALF_EVEN))
    return float(Decimal(str(value)).quantize(TWO_DECIMALS, rounding=ROUND_HALF_EVEN))


def from_odoo_decimal(value: Any) -> Decimal:
    """Convierte un float/numérico de Odoo a Decimal con 2 decimales."""
    if value in (None, False, ''):
        return Decimal('0.00')
    return Decimal(str(value)).quantize(TWO_DECIMALS, rounding=ROUND_HALF_EVEN)


class Adapter(Protocol):
    """Contrato común de los adaptadores."""

    odoo_model: str
    internal_id_field: str

    def to_odoo(self, obj: Any, *, company: Any) -> dict[str, Any]:
        """Construye el payload Odoo a partir de la entidad ERP."""

    def from_odoo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extrae los campos relevantes del payload de Odoo."""
