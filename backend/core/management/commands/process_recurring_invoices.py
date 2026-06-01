"""Genera las facturas recurrentes (venta y compra) cuyo vencimiento ha llegado.

Pensado para ejecutarse periódicamente (Windows Task Scheduler / cron),
idealmente una vez al día:

    python manage.py process_recurring_invoices
    python manage.py process_recurring_invoices --date 2026-06-01
"""
from __future__ import annotations

from datetime import datetime

from django.core.management.base import BaseCommand

from invoices.services import RecurringInvoiceService
from purchases.services import RecurringPurchaseInvoiceService


class Command(BaseCommand):
    help = 'Genera y aprueba las facturas recurrentes pendientes (venta y compra).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date', type=str, default=None,
            help='Fecha de corte ISO (YYYY-MM-DD). Por defecto, hoy.',
        )
        parser.add_argument(
            '--sales-only', action='store_true',
            help='Procesar solo facturas de venta.',
        )
        parser.add_argument(
            '--purchases-only', action='store_true',
            help='Procesar solo facturas de compra.',
        )

    def handle(self, *args, **options):
        today = None
        if options.get('date'):
            today = datetime.strptime(options['date'], '%Y-%m-%d').date()

        do_sales = not options.get('purchases_only')
        do_purchases = not options.get('sales_only')

        if do_sales:
            sales = RecurringInvoiceService.generate_due(today=today)
            self.stdout.write(self.style.SUCCESS(
                f'Ventas: {len(sales)} factura(s) recurrente(s) generada(s).',
            ))
            for inv in sales:
                self.stdout.write(f'  · {inv.number} ({inv.total_amount} €)')

        if do_purchases:
            purchases = RecurringPurchaseInvoiceService.generate_due(today=today)
            self.stdout.write(self.style.SUCCESS(
                f'Compras: {len(purchases)} factura(s) recurrente(s) generada(s).',
            ))
            for inv in purchases:
                self.stdout.write(f'  · {inv.number} ({inv.total_amount} €)')
