"""Payload sintético típico de `res.partner` devuelto por Odoo."""

PARTNER_RESPONSE = {
    'id': 42,
    'name': 'ACME S.L.',
    'vat': 'ESB12345678',
    'email': 'info@acme.example',
    'phone': '+34 911 234 567',
    'website': 'https://acme.example',
    'street': 'Calle Falsa 123',
    'city': 'Madrid',
    'zip': '28001',
    'country_id': [69, 'Spain'],
    'is_company': True,
    'customer_rank': 1,
    'supplier_rank': 0,
    'active': True,
}
