"""
Bootstrap completo de una instancia Odoo recién levantada.

Pasos (todos idempotentes):
  1. Crea la BD si no existe (vía master password).
  2. Instala módulos requeridos (`account`, `l10n_es`, `stock`).
  3. Resetea `odoo_id` de las entidades del ERP (sus IDs viejos no existen
     en la nueva BD).
  4. Auto-crea `OdooTaxMapping` por matching de porcentaje.
  5. Ejecuta `sync_to_odoo` completo.

Uso:
    python manage.py bootstrap_odoo --company 1
    python manage.py bootstrap_odoo --company 1 --db-name aeris_db --no-reset
"""
from __future__ import annotations

import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounting_sync.models import OdooConnection, OdooTaxMapping
from accounting_sync.odoo_client import OdooClient, OdooConnectionError
from accounting_sync.sync_service import get_client_for


REQUIRED_MODULES = ['account', 'l10n_es', 'stock']


class Command(BaseCommand):
    help = 'Bootstrap completo Odoo: crea BD, instala modulos, resetea y sincroniza.'

    def add_arguments(self, parser):
        parser.add_argument('--company', type=int, required=True)
        parser.add_argument(
            '--db-name', type=str, default=None,
            help='Nombre de la BD a crear/usar. Default: el de la OdooConnection.',
        )
        parser.add_argument(
            '--admin-password', type=str, default='admin',
            help='Password del admin de Odoo a crear (solo si la BD no existe).',
        )
        parser.add_argument(
            '--skip-create', action='store_true',
            help='No intenta crear la BD; asume que ya existe.',
        )
        parser.add_argument(
            '--no-reset', action='store_true',
            help='No resetea los odoo_id de las entidades del ERP.',
        )
        parser.add_argument(
            '--skip-sync', action='store_true',
            help='No ejecuta el sync_to_odoo al final.',
        )

    def handle(self, *args, **options):
        from accounts.models import Company

        company_id = options['company']
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist as exc:
            raise CommandError(f'Company {company_id} no existe.') from exc

        try:
            connection = OdooConnection.objects.get(company=company, is_active=True)
        except OdooConnection.DoesNotExist as exc:
            raise CommandError(
                f'La empresa {company} no tiene OdooConnection activa.',
            ) from exc

        db_name = options['db_name'] or connection.database
        if not db_name:
            raise CommandError('Falta --db-name y la OdooConnection no tiene database.')

        self._h1(f'Bootstrap Odoo -- company={company} db={db_name}')

        # 1. Crear BD si no existe
        if not options['skip_create']:
            self._step('1. Comprobando/creando BD en Odoo')
            self._ensure_database(connection, db_name, options['admin_password'])

        # Si cambia el db_name, actualizamos la connection
        if connection.database != db_name:
            connection.database = db_name
            connection.save(update_fields=['database'])
            self.stdout.write(f'  -- OdooConnection.database actualizado a {db_name}')

        # 2. Verificar/instalar módulos
        self._step('2. Modulos requeridos')
        self._ensure_modules(connection)

        # 3. Reset odoo_id en ERP
        if not options['no_reset']:
            self._step('3. Reset de odoo_id en entidades del ERP')
            self._reset_odoo_ids(company)

        # 4. Auto-crear OdooTaxMapping por porcentaje
        self._step('4. Auto-mapeo de impuestos por porcentaje')
        self._autoconfigure_tax_mappings(connection, company)

        # 5. Sync
        if not options['skip_sync']:
            self._step('5. Sincronizacion completa ERP -> Odoo')
            call_command('sync_to_odoo', f'--company={company_id}')

        self._h1('Bootstrap completado')

    # ── Pasos ───────────────────────────────────────────

    def _ensure_database(self, connection: OdooConnection, db_name: str, admin_pwd: str) -> None:
        master = getattr(settings, 'ODOO_MASTER_PWD', None) or self._read_env('ODOO_MASTER_PWD')
        if not master:
            raise CommandError(
                'Falta ODOO_MASTER_PWD en el .env. Necesaria para crear la BD.',
            )

        try:
            dbs = OdooClient.list_databases(connection.base_url)
        except Exception as exc:  # noqa: BLE001
            raise CommandError(
                f'No se pudo listar BDs en {connection.base_url}: {exc}\n'
                'Comprueba que Odoo esta arrancado (docker compose ps).',
            ) from exc

        if db_name in dbs:
            self.stdout.write(f'  -- BD "{db_name}" ya existe.')
            return

        self.stdout.write(
            f'  -- Creando BD "{db_name}" (puede tardar 1-3 minutos, instala base modules)...',
        )
        start = time.monotonic()
        try:
            OdooClient.create_database(
                base_url=connection.base_url,
                master_pwd=master,
                db_name=db_name,
                admin_password=admin_pwd,
            )
        except Exception as exc:  # noqa: BLE001
            raise CommandError(
                f'Fallo creando BD: {exc}\n'
                'Si master_pwd es incorrecta, verifica ODOO_MASTER_PWD en .env '
                'y odoo_config/odoo.conf. Alternativa: crea la BD a mano en '
                'http://localhost:8069/web/database/manager y relanza con --skip-create.',
            ) from exc
        self.stdout.write(self.style.SUCCESS(
            f'  -- BD creada en {time.monotonic() - start:.0f}s. '
            f'Login admin / {admin_pwd}',
        ))

        # Sincronizamos las credenciales en la OdooConnection
        connection.username = 'admin'
        connection.password = admin_pwd
        connection.save(update_fields=['username', 'password'])
        self.stdout.write('  -- OdooConnection actualizada con admin/admin.')

    def _ensure_modules(self, connection: OdooConnection) -> None:
        client = get_client_for(connection)
        try:
            client.connect()
        except OdooConnectionError as exc:
            raise CommandError(f'No se puede conectar a Odoo: {exc}') from exc

        before = client.list_modules_installed(REQUIRED_MODULES)
        self.stdout.write('  Estado antes:')
        for name, ok in before.items():
            mark = 'OK' if ok else 'NO'
            self.stdout.write(f'    [{mark}] {name}')

        missing = [n for n, ok in before.items() if not ok]
        if not missing:
            self.stdout.write(self.style.SUCCESS('  -- Todos los modulos requeridos ya estan instalados.'))
            return

        self.stdout.write(f'  -- Instalando via RPC: {missing}')
        after = client.install_modules(missing)
        still_missing = [n for n, ok in after.items() if not ok]
        for name, ok in after.items():
            if ok:
                self.stdout.write(self.style.SUCCESS(f'  -- {name} instalado.'))

        if still_missing:
            cli_modules = ','.join(REQUIRED_MODULES)
            db_name = connection.database
            raise CommandError(
                'La instalación de módulos vía RPC no se completó '
                f'({still_missing}). Ejecuta este comando para instalarlos '
                'directamente con la CLI de Odoo (más fiable):\n\n'
                f'  docker compose -f docker-compose.odoo.yml stop odoo\n'
                f'  docker compose -f docker-compose.odoo.yml run --rm odoo '
                f'odoo -d {db_name} -i {cli_modules} --stop-after-init --no-http\n'
                f'  docker compose -f docker-compose.odoo.yml start odoo\n\n'
                'Luego relanza con --skip-create.',
            )

    def _reset_odoo_ids(self, company) -> None:
        from customers.models import Customer
        from products.models import Product
        from providers.models import Provider
        from invoices.models import Invoice
        from purchases.models import PurchaseInvoice

        with transaction.atomic():
            n_cust = Customer.objects.filter(company=company, odoo_id__isnull=False).update(odoo_id=None)
            n_prov = Provider.objects.filter(company=company, odoo_id__isnull=False).update(odoo_id=None)
            n_prod = Product.objects.filter(company=company, odoo_id__isnull=False).update(odoo_id=None)
            n_inv = Invoice.objects.filter(company=company, odoo_id__isnull=False).update(odoo_id=None)
            n_pinv = PurchaseInvoice.objects.filter(
                series__company=company, odoo_id__isnull=False,
            ).update(odoo_id=None)
        self.stdout.write(
            f'  -- Reset odoo_id: customers={n_cust} providers={n_prov} '
            f'products={n_prod} sales={n_inv} purchases={n_pinv}',
        )

    def _autoconfigure_tax_mappings(self, connection: OdooConnection, company) -> None:
        from django.db.models import Q
        from core.models import TaxRate
        client = get_client_for(connection)
        client.connect()

        # TaxRate visibles para esta empresa: company=None (globales) o company=esa.
        # OJO: SQL `IN (NULL, ...)` no matchea NULLs, hay que usar Q(isnull) | Q(equal).
        rates = TaxRate.objects.filter(
            Q(company__isnull=True) | Q(company=company),
        ).distinct()

        created, updated, skipped = 0, 0, 0
        for rate in rates:
            for direction in ('sale', 'purchase'):
                tax_id = self._find_best_tax_match(client, rate, direction)
                if tax_id is None:
                    skipped += 1
                    self.stdout.write(self.style.WARNING(
                        f'  -- sin match para {rate.name} ({direction})',
                    ))
                    continue
                _, was_created = OdooTaxMapping.objects.update_or_create(
                    company=company, tax_rate=rate, direction=direction,
                    defaults={'odoo_tax_id': tax_id, 'odoo_tax_name': str(rate.name)},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'  -- OdooTaxMapping: {created} creados, {updated} actualizados, {skipped} sin match.',
        ))

    def _find_best_tax_match(self, client: OdooClient, rate, direction: str) -> int | None:
        """Heuristica: busca account.tax con mismo amount y type_tax_use, preferentemente
        sin prefijo de variante (G/S vs EU/EX/IG/RC). Si la TaxRate es una retencion,
        busca taxes con amount negativo y nombre que contenga 'WHI' o 'IRPF'.
        """
        amount = float(rate.percent)
        is_retention = rate.tax_type == 'RETENTION'

        # Busqueda primaria
        domain = [
            ('type_tax_use', '=', direction),
            ('amount', '=', amount),
        ]
        if is_retention:
            domain = [
                ('type_tax_use', '=', direction),
                ('amount', '=', -abs(amount)),
            ]

        rows = client._call(
            'account.tax', 'search_read', domain,
            ['id', 'name', 'amount', 'type_tax_use'],
        )
        if not rows:
            return None

        if is_retention:
            # Preferimos los que contengan WHI o IRPF
            prio = [r for r in rows if 'WHI' in r['name'].upper() or 'IRPF' in r['name'].upper()]
            return (prio or rows)[0]['id']

        # Para IVA, preferimos nombres simples: terminan en " G" o " S" sin tokens raros
        def score(r):
            name = r['name'].upper()
            simple = sum(token in name for token in (' G', ' S')) == 1
            extras = sum(token in name for token in ('EU', 'EX', 'IG', 'RC', 'ND', 'OSS', 'DUA', 'SE'))
            return (not simple, extras, len(name))

        rows.sort(key=score)
        return rows[0]['id']

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _read_env(name: str) -> str:
        import os
        return os.environ.get(name, '')

    def _h1(self, msg: str) -> None:
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=== ' + msg + ' ==='))

    def _step(self, msg: str) -> None:
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('-- ' + msg))
