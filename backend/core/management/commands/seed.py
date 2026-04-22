"""
Seed command — loads all hardcoded frontend data into the database.

Usage:
    python manage.py seed          # crea datos
    python manage.py seed --flush  # borra todo y recrea
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction, connection

from accounts.models import User, Company, Membership
from core.models import TaxRate, Tag, Warehouse, SalesChannel
from customers.models import Customer, CustomerNote, CustomerActivity, Quote
from products.models import (
    Category, Product, ProductVariant, ProductAttribute,
    ProductAttributeValue, PriceList, ProductSupplier, StockMovement,
)
from invoices.models import (
    InvoiceSeries, Invoice, InvoiceLine, InvoiceLineTax,
    Payment, InvoiceTimeline,
)
from tasks.models import TaskTag, Task


class Command(BaseCommand):
    help = 'Seed the database with frontend demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete all existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write('Flushing existing data...')
            self._flush()

        self.stdout.write('Seeding database...')
        with transaction.atomic():
            self._seed_accounts()
            self._seed_core()
            self._seed_customers()
            self._seed_products()
            self._seed_invoices()
            self._seed_tasks()
        self.stdout.write(self.style.SUCCESS('Done! Seed completed successfully!'))

    def _flush(self):
        with connection.cursor() as cursor:
            tables = [
                'tasks_task', 'tasks_task_tags', 'tasks_tasktag',
                'invoices_payment', 'invoices_invoicetimeline',
                'invoices_invoicelinetax', 'invoices_invoiceline',
                'invoices_invoice', 'invoices_invoiceseries',
                'products_stockmovement', 'products_productsupplier',
                'products_productattributevalue', 'products_productattribute',
                'products_productvariant', 'products_pricelist',
                'products_product_channels', 'products_product_tags',
                'products_product', 'products_category',
                'customers_quote', 'customers_customeractivity',
                'customers_customernote',
                'customers_customer_linked_contacts', 'customers_customer_tags',
                'customers_customer', 'core_tag', 'core_warehouse',
                'core_saleschannel', 'core_taxrate',
                'accounts_membership', 'accounts_company', 'accounts_user',
            ]
            cursor.execute('SET session_replication_role = replica;')
            for table in tables:
                cursor.execute(
                    f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;',
                )
            cursor.execute('SET session_replication_role = DEFAULT;')

    # ──────────────────────────────────────────────
    # Accounts (demo user + company)
    # ──────────────────────────────────────────────
    def _seed_accounts(self):
        self.stdout.write('  -> Demo user & company...')

        self.user = User.objects.create_user(
            email='demo@sazed.dev',
            password='demo1234',
            first_name='Demo',
            last_name='User',
        )
        self.company = Company.objects.create(
            name='Sazed Demo S.L.',
            slug='sazed-demo',
            tax_id='B-00000001',
            legal_name='Sazed Demo S.L.',
            email='info@sazed-demo.es',
            phone='+34 900 000 000',
            address='Calle Principal 1',
            city='Madrid',
            province='Madrid',
            postal_code='28001',
            created_by=self.user,
        )
        Membership.objects.create(
            user=self.user,
            company=self.company,
            role='owner',
            is_default=True,
        )

        self.stdout.write(
            f'    User: demo@sazed.dev / demo1234  |  Company: {self.company.name}',
        )
    # ──────────────────────────────────────────────
    # Core
    # ──────────────────────────────────────────────
    def _seed_core(self):
        self.stdout.write('  -> Tax rates, tags, warehouses, channels...')
        co = self.company

        # Tax rates
        self.iva21 = TaxRate.objects.create(
            name='IVA 21%', tax_type='VAT', percent=Decimal('21.00'),
            is_default=True, company=co,
        )
        self.iva10 = TaxRate.objects.create(
            name='IVA 10%', tax_type='VAT', percent=Decimal('10.00'),
            company=co,
        )
        self.iva4 = TaxRate.objects.create(
            name='IVA 4%', tax_type='VAT', percent=Decimal('4.00'),
            company=co,
        )
        self.irpf15 = TaxRate.objects.create(
            name='IRPF -15%', tax_type='RETENTION', percent=Decimal('-15.00'),
            company=co,
        )

        # Tags
        tag_names = [
            'Organic', 'T-Shirt', 'Summer', 'Running', 'Sport', 'Sneakers',
            'SEO', 'Digital', 'Marketing', 'Backpack', 'Urban', 'Eco',
            'Coffee', 'Premium', 'Bluetooth', 'ANC', 'Headphones',
            'Skincare', 'Natural', 'Gift Set', 'Office', 'Ergonomic', 'Chair',
            'Design', 'Logo', 'Branding', 'Bottle', 'Thermal',
            'Preferente', 'Tecnologia', 'Contacto Acme', 'Mobiliario', 'B2B',
            'Hosteleria', 'Freelance', 'Proveedor', 'Electronica',
        ]
        self.tags = {}
        for name in tag_names:
            self.tags[name] = Tag.objects.create(name=name, company=co)

        # Warehouse
        self.warehouse = Warehouse.objects.create(
            name='Warehouse Madrid', address='Poligono Industrial Norte, Madrid',
            company=co,
        )

        # Sales channels
        self.ch_web = SalesChannel.objects.create(name='Web', company=co)
        self.ch_market = SalesChannel.objects.create(name='Marketplace', company=co)

        # Categories
        cat_names = [
            'Clothing', 'Footwear', 'Accessories', 'Electronics',
            'Food & Drink', 'Furniture', 'Beauty', 'Services',
        ]
        self.categories = {}
        for name in cat_names:
            self.categories[name] = Category.objects.create(name=name, company=co)

        # Invoice series
        self.fac_series = InvoiceSeries.objects.create(
            name='Facturas generales', prefix='FAC',
            pattern='{PREFIX}-{YEAR}-{SEQ:4}', next_seq=6, is_default=True,
            company=co,
        )
        self.srv_series = InvoiceSeries.objects.create(
            name='Servicios', prefix='SRV',
            pattern='{PREFIX}-{YEAR}-{SEQ:4}', next_seq=3,
            company=co,
        )
        self.rec_series = InvoiceSeries.objects.create(
            name='Rectificativas', prefix='REC',
            pattern='{PREFIX}-{YEAR}-{SEQ:4}', next_seq=2,
            company=co,
        )

    # ──────────────────────────────────────────────
    # Customers
    # ──────────────────────────────────────────────
    def _seed_customers(self):
        self.stdout.write('  -> Customers...')
        co = self.company

        customers_data = [
            {
                'key': 'acme', 'name': 'Acme Corp.', 'contact_type': 'Company',
                'email': 'contact@acmecorp.com', 'city': 'Madrid', 'status': 'Active',
                'vat_id': 'B-12345678', 'initials': 'AC',
                'avatar_color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'phone': '+34 911 234 567', 'website': 'https://acmecorp.com',
                'address': 'Calle Gran Via 42, 3A', 'province': 'Madrid',
                'postal_code': '28013', 'legal_name': 'Acme Corporation S.L.',
                'payment_method': 'Transferencia 30 dias',
                'bank_account': 'ES12 0049 1234 5678 9012 3456',
                'tags': ['Preferente', 'Tecnologia'],
            },
            {
                'key': 'maria', 'name': 'Maria Lopez', 'contact_type': 'Person',
                'email': 'maria.lopez@email.com', 'city': 'Madrid', 'status': 'Active',
                'initials': 'ML',
                'avatar_color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'phone': '+34 612 345 678', 'address': 'Calle Serrano 15',
                'province': 'Madrid', 'postal_code': '28001',
                'payment_method': 'Transferencia',
                'tags': ['Contacto Acme'],
            },
            {
                'key': 'oficinas', 'name': 'Oficinas Modernas S.L.', 'contact_type': 'Company',
                'email': 'admin@oficinasmodernas.es', 'city': 'Barcelona', 'status': 'Active',
                'vat_id': 'B-87654321', 'initials': 'OM',
                'avatar_color': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'phone': '+34 933 456 789', 'website': 'https://oficinasmodernas.es',
                'address': 'Avinguda Diagonal 520', 'province': 'Barcelona',
                'postal_code': '08006', 'legal_name': 'Oficinas Modernas S.L.',
                'payment_method': 'Domiciliacion',
                'bank_account': 'ES98 2100 0813 6101 2345 6789',
                'is_supplier': True, 'tags': ['Mobiliario', 'B2B'],
            },
            {
                'key': 'pedro', 'name': 'Pedro Ruiz', 'contact_type': 'Person',
                'email': 'pruiz@gmail.com', 'city': 'Valencia', 'status': 'Active',
                'initials': 'PR',
                'avatar_color': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                'phone': '+34 645 678 901', 'address': 'Calle Colon 28',
                'province': 'Valencia', 'postal_code': '46004',
            },
            {
                'key': 'carlos', 'name': 'Carlos Mendez', 'contact_type': 'Person',
                'email': 'carlos.mendez@oficinasmodernas.es', 'city': 'Barcelona',
                'status': 'Active', 'initials': 'CM',
                'avatar_color': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            },
            {
                'key': 'laura', 'name': 'Laura Martin', 'contact_type': 'Person',
                'email': 'laura.martin@email.com', 'city': 'Sevilla', 'status': 'Inactive',
                'initials': 'LM',
                'avatar_color': 'linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%)',
            },
            {
                'key': 'cafemolino', 'name': 'Cafe Molino', 'contact_type': 'Company',
                'email': 'info@cafemolino.es', 'city': 'Sevilla', 'status': 'Active',
                'vat_id': 'B-11223344', 'initials': 'CM',
                'avatar_color': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                'phone': '+34 955 123 456', 'website': 'https://cafemolino.es',
                'address': 'Plaza Nueva 6', 'province': 'Sevilla',
                'postal_code': '41001', 'legal_name': 'Cafe Molino S.L.',
                'payment_method': 'Efectivo', 'tags': ['Hosteleria'],
            },
            {
                'key': 'jorge', 'name': 'Jorge Perez', 'contact_type': 'Person',
                'email': 'jorge.perez@cafemolino.es', 'city': 'Sevilla', 'status': 'Active',
                'initials': 'JP',
                'avatar_color': 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
            },
            {
                'key': 'luis', 'name': 'Luis Fernandez', 'contact_type': 'Person',
                'email': 'lfernandez@outlook.com', 'city': 'Bilbao', 'status': 'Active',
                'initials': 'LF',
                'avatar_color': 'linear-gradient(135deg, #fddb92 0%, #d1fdff 100%)',
                'phone': '+34 699 876 543', 'address': 'Alameda Mazarredo 12',
                'province': 'Vizcaya', 'postal_code': '48001',
                'tags': ['Freelance'],
            },
            {
                'key': 'techparts', 'name': 'TechParts Iberica S.A.', 'contact_type': 'Company',
                'email': 'ventas@techparts.es', 'city': 'Madrid', 'status': 'Active',
                'vat_id': 'A-99887766', 'initials': 'TI',
                'avatar_color': 'linear-gradient(135deg, #c471f5 0%, #fa71cd 100%)',
                'phone': '+34 914 567 890', 'website': 'https://techparts.es',
                'address': 'Poligono Industrial Sur, Nave 14', 'province': 'Madrid',
                'postal_code': '28906', 'legal_name': 'TechParts Iberica S.A.',
                'payment_method': 'Transferencia 30 dias',
                'bank_account': 'ES55 0182 2345 6789 0123 4567',
                'is_customer': False, 'is_supplier': True,
                'tags': ['Proveedor', 'Electronica'],
            },
            {
                'key': 'ana', 'name': 'Ana Garcia', 'contact_type': 'Person',
                'email': 'ana.garcia@techparts.es', 'city': 'Madrid', 'status': 'Active',
                'initials': 'AG',
                'avatar_color': 'linear-gradient(135deg, #96fbc4 0%, #f9f586 100%)',
                'phone': '+34 622 333 444', 'province': 'Madrid',
            },
            {
                'key': 'elena', 'name': 'Elena Vidal', 'contact_type': 'Person',
                'email': 'elena.vidal@email.com', 'city': 'Zaragoza', 'status': 'Inactive',
                'initials': 'EV',
                'avatar_color': 'linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)',
                'province': 'Zaragoza',
            },
        ]

        self.customers = {}
        for data in customers_data:
            key = data.pop('key')
            tags = data.pop('tags', [])
            cust = Customer.objects.create(company=co, **data)
            if tags:
                cust.tags.set([self.tags[t] for t in tags])
            self.customers[key] = cust

        # Linked contacts
        links = [
            ('acme', ['maria', 'pedro']),
            ('oficinas', ['carlos', 'laura', 'elena']),
            ('cafemolino', ['jorge']),
            ('techparts', ['ana']),
        ]
        for ckey, linked_keys in links:
            self.customers[ckey].linked_contacts.set(
                [self.customers[k] for k in linked_keys],
            )

        # Sample notes & activities for Acme Corp
        c1 = self.customers['acme']
        CustomerNote.objects.create(
            customer=c1, author='Admin',
            content='Cliente preferente desde 2024. Revision de condiciones en marzo.',
        )
        CustomerNote.objects.create(
            customer=c1, author='Comercial',
            content='Interesados en ampliar pedido para Q2.',
        )
        CustomerActivity.objects.create(
            customer=c1, activity_type='Reunión', date=date(2026, 1, 10),
            subject='Reunión revisión comercial',
            notes='Revisión de condiciones y precios para 2026.',
        )
        CustomerActivity.objects.create(
            customer=c1, activity_type='Email', date=date(2026, 1, 20),
            subject='Envío propuesta actualizada',
        )

        # Quote for Oficinas Modernas
        Quote.objects.create(
            customer=self.customers['oficinas'], number='PRE-2026-001',
            concept='Mobiliario oficina nueva sede',
            amount=Decimal('12500.00'), date=date(2026, 1, 25),
            valid_days=30, status='Enviado',
            notes='Incluye instalación y montaje.',
        )

        self.stdout.write(f'    Created {len(customers_data)} customers')

    # ──────────────────────────────────────────────
    # Products
    # ──────────────────────────────────────────────
    def _seed_products(self):
        self.stdout.write('  -> Products...')
        co = self.company

        products_data = [
            {
                'sku': 'ERP-001', 'name': 'Camiseta Algodón Orgánico',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Clothing', 'stock': 245, 'reserved': 12,
                'price': Decimal('29.99'), 'price_excl_tax': Decimal('24.79'),
                'cost': Decimal('12.50'), 'unit': 'ud', 'brand': 'EcoWear',
                'min_stock': 50, 'reorder_point': 80,
                'location': 'A-12-03', 'weight': '0.18 kg',
                'dimensions': '30 × 25 × 2 cm', 'shipping_class': 'Standard',
                'description': 'Camiseta de algodón 100% orgánico certificado GOTS, corte regular, costuras reforzadas. Disponible en 4 tallas.',
                'tags': ['Organic', 'T-Shirt', 'Summer'],
                'channels': ['Web', 'Marketplace'],
                'variants': [
                    {'name': 'S / White', 'sku': 'ERP-001-SW', 'price': Decimal('29.99'), 'stock': 60},
                    {'name': 'M / White', 'sku': 'ERP-001-MW', 'price': Decimal('29.99'), 'stock': 75},
                    {'name': 'L / Black', 'sku': 'ERP-001-LB', 'price': Decimal('29.99'), 'stock': 55},
                    {'name': 'XL / Navy', 'sku': 'ERP-001-XN', 'price': Decimal('29.99'), 'stock': 55},
                ],
                'attributes': [
                    {'name': 'Size', 'values': ['S', 'M', 'L', 'XL']},
                    {'name': 'Color', 'values': ['White', 'Black', 'Navy']},
                ],
                'suppliers_data': [
                    {'name': 'TextilSur S.L.', 'sku': 'TS-CAM-ORG', 'price': Decimal('12.50'), 'lead_time': '7 days', 'min_order': 50, 'primary': True},
                    {'name': 'FabricWorld', 'sku': 'FW-0892', 'price': Decimal('13.80'), 'lead_time': '14 days', 'min_order': 100, 'primary': False},
                ],
            },
            {
                'sku': 'ERP-002', 'name': 'Zapatillas Running Pro',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Footwear', 'stock': 58, 'reserved': 3,
                'price': Decimal('89.95'), 'price_excl_tax': Decimal('74.34'),
                'cost': Decimal('35.00'), 'unit': 'pair', 'brand': 'RunTech',
                'min_stock': 20, 'reorder_point': 30,
                'location': 'B-04-01', 'weight': '0.62 kg',
                'dimensions': '35 × 22 × 14 cm', 'shipping_class': 'Standard',
                'description': 'Zapatillas de running con amortiguación CloudFoam, upper de malla transpirable y suela de caucho continental.',
                'tags': ['Running', 'Sport', 'Sneakers'],
                'channels': ['Web'],
                'variants': [
                    {'name': '40 / Black-Red', 'sku': 'ERP-002-40BR', 'price': Decimal('89.95'), 'stock': 10},
                    {'name': '42 / Black-Red', 'sku': 'ERP-002-42BR', 'price': Decimal('89.95'), 'stock': 12},
                    {'name': '43 / White-Blue', 'sku': 'ERP-002-43WB', 'price': Decimal('89.95'), 'stock': 8},
                    {'name': '41 / White-Blue', 'sku': 'ERP-002-41WB', 'price': Decimal('79.95'), 'stock': 10},
                    {'name': '44 / Black-Red', 'sku': 'ERP-002-44BR', 'price': Decimal('89.95'), 'stock': 9},
                    {'name': '39 / White-Blue', 'sku': 'ERP-002-39WB', 'price': Decimal('79.95'), 'stock': 9},
                ],
                'attributes': [
                    {'name': 'Size', 'values': ['39', '40', '41', '42', '43', '44']},
                    {'name': 'Color', 'values': ['Black-Red', 'White-Blue']},
                ],
                'suppliers_data': [
                    {'name': 'SportGlobal Ltd.', 'sku': 'SG-RUN-PRO', 'price': Decimal('35.00'), 'lead_time': '21 days', 'min_order': 24, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-003', 'name': 'Consultoría SEO Mensual',
                'status': 'Active', 'product_type': 'Service',
                'category': 'Services', 'stock': None, 'reserved': 0,
                'price': Decimal('450.00'), 'price_excl_tax': Decimal('371.90'),
                'cost': Decimal('120.00'), 'unit': 'hour',
                'digital': True,
                'description': 'Servicio mensual de consultoría SEO: auditoría técnica, keyword research, on-page optimization y reporting.',
                'tags': ['SEO', 'Digital', 'Marketing'],
                'channels': ['Web'],
            },
            {
                'sku': 'ERP-004', 'name': 'Mochila Urbana 25L',
                'status': 'Inactive', 'product_type': 'Product',
                'category': 'Accessories', 'stock': 0, 'reserved': 0,
                'price': Decimal('54.50'), 'price_excl_tax': Decimal('45.04'),
                'cost': Decimal('22.00'), 'unit': 'ud', 'brand': 'UrbanPack',
                'min_stock': 10, 'reorder_point': 20,
                'location': 'C-01-05', 'weight': '0.75 kg',
                'dimensions': '48 × 32 × 18 cm', 'shipping_class': 'Standard',
                'description': 'Mochila urbana 25L en poliéster reciclado, compartimento para portátil 15", bolsillo antirrobo trasero.',
                'tags': ['Backpack', 'Urban', 'Eco'],
                'channels': [],
                'suppliers_data': [
                    {'name': 'BagCo Europa', 'sku': 'BC-URB25', 'price': Decimal('22.00'), 'lead_time': '10 days', 'min_order': 25, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-005', 'name': 'Café Arábica Premium 1kg',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Food & Drink', 'stock': 320, 'reserved': 45,
                'price': Decimal('18.75'), 'price_excl_tax': Decimal('17.05'),
                'cost': Decimal('7.80'), 'unit': 'kg', 'brand': 'CaféDirect',
                'min_stock': 100, 'reorder_point': 150,
                'location': 'D-08-02', 'weight': '1.05 kg',
                'dimensions': '28 × 12 × 8 cm', 'lot_tracking': True,
                'description': 'Café arábica 100% de origen único (Colombia), tueste medio, grano entero. Paquete de 1 kg con válvula de desgasificación.',
                'tags': ['Coffee', 'Organic', 'Premium'],
                'channels': ['Web', 'Marketplace'],
                'suppliers_data': [
                    {'name': 'CaféDirect', 'sku': 'CD-ARA-1KG', 'price': Decimal('7.80'), 'lead_time': '5 days', 'min_order': 50, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-006', 'name': 'Auriculares Bluetooth NC',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Electronics', 'stock': 14, 'reserved': 2,
                'price': Decimal('129.00'), 'price_excl_tax': Decimal('106.61'),
                'cost': Decimal('55.00'), 'unit': 'ud', 'brand': 'SoundMax',
                'min_stock': 10, 'reorder_point': 20,
                'location': 'A-02-07', 'weight': '0.28 kg',
                'dimensions': '20 × 18 × 8 cm', 'lot_tracking': True,
                'description': 'Auriculares over-ear Bluetooth 5.3 con cancelación de ruido activa (ANC), 40 h de batería, micrófono dual.',
                'tags': ['Bluetooth', 'ANC', 'Headphones'],
                'channels': ['Marketplace'],
                'variants': [
                    {'name': 'Black', 'sku': 'ERP-006-BLK', 'price': Decimal('129.00'), 'stock': 8},
                    {'name': 'White', 'sku': 'ERP-006-WHT', 'price': Decimal('129.00'), 'stock': 6},
                ],
                'attributes': [
                    {'name': 'Color', 'values': ['Black', 'White']},
                ],
                'suppliers_data': [
                    {'name': 'TechParts Asia', 'sku': 'TPA-BT-ANC40', 'price': Decimal('55.00'), 'lead_time': '30 days', 'min_order': 10, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-007', 'name': 'Set Skincare Natural',
                'status': 'Archived', 'product_type': 'Product',
                'category': 'Beauty', 'stock': 3, 'reserved': 0,
                'price': Decimal('42.00'), 'price_excl_tax': Decimal('34.71'),
                'cost': Decimal('19.50'), 'unit': 'ud', 'brand': 'BioCosmética',
                'min_stock': 5, 'reorder_point': 10,
                'location': 'E-03-01', 'weight': '0.45 kg',
                'dimensions': '22 × 15 × 10 cm', 'shipping_class': 'Fragile',
                'lot_tracking': True, 'sellable': False, 'purchasable': False,
                'description': 'Set de skincare natural con crema hidratante, sérum vitamina C y limpiador facial. Ingredientes orgánicos certificados.',
                'tags': ['Skincare', 'Natural', 'Gift Set'],
                'channels': [],
                'suppliers_data': [
                    {'name': 'BioCosmética', 'sku': 'BC-SKIN-SET', 'price': Decimal('19.50'), 'lead_time': '7 days', 'min_order': 20, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-008', 'name': 'Silla Ergonómica Oficina',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Furniture', 'stock': 27, 'reserved': 5,
                'price': Decimal('349.00'), 'price_excl_tax': Decimal('288.43'),
                'cost': Decimal('145.00'), 'unit': 'ud', 'brand': 'ErgoPlus',
                'min_stock': 5, 'reorder_point': 10,
                'location': 'F-01-01', 'weight': '14.5 kg',
                'dimensions': '68 × 68 × 120 cm', 'shipping_class': 'Bulky',
                'description': 'Silla ergonómica de oficina con soporte lumbar ajustable, reposabrazos 4D, asiento de malla transpirable y base de aluminio.',
                'tags': ['Office', 'Ergonomic', 'Chair'],
                'channels': ['Web'],
                'variants': [
                    {'name': 'Black', 'sku': 'ERP-008-BLK', 'price': Decimal('349.00'), 'stock': 12},
                    {'name': 'Gray', 'sku': 'ERP-008-GRY', 'price': Decimal('349.00'), 'stock': 10},
                    {'name': 'Blue', 'sku': 'ERP-008-BLU', 'price': Decimal('349.00'), 'stock': 5},
                ],
                'attributes': [
                    {'name': 'Color', 'values': ['Black', 'Gray', 'Blue']},
                ],
                'suppliers_data': [
                    {'name': 'MueblesPro', 'sku': 'MP-ERGO-V3', 'price': Decimal('145.00'), 'lead_time': '14 days', 'min_order': 5, 'primary': True},
                ],
            },
            {
                'sku': 'ERP-009', 'name': 'Diseño de Logo Profesional',
                'status': 'Active', 'product_type': 'Service',
                'category': 'Services', 'stock': None, 'reserved': 0,
                'price': Decimal('250.00'), 'price_excl_tax': Decimal('206.61'),
                'cost': Decimal('60.00'), 'unit': 'project',
                'digital': True,
                'description': 'Servicio de diseño de logotipo profesional: briefing, 3 conceptos, 2 rondas de revisión, entrega de archivos en AI, SVG, PNG y PDF.',
                'tags': ['Design', 'Logo', 'Branding'],
                'channels': ['Web'],
                'variants': [
                    {'name': 'Basic', 'sku': 'ERP-009-BAS', 'price': Decimal('150.00')},
                    {'name': 'Standard', 'sku': 'ERP-009-STD', 'price': Decimal('250.00')},
                    {'name': 'Premium', 'sku': 'ERP-009-PRE', 'price': Decimal('450.00')},
                ],
            },
            {
                'sku': 'ERP-010', 'name': 'Botella Térmica 750ml',
                'status': 'Active', 'product_type': 'Product',
                'category': 'Accessories', 'stock': 189, 'reserved': 0,
                'price': Decimal('24.99'), 'price_excl_tax': Decimal('20.65'),
                'cost': Decimal('8.20'), 'unit': 'ud', 'brand': 'EcoBottles',
                'min_stock': 30, 'reorder_point': 50,
                'location': 'C-02-08', 'weight': '0.35 kg',
                'dimensions': '27 × 7 × 7 cm',
                'description': 'Botella térmica de acero inoxidable 304, doble pared al vacío, 750 ml. Mantiene frío 24h y caliente 12h. Libre de BPA.',
                'tags': ['Bottle', 'Eco', 'Thermal'],
                'channels': ['Web', 'Marketplace'],
                'variants': [
                    {'name': 'Midnight Black', 'sku': 'ERP-010-MBK', 'price': Decimal('24.99'), 'stock': 45},
                    {'name': 'Arctic White', 'sku': 'ERP-010-AWT', 'price': Decimal('24.99'), 'stock': 40},
                    {'name': 'Forest Green', 'sku': 'ERP-010-FGR', 'price': Decimal('24.99'), 'stock': 38},
                    {'name': 'Ocean Blue', 'sku': 'ERP-010-OBL', 'price': Decimal('24.99'), 'stock': 35},
                    {'name': 'Rose Gold', 'sku': 'ERP-010-RGD', 'price': Decimal('24.99'), 'stock': 31},
                ],
                'attributes': [
                    {'name': 'Color', 'values': ['Midnight Black', 'Arctic White', 'Forest Green', 'Ocean Blue', 'Rose Gold']},
                ],
                'suppliers_data': [
                    {'name': 'EcoBottles', 'sku': 'EB-THERM-750', 'price': Decimal('8.20'), 'lead_time': '10 days', 'min_order': 50, 'primary': True},
                    {'name': 'SteelDrink Co.', 'sku': 'SD-750-SS', 'price': Decimal('9.10'), 'lead_time': '7 days', 'min_order': 25, 'primary': False},
                ],
            },
        ]

        # Create supplier customers (not already in customers list)
        supplier_names = set()
        for p in products_data:
            for s in p.get('suppliers_data', []):
                supplier_names.add(s['name'])

        # Map supplier names to Customer objects (create if needed)
        self.supplier_map = {}
        for sname in supplier_names:
            supp, created = Customer.objects.get_or_create(
                name=sname,
                company=co,
                defaults={
                    'contact_type': 'Company',
                    'email': f'info@{sname.lower().replace(" ", "").replace(".", "")}.com',
                    'status': 'Active',
                    'is_customer': False,
                    'is_supplier': True,
                    'initials': ''.join(w[0].upper() for w in sname.split()[:2]),
                }
            )
            self.supplier_map[sname] = supp

        self.products = {}
        for data in products_data:
            tags = data.pop('tags', [])
            channels = data.pop('channels', [])
            variants_data = data.pop('variants', [])
            attributes_data = data.pop('attributes', [])
            suppliers_data = data.pop('suppliers_data', [])
            cat_name = data.pop('category')

            product = Product.objects.create(
                **data,
                company=co,
                category=self.categories[cat_name],
                tax_rate=self.iva10 if cat_name == 'Food & Drink' else self.iva21,
                warehouse=self.warehouse if data.get('stock') is not None else None,
                created_by='Admin',
            )

            # Tags
            if tags:
                product.tags.set([self.tags[t] for t in tags])

            # Channels
            channel_map = {'Web': self.ch_web, 'Marketplace': self.ch_market}
            if channels:
                product.channels.set([channel_map[c] for c in channels])

            # Variants
            for v in variants_data:
                ProductVariant.objects.create(product=product, **v)

            # Attributes
            for attr_data in attributes_data:
                attr = ProductAttribute.objects.create(
                    product=product, name=attr_data['name'],
                )
                for i, val in enumerate(attr_data['values']):
                    ProductAttributeValue.objects.create(
                        attribute=attr, value=val, position=i,
                    )

            # Suppliers
            for s in suppliers_data:
                ProductSupplier.objects.create(
                    product=product,
                    supplier=self.supplier_map[s['name']],
                    supplier_sku=s['sku'],
                    purchase_price=s['price'],
                    lead_time=s['lead_time'],
                    min_order=s['min_order'],
                    is_primary=s['primary'],
                )

            self.products[data['sku']] = product

        self.stdout.write(f'    Created {len(products_data)} products')

    # ──────────────────────────────────────────────
    # Invoices
    # ──────────────────────────────────────────────
    def _seed_invoices(self):
        self.stdout.write('  -> Invoices...')

        invoices_data = [
            {
                'invoice_type': 'Standard', 'status': 'Paid',
                'series': self.fac_series, 'number': 'FAC-2026-0001',
                'customer_key': 'acme', 'issue_date': date(2026, 1, 5),
                'due_date': date(2026, 2, 4), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('1335.00'), 'total_tax': Decimal('280.35'),
                'total_amount': Decimal('1615.35'), 'paid_amount': Decimal('1615.35'),
                'balance_due': Decimal('0.00'),
                'locked_at': '2026-01-05T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Camiseta Algodón Orgánico', 'qty': 50, 'price': Decimal('22.00'), 'discount_type': 'percent', 'discount_value': Decimal('5'), 'subtotal': Decimal('1045.00'), 'tax': 'iva21'},
                    {'pos': 2, 'desc': 'Gorra Canvas', 'qty': 20, 'price': Decimal('14.50'), 'subtotal': Decimal('290.00'), 'tax': 'iva21'},
                ],
                'payments': [
                    {'date': date(2026, 2, 2), 'amount': Decimal('1615.35'), 'method': 'Transfer', 'reference': 'OP-20260202-001'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Approved',
                'series': self.fac_series, 'number': 'FAC-2026-0002',
                'customer_key': 'oficinas', 'issue_date': date(2026, 1, 15),
                'due_date': date(2026, 2, 14), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('2019.00'), 'total_tax': Decimal('423.99'),
                'total_amount': Decimal('2442.99'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('2442.99'),
                'locked_at': '2026-01-15T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Silla Ergonómica Oficina – Black', 'qty': 3, 'price': Decimal('295.00'), 'subtotal': Decimal('885.00'), 'tax': 'iva21'},
                    {'pos': 2, 'desc': 'Mesa Standing Desk', 'qty': 3, 'price': Decimal('420.00'), 'discount_type': 'percent', 'discount_value': Decimal('10'), 'subtotal': Decimal('1134.00'), 'tax': 'iva21'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'PartiallyPaid',
                'series': self.fac_series, 'number': 'FAC-2026-0003',
                'customer_key': 'cafemolino', 'issue_date': date(2026, 1, 20),
                'due_date': date(2026, 2, 19), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('1750.00'), 'total_tax': Decimal('202.50'),
                'total_amount': Decimal('1952.50'), 'paid_amount': Decimal('1000.00'),
                'balance_due': Decimal('952.50'),
                'locked_at': '2026-01-20T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Café Arábica Premium 1kg', 'qty': 100, 'price': Decimal('15.00'), 'subtotal': Decimal('1500.00'), 'tax': 'iva10'},
                    {'pos': 2, 'desc': 'Diseño de Logo Profesional – Standard', 'qty': 1, 'price': Decimal('250.00'), 'subtotal': Decimal('250.00'), 'tax': 'iva21'},
                ],
                'payments': [
                    {'date': date(2026, 2, 1), 'amount': Decimal('1000.00'), 'method': 'Transfer', 'reference': 'OP-CM-001'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Draft',
                'series': self.fac_series, 'number': None,
                'customer_key': 'luis', 'issue_date': date(2026, 2, 14),
                'due_date': date(2026, 3, 16), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('224.90'), 'total_tax': Decimal('47.23'),
                'total_amount': Decimal('272.13'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('272.13'),
                'lines': [
                    {'pos': 1, 'desc': 'Zapatillas Running Pro – 42 Black/Red', 'qty': 2, 'price': Decimal('89.95'), 'subtotal': Decimal('179.90'), 'tax': 'iva21'},
                    {'pos': 2, 'desc': 'Calcetines Técnicos', 'qty': 4, 'price': Decimal('12.50'), 'discount_type': 'percent', 'discount_value': Decimal('10'), 'subtotal': Decimal('45.00'), 'tax': 'iva21'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Approved',
                'series': self.fac_series, 'number': 'FAC-2026-0004',
                'customer_key': 'techparts', 'issue_date': date(2026, 2, 1),
                'due_date': date(2026, 3, 3), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('645.00'), 'total_tax': Decimal('135.45'),
                'total_amount': Decimal('780.45'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('780.45'),
                'locked_at': '2026-02-01T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Auriculares Bluetooth NC – Black', 'qty': 5, 'price': Decimal('129.00'), 'subtotal': Decimal('645.00'), 'tax': 'iva21'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Paid',
                'series': self.srv_series, 'number': 'SRV-2026-0001',
                'customer_key': 'acme', 'issue_date': date(2026, 1, 1),
                'due_date': date(2026, 1, 31), 'payment_method': 'Direct debit',
                'subtotal': Decimal('450.00'), 'total_tax': Decimal('94.50'),
                'total_retention': Decimal('67.50'),
                'total_amount': Decimal('477.00'), 'paid_amount': Decimal('477.00'),
                'balance_due': Decimal('0.00'),
                'locked_at': '2026-01-01T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Consultoría SEO Mensual – Enero 2026', 'qty': 1, 'price': Decimal('450.00'), 'subtotal': Decimal('450.00'), 'tax': 'iva21', 'retention': 'irpf15'},
                ],
                'payments': [
                    {'date': date(2026, 1, 28), 'amount': Decimal('477.00'), 'method': 'DirectDebit', 'reference': 'DD-ACM-2026-01'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Voided',
                'series': self.fac_series, 'number': 'FAC-2026-0005',
                'customer_key': 'elena', 'issue_date': date(2026, 2, 5),
                'due_date': date(2026, 3, 7), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('109.00'), 'total_tax': Decimal('22.89'),
                'total_amount': Decimal('131.89'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('0.00'),
                'locked_at': '2026-02-05T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Mochila Urbana 25L', 'qty': 2, 'price': Decimal('54.50'), 'subtotal': Decimal('109.00'), 'tax': 'iva21'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Draft',
                'series': self.fac_series, 'number': None,
                'customer_key': 'maria', 'issue_date': date(2026, 2, 16),
                'due_date': date(2026, 3, 18), 'payment_method': 'Transfer 30 days',
                'subtotal': Decimal('362.37'), 'total_tax': Decimal('76.10'),
                'total_amount': Decimal('438.47'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('438.47'),
                'lines': [
                    {'pos': 1, 'desc': 'Botella Térmica 750ml – Mint', 'qty': 10, 'price': Decimal('24.99'), 'discount_type': 'percent', 'discount_value': Decimal('15'), 'subtotal': Decimal('212.42'), 'tax': 'iva21'},
                    {'pos': 2, 'desc': 'Camiseta Algodón Orgánico – M/White', 'qty': 5, 'price': Decimal('29.99'), 'subtotal': Decimal('149.95'), 'tax': 'iva21'},
                ],
            },
            {
                'invoice_type': 'CreditNote', 'status': 'Approved',
                'series': self.rec_series, 'number': 'REC-2026-0001',
                'customer_key': 'pedro', 'issue_date': date(2026, 2, 12),
                'due_date': date(2026, 2, 12), 'payment_method': 'Transfer',
                'subtotal': Decimal('-29.99'), 'total_tax': Decimal('-6.30'),
                'total_amount': Decimal('-36.29'), 'paid_amount': Decimal('-36.29'),
                'balance_due': Decimal('0.00'),
                'locked_at': '2026-02-12T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Camiseta Algodón Orgánico – L/Black (devolución)', 'qty': -1, 'price': Decimal('29.99'), 'subtotal': Decimal('-29.99'), 'tax': 'iva21'},
                ],
                'payments': [
                    {'date': date(2026, 2, 13), 'amount': Decimal('-36.29'), 'method': 'Transfer', 'reference': 'REF-RET-012'},
                ],
            },
            {
                'invoice_type': 'Standard', 'status': 'Approved',
                'series': self.srv_series, 'number': 'SRV-2026-0002',
                'customer_key': 'acme', 'issue_date': date(2026, 2, 1),
                'due_date': date(2026, 2, 28), 'payment_method': 'Direct debit',
                'subtotal': Decimal('450.00'), 'total_tax': Decimal('94.50'),
                'total_retention': Decimal('67.50'),
                'total_amount': Decimal('477.00'), 'paid_amount': Decimal('0.00'),
                'balance_due': Decimal('477.00'),
                'locked_at': '2026-02-01T10:00:00Z',
                'lines': [
                    {'pos': 1, 'desc': 'Consultoría SEO Mensual – Febrero 2026', 'qty': 1, 'price': Decimal('450.00'), 'subtotal': Decimal('450.00'), 'tax': 'iva21', 'retention': 'irpf15'},
                ],
            },
        ]

        tax_map = {
            'iva21': self.iva21,
            'iva10': self.iva10,
            'iva4': self.iva4,
            'irpf15': self.irpf15,
        }

        for inv_data in invoices_data:
            lines_data = inv_data.pop('lines', [])
            payments_data = inv_data.pop('payments', [])
            customer_key = inv_data.pop('customer_key')
            locked_at = inv_data.pop('locked_at', None)

            customer = self.customers[customer_key]

            invoice = Invoice(
                customer=customer,
                **inv_data,
            )
            if locked_at:
                invoice.locked_at = locked_at
                # Snapshots
                invoice.customer_name_snapshot = customer.name
                invoice.customer_vat_snapshot = customer.vat_id or ''
                invoice.customer_address_snapshot = {
                    'address': customer.address,
                    'city': customer.city,
                    'province': customer.province,
                    'postal_code': customer.postal_code,
                    'country': customer.country,
                }
            invoice.save()

            # Lines
            for line_data in lines_data:
                tax_key = line_data.pop('tax', 'iva21')
                retention_key = line_data.pop('retention', None)
                line = InvoiceLine.objects.create(
                    invoice=invoice,
                    position=line_data['pos'],
                    description=line_data['desc'],
                    quantity=Decimal(str(line_data['qty'])),
                    unit_price=line_data['price'],
                    discount_type=line_data.get('discount_type'),
                    discount_value=line_data.get('discount_value'),
                    subtotal=line_data['subtotal'],
                )
                # Overwrite auto-calculated subtotal for seed consistency
                InvoiceLine.objects.filter(pk=line.pk).update(
                    subtotal=line_data['subtotal'],
                    discount_amount=line_data.get('discount_amount', line.discount_amount),
                )

                # Tax
                tax_rate_obj = tax_map[tax_key]
                tax_amount = line_data['subtotal'] * tax_rate_obj.percent / 100
                InvoiceLineTax.objects.create(
                    invoice_line=line,
                    tax_rate=tax_rate_obj,
                    tax_name=tax_rate_obj.name,
                    tax_percent=tax_rate_obj.percent,
                    is_retention=False,
                    tax_amount=tax_amount,
                )

                # Retention if applicable
                if retention_key:
                    ret_obj = tax_map[retention_key]
                    ret_amount = line_data['subtotal'] * abs(ret_obj.percent) / 100
                    InvoiceLineTax.objects.create(
                        invoice_line=line,
                        tax_rate=ret_obj,
                        tax_name=ret_obj.name,
                        tax_percent=ret_obj.percent,
                        is_retention=True,
                        tax_amount=ret_amount,
                    )

            # Payments (skip auto-recalculation, set values directly)
            for pay_data in payments_data:
                Payment.objects.create(invoice=invoice, **pay_data)
                # Re-set the invoice amounts (since Payment.save() auto-updates)
                Invoice.objects.filter(pk=invoice.pk).update(
                    paid_amount=inv_data.get('paid_amount', invoice.paid_amount),
                    balance_due=inv_data.get('balance_due', invoice.balance_due),
                    status=inv_data.get('status', invoice.status),
                )

            # Timeline
            InvoiceTimeline.objects.create(
                invoice=invoice,
                event_type='created',
                action='Factura creada',
                actor='System',
                date=invoice.issue_date,
            )
            if invoice.status != 'Draft':
                InvoiceTimeline.objects.create(
                    invoice=invoice,
                    event_type='approved',
                    action=f'Factura {invoice.number} aprobada',
                    actor='System',
                    date=invoice.issue_date,
                )
            if invoice.status == 'Voided':
                InvoiceTimeline.objects.create(
                    invoice=invoice,
                    event_type='voided',
                    action=f'Factura {invoice.number} anulada',
                    actor='System',
                    date=invoice.issue_date,
                )

        self.stdout.write(f'    Created {len(invoices_data)} invoices')

    # ──────────────────────────────────────────────
    # Tasks
    # ──────────────────────────────────────────────
    def _seed_tasks(self):
        self.stdout.write('  -> Tasks...')
        co = self.company

        # Task tags
        task_tags = {
            'Design': TaskTag.objects.create(label='Design', color_class='tag-purple'),
            'High Priority': TaskTag.objects.create(label='High Priority', color_class='tag-red'),
            'Documentation': TaskTag.objects.create(label='Documentation', color_class='tag-blue'),
            'Marketing': TaskTag.objects.create(label='Marketing', color_class='tag-green'),
            'Development': TaskTag.objects.create(label='Development', color_class='tag-orange'),
            'Mobile': TaskTag.objects.create(label='Mobile', color_class='tag-pink'),
        }

        today = date.today()

        tasks_data = [
            {
                'title': 'Review design mockups for landing page',
                'completed': False, 'due_date': today, 'status': 'upcoming',
                'tags': ['Design', 'High Priority'],
            },
            {
                'title': 'Update user documentation',
                'completed': True, 'due_date': today - timedelta(days=1),
                'status': 'completed',
                'tags': ['Documentation'],
            },
            {
                'title': 'Prepare Q1 presentation slides',
                'completed': False, 'due_date': today + timedelta(days=3),
                'status': 'upcoming',
                'tags': ['Marketing'],
            },
            {
                'title': 'Code review for mobile app PR #234',
                'completed': False, 'due_date': today + timedelta(days=2),
                'status': 'upcoming',
                'tags': ['Development', 'Mobile'],
            },
        ]

        for data in tasks_data:
            tag_names = data.pop('tags')
            task = Task.objects.create(company=co, **data)
            task.tags.set([task_tags[t] for t in tag_names])

        self.stdout.write(f'    Created {len(tasks_data)} tasks')
