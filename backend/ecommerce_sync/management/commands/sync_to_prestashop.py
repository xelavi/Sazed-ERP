"""
Push masivo ERP → PrestaShop (carga inicial / por lotes).

Idempotente: si la entidad ya tiene `prestashop_id`, hace update; si no,
intenta enlazar por SKU/email y, en último término, crea.

Uso:
    python manage.py sync_to_prestashop --company <id>
    python manage.py sync_to_prestashop --company <id> --only products
    python manage.py sync_to_prestashop --company <id> --dry-run
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from customers.models import Customer
from ecommerce_sync.models import StoreConnection
from products.models import Product


class Command(BaseCommand):
    help = 'Sincroniza productos y clientes del ERP hacia PrestaShop.'

    def add_arguments(self, parser):
        parser.add_argument('--company', type=int, required=True)
        parser.add_argument(
            '--only', choices=['products', 'customers'], default=None,
            help='Limita la sincronización a una sola entidad.',
        )
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        from ecommerce_sync import sync_service

        company_id = opts['company']
        try:
            connection = StoreConnection.objects.select_related('company').get(
                company_id=company_id, is_active=True,
            )
        except StoreConnection.DoesNotExist:
            raise CommandError(
                f'No hay StoreConnection activa para la company {company_id}.'
            )
        company = connection.company

        do_products = opts['only'] in (None, 'products')
        do_customers = opts['only'] in (None, 'customers')

        if do_products:
            qs = Product.objects.filter(company=company, sellable=True)
            self.stdout.write(f'Productos a sincronizar: {qs.count()}')
            self._push_all(qs, sync_service.push_product, company, opts['dry_run'])

        if do_customers:
            qs = Customer.objects.filter(company=company, is_customer=True)
            self.stdout.write(f'Clientes a sincronizar: {qs.count()}')
            self._push_all(qs, sync_service.push_customer, company, opts['dry_run'])

        self.stdout.write(self.style.SUCCESS('Sincronización finalizada.'))

    def _push_all(self, qs, push_fn, company, dry_run):
        ok = err = 0
        for obj in qs.iterator():
            if dry_run:
                self.stdout.write(f'  [dry-run] {obj}')
                continue
            try:
                push_fn(obj, company)
                ok += 1
            except Exception as exc:  # noqa: BLE001
                err += 1
                self.stderr.write(self.style.ERROR(f'  ERROR {obj}: {exc}'))
        if not dry_run:
            self.stdout.write(f'  OK={ok} ERR={err}')
