"""
Pull PrestaShop → ERP (polling de pedidos).

PrestaShop no emite webhooks, así que este comando se programa cada N
minutos (Task Scheduler / cron) para traer los pedidos nuevos y
convertirlos en facturas del ERP.

Uso:
    python manage.py pull_prestashop
    python manage.py pull_prestashop --company <id>

Esqueleto: la conversión pedido → factura se implementa en la fase de
pull de pedidos (`sync_service.pull_orders`).
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from ecommerce_sync.models import StoreConnection


class Command(BaseCommand):
    help = 'Trae pedidos nuevos de PrestaShop y los convierte en facturas.'

    def add_arguments(self, parser):
        parser.add_argument('--company', type=int, default=None)

    def handle(self, *args, **opts):
        from ecommerce_sync import sync_service

        qs = StoreConnection.objects.filter(is_active=True, pull_orders=True)
        if opts['company']:
            qs = qs.filter(company_id=opts['company'])

        for connection in qs.select_related('company'):
            self.stdout.write(f'Pull de {connection.company}…')
            try:
                result = sync_service.pull_all(connection.company)
                self.stdout.write(self.style.SUCCESS(f'  {result}'))
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f'  ERROR: {exc}'))
