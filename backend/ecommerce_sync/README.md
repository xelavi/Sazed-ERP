# `ecommerce_sync` — integración ERP ↔ e-commerce (PrestaShop)

Sincroniza la parte "comercial" del ERP con una tienda online, replicando
el patrón de `accounting_sync` (Odoo). El ERP es la fuente de verdad del
catálogo y los clientes; la tienda es un canal más.

```
[ ERP Django ]  ──push (Webservice REST/XML)──▶  [ PrestaShop ]
                ◀──pull pedidos (polling)──
```

Diseñado para ser **multiplataforma**: la lógica de negocio depende de la
interfaz `clients/base.py::EcommerceClient`. Hoy hay `PrestaShopClient`;
añadir Shopify/WooCommerce es escribir una clase nueva y registrarla en
`clients/__init__.py::get_client_for`.

## Estado (esqueleto)

| Pieza | Estado |
|---|---|
| `StoreConnection` / `StoreTaxMapping` / `EcommerceSyncLog` | ✅ modelos + migración |
| `PrestaShopClient` (lectura, test, stock) | ✅ funcional y validado |
| `PrestaShopClient` (create/update XML) | ✅ funcional (refinar campos) |
| Adapters Product / Customer / Order | ✅ básicos (variantes/galería → pendiente) |
| `push_product` (+ stock + imagen) / `push_customer` | ✅ idempotente |
| `pull_customers` / `pull_products` (tienda → ERP) | ✅ idempotente |
| `pull_orders` (pedido → factura Borrador) | ✅ matching por `prestashop_id` |
| Signals push en tiempo real (Product/Customer) | ✅ |
| Comandos `sync_to_prestashop` / `pull_prestashop` / `purge_demo_products` | ✅ |
| API REST (`/api/integrations/store/...`) + admin + pantalla Home | ✅ |

## Infraestructura

PrestaShop 8.1 + MariaDB vía `docker-compose.prestashop.yml` (raíz del repo).

```bash
docker compose -f docker-compose.prestashop.yml up -d
```

- Tienda: <http://localhost:8080>
- Back office: <http://localhost:8080/admin1234>
- Webservice: <http://localhost:8080/api/>

El Webservice se activa y se crea la API key con `backend/ecommerce_setup.sql`
(idempotente). Auth = HTTP Basic con la API key como usuario y password vacío.

## Configuración en el ERP

```http
POST /api/integrations/store/test-connection/
{ "platform": "prestashop", "base_url": "http://localhost:8080", "api_key": "<key>" }

POST /api/integrations/store/connections/
{ "company": <id>, "platform": "prestashop",
  "base_url": "http://localhost:8080", "api_key": "<key>" }
```

## Uso

```bash
# Carga inicial ERP → tienda
python manage.py sync_to_prestashop --company <id>
python manage.py sync_to_prestashop --company <id> --only products --dry-run

# Polling de pedidos tienda → ERP (programar cada N min en Task Scheduler)
python manage.py pull_prestashop
```

## Cifrado

La API key se guarda cifrada (Fernet) con `EncryptedTextField`, reutilizando
`ODOO_ENCRYPTION_KEY` salvo que se defina `ECOMMERCE_ENCRYPTION_KEY`.

## Pendiente (próximas fases)

1. `pull_orders`: pedido PrestaShop → `Invoice` (encadena con el push a Odoo)
   y descuento de stock en el ERP.
2. Adapters: categorías, imágenes, variantes (combinations) y direcciones.
3. `StoreTaxMapping` aplicado en el push de precios con IVA.
4. Tests (pytest) con marca `integration` para los que requieren PrestaShop.
5. Frontend: pantalla de conexión (espejo de la de Odoo).
