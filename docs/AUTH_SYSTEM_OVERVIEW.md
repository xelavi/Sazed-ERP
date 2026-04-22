# 🔐 Sistema de Autenticación y Gestión de Usuarios - Resumen Ejecutivo

> **Proyecto:** Sazed ERP (TFG)  
> **Fecha:** 2026-04-12  
> **Estado:** 📋 Diseño completo (no implementado)

---

## 📚 Documentación

Este análisis está dividido en 3 documentos complementarios:

1. **[FRONTEND_AUTH_DESIGN.md](./FRONTEND_AUTH_DESIGN.md)** — Diseño completo de arquitectura, flujos, componentes y vistas
2. **[AUTH_UI_MOCKUPS.md](./AUTH_UI_MOCKUPS.md)** — Mockups visuales ASCII de todas las pantallas
3. **[AUTH_IMPLEMENTATION_NOTES.md](./AUTH_IMPLEMENTATION_NOTES.md)** — Consideraciones técnicas, edge cases y debugging

---

## 🎯 Resumen

El frontend de Sazed ERP necesita un **sistema completo de autenticación y gestión de usuarios/empresas** que se integre con el backend Django ya implementado. El backend proporciona:

- ✅ Autenticación basada en **sesiones Django** (HTTP-only cookies)
- ✅ Sistema **multi-empresa** (un usuario puede pertenecer a múltiples empresas)
- ✅ **Roles por empresa** (owner, admin, editor, viewer)
- ✅ **Middleware X-Company** que scope todos los datos por empresa activa
- ✅ API REST completa con endpoints de auth, perfil y empresas

---

## 🏗️ Componentes principales a implementar

### Vistas nuevas

| Vista | Ruta | Descripción |
|-------|------|-------------|
| **LoginView** | `/login` | Inicio de sesión con email + password |
| **RegisterView** | `/register` | Crear cuenta + primera empresa |
| **ProfileView** | `/profile` | Ver/editar perfil, cambiar contraseña, listar empresas |
| **CompanySettingsView** | `/settings/company` | Configuración de empresa (info, facturación, miembros, plan) |

### Componentes reutilizables

| Componente | Descripción |
|------------|-------------|
| **CompanySwitcher** | Dropdown en el header para cambiar entre empresas |
| **ChangePasswordModal** | Modal para cambiar contraseña |
| **CreateCompanyModal** | Modal para crear nueva empresa |
| **InviteMemberModal** | Modal para invitar miembros al equipo |

### Infraestructura

| Archivo | Descripción |
|---------|-------------|
| **composables/useAuth.js** | Composable global para estado de autenticación |
| **services/auth.js** | Servicio API para endpoints de auth |
| **layouts/DefaultLayout.vue** | Layout con sidebar (actual) |
| **layouts/EmptyLayout.vue** | Layout vacío para login/register |
| **router guard** | Protección de rutas privadas y recuperación de sesión |

---

## 🔄 Flujos principales

### 1. Registro + primera empresa
```
Usuario → /register
  ├─ Introduce: nombre, email, password, nombre_empresa
  ├─ POST /api/auth/register/
  └─ Backend crea User + Company + Membership (role=owner)
  └─ Login automático → redirige a /home
```

### 2. Login
```
Usuario → /login
  ├─ Introduce: email, password
  ├─ POST /api/auth/login/
  └─ Django establece cookie de sesión HTTP-only
  └─ Response: {user, companies, company (default)}
  └─ Redirige a /home o a ?redirect=...
```

### 3. Recuperación de sesión (al recargar página)
```
Usuario recarga la página → Router guard
  ├─ Detecta que no hay user en state
  ├─ GET /api/auth/me/
  ├─ Django valida cookie de sesión
  └─ Si válida: devuelve {user, companies}
      └─ Guardar en state + continuar navegación
  └─ Si inválida (401): redirigir a /login
```

### 4. Cambio de empresa
```
Usuario activo en Empresa A, click en dropdown:
  ├─ Selecciona Empresa B
  ├─ POST /api/companies/switch/ {company_id: B}
  ├─ Backend marca B como is_default=true
  └─ Frontend actualiza activeCompany
      └─ Actualiza header X-Company
      └─ Reload completo o recarga datos del módulo actual
```

### 5. Editar perfil
```
Usuario en /profile:
  ├─ Edita nombre, apellidos, avatar
  ├─ PATCH /api/auth/profile/
  └─ Actualiza state + toast "Perfil actualizado"
```

---

## 🔑 Conceptos clave

### Autenticación basada en sesiones

**No hay tokens JWT.** Django usa cookies HTTP-only:

```javascript
// ⚠️ CRÍTICO: Enviar cookies en todas las peticiones
fetch(url, {
  credentials: 'include',
  // ...
})
```

### Header X-Company

**Todos los datos están scoped por empresa.** El frontend debe enviar:

```
X-Company: {company_id}
```

En TODAS las peticiones (excepto `/api/auth/` y `/api/companies/`). El middleware de Django inyecta `request.company` en el backend.

**Implementación:**

```javascript
// services/api.js
let activeCompanyId = null

function apiFetch(endpoint, options = {}) {
  const headers = { ...options.headers }
  
  // Añadir X-Company si no es ruta de auth/companies
  if (activeCompanyId && !isAuthRoute(endpoint)) {
    headers['X-Company'] = activeCompanyId
  }
  
  return fetch(url, {
    credentials: 'include',
    headers,
    ...options,
  })
}
```

### Multi-tenancy

- Un **User** puede pertenecer a múltiples **Companies**
- Cada relación es un **Membership** con un **role** (owner/admin/editor/viewer)
- Una empresa puede estar marcada como `is_default=true` (empresa activa por defecto)
- Al cambiar de empresa, **TODOS los datos** (productos, clientes, facturas) cambian

### Persistencia de sesión

La cookie de sesión persiste entre recargas. El frontend debe:

1. Intentar recuperar sesión con `GET /api/auth/me/` al cargar la app
2. Si OK → guardar user + companies en state
3. Si 401 → redirigir a `/login`

---

## 🎨 Diseño y UX

### Consistencia con sistema existente

- **Colores:** Variables CSS de `src/style.css` (`--primary-color`, etc.)
- **Componentes:** Clases reutilizables (`.btn`, `.card`, `.input`, `.badge`)
- **Iconos:** `lucide-vue-next` (ya configurado)
- **Layout:** Sidebar + header (para vistas privadas), vacío (para login/register)

### Estados de carga y errores

- Loading states en botones: spinner + "Cargando..."
- Toasts para confirmaciones/errores (usar `vue-toastification` o similar)
- Validación inline en formularios (borde rojo + mensaje)
- Skeleton loaders mientras cargan datos

### Responsive

- Login/register: mobile-first (card 100% width en mobile)
- Dashboard: mantener diseño existente (sidebar collapsible)

---

## 🔒 Seguridad

### Frontend

- ✅ Validar inputs (formato email, longitud password ≥8)
- ✅ Sanitizar HTML (Vue lo hace automáticamente con `{{ }}`)
- ❌ NO guardar contraseñas nunca (ni siquiera temporalmente)
- ✅ Usar HTTPS en producción

### Backend (ya implementado)

- ✅ Passwords hasheados con PBKDF2
- ✅ Cookies HTTP-only + SameSite=Lax
- ✅ CSRF protection
- ⚠️ Rate limiting (pendiente)

---

## 📅 Plan de implementación (10-14 días)

| Fase | Duración | Tareas |
|------|----------|--------|
| **1. Infraestructura** | 1-2 días | useAuth(), auth.js, api.js (X-Company), layouts, router guard, toasts |
| **2. Login/Register** | 2-3 días | LoginView, RegisterView, validación, errores, loading states |
| **3. CompanySwitcher** | 1 día | Dropdown, switch empresas, menú usuario en header |
| **4. Perfil usuario** | 2 días | ProfileView, edición, ChangePasswordModal, upload avatar |
| **5. Settings empresa** | 3 días | CompanySettingsView (tabs), CreateCompanyModal, InviteMemberModal |
| **6. Testing** | 1-2 días | Flujos completos, edge cases, responsive, accesibilidad |
| **7. Integración** | 1 día | requiresAuth en todas las rutas, verificar X-Company en módulos |

**Total:** 10-14 días para un desarrollador familiarizado con Vue 3 + Django REST Framework.

---

## ⚠️ Puntos críticos

### 1. Cookies no se guardan

**Problema común:** Login parece exitoso pero siguientes peticiones devuelven 401.

**Solución:**
- Verificar `credentials: 'include'` en fetch
- Verificar `CORS_ALLOW_CREDENTIALS = True` en Django
- Verificar que frontend y backend están en mismo dominio o CORS configurado

### 2. X-Company faltante

**Problema:** Peticiones devuelven 403 o datos vacíos.

**Solución:**
- Verificar que `setActiveCompany(id)` se llama después de login/fetchMe
- Verificar que `apiFetch` añade el header (excepto en rutas exentas)

### 3. Sesión no persiste al recargar

**Problema:** Usuario recarga página y pierde sesión.

**Solución:**
- Implementar router guard que llame a `fetchMe()` en cada navegación si no hay user
- Guardar `activeCompanyId` en sessionStorage para restaurar empresa activa

### 4. Cambio de empresa con datos obsoletos

**Problema:** Usuario cambia de empresa, datos antiguos siguen en pantalla.

**Solución A (simple):** Reload completo con `window.location.reload()`
**Solución B (elegante):** Reactive reload con `watch(activeCompany, () => loadData())`

---

## 📊 Métricas de éxito

Al finalizar la implementación, el sistema debe cumplir:

- [ ] Usuario puede registrarse y crear su primera empresa
- [ ] Usuario puede iniciar sesión y la sesión persiste al recargar
- [ ] Usuario puede editar su perfil y cambiar contraseña
- [ ] Usuario puede cambiar entre empresas si pertenece a múltiples
- [ ] Usuario con rol owner/admin puede gestionar empresa (info, miembros)
- [ ] Todas las rutas privadas están protegidas (redirigen a /login si no auth)
- [ ] Header X-Company se envía en todas las peticiones a datos (productos, clientes...)
- [ ] Manejo correcto de errores (401, 403, validation errors)
- [ ] UI responsive en mobile, tablet y desktop
- [ ] Estados de carga en todas las acciones asíncronas
- [ ] Toasts informativos para todas las acciones (éxito/error)

---

## 🚀 Próximos pasos

1. **Leer documentación completa:**
   - [FRONTEND_AUTH_DESIGN.md](./FRONTEND_AUTH_DESIGN.md) → Arquitectura detallada
   - [AUTH_UI_MOCKUPS.md](./AUTH_UI_MOCKUPS.md) → Mockups visuales
   - [AUTH_IMPLEMENTATION_NOTES.md](./AUTH_IMPLEMENTATION_NOTES.md) → Detalles técnicos

2. **Configurar entorno de desarrollo:**
   - Backend: `python manage.py runserver`
   - Frontend: `npm run dev`
   - Verificar que CORS está configurado correctamente

3. **Implementar infraestructura base:**
   - Crear `useAuth.js`
   - Crear `auth.js`
   - Modificar `api.js` para soportar cookies + X-Company
   - Crear layouts

4. **Implementar vistas de autenticación:**
   - LoginView → RegisterView → ProfileView → CompanySettingsView

5. **Testing exhaustivo:**
   - Probar todos los flujos
   - Probar edge cases (sesión expirada, cambio de empresa, etc.)
   - Probar responsive

6. **Documentar para el equipo:**
   - Guía de uso del sistema de auth
   - Cómo añadir nuevas rutas protegidas
   - Cómo manejar permisos por rol

---

## 📞 Contacto

Para dudas sobre este diseño, consultar:
- [FRONTEND_AUTH_DESIGN.md](./FRONTEND_AUTH_DESIGN.md) → Sección específica
- [AUTH_IMPLEMENTATION_NOTES.md](./AUTH_IMPLEMENTATION_NOTES.md) → Troubleshooting

---

**Nota:** Este es un diseño completo basado en el análisis del backend existente y los requisitos del proyecto. La implementación debe seguir estos lineamientos pero puede ajustarse según necesidades emergentes durante el desarrollo.
