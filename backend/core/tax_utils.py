"""Utilidades para resolver tipos impositivos y crear líneas de impuesto.

Compartido por los serializers de facturas de venta y de compra para que el
impuesto editado en el frontend (un porcentaje por línea) se persista como un
registro `InvoiceLineTax` / `PurchaseInvoiceLineTax` enlazado a un `TaxRate`.
"""
from decimal import Decimal

from .models import TaxRate

CENTS = Decimal('0.01')


def resolve_vat_rate(percent, company=None):
    """Devuelve el TaxRate de IVA/IGIC activo con ese porcentaje.

    Prefiere el tipo configurado para la empresa; si no, usa uno global.
    Excluye retenciones (IRPF).
    """
    if percent is None:
        return None
    try:
        percent = Decimal(str(percent))
    except (TypeError, ValueError):
        return None
    if percent <= 0:
        return None

    qs = TaxRate.objects.filter(percent=percent, active=True).exclude(
        tax_type=TaxRate.TaxType.RETENTION,
    )
    if company is not None:
        return qs.filter(company=company).first() or qs.filter(
            company__isnull=True,
        ).first()
    return qs.first()


def apply_line_vat(line_tax_model, line, tax_percent, company=None, line_fk_name='invoice_line'):
    """Crea la línea de impuesto para `line` a partir de un porcentaje de IVA.

    No hace nada si el porcentaje es 0/None o no existe un TaxRate equivalente.
    El importe se calcula sobre el subtotal de la línea (ya neto de su descuento).
    `line_fk_name` permet especificar el nom del FK (p.ex. 'quote_line' per a QuoteLineTax).
    """
    rate = resolve_vat_rate(tax_percent, company)
    if rate is None:
        return None

    base = line.subtotal or Decimal('0')
    tax_amount = (base * rate.percent / Decimal('100')).quantize(CENTS)
    return line_tax_model.objects.create(
        **{line_fk_name: line},
        tax_rate=rate,
        tax_name=rate.name,
        tax_percent=rate.percent,
        is_retention=False,
        tax_amount=tax_amount,
    )
