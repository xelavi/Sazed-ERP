# Análisis MVP - Sazed ERP vs. Holded

**Fecha:** 17 de febrero de 2026  
**Objetivo:** Identificar los módulos y funcionalidades críticas para convertir Sazed ERP en un MVP viable comparado con software líder del mercado como Holded.

---

## 📊 Estado Actual del Proyecto

### ✅ Módulos Implementados (Funcionales)

| Módulo | Estado | Funcionalidad | Líneas de Código |
|--------|--------|---------------|------------------|
| **Dashboard** (`Home.vue`) | ✅ Completo | Vista general con pasos de configuración, KPIs básicos | ~200 |
| **Productos** (`Products.vue`) | ✅ Completo | CRUD de productos, búsqueda, filtros, paginación, modales de creación/edición | ~800 |
| **Facturas** (`Invoices.vue`) | ✅ Completo | Listado de facturas, filtros avanzados, estados (Draft, Approved, Paid, Overdue, etc.), creación/edición | 2,142 |
| **Clientes** (`Customers.vue`) | ✅ Completo | Listado de clientes, búsqueda, filtros por tipo (persona/empresa), segmentación por tags | 701 |
| **Wallet** (`Wallet.vue`) | ✅ Completo | Balance, historial de transacciones, movimientos | ~400 |

**Total implementado:** ~4,243 líneas de código funcional

### ⚠️ Módulos Placeholder (Sin implementar)

| Módulo | Categoría | Criticidad MVP | Prioridad |
|--------|-----------|----------------|-----------|
| **Collections** | Catálogo | Media | 3 |
| **Inventory** | Catálogo | 🔴 ALTA | 1 |
| **Orders** | Ventas | 🔴 ALTA | 1 |
| **Card** | Finanzas | Baja | 5 |
| **Payout** | Finanzas | Media | 4 |
| **Marketing** | Marketing | Baja | 6 |
| **Online Store** | Canal venta | Baja | 7 |
| **Sell Link** | Canal venta | Baja | 7 |
| **Settings** | Configuración | 🔴 ALTA | 2 |

---

## 🏆 Análisis Comparativo: Sazed ERP vs. Holded

### Holded - Módulos Core

Holded es un **ERP todo-en-uno para PyMEs** con estos módulos principales:

#### 1. **Facturación** ⭐⭐⭐⭐⭐
- Facturas de venta y compra
- Presupuestos y albaranes
- Facturas recurrentes
- Plantillas personalizables
- Firma electrónica
- **Estado en Sazed:** ✅ Implementado (facturas venta)

#### 2. **Contabilidad** ⭐⭐⭐⭐⭐
- Libro mayor
- Plan contable
- Conciliación bancaria
- Declaraciones fiscales (Modelos AEAT)
- Asientos contables
- **Estado en Sazed:** ❌ No existe

#### 3. **Gestión de Clientes (CRM)** ⭐⭐⭐⭐
- Fichas de clientes
- Historial de interacciones
- Pipeline de ventas
- Seguimiento de oportunidades
- **Estado en Sazed:** ⚠️ Parcial (solo listado básico)

#### 4. **Proyectos & Tareas** ⭐⭐⭐⭐
- Gestión de proyectos
- Tiempo trackeable
- Facturación por proyecto
- Control de rentabilidad
- **Estado en Sazed:** ❌ No existe

#### 5. **Inventario & Almacén** ⭐⭐⭐⭐
- Control de stock
- Movimientos de almacén
- Alertas de stock mínimo
- Valoración de inventario (PMP, FIFO)
- Multi-almacén
- **Estado en Sazed:** ❌ No existe

#### 6. **Compras** ⭐⭐⭐⭐
- Facturas de proveedores
- Pedidos a proveedores
- Control de gastos
- **Estado en Sazed:** ❌ No existe

#### 7. **Tesorería** ⭐⭐⭐⭐
- Previsión de cobros/pagos
- Conciliación bancaria
- Vencimientos
- Flujo de caja
- **Estado en Sazed:** ⚠️ Muy básico (Wallet)

#### 8. **Informes & Analytics** ⭐⭐⭐⭐
- Dashboard personalizable
- Informes financieros
- Gráficos y KPIs
- Exportación Excel/PDF
- **Estado en Sazed:** ⚠️ Dashboard básico

#### 9. **Documentos** ⭐⭐⭐
- Generación PDF
- Envío por email automatizado
- Plantillas customizables
- **Estado en Sazed:** ❌ No existe

#### 10. **Configuración & Usuarios** ⭐⭐⭐⭐
- Multi-empresa
- Roles y permisos
- Personalización
- Integraciones (API)
- **Estado en Sazed:** ❌ No existe

---

## 🎯 Módulos y Funcionalidades para un MVP Viable

Para que Sazed ERP sea un MVP competitivo, debe cubrir el **ciclo de vida comercial básico** de una PyME:

### 🔴 CRÍTICO (MVP Phase 1 - Sprint 1-2)

#### 1. **Módulo de Pedidos (Orders)**
**Justificación:** Es el nexo entre Productos → Facturación → Inventario. Sin pedidos, el flujo comercial está incompleto.

**Funcionalidades mínimas:**
- ✅ Crear pedido desde cliente
- ✅ Añadir productos/servicios con cantidad y precio
- ✅ Estados: Draft, Confirmed, In Progress, Completed, Cancelled
- ✅ Conversión a factura con 1 click
- ✅ Cálculo automático de totales + IVA
- ✅ Búsqueda y filtros
- 📄 Generación PDF (opcional MVP)

**Complejidad:** Media (800-1000 líneas, similar a Products.vue)

---

#### 2. **Módulo de Inventario (Inventory)**
**Justificación:** Control de stock es esencial para cualquier negocio que venda productos físicos.

**Funcionalidades mínimas:**
- ✅ Listado de productos con stock actual
- ✅ Movimientos de entrada/salida
- ✅ Ajustes manuales de inventario
- ⚠️ Alertas de stock bajo (badge visual)
- ✅ Historial de movimientos por producto
- ✅ Filtros por categoría y estado (In stock, Low stock, Out of stock)

**Complejidad:** Media-Alta (1000-1200 líneas)

---

#### 3. **Configuración (Settings)**
**Justificación:** Sin configuración, el sistema no es personalizable ni funcional para clientes reales.

**Funcionalidades mínimas:**
- ✅ Datos de la empresa (nombre, NIF, dirección, logo)
- ✅ Series de facturación (prefijos, numeración)
- ✅ Configuración fiscal (IVA, IGIC, retenciones)
- ✅ Tipos de pago (transferencia, efectivo, tarjeta)
- ✅ Moneda por defecto
- ⚠️ Usuarios y roles (admin/user básico)
- 📄 Plantillas de documentos (V2)

**Complejidad:** Media (600-800 líneas)

---

### 🟡 IMPORTANTE (MVP Phase 2 - Sprint 3-4)

#### 4. **Contabilidad Básica**
**Funcionalidades mínimas:**
- ✅ Registro de gastos (facturas de proveedores)
- ✅ Categorización de ingresos/gastos
- ✅ Balance P&L simplificado (Ingresos - Gastos)
- ✅ Exportación datos contables (CSV para gestoría)
- ⚠️ Conciliación bancaria (V2)

**Complejidad:** Alta (1500+ líneas)

---

#### 5. **CRM Mejorado**
**Mejoras sobre Customers.vue actual:**
- ✅ Historial de facturas por cliente
- ✅ Notas y comentarios
- ✅ Estado del cliente (Activo, Inactivo, Moroso)
- ✅ Vista de detalle con tabs (Datos, Facturas, Pedidos, Notas)
- ✅ Indicadores: Total facturado, Deuda pendiente, Última compra

**Complejidad:** Media (400-600 líneas adicionales)

---

#### 6. **Tesorería (Treasury)**
**Mejoras sobre Wallet.vue actual:**
- ✅ Previsión de cobros/pagos futuros
- ✅ Vencimientos de facturas
- ✅ Registro de pagos realizados/recibidos
- ✅ Conciliación con facturas
- 📊 Gráfico de flujo de caja proyectado

**Complejidad:** Alta (800-1000 líneas)

---

### 🟢 NICE-TO-HAVE (MVP Phase 3 - Sprint 5+)

#### 7. **Presupuestos (Quotes)**
- Crear presupuestos
- Envío por email
- Conversión a pedido/factura
- Estados: Pending, Accepted, Rejected

**Complejidad:** Media (600-800 líneas)

---

#### 8. **Informes & Dashboards**
- Dashboard con KPIs en tiempo real
- Gráficos de ventas por periodo
- Top productos vendidos
- Informe de clientes más rentables
- Exportación Excel/PDF

**Complejidad:** Media-Alta (1000+ líneas)

---

#### 9. **Albaranes (Delivery Notes)**
- Documento de entrega previo a facturación
- Conversión albarán → factura
- Estados: Pending, Delivered

**Complejidad:** Media (400-600 líneas)

---

#### 10. **Multi-usuario & Roles (RBAC)**
- Sistema de autenticación (login/logout)
- Roles: Owner, Admin, Sales, Accountant
- Permisos granulares por módulo
- Audit log de acciones

**Complejidad:** Alta (requiere backend seguro)

---

## 🚀 Roadmap Sugerido

### **Sprint 1-2 (2-3 semanas) - MVP Core**
- [ ] Implementar módulo Orders
- [ ] Implementar módulo Inventory
- [ ] Implementar módulo Settings (configuración básica)
- [ ] Mejorar conexión entre módulos (Pedido → Factura → Inventario)

### **Sprint 3-4 (2-3 semanas) - Ciclo Financiero**
- [ ] Módulo Contabilidad básica (Gastos)
- [ ] Mejorar CRM (historial, notas)
- [ ] Mejorar Tesorería (vencimientos, previsiones)
- [ ] Sistema de notificaciones (facturas vencidas, stock bajo)

### **Sprint 5-6 (2-3 semanas) - Valor Añadido**
- [ ] Presupuestos
- [ ] Albaranes
- [ ] Informes avanzados
- [ ] Generación de PDFs (facturas, presupuestos)

### **Sprint 7+ (Post-MVP) - Escalabilidad**
- [ ] Backend real (Node.js/Supabase/Firebase)
- [ ] Multi-usuario con autenticación
- [ ] API REST
- [ ] Integraciones (email, bancos, marketplaces)
- [ ] Factura electrónica (VeriFactu, TicketBAI)

---

## 📋 Checklist MVP Mínimo (Para entrega de TFG)

### ✅ Funcionalidades Imprescindibles

- [x] **Gestión de productos** (añadir, editar, eliminar, búsqueda)
- [x] **Gestión de clientes** (añadir, editar, eliminar, búsqueda)
- [ ] **Gestión de pedidos** (crear, editar, estados, conversión a factura)
- [x] **Facturación** (crear facturas, estados, búsqueda, cálculo IVA)
- [ ] **Control de inventario** (stock, movimientos, alertas)
- [ ] **Configuración** (datos empresa, series, impuestos)
- [x] **Dashboard** (KPIs básicos, resumen ventas)
- [x] **Wallet/Tesorería** (balance, transacciones)

### 🎨 UX/UI

- [x] Sistema de diseño consistente (CSS Variables)
- [x] Navegación sidebar funcional
- [x] Responsive design básico
- [x] Iconografía (Lucide)
- [ ] Feedback visual (toasts, confirmaciones)
- [ ] Loading states & error handling

### 🧪 Testing & Calidad

- [ ] Tests unitarios (Vitest)
- [ ] Tests E2E (Playwright/Cypress)
- [ ] Validación de formularios
- [ ] Manejo de errores
- [ ] Documentación técnica

### 📦 Deployment

- [ ] Build optimizado
- [ ] Hosting (Vercel/Netlify/GitHub Pages)
- [ ] Variables de entorno
- [ ] Analytics básico

---

## 💡 Recomendaciones Estratégicas

### 1. **Prioriza el Flujo de Valor**
El ciclo **Producto → Pedido → Factura → Cobro → Inventario** debe ser fluido y sin fricción. Es el core de cualquier ERP.

### 2. **Diferenciación vs. Holded**
Holded es muy completo pero **complejo**. Sazed puede diferenciarse siendo:
- **Más simple y minimalista** (menos opciones, mejor UX)
- **Especializado en e-commerce** (integración con canales online)
- **Open source** (comunidad, extensible)
- **Enfocado en freelancers/startups** (no PyMEs tradicionales)

### 3. **Backend es el Siguiente Gran Paso**
Actualmente todo está en frontend con datos hardcoded. Para un producto real, necesitas:
- Base de datos (PostgreSQL, MySQL, Supabase)
- API REST/GraphQL
- Autenticación (JWT, OAuth)
- Almacenamiento de archivos (PDFs, imágenes)

Opciones rápidas para MVP:
- **Supabase** (PostgreSQL + Auth + Storage + Realtime)
- **Firebase** (NoSQL + Auth + Hosting)
- **Pocketbase** (SQLite all-in-one backend)

### 4. **Generación de PDFs**
Es crítico para facturas. Opciones:
- **Puppeteer** (Chromium headless, genera PDF desde HTML)
- **jsPDF** + **html2canvas** (frontend, más limitado)
- **PDFKit** (Node.js, más control)
- **Plantillas HTML → PDF server-side** (recomendado)

### 5. **Factura Electrónica (No prioritario MVP)**
En España hay iniciativas como **VeriFactu**, **TicketBAI** (País Vasco), **Batuz** (Navarra). Son obligatorias para ciertos sectores/comunidades pero:
- La normativa está en transición
- Requiere certificación técnica
- Es mejor dejarlo como integración V2

---

## 🎓 Conclusión para TFG

**Para un TFG sólido, el MVP debe incluir:**

### ✅ Módulos Core (Obligatorios)
1. Productos ✅
2. Clientes ✅
3. Pedidos ⚠️
4. Facturas ✅
5. Inventario ⚠️
6. Configuración ⚠️
7. Dashboard ✅

### ⭐ Valor Diferencial (Recomendado)
- UX excepcional (animaciones, feedback, onboarding)
- Diseño impecable (portfolio material)
- Documentación técnica detallada
- Tests automatizados
- Deploy en producción (demo live)

### 📈 Puntos Extra (Si hay tiempo)
- Backend funcional (Supabase)
- Multi-usuario
- Generación PDFs
- Informes visuales

---

**Estimación de trabajo restante:** 6-8 semanas de desarrollo full-time para MVP completo.

**Próximo paso:** Implementar módulo **Orders** siguiendo el patrón de `Invoices.vue` (especificación en `/docs/specs/`).
