# 🗺️ MVP Roadmap - Sazed ERP

> **Objetivo:** Convertir Sazed ERP en un producto mínimo viable funcional para PyMEs y autónomos  
> **Plazo estimado:** 6-8 semanas  
> **Enfoque:** Implementar el ciclo comercial completo (Producto → Pedido → Factura → Cobro → Inventario)

---

## 📊 Progreso Actual

```
████████████░░░░░░░░ 60% Completado

Implementado:     ~4,200 líneas
Falta por hacer:  ~3,500 líneas estimadas
```

---

## 🎯 Fase 1: MVP Core (Semanas 1-2)

### Objetivo: Ciclo Comercial Completo

#### 1.1 Módulo de Pedidos (Orders) - 🔴 CRÍTICO
**Tiempo estimado:** 4-5 días  
**Complejidad:** Media  

**User Stories:**
- [ ] Como vendedor, quiero crear un pedido para un cliente para registrar una venta
- [ ] Como vendedor, quiero añadir productos al pedido desde el catálogo
- [ ] Como vendedor, quiero calcular automáticamente el total con IVA
- [ ] Como vendedor, quiero cambiar el estado del pedido (Draft → Confirmed → Completed)
- [ ] Como vendedor, quiero convertir un pedido en factura con un click
- [ ] Como administrador, quiero ver un listado de todos los pedidos con filtros

**Archivos a crear:**
```
src/
  views/
    Orders.vue           (listado + filtros)
  components/
    OrderFormModal.vue   (crear/editar pedido)
    OrderDetailDrawer.vue (detalle lateral)
```

**Datos del modelo:**
```typescript
interface Order {
  id: string
  number: string           // ORD-2026-0001
  customerId: string
  customerName: string
  status: 'draft' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  orderDate: string
  deliveryDate: string
  lines: OrderLine[]
  subtotal: number
  tax: number
  total: number
  notes: string
  createdAt: string
  updatedAt: string
}

interface OrderLine {
  productId: string
  productName: string
  quantity: number
  unitPrice: number
  taxRate: number
  subtotal: number
  total: number
}
```

---

#### 1.2 Módulo de Inventario (Inventory) - 🔴 CRÍTICO
**Tiempo estimado:** 5-6 días  
**Complejidad:** Media-Alta  

**User Stories:**
- [ ] Como gerente, quiero ver el stock actual de todos mis productos
- [ ] Como gerente, quiero registrar entradas de mercancía al almacén
- [ ] Como gerente, quiero registrar salidas de mercancía (ventas, mermas)
- [ ] Como gerente, quiero ajustar el inventario manualmente
- [ ] Como sistema, quiero descontar stock automáticamente cuando se completa un pedido
- [ ] Como gerente, quiero recibir alertas cuando un producto esté bajo de stock

**Archivos a crear:**
```
src/
  views/
    Inventory.vue           (listado con stock)
    InventoryMovements.vue  (historial de movimientos)
  components/
    StockAdjustmentModal.vue
    MovementFormModal.vue
```

**Datos del modelo:**
```typescript
interface InventoryItem {
  productId: string
  productName: string
  sku: string
  currentStock: number
  minStock: number
  maxStock: number
  unitCost: number
  totalValue: number
  status: 'in_stock' | 'low_stock' | 'out_of_stock'
  lastMovement: string
}

interface StockMovement {
  id: string
  productId: string
  type: 'in' | 'out' | 'adjustment'
  reason: 'purchase' | 'sale' | 'return' | 'loss' | 'adjustment'
  quantity: number
  previousStock: number
  newStock: number
  unitCost: number
  reference: string  // ID de pedido/factura relacionada
  notes: string
  createdBy: string
  createdAt: string
}
```

**Lógica de Negocio:**
- Al completar un pedido → genera movimiento OUT
- Al recibir mercancía → genera movimiento IN
- Al ajustar manualmente → genera movimiento ADJUSTMENT
- Si stock < minStock → badge "Low stock" en rojo
- Si stock = 0 → badge "Out of stock" en gris

---

#### 1.3 Módulo de Configuración (Settings) - 🔴 CRÍTICO
**Tiempo estimado:** 3-4 días  
**Complejidad:** Media  

**User Stories:**
- [ ] Como administrador, quiero configurar los datos de mi empresa
- [ ] Como administrador, quiero configurar series de numeración para facturas
- [ ] Como administrador, quiero definir los tipos de IVA aplicables
- [ ] Como administrador, quiero configurar los métodos de pago aceptados
- [ ] Como administrador, quiero personalizar el logo de la empresa

**Archivos a crear:**
```
src/
  views/
    Settings.vue
  components/
    settings/
      CompanySettings.vue
      InvoiceSettings.vue
      TaxSettings.vue
      PaymentSettings.vue
```

**Datos del modelo:**
```typescript
interface CompanySettings {
  name: string
  taxId: string        // NIF/CIF
  address: string
  city: string
  postalCode: string
  country: string
  phone: string
  email: string
  website: string
  logo: string         // URL o base64
}

interface InvoiceSeries {
  id: string
  prefix: string       // "FAC", "ORD", "PRE"
  nextNumber: number
  format: string       // "{prefix}-{year}-{number:4}"
  resetYearly: boolean
}

interface TaxRate {
  id: string
  name: string         // "IVA General", "IVA Reducido"
  rate: number         // 21, 10, 4
  type: 'vat' | 'igic' | 'retention'
  isDefault: boolean
}

interface PaymentMethod {
  id: string
  name: string         // "Transferencia", "Efectivo", "Tarjeta"
  type: 'bank_transfer' | 'cash' | 'card' | 'paypal' | 'other'
  isActive: boolean
}
```

---

#### 1.4 Integración entre Módulos
**Tiempo estimado:** 2-3 días  

**Tareas:**
- [ ] Conectar Orders → Invoices (conversión)
- [ ] Conectar Orders → Inventory (descuento stock al completar)
- [ ] Conectar Products con stock real desde Inventory
- [ ] Validar disponibilidad de stock al crear pedido
- [ ] Actualizar dashboard con datos de pedidos e inventario

---

## 🎯 Fase 2: Ciclo Financiero (Semanas 3-4)

### 2.1 Módulo de Gastos (Expenses)
**Tiempo estimado:** 4-5 días  

**User Stories:**
- [ ] Como contable, quiero registrar facturas de proveedores
- [ ] Como contable, quiero categorizar gastos (oficina, transporte, servicios)
- [ ] Como contable, quiero ver un balance P&L simple
- [ ] Como contable, quiero exportar datos para mi gestoría

---

### 2.2 CRM Mejorado
**Tiempo estimado:** 3-4 días  

**Mejoras sobre Customers.vue:**
- [ ] Vista de detalle con tabs (Datos, Facturas, Pedidos, Notas)
- [ ] Historial cronológico de interacciones
- [ ] Indicadores: Total facturado, Deuda pendiente, Días desde última compra
- [ ] Notas y comentarios internos
- [ ] Tags y segmentación

---

### 2.3 Tesorería Avanzada
**Tiempo estimado:** 4-5 días  

**Mejoras sobre Wallet.vue:**
- [ ] Calendario de vencimientos (facturas por cobrar/pagar)
- [ ] Gráfico de flujo de caja proyectado
- [ ] Conciliación de pagos con facturas
- [ ] Estados: Pendiente, Parcialmente cobrado, Cobrado, Vencido

---

## 🎯 Fase 3: Valor Añadido (Semanas 5-6)

### 3.1 Presupuestos (Quotes)
**Tiempo estimado:** 4-5 días  

- [ ] Crear presupuestos similares a facturas
- [ ] Estados: Pending, Sent, Accepted, Rejected, Expired
- [ ] Conversión presupuesto → pedido → factura
- [ ] Envío por email (simulado sin backend)

---

### 3.2 Informes & Analytics
**Tiempo estimado:** 5-6 días  

- [ ] Dashboard con gráficos interactivos (Chart.js / ApexCharts)
- [ ] Informe de ventas por periodo
- [ ] Top 10 productos más vendidos
- [ ] Top 10 clientes más rentables
- [ ] Evolución de inventario
- [ ] Exportación Excel/CSV

---

### 3.3 Generación de PDFs
**Tiempo estimado:** 3-4 días  

- [ ] Template HTML para facturas
- [ ] Generación PDF en frontend (jsPDF)
- [ ] Descarga automática
- [ ] Preview antes de descargar

---

## 🎯 Fase 4: Backend & Deploy (Semanas 7-8)

### 4.1 Backend con Supabase
**Tiempo estimado:** 5-7 días  

**Tareas:**
- [ ] Crear proyecto Supabase
- [ ] Diseñar esquema de base de datos
- [ ] Migrar datos hardcoded → PostgreSQL
- [ ] Implementar autenticación (Supabase Auth)
- [ ] Conectar frontend con Supabase Client

**Tablas principales:**
```sql
companies
users
products
customers
orders
order_lines
invoices
invoice_lines
payments
inventory_items
stock_movements
expenses
settings
```

---

### 4.2 Autenticación & Multi-usuario
**Tiempo estimado:** 3-4 días  

- [ ] Login/Logout/Registro
- [ ] Roles: Owner, Admin, Sales, Accountant
- [ ] Protección de rutas por rol
- [ ] Perfil de usuario

---

### 4.3 Deploy & CI/CD
**Tiempo estimado:** 2-3 días  

- [ ] Deploy frontend en Vercel/Netlify
- [ ] Variables de entorno
- [ ] GitHub Actions (CI/CD)
- [ ] Dominio custom
- [ ] Analytics (Plausible/Google Analytics)

---

## 📈 KPIs de Éxito MVP

### Funcionalidad
- ✅ Ciclo completo: Producto → Pedido → Factura → Cobro → Inventario
- ✅ 0 bugs críticos en flujo principal
- ✅ Todos los formularios con validación

### UX/UI
- ✅ Diseño consistente en todas las pantallas
- ✅ Responsive en mobile/tablet/desktop
- ✅ Tiempo de carga < 2 segundos
- ✅ Feedback visual en todas las acciones

### Código
- ✅ Cobertura tests > 70%
- ✅ 0 errores en build
- ✅ Documentación técnica completa

### Demo
- ✅ App deployada en producción
- ✅ Video demo de 2-3 minutos
- ✅ Datos de ejemplo cargados

---

## 🚀 Quick Wins (Mejoras Rápidas)

Estos son cambios menores que añaden mucho valor con poco esfuerzo:

### Semana Actual (1-2 días)
- [ ] Añadir Loading states (spinners)
- [ ] Añadir Toasts de confirmación (vue-toastification)
- [ ] Validación de formularios (vee-validate)
- [ ] Animaciones de transición (CSS)
- [ ] Dark mode toggle básico

### Siguiente Semana (2-3 días)
- [ ] Paginación real en todas las tablas
- [ ] Exportar a CSV en todos los listados
- [ ] Drag & drop para reordenar
- [ ] Keyboard shortcuts (Ctrl+N para nuevo, etc.)
- [ ] Búsqueda global en header (Cmd+K)

---

## 🎓 Checklist Entrega TFG

### Documentación
- [ ] README actualizado con screenshots
- [ ] Arquitectura técnica documentada
- [ ] Manual de usuario (español)
- [ ] API docs (si backend)
- [ ] Memoria del TFG (LaTeX/Word)

### Código
- [ ] Tests unitarios (Vitest)
- [ ] Tests E2E (Playwright)
- [ ] Linter configurado (ESLint)
- [ ] Code review completo

### Presentación
- [ ] Slides presentación (15-20 min)
- [ ] Video demo (3-5 min)
- [ ] Repositorio GitHub público
- [ ] Deploy live accesible

---

## 💡 Mejores Prácticas

### 1. Componentes Reutilizables
Extrae patrones comunes:
```
src/components/common/
  DataTable.vue          (tabla genérica con filtros)
  FormModal.vue          (modal genérico de formulario)
  StatusBadge.vue        (badge de estados)
  ConfirmDialog.vue      (confirmación acciones destructivas)
  EmptyState.vue         (cuando no hay datos)
```

### 2. Composables (Vue 3)
Extrae lógica reutilizable:
```
src/composables/
  useFilters.js          (lógica de filtros)
  usePagination.js       (lógica de paginación)
  useFormValidation.js   (validación)
  useApi.js              (llamadas API)
  useToast.js            (notificaciones)
```

### 3. Store Ligero (Pinia)
Para estado global:
```
src/stores/
  auth.js                (usuario actual)
  settings.js            (configuración global)
  notifications.js       (notificaciones)
```

### 4. Utils
```
src/utils/
  formatters.js          (fechas, moneda, números)
  validators.js          (validaciones custom)
  constants.js           (constantes globales)
  helpers.js             (funciones auxiliares)
```

---

## 🎯 Próximos Pasos Inmediatos

### Esta Semana (Prioridad 1)
1. **Crear Orders.vue** siguiendo patrón de Invoices.vue
2. **Crear Inventory.vue** con control de stock
3. **Crear Settings.vue** con configuración empresa

### Siguiente Semana (Prioridad 2)
1. Conectar módulos (Orders → Invoices, Orders → Inventory)
2. Añadir validaciones y feedback visual
3. Implementar tests básicos

---

**Última actualización:** 17 de febrero de 2026  
**Próxima revisión:** Al completar Fase 1
