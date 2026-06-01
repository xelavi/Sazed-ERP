"""
Comando programable para Windows Task Scheduler / cron.

Recorre todas las OdooConnection activas y ejecuta pull_invoice_payments
sobre cada una.

Uso:
    python manage.py pull_odoo_payments
    python manage.py pull_odoo_payments --company <id> --since 2026-01-01
"""
from __future__ import annotations

from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounting_sync import sync_service
from accounting_sync.models import OdooConnection


class Command(BaseCommand):
    help = 'Sincroniza estado de pagos desde Odoo hacia el ERP.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company', type=int, default=None,
            help='ID de la Company a sincronizar (por defecto: todas activas).',
        )
        parser.add_argument(
            '--since', type=str, default=None,
            help='Fecha mínima ISO (YYYY-MM-DD) o ISO completa. Si se omite, '
                 'se usa el last_sync_at de cada conexión.',
        )

    def handle(self, *args, **options):
        qs = OdooConnection.objects.filter(is_active=True)
        if options.get('company'):
            qs = qs.filter(company_id=options['company'])

        since = None
        if options.get('since'):
            since = self._parse_since(options['since'])

        total = 0
        for connection in qs.select_related('company'):
            company = connection.company
            self.stdout.write(f'» {company} — pulling pagos…')
            try:
                result = sync_service.pull_invoice_payments(
                    company, since=since,
                )
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(
                    f'  ✗ {company}: {type(exc).__name__}: {exc}'
                ))
                continue
            total += result['sales_updated'] + result['purchases_updated']
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ filas={result['rows']} "
                f"ventas={result['sales_updated']} "
                f"compras={result['purchases_updated']} "
                f"errors={result['errors']}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Total facturas actualizadas: {total}',
        ))

    @staticmethod
    def _parse_since(value: str) -> datetime:
        for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
            try:
                dt = datetime.strptime(value, fmt)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt
            except ValueError:
                continue
        raise ValueError(f'Formato --since no reconocido: {value!r}')
