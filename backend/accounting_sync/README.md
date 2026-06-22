# `accounting_sync` — integración ERP ↔ Odoo Community 17

Este módulo delega toda la contabilidad y la lógica fiscal en una
instancia Odoo Community 17 self-hosted. El ERP sigue siendo la fuente
de verdad para contactos, productos y facturas (incluyendo VeriFactu /
AEAT), y Odoo recibe la información para llevar la contabilidad.

> **Estado actual (Fase 3)**: aprovisionamiento automático de una BD
> Odoo por Company al crearse en el ERP, push completo de contactos /
> productos / facturas, pull de cobros y botón "Abrir contabilidad"
> con auto-login en pestaña nueva.

## Aprovisionamiento automático (una BD Odoo por Company)

Al crear una empresa en el ERP, el serializer encola un
`OdooProvisioningJob` (modelo en `accounting_sync.models`). Un
management command lo procesa en background:

1. Crea la BD en Odoo vía master password (`erp_<slug>`).
2. Instala `account`, `l10n_es`, `stock` (1–2 min).
3. Renombra `res.company` con el nombre/CIF del ERP.
4. Crea usuario API (`api@local`) con rol Accounting Administrator.
5. Persiste `OdooConnection` activa para esa Company.
6. Auto-descubre los `account.tax` de l10n_es y crea `OdooTaxMapping`.

El frontend hace polling al endpoint
`GET /api/integrations/odoo/provisioning/?company_id=X` y muestra un
modal de progreso (estado: pending → running → done|failed).

### Worker permanente con Windows Task Scheduler

El worker hay que dejarlo corriendo cada minuto:

1. **Task Scheduler → Create Basic Task**
2. Nombre: `Odoo Provisioning Worker`.
3. Trigger: Daily, **Recur every 1 days**, edita el trigger y marca
   *Repeat task every 1 minute* for a duration of *Indefinitely*.
4. Action: Start a program:
   - Program: `python.exe` (absoluto)
   - Arguments: `manage.py process_odoo_provisioning --max 3`
   - Start in: `C:\Users\xelavi\Documents\TFG\backend`
5. Marca *Run whether user is logged on or not*.

> Cron equivalente: `* * * * * cd backend && python manage.py process_odoo_provisioning --max 3 >> /var/log/odoo_prov.log 2>&1`

### Apertura de Odoo con auto-login

El endpoint `POST /api/integrations/odoo/sso-login/` con body
`{company_id: X}` devuelve `{url, db, login, password, redirect}`. El
frontend lo usa en `frontend/src/services/odoo.js` para generar un
form auto-submit en una pestaña nueva apuntando a `/web/login` de
Odoo con la BD correcta — el usuario nunca introduce credenciales.

---

## 1. Arquitectura en una frase

```
[ ERP Django ]  ──push (XML-RPC)──>  [ Odoo 17 Docker ]
                ──pull pagos (Fase 2)──
```

- Cliente XML/JSON-RPC: `odoorpc` con reintentos `tenacity`.
- Credenciales: cifradas con Fernet en BD (`OdooConnection.password`).
- Auditoría: cada operación se registra en `SyncLog`.
- Mapeo de impuestos: tabla explícita `OdooTaxMapping`
  (TaxRate del ERP ↔ account.tax de Odoo).

---

## 2. Arrancar Odoo en local (Docker)

### 2.1 Variables de entorno

Añade al `.env` de la raíz del repositorio:

```dotenv
# Postgres de Odoo
ODOO_DB_USER=odoo
ODOO_DB_PASSWORD=<generar con: openssl rand -hex 24>

# Contraseña maestra de Odoo (creación/borrado/duplicado de BD)
ODOO_MASTER_PWD=<generar con: openssl rand -hex 24>

# Clave de cifrado Fernet para OdooConnection.password
ODOO_ENCRYPTION_KEY=<generar con:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
>
```

### 2.2 Arrancar el stack

```bash
docker compose -f docker-compose.odoo.yml up -d
```

La primera arranque tarda 2–3 minutos (Odoo compila assets). Si ves
errores 502 al abrir el navegador, espera un poco más.

### 2.3 Crear la base de datos desde el asistente

1. Abre <http://localhost:8069>.
2. Master Password: la de `ODOO_MASTER_PWD`.
3. Database Name: por ejemplo `erp_demo`.
4. Email: tu correo. Password: una clave para el admin de Odoo.
5. Language: **Spanish (ES) / Español**.
6. Country: **Spain**.
7. Marca "Demo data" solo si quieres datos de prueba.
8. Pulsa **Create database** y espera.

### 2.4 Instalar módulos de localización española

Dentro de Odoo, ve a **Apps** y, si no aparece el listado, pulsa
**Update Apps List** desde el menú de desarrollador
(activa modo desarrollador en Settings → Developer Tools).

Instala:

- **Accounting** (Comptabilitat)
- **l10n_es** (Pla General Comptable)
- **l10n_es_aeat** *(opcional, puede no estar disponible aún en 17.0;
  no es bloqueante para el TFG)*

### 2.5 Crear el usuario API

1. **Settings → Users & Companies → Users → Create**.
2. Nombre: `api_user`, Email: `api@local`.
3. Aplicación → Accounting: **Administrator** (Accounting Administrator).
4. Guarda y, en el usuario creado, "Change Password" → anota la clave.

### 2.6 Configurar la conexión en el ERP

Vía API o admin:

```http
POST /api/integrations/odoo/test-connection/
Content-Type: application/json
X-Company: <company_id>

{
  "base_url": "http://localhost:8069",
  "database": "erp_demo",
  "username": "api@local",
  "password": "<contraseña del usuario API>"
}
```

Si responde `{ "ok": true, ... }`, persiste la conexión:

```http
POST /api/integrations/odoo/connections/
{
  "company": <company_id>,
  "base_url": "http://localhost:8069",
  "database": "erp_demo",
  "username": "api@local",
  "password": "<contraseña>"
}
```

### 2.7 Crear los mapeos de impuestos

Antes de hacer push de productos con IVA, registra al menos los
impuestos estándar españoles. En Odoo, **Accounting → Configuration →
Taxes**, anota los IDs de `IVA 21% (Bienes)`, `IVA 10%`, `IVA 4%` en
versión venta y compra, y crea los `OdooTaxMapping` correspondientes
desde el admin o `POST /api/integrations/odoo/tax-mappings/`.

---

## 3. Sincronización inicial y polling de pagos

### 3.1 Comando `sync_to_odoo` (push inicial / por lotes)

Sincroniza contactos, productos y facturas hacia Odoo en bloques de 50
con commit DB por bloque. Idempotente: si una entidad ya tiene
`odoo_id`, hace `write` en lugar de `create`.

```bash
# Sync completo de los últimos 12 meses
python manage.py sync_to_odoo --company <id>

# Solo contactos y productos (recomendado en la primera ejecución)
python manage.py sync_to_odoo --company <id> --skip-invoices

# Desde una fecha concreta
python manage.py sync_to_odoo --company <id> --since 2025-01-01

# Vista previa (no escribe nada en Odoo)
python manage.py sync_to_odoo --company <id> --dry-run
```

Orden de ejecución:
1. Verifica conexión + módulos `l10n_es` instalados.
2. Clientes (`customers.Customer`).
3. Proveedores (`providers.Provider`).
4. Productos (`products.Product`).
5. Facturas de venta no-draft (con `action_post` automático).
6. Facturas de compra no-draft (en draft en Odoo).
7. Resumen con totales y lista de errores.

### 3.2 Comando `pull_odoo_payments` (polling cada 5 min)

Lee de Odoo las facturas modificadas desde `last_sync_at` y actualiza
`status`, `paid_amount` y `balance_due` en el ERP.

```bash
python manage.py pull_odoo_payments
# Filtrado por empresa o fecha concreta:
python manage.py pull_odoo_payments --company <id> --since 2026-05-01
```

Mapeo de estados Odoo → ERP:
- `paid` → `Paid`
- `partial` / `in_payment` → `PartiallyPaid`
- `reversed` → `Voided`
- `not_paid` → `Approved`

Las facturas creadas directamente en Odoo (sin `odoo_id` en el ERP) se
**ignoran** según decisión de proyecto.

### 3.3 Programación con Windows Task Scheduler

1. Abre **Task Scheduler** → **Create Basic Task**.
2. Nombre: `Odoo Payment Pull`.
3. Trigger: `Daily`, hora de inicio cualquiera, **Recur every: 1 days**.
4. Tras crear, edita la tarea → pestaña **Triggers** → Edit →
   **Repeat task every: 5 minutes** for a duration of `Indefinitely`.
5. Action: **Start a program**:
   - Program: `python.exe` (ruta absoluta si no está en PATH)
   - Arguments: `manage.py pull_odoo_payments`
   - Start in: `C:\Users\xelavi\Documents\TFG\backend`
6. Marca **Run whether user is logged on or not** si quieres que se
   ejecute en background.

> Cron equivalente (Linux/macOS): `*/5 * * * * cd backend && python manage.py pull_odoo_payments >> /var/log/odoo_pull.log 2>&1`

---

## 4. Tests

```bash
cd backend
pytest -m "not integration"
```

Cobertura objetivo: >80 % en `accounting_sync/`. Los tests marcados
`@pytest.mark.integration` necesitan un Odoo real y se ejecutan con
`pytest -m integration` (no entran en CI por defecto).

---

## 5. Estado de la sincronización

| Entidad         | Push       | Pull                                  |
|-----------------|------------|---------------------------------------|
| Customer        | ✅ Fase 1   | —                                     |
| Provider        | ✅ Fase 2   | —                                     |
| Product         | ✅ Fase 1   | —                                     |
| SalesInvoice    | ✅ Fase 2   | ✅ estado de cobro                     |
| PurchaseInvoice | ✅ Fase 2   | ✅ estado de pago                      |
| Payments        | —          | ✅ vía `pull_odoo_payments` cada 5 min |

VeriFactu / AEAT permanece en el ERP: Odoo solo recibe la factura para
contabilizarla, sin invocar l10n_es_aeat.
