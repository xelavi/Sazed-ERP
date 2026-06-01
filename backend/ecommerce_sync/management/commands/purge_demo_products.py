"""
Borra de PrestaShop los productos que NO están enlazados a ningún producto
del ERP — es decir, los productos demo que trae la instalación.

Los productos sincronizados desde el ERP (con `prestashop_id`) se preservan.

Uso:
    python manage.py purge_demo_products --company <id>
    python manage.py purge_demo_products --company <id> --dry-run
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from ecommerce_sync.clients import get_client_for
from ecommerce_sync.models import StoreConnection
from products.models import Product


class Command(BaseCommand):
    help = 'Elimina los productos demo de PrestaShop (los no enlazados al ERP).'

    def add_arguments(self, parser):
        parser.add_argument('--company', type=int, required=True)
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        try:
            connection = StoreConnection.objects.select_related('company').get(
                company_id=opts['company'], is_active=True,
            )
        except StoreConnection.DoesNotExist:
            raise CommandError(
                f'No hay StoreConnection activa para la company {opts["company"]}.'
            )
        client = get_client_for(connection)

        linked_ids = set(
            Product.objects.exclude(prestashop_id__isnull=True)
            .values_list('prestashop_id', flat=True)
        )
        all_ids = client.list_all_product_ids()
        to_delete = [pid for pid in all_ids if pid not in linked_ids]

        self.stdout.write(
            f'Productos en la tienda: {len(all_ids)} · '
            f'enlazados al ERP: {len(all_ids) - len(to_delete)} · '
            f'a borrar (demo): {len(to_delete)}'
        )
        if opts['dry_run']:
            self.stdout.write(self.style.WARNING(f'[dry-run] se borrarían: {to_delete}'))
            return

        ok = err = 0
        for pid in to_delete:
            try:
                client.delete_product(pid)
                ok += 1
            except Exception as exc:  # noqa: BLE001
                err += 1
                self.stderr.write(self.style.ERROR(f'  ERROR borrando producto {pid}: {exc}'))
        self.stdout.write(self.style.SUCCESS(f'Borrados {ok} productos demo (errores: {err}).'))
