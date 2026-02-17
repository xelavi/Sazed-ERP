# ✅ MVP Implementation Checklist

Guía práctica paso a paso para completar el MVP de Sazed ERP.

---

## 🎯 Objetivo MVP
Tener un ERP funcional con el ciclo comercial completo: **Producto → Pedido → Factura → Cobro → Inventario**

**Plazo:** 6-8 semanas  
**Fecha inicio:** 17 febrero 2026  
**Fecha objetivo:** 31 marzo 2026

---

## 📅 Semana 1-2: Core MVP

### 🛒 Módulo de Pedidos (Orders)

#### Día 1-2: Setup & Listado
- [ ] Crear archivo `src/views/Orders.vue`
- [ ] Copiar estructura base de `Invoices.vue`
- [ ] Definir interfaz `Order` en comentarios
- [ ] Crear datos mockup (10-15 pedidos)
- [ ] Implementar tabla con columnas:
  - [ ] Checkbox selección
  - [ ] Número pedido (ORD-2026-XXXX)
  - [ ] Cliente con avatar
  - [ ] Fecha pedido
  - [ ] Estado con badge
  - [ ] Total con símbolo €
  - [ ] Acciones (ver, editar, eliminar)
- [ ] Añadir ruta `/orders` en `router/index.js`
- [ ] Actualizar sidebar en `App.vue` (cambiar placeholder)

#### Día 2-3: Filtros & Búsqueda
- [ ] Barra de búsqueda (nº pedido, cliente)
- [ ] Filtro por estado (Draft, Confirmed, Completed, Cancelled)
- [ ] Filtro por cliente (dropdown)
- [ ] Filtro por rango de fechas
- [ ] Botón "Clear filters"
- [ ] Contador de resultados

#### Día 3-5: Formulario de Creación/Edición
- [ ] Crear `src/components/OrderFormModal.vue`
- [ ] Formulario con campos:
  - [ ] Cliente (select con búsqueda)
  - [ ] Fecha pedido (datepicker)
  - [ ] Fecha entrega estimada
  - [ ] Estado
  - [ ] Notas internas
- [ ] Tabla de líneas de pedido:
  - [ ] Selector de producto
  - [ ] Cantidad (input número)
  - [ ] Precio unitario (auto desde producto)
  - [ ] Descuento % (opcional)
  - [ ] Subtotal (calculado)
- [ ] Botón "+ Añadir línea"
- [ ] Botón "Eliminar línea" (icono papelera)
- [ ] Resumen totales en footer:
  - [ ] Subtotal
  - [ ] IVA (configurable por línea)
  - [ ] Total
- [ ] Validaciones:
  - [ ] Cliente requerido
  - [ ] Al menos 1 línea
  - [ ] Cantidad > 0
  - [ ] Precio >= 0
- [ ] Botones "Cancelar" y "Guardar"

#### Día 5: Conversión a Factura
- [ ] Botón "Convertir a factura" en detalle de pedido
- [ ] Modal de confirmación
- [ ] Crear factura con datos del pedido
- [ ] Cambiar estado pedido a "Completed"
- [ ] Redireccionar a la factura creada
- [ ] Toast de confirmación

#### Testing
- [ ] Crear pedido nuevo ✓
- [ ] Editar pedido existente ✓
- [ ] Eliminar pedido ✓
- [ ] Buscar y filtrar ✓
- [ ] Convertir a factura ✓

---

### 📦 Módulo de Inventario (Inventory)

#### Día 6-7: Setup & Listado Stock
- [ ] Crear archivo `src/views/Inventory.vue`
- [ ] Definir interfaz `InventoryItem` y `StockMovement`
- [ ] Crear datos mockup vinculados a productos
- [ ] Tabla con columnas:
  - [ ] Imagen producto
  - [ ] Nombre + SKU
  - [ ] Stock actual (número grande)
  - [ ] Stock mínimo
  - [ ] Estado (badge: In stock / Low stock / Out of stock)
  - [ ] Valor total (stock × coste unitario)
  - [ ] Último movimiento (fecha + tipo)
  - [ ] Acciones (ajustar, historial)
- [ ] Cálculo automático de estados:
  - [ ] Verde si stock > minStock
  - [ ] Amarillo si stock <= minStock && stock > 0
  - [ ] Rojo si stock = 0
- [ ] Añadir ruta `/inventory` en router
- [ ] Actualizar sidebar

#### Día 7-8: Movimientos de Stock
- [ ] Crear `src/views/InventoryMovements.vue`
- [ ] Tabla historial con columnas:
  - [ ] Fecha/hora
  - [ ] Producto
  - [ ] Tipo (badge: IN/OUT/ADJUSTMENT)
  - [ ] Motivo (compra, venta, ajuste, pérdida)
  - [ ] Cantidad (+/-)
  - [ ] Stock anterior → nuevo
  - [ ] Referencia (link a pedido/factura)
  - [ ] Usuario
  - [ ] Notas
- [ ] Filtros:
  - [ ] Por producto
  - [ ] Por tipo de movimiento
  - [ ] Por rango de fechas
- [ ] Exportar CSV

#### Día 8-9: Ajuste Manual de Stock
- [ ] Crear `src/components/StockAdjustmentModal.vue`
- [ ] Formulario:
  - [ ] Producto (select)
  - [ ] Stock actual (readonly, resaltado)
  - [ ] Nuevo stock (input)
  - [ ] Diferencia (calculada, +/- en color)
  - [ ] Motivo (select: Recuento, Pérdida, Error, Otro)
  - [ ] Notas (textarea)
- [ ] Validaciones:
  - [ ] Nuevo stock >= 0
  - [ ] Motivo requerido si diferencia > threshold
- [ ] Al guardar:
  - [ ] Actualizar stock en InventoryItem
  - [ ] Crear StockMovement tipo ADJUSTMENT
  - [ ] Toast confirmación

#### Día 9-10: Integración con Pedidos
- [ ] Al completar pedido → generar movimientos OUT
- [ ] Al cancelar pedido completado → revertir stock
- [ ] Validación: no permitir completar pedido si stock insuficiente
- [ ] Confirmación al usuario si va a quedar stock bajo

#### Extra: Entradas de Mercancía
- [ ] Crear `src/components/StockInModal.vue`
- [ ] Formulario entrada de mercancía:
  - [ ] Producto (select multiple)
  - [ ] Cantidad
  - [ ] Coste unitario
  - [ ] Proveedor (opcional)
  - [ ] Nº. albarán/factura proveedor
  - [ ] Fecha recepción
- [ ] Generar movimientos IN
- [ ] Actualizar coste medio ponderado (opcional MVP)

#### Testing
- [ ] Ver stock todos los productos ✓
- [ ] Ajustar stock manualmente ✓
- [ ] Registrar entrada mercancía ✓
- [ ] Ver historial de movimientos ✓
- [ ] Completar pedido descuenta stock ✓
- [ ] Alertas visual de stock bajo ✓

---

### ⚙️ Módulo de Configuración (Settings)

#### Día 11-12: Setup & Navegación
- [ ] Crear archivo `src/views/Settings.vue`
- [ ] Layout con tabs o sidebar secundario:
  - [ ] Company (datos empresa)
  - [ ] Invoice (series y numeración)
  - [ ] Taxes (impuestos)
  - [ ] Payments (métodos de pago)
  - [ ] Users (futuro)
- [ ] Añadir ruta `/settings` en router
- [ ] Actualizar sidebar

#### Día 12-13: Company Settings
- [ ] Crear `src/components/settings/CompanySettings.vue`
- [ ] Formulario:
  - [ ] Logo empresa (upload mockup)
  - [ ] Nombre comercial
  - [ ] NIF/CIF
  - [ ] Dirección
  - [ ] Ciudad
  - [ ] Código postal
  - [ ] País (select)
  - [ ] Teléfono
  - [ ] Email
  - [ ] Website
- [ ] Validaciones:
  - [ ] NIF formato español (regex)
  - [ ] Email válido
  - [ ] Teléfono formato internacional
- [ ] Botón "Guardar cambios"
- [ ] Preview logo en tiempo real

#### Día 13: Invoice Settings
- [ ] Crear `src/components/settings/InvoiceSettings.vue`
- [ ] Configuración de series:
  - [ ] Lista de series existentes (FAC, ORD, PRE)
  - [ ] Botón "+ Nueva serie"
- [ ] Formulario serie:
  - [ ] Prefijo (ej: FAC)
  - [ ] Siguiente número
  - [ ] Formato (template: {prefix}-{year}-{number:4})
  - [ ] Reset anual (checkbox)
- [ ] Vista previa número generado
- [ ] Editar/Eliminar serie (con confirmación)

#### Día 14: Tax Settings
- [ ] Crear `src/components/settings/TaxSettings.vue`
- [ ] Lista de tipos impositivos:
  - [ ] IVA General 21%
  - [ ] IVA Reducido 10%
  - [ ] IVA Superreducido 4%
  - [ ] IGIC Canarias (7%, 3%, 0%)
  - [ ] IRPF Retención 15%
- [ ] Formulario impuesto:
  - [ ] Nombre
  - [ ] Tipo (VAT, IGIC, Retention)
  - [ ] Porcentaje
  - [ ] Por defecto (radio)
  - [ ] Activo (switch)
- [ ] CRUD completo

#### Día 14: Payment Settings
- [ ] Crear `src/components/settings/PaymentSettings.vue`
- [ ] Lista de métodos de pago:
  - [ ] Transferencia bancaria
  - [ ] Tarjeta de crédito
  - [ ] Efectivo
  - [ ] PayPal
  - [ ] Bizum
- [ ] Formulario método:
  - [ ] Nombre
  - [ ] Tipo (select)
  - [ ] Activo (switch)
  - [ ] Instrucciones (textarea) - ej: "IBAN: ES00..."
- [ ] Reordenar con drag & drop (opcional)

#### Testing
- [ ] Cambiar datos empresa ✓
- [ ] Subir logo ✓
- [ ] Crear nueva serie facturas ✓
- [ ] Modificar tipos de IVA ✓
- [ ] Añadir método de pago ✓
- [ ] Configuración persiste entre vistas ✓

---

## 📅 Semana 3: Integración & UX Polish

### 🔗 Integración entre Módulos

#### Día 15-16: Conexión Orders ↔ Invoices
- [ ] En listado de facturas, mostrar si viene de pedido
- [ ] Link "Ver pedido origen" en detalle de factura
- [ ] En listado de pedidos, mostrar si ya tiene factura
- [ ] Prevenir duplicar factura de mismo pedido
- [ ] Al editar pedido, si tiene factura → warning

#### Día 16-17: Conexión Orders ↔ Inventory
- [ ] Al crear pedido → verificar stock disponible
- [ ] Al completar pedido → descuento automático de stock
- [ ] Toast confirmación: "Stock actualizado: -X unidades"
- [ ] Al cancelar pedido completado → popup "¿Revertir stock?"
- [ ] En detalle pedido, mostrar estado stock actual de productos

#### Día 17: Conexión Products ↔ Inventory
- [ ] En listado de productos, mostrar columna "Stock"
- [ ] Badge de estado (In stock, Low, Out of stock)
- [ ] Link rápido a Inventario desde producto
- [ ] Al editar producto, mostrar advertencia si cambias precio y hay pedidos activos

#### Día 18: Dashboard Actualizado
- [ ] Añadir KPI "Pedidos pendientes"
- [ ] Añadir KPI "Stock bajo" (productos con alerta)
- [ ] Tabla "Últimos pedidos" (5 más recientes)
- [ ] Gráfico "Productos más vendidos" (desde pedidos)
- [ ] Widget "Acciones rápidas" (Nuevo pedido, Entrada stock)

---

### 🎨 UX Polish

#### Día 19: Loading States
- [ ] Instalar `vue-loading-overlay` o crear spinner custom
- [ ] Añadir loading state en:
  - [ ] Carga inicial de listados
  - [ ] Guardar formularios
  - [ ] Eliminar items
  - [ ] Exportar datos
- [ ] Skeleton loaders en tablas grandes (opcional)

#### Día 19: Toast Notifications
- [ ] Instalar `vue-toastification`
- [ ] Crear composable `useToast.js`
- [ ] Añadir toasts en:
  - [ ] Guardar success → verde
  - [ ] Eliminar success → naranja
  - [ ] Errores → rojo
  - [ ] Advertencias → amarillo
  - [ ] Info → azul

#### Día 20: Validación de Formularios
- [ ] Instalar `vee-validate` + `yup` o usar validación nativa
- [ ] Añadir validación en todos los formularios:
  - [ ] Campos requeridos (borde rojo + mensaje)
  - [ ] Formatos email, teléfono, NIF
  - [ ] Rangos numéricos (precio > 0, cantidad > 0)
  - [ ] Longitud máxima textos
- [ ] Deshabilitar botón "Guardar" si form inválido
- [ ] Focus automático en primer error

#### Día 20: Confirmaciones
- [ ] Crear componente `ConfirmDialog.vue` reutilizable
- [ ] Añadir confirmación en:
  - [ ] Eliminar producto/cliente/pedido/factura
  - [ ] Cancelar pedido
  - [ ] Completar pedido con stock bajo
  - [ ] Borrar serie en Settings
- [ ] Variantes: Info, Warning, Danger

#### Día 21: Animaciones & Transiciones
- [ ] Transiciones de ruta (fade in/out)
- [ ] Hover effects en cards y botones
- [ ] Animación al abrir/cerrar modales
- [ ] Skeleton loader para tablas
- [ ] Animación al añadir/eliminar items de lista

---

## 📅 Semana 4: Testing & Documentación

### 🧪 Testing

#### Día 22-23: Tests Unitarios (Vitest)
- [ ] Setup Vitest si no está configurado
- [ ] Tests para utils/formatters.js:
  - [ ] `formatCurrency()`
  - [ ] `formatDate()`
  - [ ] `calculateTax()`
- [ ] Tests para componentes simples:
  - [ ] `StatusBadge.vue`
  - [ ] `ConfirmDialog.vue`
- [ ] Target: >70% coverage en utils

#### Día 23-24: Tests E2E (Playwright)
- [ ] Setup Playwright
- [ ] Crear test flow completo:
  - [ ] Login → Dashboard
  - [ ] Crear producto
  - [ ] Crear cliente
  - [ ] Crear pedido con ese producto
  - [ ] Completar pedido
  - [ ] Verificar stock descontado
  - [ ] Convertir a factura
  - [ ] Verificar factura creada
- [ ] Grabar video del test passing

#### Día 24-25: Manual Testing
- [ ] Checklist de todos los flujos:
  - [ ] ✓ CRUD productos
  - [ ] ✓ CRUD clientes
  - [ ] ✓ CRUD pedidos
  - [ ] ✓ CRUD facturas
  - [ ] ✓ Gestión inventario
  - [ ] ✓ Configuración
- [ ] Testing responsive:
  - [ ] Desktop (1920x1080)
  - [ ] Tablet (768x1024)
  - [ ] Mobile (375x667)
- [ ] Testing en navegadores:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge

---

### 📝 Documentación

#### Día 25-26: Documentación Técnica
- [ ] Actualizar README.md principal:
  - [ ] Descripción proyecto
  - [ ] Screenshots
  - [ ] Features implementadas
  - [ ] Tech stack
  - [ ] Instalación
  - [ ] Scripts disponibles
  - [ ] Estructura del proyecto
- [ ] Crear CONTRIBUTING.md (si open source)
- [ ] Crear CHANGELOG.md
- [ ] Comentarios JSDoc en funciones complejas

#### Día 26-27: Manual de Usuario
- [ ] Crear `docs/USER_GUIDE.md`
- [ ] Secciones:
  - [ ] Primeros pasos
  - [ ] Configuración inicial
  - [ ] Gestión de productos
  - [ ] Gestión de clientes
  - [ ] Crear pedidos
  - [ ] Facturación
  - [ ] Control de inventario
  - [ ] Informes
- [ ] Screenshots de cada pantalla
- [ ] GIFs animados de flujos principales

#### Día 27-28: Video Demo
- [ ] Script del video (2-3 minutos):
  - [ ] Intro (0:00-0:15): Qué es Sazed ERP
  - [ ] Tour interfaz (0:15-0:45): Sidebar, dashboard
  - [ ] Flujo productos (0:45-1:00)
  - [ ] Flujo pedidos (1:00-1:30)
  - [ ] Conversión a factura (1:30-1:45)
  - [ ] Inventario (1:45-2:15)
  - [ ] Settings (2:15-2:30)
  - [ ] Outro + CTA (2:30-2:45)
- [ ] Grabar con OBS Studio / Loom
- [ ] Edición básica (cortes, música de fondo)
- [ ] Subir a YouTube/Vimeo

---

## 📅 Semana 5-6: Backend & Auth

### 🗄️ Backend con Supabase

#### Día 29-30: Setup Supabase
- [ ] Crear cuenta en Supabase
- [ ] Crear nuevo proyecto
- [ ] Obtener URL y API keys
- [ ] Instalar `@supabase/supabase-js`
- [ ] Crear `src/lib/supabase.js` con configuración
- [ ] Variables de entorno (`.env.local`)

#### Día 31-32: Diseño Base de Datos
- [ ] Crear archivo `schema.sql` con tablas:
  ```sql
  companies
  users
  products
  customers
  orders
  order_lines
  invoices
  invoice_lines
  inventory_items
  stock_movements
  payments
  settings
  ```
- [ ] Definir relaciones y foreign keys
- [ ] Definir índices
- [ ] Ejecutar en Supabase SQL Editor

#### Día 33-35: Migración Frontend → Backend
- [ ] Crear composables API:
  - [ ] `useProducts.js`
  - [ ] `useCustomers.js`
  - [ ] `useOrders.js`
  - [ ] `useInvoices.js`
  - [ ] `useInventory.js`
- [ ] Reemplazar datos hardcoded por llamadas API
- [ ] Añadir loading states
- [ ] Manejo de errores
- [ ] Testing paso a paso

#### Día 36-38: Row Level Security (RLS)
- [ ] Habilitar RLS en todas las tablas
- [ ] Políticas básicas:
  - [ ] Users solo ven su company
  - [ ] CRUD según rol
- [ ] Testing de permisos

---

### 🔐 Autenticación

#### Día 39-40: Login/Registro
- [ ] Crear `src/views/Login.vue`
- [ ] Crear `src/views/Register.vue`
- [ ] Integrar Supabase Auth
- [ ] Validación formularios
- [ ] Manejo de errores (credenciales incorrectas)
- [ ] Redirección post-login

#### Día 40-41: Session Management
- [ ] Crear store Pinia `auth.js`
- [ ] Persistir sesión en localStorage
- [ ] Auto-login al recargar
- [ ] Logout con confirmación
- [ ] Middleware de rutas (proteger páginas privadas)

#### Día 41-42: User Profile
- [ ] Crear `src/views/Profile.vue`
- [ ] Ver/editar datos usuario:
  - [ ] Nombre
  - [ ] Email
  - [ ] Avatar
  - [ ] Cambiar contraseña
- [ ] Upload de avatar (Supabase Storage)

---

## 📅 Semana 7-8: Deploy & Final Polish

### 🚀 Deployment

#### Día 43-44: Build & Optimize
- [ ] Ejecutar `npm run build`
- [ ] Verificar 0 errores/warnings
- [ ] Optimizar imágenes (compression)
- [ ] Lazy loading de rutas
- [ ] Code splitting
- [ ] Minificación CSS
- [ ] Lighthouse audit (Target: >90)

#### Día 44-45: Deploy Frontend
- [ ] Crear cuenta Vercel/Netlify
- [ ] Conectar repositorio GitHub
- [ ] Configurar variables de entorno
- [ ] Deploy automático
- [ ] Configurar dominio (opcional)
- [ ] SSL/HTTPS
- [ ] Testing producción

#### Día 45: Analytics & Monitoring
- [ ] Instalar Plausible Analytics o PostHog
- [ ] Configurar eventos custom
- [ ] Error tracking (Sentry opcional)
- [ ] Uptime monitoring (UptimeRobot)

---

### 🎨 Final Polish

#### Día 46-47: Detalles Finales
- [ ] Revisar todos los textos (typos, gramática)
- [ ] Revisar consistencia de iconos
- [ ] Revisar espaciados y alineaciones
- [ ] Añadir empty states en todas las vistas
- [ ] Añadir favicon personalizado
- [ ] Metatags SEO (title, description, OG image)
- [ ] PWA manifest (opcional)

#### Día 48: QA Final
- [ ] Testing completo de todos los flujos
- [ ] Testing responsive todos los dispositivos
- [ ] Testing dark mode (si implementado)
- [ ] Testing con datos reales (no mockup)
- [ ] Pedir feedback a 3-5 usuarios reales

---

### 🎓 Preparación TFG

#### Día 49-50: Memoria TFG
- [ ] Introducción y contexto
- [ ] Objetivos del proyecto
- [ ] Estado del arte (análisis competencia)
- [ ] Análisis de requisitos
- [ ] Diseño de la solución
- [ ] Implementación (arquitectura, tech stack)
- [ ] Pruebas y validación
- [ ] Conclusiones y trabajo futuro
- [ ] Bibliografía
- [ ] Anexos (código relevante, screenshots)

#### Día 51-52: Presentación
- [ ] Crear slides (PowerPoint/Keynote/Reveal.js)
- [ ] Estructura:
  - [ ] Portada
  - [ ] Introducción (problema)
  - [ ] Objetivos
  - [ ] Solución propuesta
  - [ ] Demo en vivo (5 min)
  - [ ] Arquitectura técnica
  - [ ] Resultados y métricas
  - [ ] Conclusiones
  - [ ] Trabajo futuro
- [ ] Ensayar presentación (15-20 min)
- [ ] Preparar respuestas a preguntas frecuentes

---

## ✅ Checklist Final Pre-Entrega

### Código
- [ ] 0 errores en consola
- [ ] 0 warnings de Vue
- [ ] Código comentado (funciones complejas)
- [ ] Variables y funciones con nombres descriptivos
- [ ] Sin console.log() en producción
- [ ] Sin código comentado/muerto

### Testing
- [ ] Tests unitarios pasan ✓
- [ ] Tests E2E pasan ✓
- [ ] Coverage >70%
- [ ] Lighthouse score >90

### Documentación
- [ ] README completo
- [ ] USER_GUIDE.md
- [ ] CHANGELOG.md
- [ ] Comentarios JSDoc
- [ ] Memoria TFG
- [ ] Slides presentación

### Deploy
- [ ] Frontend desplegado y accesible
- [ ] Backend (Supabase) configurado
- [ ] Dominio custom (opcional)
- [ ] SSL activo
- [ ] Analytics funcionando

### Demo
- [ ] Video demo grabado y publicado
- [ ] Datos de ejemplo cargados
- [ ] Usuario demo (email: demo@sazed.com, pass: demo1234)
- [ ] Tour guiado en primera carga

### Legal
- [ ] Licencia MIT en repo
- [ ] GDPR compliance (si aplica)
- [ ] Aviso legal en footer
- [ ] Política privacidad (si aplica)

---

## 🎉 Criterios de Éxito

### Funcional ✅
- [x] Ciclo completo funciona: Producto → Pedido → Factura → Stock
- [x] Backend con persistencia real (Supabase)
- [x] Autenticación y multi-usuario
- [x] 0 bugs críticos

### UI/UX ✅
- [x] Diseño consistente y profesional
- [x] Responsive 100%
- [x] Feedback visual en todas las acciones
- [x] Loading states y error handling

### Código ✅
- [x] Arquitectura limpia y escalable
- [x] Componentes reutilizables
- [x] Tests automatizados
- [x] Documentación completa

### Presentación ✅
- [x] Demo deployada y accesible
- [x] Video de alta calidad
- [x] Presentación pulida
- [x] Portfolio material

---

**🚀 ¡A por ello! Siguiente paso: Implementar Orders.vue**

