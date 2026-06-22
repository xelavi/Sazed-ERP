"""
Comando de sincronización inicial / por lotes ERP → Odoo.

Uso:
    python manage.py sync_to_odoo --company <id>
    python manage.py sync_to_odoo --company <id> --since 2025-01-01 --dry-run

Orden estricto:
    1. Verifica conexión y módulos l10n_es instalados.
    2. Contactos (clientes y proveedores).
    3. Productos.
    4. Facturas de venta (últimos 12 meses por defecto).
    5. Facturas de compra (últimos 12 meses por defecto).
    6. Resumen.

Procesa en bloques de 50 con commit DB por bloque (idempotencia
garantizada por `odoo_id`).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounting_sync import sync_service
from accounting_sync.models import OdooConnection
from accounting_sync.odoo_client import OdooConnectionError

BATCH_SIZE = 50


@dataclass
class Stats:
    customers: int = 0
    providers: int = 0
    products: int = 0
    sales_invoices: int = 0
    purchase_invoices: int = 0
    errors: list[str] = field(default_factory=list)


class Command(BaseCommand):
    help = 'Sincroniza por lotes contactos, productos y facturas hacia Odoo.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company', type=int, required=True,
            help='ID de la Company a sincronizar.',
        )
        parser.add_argument(
            '--since', type=str, default=None,
            help='Fecha mínima ISO (YYYY-MM-DD) para facturas. '
                 'Default: hoy menos 12 meses.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='No escribe nada en Odoo; sólo lista lo que haría.',
        )
        parser.add_argument(
            '--skip-invoices', action='store_true',
            help='Solo sincroniza contactos y productos (útil para primer arranque).',
        )

    def handle(self, *args, **options):
        from accounts.models import Company

        company_id = options['company']
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist as exc:
            raise CommandError(f'Company {company_id} no existe.') from exc

        try:
            connection = OdooConnection.objects.get(
                company=company, is_active=True,
            )
        except OdooConnection.DoesNotExist as exc:
            raise CommandError(
                f'La empresa {company} no tiene OdooConnection activa.',
            ) from exc

        since = self._resolve_since(options.get('since'))
        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE(
            f'─── Sync ERP → Odoo · {company} · desde {since.date()} '
            f'{"[DRY-RUN]" if dry_run else ""} ───',
        ))

        # 1. Verifica conexión y módulos
        self._verify_connection(connection)

        stats = Stats()

        # 2. Contactos
        self._sync_customers(company, stats, dry_run)
        self._sync_providers(company, stats, dry_run)

        # 3. Productos
        self._sync_products(company, stats, dry_run)

        # 4 y 5. Facturas
        if not options['skip_invoices']:
            self._sync_sales_invoices(company, stats, since, dry_run)
            self._sync_purchase_invoices(company, stats, since, dry_run)

        # 6. Resumen
        self._print_summary(stats, dry_run)

    # ── Pasos ───────────────────────────────────────────

    def _verify_connection(self, connection: OdooConnection) -> None:
        client = sync_service.get_client_for(connection)
        try:
            client.connect()
        except OdooConnectionError as exc:
            raise CommandError(f'No se pudo conectar a Odoo: {exc}') from exc

        modules = client.list_modules_installed(['l10n_es', 'l10n_es_aeat'])
        self.stdout.write(
            f"  · l10n_es={'✓' if modules.get('l10n_es') else '✗'}  "
            f"l10n_es_aeat={'✓' if modules.get('l10n_es_aeat') else '○ (opcional)'}"
        )
        if not modules.get('l10n_es'):
            self.stdout.write(self.style.WARNING(
                '  ⚠ l10n_es no está instalado en Odoo. La sincronización '
                'puede crear cuentas/impuestos incorrectos. Instala el módulo '
                'antes de continuar.',
            ))

    def _sync_customers(self, company, stats: Stats, dry_run: bool) -> None:
        from customers.models import Customer

        qs = Customer.objects.filter(company=company).order_by('pk')
        self.stdout.write(f'» Contactos (clientes): {qs.count()}')
        for batch in self._batched(qs):
            with transaction.atomic():
                for customer in batch:
                    if dry_run:
                        self.stdout.write(f'   · would push customer {customer.pk} {customer.name}')
                        continue
                    try:
                        sync_service.push_contact(customer, company)
                        stats.customers += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f'customer:{customer.pk} {type(exc).__name__}: {exc}'
                        stats.errors.append(msg)
                        self.stderr.write(self.style.ERROR(f'   ✗ {msg}'))

    def _sync_providers(self, company, stats: Stats, dry_run: bool) -> None:
        # Provider ha estat fusionat amb Customer (is_supplier=True)
        from customers.models import Customer

        qs = Customer.objects.filter(company=company, is_supplier=True).order_by('pk')
        self.stdout.write(f'» Contactos (proveedores): {qs.count()}')
        for batch in self._batched(qs):
            with transaction.atomic():
                for provider in batch:
                    if dry_run:
                        self.stdout.write(f'   · would push provider {provider.pk} {provider.name}')
                        continue
                    try:
                        sync_service.push_provider(provider, company)
                        stats.providers += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f'provider:{provider.pk} {type(exc).__name__}: {exc}'
                        stats.errors.append(msg)
                        self.stderr.write(self.style.ERROR(f'   ✗ {msg}'))

    def _sync_products(self, company, stats: Stats, dry_run: bool) -> None:
        from products.models import Product

        qs = Product.objects.filter(company=company).order_by('pk')
        self.stdout.write(f'» Productos: {qs.count()}')
        for batch in self._batched(qs):
            with transaction.atomic():
                for product in batch:
                    if dry_run:
                        self.stdout.write(f'   · would push product {product.pk} {product.sku}')
                        continue
                    try:
                        sync_service.push_product(product, company)
                        stats.products += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f'product:{product.pk} {type(exc).__name__}: {exc}'
                        stats.errors.append(msg)
                        self.stderr.write(self.style.ERROR(f'   ✗ {msg}'))

    def _sync_sales_invoices(self, company, stats: Stats, since, dry_run: bool) -> None:
        from invoices.models import Invoice

        qs = (
            Invoice.objects
            .filter(company=company, issue_date__gte=since.date())
            .exclude(status='Draft')
            .order_by('issue_date', 'pk')
        )
        self.stdout.write(f'» Facturas de venta desde {since.date()}: {qs.count()}')
        for batch in self._batched(qs):
            with transaction.atomic():
                for invoice in batch:
                    if dry_run:
                        self.stdout.write(f'   · would push sales {invoice.pk} {invoice.number}')
                        continue
                    try:
                        sync_service.push_sales_invoice(invoice, company, post=True)
                        stats.sales_invoices += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f'sales:{invoice.pk} {type(exc).__name__}: {exc}'
                        stats.errors.append(msg)
                        self.stderr.write(self.style.ERROR(f'   ✗ {msg}'))

    def _sync_purchase_invoices(self, company, stats: Stats, since, dry_run: bool) -> None:
        from purchases.models import PurchaseInvoice

        qs = (
            PurchaseInvoice.objects
            .filter(company=company, issue_date__gte=since.date())
            .exclude(status='Draft')
            .order_by('issue_date', 'pk')
        )
        self.stdout.write(f'» Facturas de compra desde {since.date()}: {qs.count()}')
        for batch in self._batched(qs):
            with transaction.atomic():
                for invoice in batch:
                    if dry_run:
                        self.stdout.write(f'   · would push purchase {invoice.pk} {invoice.number}')
                        continue
                    try:
                        sync_service.push_purchase_invoice(invoice, company, post=False)
                        stats.purchase_invoices += 1
                    except Exception as exc:  # noqa: BLE001
                        msg = f'purchase:{invoice.pk} {type(exc).__name__}: {exc}'
                        stats.errors.append(msg)
                        self.stderr.write(self.style.ERROR(f'   ✗ {msg}'))

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _batched(qs, size: int = BATCH_SIZE):
        bucket = []
        for item in qs.iterator(chunk_size=size):
            bucket.append(item)
            if len(bucket) >= size:
                yield bucket
                bucket = []
        if bucket:
            yield bucket

    @staticmethod
    def _resolve_since(value: str | None) -> datetime:
        if value is None:
            return timezone.now() - timedelta(days=365)
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                dt = datetime.strptime(value, fmt)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                return dt
            except ValueError:
                continue
        raise CommandError(f'Formato --since no reconocido: {value!r}')

    def _print_summary(self, stats: Stats, dry_run: bool) -> None:
        prefix = '[DRY-RUN] ' if dry_run else ''
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'{prefix}Resumen:'))
        self.stdout.write(f'  clientes:        {stats.customers}')
        self.stdout.write(f'  proveedores:     {stats.providers}')
        self.stdout.write(f'  productos:       {stats.products}')
        self.stdout.write(f'  facturas venta:  {stats.sales_invoices}')
        self.stdout.write(f'  facturas compra: {stats.purchase_invoices}')
        if stats.errors:
            self.stdout.write(self.style.WARNING(
                f'  errores:         {len(stats.errors)}',
            ))
            for err in stats.errors[:20]:
                self.stdout.write(f'    - {err}')
            if len(stats.errors) > 20:
                self.stdout.write(f'    … y {len(stats.errors) - 20} más.')
