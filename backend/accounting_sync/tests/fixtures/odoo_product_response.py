"""Payload sintético típico de `product.product` devuelto por Odoo."""

PRODUCT_RESPONSE = {
    'id': 101,
    'name': 'Producto demo',
    'default_code': 'SKU-001',
    'type': 'product',
    'list_price': 19.99,
    'standard_price': 12.50,
    'sale_ok': True,
    'purchase_ok': True,
    'active': True,
    'description_sale': 'Descripción comercial',
    'taxes_id': [1],
}
