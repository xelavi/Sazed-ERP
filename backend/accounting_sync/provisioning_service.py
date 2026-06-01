"""
Aprovisionamiento automático ERP → Odoo.

Función principal: `provision_for_company(job)`.

Pasos (idempotentes):
    1. Crear BD nueva en Odoo vía master password.
    2. Conectar como admin e instalar `account`, `l10n_es`, `stock`.
    3. Actualizar `res.company` con el nombre/CIF de la Company del ERP.
    4. Crear usuario API `api@local`.
    5. Crear `OdooConnection` activa para la Company.
    6. Auto-descubrir impuestos l10n_es → crear `OdooTaxMapping`.

El servicio NUNCA lanza excepciones: captura todo y registra el error
en `job.error_message`. El management command es el responsable de
re-encolar si `attempts < max_attempts`.
"""
from __future__ import annotations

import logging
import secrets
import time
from typing import Iterable

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    OdooConnection,
    OdooProvisioningJob,
    OdooTaxMapping,
)
from .odoo_client import OdooClient, OdooConnectionError

logger = logging.getLogger(__name__)


REQUIRED_MODULES = ['account', 'l10n_es', 'stock']
API_USER_LOGIN = 'api@local'
# Grupos que necesita el usuario API para sincronizar y ver toda la contabilidad:
# - account.group_account_user: funciones de contabilidad COMPLETAS
#   (plan de cuentas, asientos, libro mayor, balances), no solo facturación.
# - account.group_account_manager: administración de facturación/impuestos.
# - base.group_partner_manager: crear/editar contactos (res.partner).
API_USER_GROUPS = [
    'account.group_account_user',
    'account.group_account_manager',
    'base.group_partner_manager',
]

# Tesorería simulada: cada empresa arranca con este saldo en banco.
OPENING_BALANCE = 10000.0
OPENING_BALANCE_REF = 'ERP-OPENING-BALANCE'
BANK_ACCOUNT_CODE = '572'   # Bancos c/c (prefijo PGC español)
EQUITY_ACCOUNT_CODE = '100'  # Capital social


def build_database_name(company) -> str:
    """Genera un nombre de BD único y seguro a partir del slug de la company."""
    base = slugify(company.slug or company.name or f'company-{company.pk}')
    base = base.replace('-', '_')[:40] or f'company_{company.pk}'
    return f'erp_{base}'


def enqueue_for_company(company) -> OdooProvisioningJob:
    """Crea (o reusa) un job pendiente para la company.

    Si ya hay un job pending/running para esta company, devuelve ese
    (idempotente — evita encolar provisioning concurrentes).
    """
    existing = (
        OdooProvisioningJob.objects
        .filter(company=company, status__in=[
            OdooProvisioningJob.Status.PENDING,
            OdooProvisioningJob.Status.RUNNING,
        ])
        .first()
    )
    if existing:
        return existing

    return OdooProvisioningJob.objects.create(
        company=company,
        database_name=build_database_name(company),
        admin_password=secrets.token_urlsafe(16),
        status=OdooProvisioningJob.Status.PENDING,
    )


def provision_for_company(job: OdooProvisioningJob) -> bool:
    """Ejecuta el aprovisionamiento. Devuelve True si terminó OK.

    Nunca lanza: registra el error en el job.
    """
    job.status = OdooProvisioningJob.Status.RUNNING
    job.started_at = timezone.now()
    job.attempts += 1
    job.save(update_fields=['status', 'started_at', 'attempts'])

    try:
        company = job.company
        master_pwd = getattr(settings, 'ODOO_MASTER_PWD', '') or ''
        base_url = getattr(settings, 'ODOO_BASE_URL', 'http://localhost:8069')

        if not master_pwd:
            raise RuntimeError(
                'ODOO_MASTER_PWD no configurado. Define la variable en el .env '
                'y reinicia el server.',
            )

        # 1. Crear la BD si no existe
        _log(job, f'Comprobando BD "{job.database_name}" en {base_url}…')
        existing_dbs = OdooClient.list_databases(base_url)
        if job.database_name in existing_dbs:
            _log(job, f'BD "{job.database_name}" ya existe; reutilizando.')
        else:
            _log(job, f'Creando BD "{job.database_name}" (1-3 minutos, instala base modules)…')
            t0 = time.monotonic()
            OdooClient.create_database(
                base_url=base_url,
                master_pwd=master_pwd,
                db_name=job.database_name,
                admin_password=job.admin_password,
            )
            _log(job, f'BD creada en {time.monotonic() - t0:.0f}s.')

        # 2. Conectar como admin e instalar módulos
        admin_client = OdooClient(
            base_url=base_url,
            database=job.database_name,
            username='admin',
            password=job.admin_password,
        )
        _log(job, 'Conectando como admin…')
        admin_client.connect()

        _log(job, f'Instalando módulos {REQUIRED_MODULES} (~1 min)…')
        installed = admin_client.install_modules(REQUIRED_MODULES, timeout=600)
        missing = [n for n, ok in installed.items() if not ok]
        if missing:
            raise RuntimeError(
                f'Módulos sin instalar tras 10 min: {missing}. '
                'Instálalos manualmente con la CLI de Odoo.',
            )
        _log(job, 'Módulos instalados.')

        # 3. Renombrar res.company con el nombre de la Company del ERP.
        # Solo enviamos el VAT si pasa la validación NIF/CIF de l10n_es;
        # un CIF inválido haría fallar el write (mismo criterio que ContactAdapter).
        from .adapters.contact_adapter import ContactAdapter
        raw_vat = getattr(company, 'tax_id', None) or None
        valid_vat = ContactAdapter._vat_with_prefix(raw_vat) or None
        if raw_vat and not valid_vat:
            _log(job, f'CIF "{raw_vat}" no válido para l10n_es; se omite (configúralo luego en Odoo).')
        _log(job, f'Configurando res.company -> "{company.name}"...')
        admin_client.update_main_company(name=company.name, vat=valid_vat)

        # 4. Crear usuario API
        api_password = secrets.token_urlsafe(16)
        _log(job, f'Creando usuario API "{API_USER_LOGIN}"…')
        admin_client.create_api_user(
            login=API_USER_LOGIN,
            password=api_password,
            name='ERP Sync API',
            groups=API_USER_GROUPS,
        )

        # 5. Crear / actualizar OdooConnection
        _log(job, 'Persistiendo OdooConnection…')
        conn, created = OdooConnection.objects.update_or_create(
            company=company,
            defaults={
                'base_url': base_url,
                'database': job.database_name,
                'username': API_USER_LOGIN,
                'password': api_password,
                'is_active': True,
                'last_sync_status': OdooConnection.SyncStatus.NEVER,
            },
        )
        _log(job, f'OdooConnection {"creada" if created else "actualizada"}.')

        # 6. Auto-configurar OdooTaxMapping
        _log(job, 'Detectando impuestos l10n_es y mapeándolos…')
        api_client = OdooClient(
            base_url=base_url,
            database=job.database_name,
            username=API_USER_LOGIN,
            password=api_password,
        )
        n_created, n_skipped = autoconfigure_tax_mappings(api_client, company)
        _log(job, f'OdooTaxMapping: {n_created} creados, {n_skipped} sin match (configúralos a mano).')

        # 7. Saldo inicial de tesorería (asiento de apertura)
        _log(job, f'Creando saldo inicial de {OPENING_BALANCE:.0f} € en banco…')
        try:
            move_id = ensure_opening_balance(admin_client)
            _log(job, 'Saldo inicial creado.' if move_id else 'Saldo inicial ya existía; se omite.')
        except Exception as exc:  # noqa: BLE001
            _log(job, f'No se pudo crear el saldo inicial (no bloqueante): {exc}')

        # Done
        job.status = OdooProvisioningJob.Status.DONE
        job.finished_at = timezone.now()
        job.error_message = ''
        job.save(update_fields=['status', 'finished_at', 'error_message', 'logs'])
        _log(job, 'Provisioning completado.')
        return True

    except OdooConnectionError as exc:
        return _mark_failed(job, f'Conexión Odoo: {exc}')
    except Exception as exc:  # noqa: BLE001
        logger.exception('Provisioning falló para company=%s', job.company_id)
        return _mark_failed(job, f'{type(exc).__name__}: {exc}')


# ── Helpers ─────────────────────────────────────────────


def _log(job: OdooProvisioningJob, line: str) -> None:
    job.append_log(line)
    job.save(update_fields=['logs'])
    logger.info('[provision job=%s] %s', job.pk, line)


def _mark_failed(job: OdooProvisioningJob, message: str) -> bool:
    job.status = OdooProvisioningJob.Status.FAILED
    job.error_message = message
    job.finished_at = timezone.now()
    job.append_log(f'ERROR: {message}')
    job.save(update_fields=['status', 'error_message', 'finished_at', 'logs'])
    return False


def ensure_opening_balance(client: OdooClient) -> int | None:
    """Configura la tesorería simulada y crea el asiento de apertura.

    1. Hace que el diario de banco concilie los pagos directo contra su
       cuenta (para que cobros/pagos muevan el banco al instante).
    2. Crea el asiento de apertura: Debe banco / Haber capital.

    Devuelve el id del asiento creado, o None si ya existía.
    """
    bank_journal = client.find_bank_journal()
    bank_account_id = None
    if bank_journal and bank_journal.get('default_account_id'):
        bank_account_id = bank_journal['default_account_id'][0]
    if not bank_account_id:
        bank_account_id = client.find_account_id_like(BANK_ACCOUNT_CODE, 'asset_cash')

    equity_account_id = client.find_account_id_like(EQUITY_ACCOUNT_CODE, 'equity')
    journal_id = client.find_general_journal_id()

    if not (bank_account_id and equity_account_id and journal_id):
        raise RuntimeError(
            f'Faltan cuentas/diario para el saldo inicial '
            f'(banco={bank_account_id}, capital={equity_account_id}, diario={journal_id}).',
        )

    # Pagos directos al banco (sin cuenta transitoria de cobros pendientes).
    if bank_journal:
        client.set_journal_direct_payment_account(bank_journal['id'], bank_account_id)

    return client.create_opening_balance(
        bank_account_id=bank_account_id,
        equity_account_id=equity_account_id,
        journal_id=journal_id,
        amount=OPENING_BALANCE,
        ref=OPENING_BALANCE_REF,
    )


def autoconfigure_tax_mappings(client: OdooClient, company) -> tuple[int, int]:
    """Crea OdooTaxMapping por matching de porcentaje en account.tax.

    Devuelve (creados, sin_match). Idempotente.
    """
    from core.models import TaxRate

    rates = TaxRate.objects.filter(
        Q(company__isnull=True) | Q(company=company),
    ).distinct()

    created, skipped = 0, 0
    for rate in rates:
        for direction in ('sale', 'purchase'):
            tax_id = _find_best_tax_match(client, rate, direction)
            if tax_id is None:
                skipped += 1
                continue
            _, was_created = OdooTaxMapping.objects.update_or_create(
                company=company, tax_rate=rate, direction=direction,
                defaults={'odoo_tax_id': tax_id, 'odoo_tax_name': str(rate.name)},
            )
            if was_created:
                created += 1
    return created, skipped


def _find_best_tax_match(client: OdooClient, rate, direction: str) -> int | None:
    """Match heurístico: porcentaje + dirección, descarta variantes raras."""
    amount = float(rate.percent)
    is_retention = getattr(rate, 'tax_type', '') == 'RETENTION'

    domain: list = [
        ('type_tax_use', '=', direction),
        ('amount', '=', -abs(amount) if is_retention else amount),
    ]
    rows = client._call(
        'account.tax', 'search_read', domain,
        ['id', 'name', 'amount', 'type_tax_use'],
    )
    if not rows:
        return None

    if is_retention:
        prio = [r for r in rows if 'WHI' in r['name'].upper() or 'IRPF' in r['name'].upper()]
        return (prio or rows)[0]['id']

    def score(r):
        name = r['name'].upper()
        simple = sum(token in name for token in (' G', ' S')) == 1
        extras = sum(token in name for token in ('EU', 'EX', 'IG', 'RC', 'ND', 'OSS', 'DUA', 'SE'))
        return (not simple, extras, len(name))

    rows.sort(key=score)
    return rows[0]['id']
