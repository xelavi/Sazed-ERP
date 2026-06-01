"""Adaptador `PurchaseInvoice` ↔ `account.move` (in_invoice)."""
from __future__ import annotations

import logging
from typing import Any

from ..models import OdooTaxMapping
from ..odoo_client import OdooClient
from .base import to_odoo_float

logger = logging.getLogger(__name__)


class PurchaseInvoiceAdapter:
    """Mapea `purchases.PurchaseInvoice` con `account.move` (in_invoice)."""

    odoo_model = 'account.move'
    internal_id_field = 'odoo_id'

    def __init__(self, client: OdooClient) -> None:
        self.client = client
        self._currency_cache: dict[str, int] = {}

    def _currency_id(self, code: str) -> int | None:
        if code not in self._currency_cache:
            cid = self.client.find_currency_id(code)
            if cid is not None:
                self._currency_cache[code] = cid
            return cid
        return self._currency_cache[code]

    @staticmethod
    def _move_type(invoice: Any) -> str:
        return 'in_refund' if invoice.invoice_type == 'CreditNote' else 'in_invoice'

    def _resolve_tax_ids(self, line: Any, company: Any) -> list[int]:
        tax_ids: list[int] = []
        for line_tax in line.taxes.all():
            mapping = OdooTaxMapping.objects.filter(
                company=company,
                tax_rate=line_tax.tax_rate,
                direction='purchase',
            ).first()
            if mapping:
                tax_ids.append(mapping.odoo_tax_id)
            else:
                logger.warning(
                    'Línea %s sin OdooTaxMapping (purchase) para tax_rate=%s '
                    '(%s). Se enviará sin ese impuesto.',
                    line.pk, line_tax.tax_rate_id, line_tax.tax_name,
                )
        return tax_ids

    def _build_line(self, line: Any, company: Any) -> dict[str, Any]:
        product = getattr(line, 'product', None)
        line_data: dict[str, Any] = {
            'name': line.description or (product.name if product else 'Línea'),
            'quantity': to_odoo_float(line.quantity),
            'price_unit': to_odoo_float(line.unit_price),
        }
        if product and product.odoo_id:
            line_data['product_id'] = product.odoo_id

        tax_ids = self._resolve_tax_ids(line, company)
        if tax_ids:
            line_data['tax_ids'] = [(6, 0, tax_ids)]

        if line.discount_type == 'percent' and line.discount_value:
            line_data['discount'] = float(line.discount_value)

        return line_data

    def to_odoo(self, invoice: Any, *, company: Any) -> dict[str, Any]:
        """Construye el payload `account.move` (in_invoice) desde PurchaseInvoice.

        Requiere `invoice.provider.odoo_id` poblado.
        """
        provider = invoice.provider
        if not provider.odoo_id:
            raise ValueError(
                f'Provider {provider.pk} sin odoo_id. '
                'Llama a push_provider() antes de push_purchase_invoice().',
            )

        lines = [
            (0, 0, self._build_line(line, company))
            for line in invoice.lines.all().order_by('position')
        ]

        data: dict[str, Any] = {
            'move_type': self._move_type(invoice),
            'partner_id': provider.odoo_id,
            'invoice_date': invoice.issue_date.isoformat(),
            'invoice_date_due': invoice.due_date.isoformat(),
            'invoice_line_ids': lines,
            'ref': invoice.number or f'ERP-PUR-{invoice.pk}',
            'narration': invoice.provider_notes or False,
        }

        currency_id = self._currency_id(invoice.currency or 'EUR')
        if currency_id:
            data['currency_id'] = currency_id

        if invoice.invoice_type == 'CreditNote' and invoice.rectified_invoice:
            if invoice.rectified_invoice.odoo_id:
                data['reversed_entry_id'] = invoice.rectified_invoice.odoo_id

        return data

    def from_odoo(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            'number': data.get('name') or '',
            'state': data.get('state'),
            'payment_state': data.get('payment_state'),
            'total_amount': data.get('amount_total'),
            'balance_due': data.get('amount_residual'),
            'issue_date': data.get('invoice_date'),
        }
