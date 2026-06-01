"""
Cliente Odoo basado en odoorpc.

Encapsula la conexión XML-RPC con reintentos automáticos para errores
transitorios y exposición de métodos con nombres del dominio del ERP
en lugar de los crudos de odoorpc.

Nunca se loguea el password.
"""
from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

import odoorpc
from django.conf import settings
from odoorpc.error import RPCError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class OdooConnectionError(Exception):
    """Error de conexión o autenticación con Odoo."""


class OdooClient:
    """Cliente Odoo con cache de sesión y reintentos.

    Args:
        base_url: URL completa (`http://host:8069` o `https://...`).
        database: nombre de la base de datos en Odoo.
        username: usuario API.
        password: contraseña en claro (sólo en memoria).
        timeout: timeout por defecto de las peticiones (segundos).
    """

    def __init__(
        self,
        base_url: str,
        database: str,
        username: str,
        password: str,
        timeout: int | None = None,
    ) -> None:
        self.base_url = base_url.rstrip('/')
        self.database = database
        self.username = username
        self._password = password
        self.timeout = timeout or getattr(settings, 'ODOO_RPC_TIMEOUT', 30)

        parsed = urlparse(self.base_url)
        self.host = parsed.hostname or 'localhost'
        self.port = parsed.port or (443 if parsed.scheme == 'https' else 8069)
        self.protocol = 'jsonrpc+ssl' if parsed.scheme == 'https' else 'jsonrpc'

        self._odoo: odoorpc.ODOO | None = None
        self._uid: int | None = None

    # ── Conexión ─────────────────────────────────────────

    def connect(self) -> int:
        """Establece sesión con Odoo y devuelve el UID autenticado."""
        if self._odoo is not None and self._uid is not None:
            return self._uid

        logger.info(
            'Conectando a Odoo %s:%s db=%s user=%s',
            self.host, self.port, self.database, self.username,
        )
        try:
            odoo = odoorpc.ODOO(
                self.host, port=self.port, protocol=self.protocol,
                timeout=self.timeout,
            )
            odoo.login(self.database, self.username, self._password)
        except (odoorpc.error.Error, ConnectionError, OSError) as exc:
            logger.error('Fallo autenticando contra Odoo: %s', exc)
            raise OdooConnectionError(str(exc)) from exc

        self._odoo = odoo
        self._uid = odoo.env.uid
        return self._uid

    @property
    def env(self):
        """Devuelve el `env` de odoorpc (autoconecta si hace falta)."""
        self.connect()
        assert self._odoo is not None  # narrow para mypy
        return self._odoo.env

    def server_version(self) -> str:
        """Versión del servidor Odoo (no requiere autenticación)."""
        odoo = odoorpc.ODOO(
            self.host, port=self.port, protocol=self.protocol,
            timeout=self.timeout,
        )
        return odoo.version

    def web_session_id(self) -> str:
        """Autentica vía `/web/session/authenticate` y devuelve el session_id.

        Este endpoint es JSON-RPC y NO exige csrf_token (a diferencia de
        `/web/login`), por lo que sirve para construir un auto-login: el
        navegador solo necesita la cookie `session_id` para entrar.

        Raises:
            OdooConnectionError: si las credenciales fallan o no llega cookie.
        """
        import requests

        url = f'{self.base_url}/web/session/authenticate'
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'db': self.database,
                'login': self.username,
                'password': self._password,
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise OdooConnectionError(f'No se pudo autenticar en Odoo web: {exc}') from exc

        body = resp.json()
        if body.get('error') or not (body.get('result') or {}).get('uid'):
            raise OdooConnectionError('Credenciales rechazadas por Odoo web.')

        session_id = resp.cookies.get('session_id')
        if not session_id:
            raise OdooConnectionError('Odoo no devolvió cookie session_id.')
        return session_id

    # ── Helpers internos con reintentos ─────────────────

    _retry = retry(
        retry=retry_if_exception_type((RPCError, ConnectionError, OSError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )

    @_retry
    def _search(self, model: str, domain: list, limit: int | None = None) -> list[int]:
        env = self.env
        kwargs: dict[str, Any] = {}
        if limit is not None:
            kwargs['limit'] = limit
        return env[model].search(domain, **kwargs)

    @_retry
    def _read(self, model: str, ids: list[int], fields: list[str] | None = None) -> list[dict]:
        env = self.env
        return env[model].read(ids, fields) if fields else env[model].read(ids)

    @_retry
    def _create(self, model: str, values: dict) -> int:
        env = self.env
        return env[model].create(values)

    @_retry
    def _write(self, model: str, ids: list[int], values: dict) -> bool:
        env = self.env
        return env[model].write(ids, values)

    @_retry
    def _call(self, model: str, method: str, *args, **kwargs):
        env = self.env
        return getattr(env[model], method)(*args, **kwargs)

    # ── Métodos de dominio ──────────────────────────────

    # Países
    def find_country_id(self, code: str = 'ES') -> int | None:
        """Devuelve el ID de `res.country` por su código ISO ('ES')."""
        ids = self._search('res.country', [('code', '=', code)], limit=1)
        return ids[0] if ids else None

    # Monedas
    def find_currency_id(self, code: str = 'EUR') -> int | None:
        """Devuelve el ID de `res.currency` por su código ISO ('EUR')."""
        ids = self._search('res.currency', [('name', '=', code)], limit=1)
        return ids[0] if ids else None

    # Partners
    def find_partner_by_vat(self, vat: str) -> int | None:
        ids = self._search('res.partner', [('vat', '=', vat)], limit=1)
        return ids[0] if ids else None

    def create_partner(self, data: dict) -> int:
        return self._create('res.partner', data)

    def update_partner(self, partner_id: int, data: dict) -> bool:
        return self._write('res.partner', [partner_id], data)

    def get_partner(self, partner_id: int) -> dict | None:
        rows = self._read('res.partner', [partner_id])
        return rows[0] if rows else None

    # Productos
    def find_product_by_default_code(self, default_code: str) -> int | None:
        ids = self._search(
            'product.product', [('default_code', '=', default_code)], limit=1,
        )
        return ids[0] if ids else None

    def create_product(self, data: dict) -> int:
        return self._create('product.product', data)

    def update_product(self, product_id: int, data: dict) -> bool:
        return self._write('product.product', [product_id], data)

    # Impuestos
    def find_tax(
        self,
        name: str | None = None,
        amount: float | None = None,
        type_tax_use: str | None = None,
    ) -> int | None:
        domain: list = []
        if name:
            domain.append(('name', '=', name))
        if amount is not None:
            domain.append(('amount', '=', amount))
        if type_tax_use:
            domain.append(('type_tax_use', '=', type_tax_use))
        if not domain:
            return None
        ids = self._search('account.tax', domain, limit=1)
        return ids[0] if ids else None

    # Facturas (account.move)
    def create_invoice(self, data: dict) -> int:
        return self._create('account.move', data)

    def update_invoice(self, invoice_id: int, data: dict) -> bool:
        return self._write('account.move', [invoice_id], data)

    def post_invoice(self, invoice_id: int) -> Any:
        """Confirma la factura en Odoo (transición draft → posted)."""
        return self._call('account.move', 'action_post', [invoice_id])

    def get_invoice(self, invoice_id: int, fields: list[str] | None = None) -> dict | None:
        rows = self._read('account.move', [invoice_id], fields)
        return rows[0] if rows else None

    def list_invoices_since(
        self,
        since,
        move_types: list[str] | None = None,
        fields: list[str] | None = None,
    ) -> list[dict]:
        """Devuelve facturas modificadas desde `since` (datetime aware).

        Args:
            since: datetime mínimo de `write_date`. Si es None, sin filtro.
            move_types: lista de tipos (`out_invoice`, `in_invoice`, …).
            fields: campos a leer; si None, defaults razonables.
        """
        types = move_types or ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']
        domain: list = [('move_type', 'in', types)]
        if since is not None:
            # Odoo espera 'YYYY-MM-DD HH:MM:SS' en UTC
            since_str = since.strftime('%Y-%m-%d %H:%M:%S')
            domain.append(('write_date', '>=', since_str))
        fields = fields or [
            'id', 'name', 'move_type', 'state', 'payment_state',
            'amount_total', 'amount_residual', 'invoice_date',
            'partner_id', 'write_date',
        ]
        return self._call('account.move', 'search_read', domain, fields)

    # Módulos instalados (verificación l10n_es)
    def list_modules_installed(self, names: list[str]) -> dict[str, bool]:
        """Devuelve un dict {name: instalado?} para los módulos indicados."""
        if not names:
            return {}
        rows = self._call(
            'ir.module.module',
            'search_read',
            [('name', 'in', names)],
            ['name', 'state'],
        )
        installed = {row['name']: row['state'] == 'installed' for row in rows}
        return {n: installed.get(n, False) for n in names}

    def install_modules(self, names: list[str], timeout: int = 600) -> dict[str, bool]:
        """Instala los módulos pedidos si no están ya instalados.

        Args:
            names: módulos a instalar (p. ej. ['account', 'l10n_es', 'stock']).
            timeout: timeout total en segundos para la operación de instalación.

        Returns:
            Dict {name: instalado?} con el estado tras la operación.

        Notas:
            Si Odoo tarda más que el timeout del HTTP client, se asume que la
            instalación continúa en background y se hace polling de estado
            hasta `timeout` segundos.
        """
        if not names:
            return {}
        env = self.env
        Module = env['ir.module.module']

        # Refresca la lista de apps disponibles
        try:
            self._call('ir.module.module', 'update_list')
        except Exception:  # noqa: BLE001
            pass

        rows = self._call(
            'ir.module.module',
            'search_read',
            [('name', 'in', names)],
            ['id', 'name', 'state'],
        )
        to_install_ids = [r['id'] for r in rows if r['state'] != 'installed']
        if not to_install_ids:
            return {r['name']: True for r in rows}

        logger.info('Instalando modulos Odoo: %s', [r['name'] for r in rows if r['id'] in to_install_ids])

        # Subimos el timeout del HTTP client mientras dure la instalación
        prev_timeout = self._odoo.config.get('timeout') if self._odoo else None
        if self._odoo:
            self._odoo.config['timeout'] = timeout
        try:
            try:
                Module.button_immediate_install(to_install_ids)
            except (TimeoutError, OSError) as exc:
                logger.warning(
                    'button_immediate_install lanzó %s; polleamos estado.', type(exc).__name__,
                )
        finally:
            if self._odoo and prev_timeout is not None:
                self._odoo.config['timeout'] = prev_timeout

        # Polling de estado hasta que todos los pedidos estén instalados
        import time as _t
        deadline = _t.monotonic() + timeout
        while _t.monotonic() < deadline:
            rows = self._call(
                'ir.module.module',
                'search_read',
                [('name', 'in', names)],
                ['name', 'state'],
            )
            installed = {row['name']: row['state'] == 'installed' for row in rows}
            if all(installed.get(n) for n in names):
                return {n: installed.get(n, False) for n in names}
            _t.sleep(3)

        # Devuelve el último estado leído
        return {n: installed.get(n, False) for n in names}

    # Usuarios
    def create_api_user(
        self,
        login: str,
        password: str,
        name: str = 'API User',
        groups: list[str] | None = None,
    ) -> int:
        """Crea un usuario con los grupos indicados (XML IDs).

        Si ya existe un usuario con ese `login`, devuelve su ID y le
        resetea la contraseña + grupos sin volver a crearlo (idempotente).
        """
        env = self.env
        existing = self._search('res.users', [('login', '=', login)], limit=1)
        group_ids = self._resolve_group_ids(groups or ['account.group_account_manager'])
        values: dict[str, Any] = {
            'name': name,
            'login': login,
            'password': password,
            'groups_id': [(6, 0, group_ids)],
        }
        if existing:
            self._write('res.users', existing, values)
            return existing[0]
        return self._create('res.users', values)

    def _resolve_group_ids(self, xml_ids: list[str]) -> list[int]:
        """Convierte XML IDs (`module.name`) a IDs numéricos de `res.groups`.

        Resuelve vía `ir.model.data.search_read` porque los helpers
        `_xmlid_to_res_id` / `xmlid_to_res_id` son privados y Odoo no los
        expone por RPC.
        """
        ids: list[int] = []
        for xml in xml_ids:
            try:
                module, name = xml.split('.', 1)
            except ValueError:
                logger.warning('XML ID de grupo mal formado: %r', xml)
                continue
            rows = self._call(
                'ir.model.data', 'search_read',
                [('module', '=', module), ('name', '=', name)],
                ['res_id'],
            )
            if rows:
                ids.append(rows[0]['res_id'])
            else:
                logger.warning('Grupo Odoo %r no encontrado, se omite.', xml)
        return ids

    # res.company (la empresa contable dentro de Odoo)
    def update_main_company(self, name: str, vat: str | None = None) -> int:
        """Renombra (y opcionalmente fija el VAT de) la `res.company` por defecto.

        En una BD recién creada hay una sola company. La identificamos por
        el menor ID. Devolvemos su ID por si el caller la quiere referenciar.
        """
        ids = self._search('res.company', [], limit=1)
        if not ids:
            return 0
        values: dict[str, Any] = {'name': name}
        if vat:
            values['vat'] = vat
        self._write('res.company', ids, values)
        return ids[0]

    # ── Contabilidad: tesorería simulada ────────────────

    def find_account_id(self, code: str) -> int | None:
        """ID de `account.account` por código exacto (p. ej. '572001')."""
        ids = self._search('account.account', [('code', '=', code)], limit=1)
        return ids[0] if ids else None

    def find_account_id_like(self, code_prefix: str, account_type: str | None = None) -> int | None:
        """Primera `account.account` cuyo código empieza por `code_prefix`."""
        domain: list = [('code', '=like', f'{code_prefix}%')]
        if account_type:
            domain.append(('account_type', '=', account_type))
        ids = self._search('account.account', domain, limit=1)
        return ids[0] if ids else None

    def find_bank_journal(self) -> dict | None:
        """Diario de banco (type='bank') con su cuenta por defecto."""
        rows = self._call(
            'account.journal', 'search_read',
            [('type', '=', 'bank')], ['id', 'name', 'default_account_id'],
        )
        return rows[0] if rows else None

    def find_general_journal_id(self) -> int | None:
        """Diario para asientos varios (type='general')."""
        ids = self._search('account.journal', [('type', '=', 'general')], limit=1)
        return ids[0] if ids else None

    def create_opening_balance(
        self, *, bank_account_id: int, equity_account_id: int,
        journal_id: int, amount: float, ref: str,
    ) -> int | None:
        """Crea y contabiliza un asiento de apertura (Debe banco / Haber capital).

        Idempotente: si ya existe un asiento con ese `ref`, no crea otro y
        devuelve None.
        """
        existing = self._search('account.move', [('ref', '=', ref)], limit=1)
        if existing:
            return None

        move_id = self._create('account.move', {
            'move_type': 'entry',
            'journal_id': journal_id,
            'ref': ref,
            'line_ids': [
                (0, 0, {'account_id': bank_account_id, 'debit': amount, 'credit': 0.0,
                        'name': 'Saldo inicial'}),
                (0, 0, {'account_id': equity_account_id, 'debit': 0.0, 'credit': amount,
                        'name': 'Saldo inicial'}),
            ],
        })
        self._call('account.move', 'action_post', [move_id])
        return move_id

    def set_journal_direct_payment_account(self, journal_id: int, account_id: int) -> int:
        """Hace que los pagos del diario concilien directo contra `account_id`.

        Por defecto Odoo manda los pagos a una cuenta transitoria ("cobros
        pendientes") y el dinero solo llega al banco al conciliar el extracto.
        Poniendo `payment_account_id` = cuenta del banco en las líneas de
        método de pago, cada cobro/pago mueve el banco al instante.

        Devuelve el número de líneas configuradas.
        """
        line_ids = self._search(
            'account.payment.method.line', [('journal_id', '=', journal_id)],
        )
        if line_ids:
            self._write(
                'account.payment.method.line', line_ids,
                {'payment_account_id': account_id},
            )
        return len(line_ids)

    def invoice_payment_state(self, move_id: int) -> str | None:
        rows = self._read('account.move', [move_id], ['payment_state'])
        return rows[0]['payment_state'] if rows else None

    def register_invoice_payment(self, move_id: int, journal_id: int) -> bool:
        """Registra el pago/cobro total de una factura ya contabilizada.

        Usa el wizard `account.payment.register`, que crea el account.payment,
        lo contabiliza y lo concilia con la factura (mueve la cuenta de banco).
        La dirección (cobro/pago) la deduce Odoo del move_type.

        Idempotente: si la factura ya está pagada/en pago, no hace nada.
        """
        state = self.invoice_payment_state(move_id)
        if state in ('paid', 'in_payment', 'reversed'):
            return False

        # odoorpc: create() devuelve un int (id), no un recordset; los métodos
        # del wizard se invocan sobre el proxy de modelo pasando la lista de ids.
        register = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=[move_id],
        )
        wizard_id = register.create({'journal_id': journal_id})
        register.action_create_payments([wizard_id])
        return True

    # Bases de datos (gestión, requiere master password)
    @staticmethod
    def create_database(
        base_url: str, master_pwd: str, db_name: str,
        admin_password: str = 'admin', lang: str = 'es_ES',
        country_code: str = 'ES', demo: bool = False,
    ) -> None:
        """Crea una nueva BD vía el servicio `db.create_database` de Odoo.

        Llamada bloqueante: puede tardar 1-3 minutos en instalar el módulo base.
        """
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 8069)
        protocol = 'jsonrpc+ssl' if parsed.scheme == 'https' else 'jsonrpc'
        odoo = odoorpc.ODOO(host, port=port, protocol=protocol, timeout=600)
        odoo.db.create(master_pwd, db_name, demo, lang, admin_password)

    @staticmethod
    def list_databases(base_url: str) -> list[str]:
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or (443 if parsed.scheme == 'https' else 8069)
        protocol = 'jsonrpc+ssl' if parsed.scheme == 'https' else 'jsonrpc'
        odoo = odoorpc.ODOO(host, port=port, protocol=protocol, timeout=30)
        return odoo.db.list()
