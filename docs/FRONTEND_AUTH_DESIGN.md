# Diseño del Sistema de Autenticación y Gestión de Usuarios - Frontend

> **Fecha:** 2026-04-12  
> **Proyecto:** Sazed ERP (TFG)  
> **Stack:** Vue 3 + Vue Router + Composition API  
> **Backend API:** Django REST Framework con autenticación de sesión

---

## 📋 Índice

1. [Resumen ejecutivo](#resumen-ejecutivo)
2. [Análisis del backend existente](#análisis-del-backend-existente)
3. [Arquitectura propuesta](#arquitectura-propuesta)
4. [Vistas y componentes necesarios](#vistas-y-componentes-necesarios)
5. [Flujos de usuario](#flujos-de-usuario)
6. [Estado global y servicios](#estado-global-y-servicios)
7. [Rutas y navegación](#rutas-y-navegación)
8. [Consideraciones de diseño](#consideraciones-de-diseño)
9. [Plan de implementación](#plan-de-implementación)

---

## 1. Resumen ejecutivo

Este documento define el diseño completo del sistema de autenticación y gestión de usuarios/empresas para el frontend de Sazed ERP. El backend ya está implementado y proporciona:

- ✅ **Autenticación basada en sesiones** (Django session auth)
- ✅ **Sistema multi-empresa** (multi-tenancy)
- ✅ **Usuarios con múltiples empresas** (un user puede pertenecer a varias companies con diferentes roles)
- ✅ **API REST completa** para auth, usuarios y empresas

El frontend necesita:

- ❌ Sistema de login/registro
- ❌ Gestión de sesión y estado del usuario
- ❌ Selector/switcher de empresa activa
- ❌ Vista de perfil de usuario
- ❌ Vista de gestión de empresa
- ❌ Protección de rutas privadas
- ❌ Manejo de permisos por rol

---

## 2. Análisis del backend existente

### 2.1 Modelo de datos

#### User (custom user model)
```python
User:
  - email (unique, USERNAME_FIELD)
  - password (hashed)
  - first_name
  - last_name
  - avatar (imagen, opcional)
  - is_active
  - date_joined
  
  # Propiedades calculadas:
  - full_name (first_name + last_name)
  - initials (iniciales para avatar)
```

#### Company
```python
Company:
  # Identidad
  - name (nombre comercial)
  - slug (unique, URL-friendly)
  - tax_id (CIF/NIF)
  - legal_name (razón social)
  
  # Contacto
  - email, phone, website
  - address, city, province, postal_code, country
  
  # Branding
  - logo (imagen)
  - primary_color (color hex)
  
  # Plan y configuración
  - plan (free/starter/pro)
  - currency (EUR, USD...)
  - fiscal_year_start
  - invoice_prefix
  
  # Audit
  - created_by (User)
  - created_at, updated_at
```

#### Membership (relación User ↔ Company)
```python
Membership:
  - user (FK User)
  - company (FK Company)
  - role (owner/admin/editor/viewer)
  - is_default (bool - empresa activa por defecto)
  - invited_by (User, opcional)
  - joined_at
```

### 2.2 Endpoints disponibles

#### Autenticación
- `POST /api/auth/register/` → Crear cuenta + primera empresa
  - Body: `{email, password, first_name, last_name, company_name}`
  - Response: `{user, company, role}`
  - Crea automáticamente un User, Company y Membership (role=owner)

- `POST /api/auth/login/` → Iniciar sesión
  - Body: `{email, password}`
  - Response: `{user, company, role}`
  - Establece cookie de sesión HTTP-only

- `POST /api/auth/logout/` → Cerrar sesión
  - Requiere autenticación
  - Invalida la sesión

- `GET /api/auth/me/` → Info del usuario actual
  - Response: `{user, companies: [{id, name, slug, logo, role, is_default}]}`
  - Lista todas las empresas del usuario

#### Perfil
- `PATCH /api/auth/profile/` → Actualizar perfil
  - Body: `{first_name, last_name, avatar}` (multipart/form-data para avatar)

- `POST /api/auth/change-password/` → Cambiar contraseña
  - Body: `{current_password, new_password}`

#### Empresas
- `GET /api/companies/` → Listar empresas del usuario
- `POST /api/companies/` → Crear nueva empresa
  - Body: `{name, tax_id, legal_name, email, currency}`
  - Añade automáticamente membership como owner

- `GET /api/companies/{id}/` → Ver detalle de empresa
- `PATCH /api/companies/{id}/` → Actualizar empresa
- `DELETE /api/companies/{id}/` → Eliminar empresa (solo owner)

- `POST /api/companies/switch/` → Cambiar empresa activa
  - Body: `{company_id}`
  - Marca la empresa como default para el usuario

- `GET /api/companies/{id}/members/` → Listar miembros
- `POST /api/companies/{id}/members/` → Invitar miembro
  - Body: `{email, role}`
  - Crea o invita usuario a la empresa

### 2.3 Middleware de empresa (X-Company header)

El backend tiene un middleware que:
- Lee el header `X-Company: {company_id}` en cada request
- Si no hay header, usa la empresa por defecto del usuario (`is_default=True`)
- Inyecta `request.company` y `request.membership` en todos los endpoints
- **Todos los datos (productos, clientes, facturas) están scoped por empresa**

Esto significa que el frontend **DEBE** enviar el header `X-Company` en TODAS las peticiones a la API (excepto en `/api/auth/` y `/api/companies/`).

### 2.4 Sistema de roles

Roles disponibles en `Membership.Role`:
- `owner` (Propietario) — Control total
- `admin` (Administrador) — Gestión completa excepto borrar empresa
- `editor` (Editor) — Crear/editar datos
- `viewer` (Solo lectura) — Solo ver

El backend expone `membership.can_manage` y otras propiedades para verificar permisos.

---

## 3. Arquitectura propuesta

### 3.1 Capa de estado global (Composable o Pinia)

Aunque el proyecto no usa Pinia actualmente, necesitamos un **store reactivo global** para la sesión. Propuestas:

#### Opción A: Composable `useAuth()` (recomendada para este proyecto)
```javascript
// src/composables/useAuth.js
import { ref, readonly, computed } from 'vue'

const user = ref(null)
const companies = ref([])
const activeCompany = ref(null)
const isLoading = ref(true)
const isAuthenticated = computed(() => !!user.value)

export function useAuth() {
  return {
    // Estado (readonly)
    user: readonly(user),
    companies: readonly(companies),
    activeCompany: readonly(activeCompany),
    isLoading: readonly(isLoading),
    isAuthenticated,
    
    // Métodos
    async login(credentials) { ... },
    async register(data) { ... },
    async logout() { ... },
    async fetchMe() { ... },
    async switchCompany(companyId) { ... },
    async updateProfile(data) { ... },
    async changePassword(data) { ... },
  }
}
```

**Ventajas:**
- No requiere Pinia (menos dependencias)
- Suficiente para auth simple
- Singleton mediante closure de módulo
- Compatible con el diseño actual del proyecto

#### Opción B: Pinia Store (más escalable)
Si se decide adoptar Pinia para otros módulos en el futuro.

### 3.2 Servicio de API

Crear `src/services/auth.js` para encapsular las llamadas al backend:

```javascript
// src/services/auth.js
import { get, post, patch } from './api'

export const authService = {
  async login(email, password) {
    return post('/auth/login/', { email, password })
  },
  
  async register(data) {
    return post('/auth/register/', data)
  },
  
  async logout() {
    return post('/auth/logout/')
  },
  
  async me() {
    return get('/auth/me/')
  },
  
  async updateProfile(data) {
    return patch('/auth/profile/', data)
  },
  
  async changePassword(currentPassword, newPassword) {
    return post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
  
  async switchCompany(companyId) {
    return post('/companies/switch/', { company_id: companyId })
  },
}
```

### 3.3 Interceptor para header X-Company

Modificar `src/services/api.js` para añadir automáticamente el header `X-Company`:

```javascript
// src/services/api.js
let activeCompanyId = null

export function setActiveCompany(companyId) {
  activeCompanyId = companyId
}

async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  // Añadir X-Company si está configurado (excepto en rutas de auth)
  if (activeCompanyId && !endpoint.startsWith('/auth/') && !endpoint.startsWith('/companies/')) {
    headers['X-Company'] = activeCompanyId
  }
  
  const config = {
    credentials: 'include', // IMPORTANTE: enviar cookies de sesión
    headers,
    ...options,
  }
  
  // ... resto del código
}
```

---

## 4. Vistas y componentes necesarios

### 4.1 Vistas principales

#### 📄 `/login` — LoginView.vue
**Propósito:** Pantalla de inicio de sesión

**Elementos:**
- Logo centrado
- Título "Iniciar sesión"
- Form con:
  - Input email (type="email", required)
  - Input password (type="password", required)
  - Checkbox "Recordarme" (opcional, visual)
  - Botón "Iniciar sesión" (primario, full-width)
- Link "¿Olvidaste tu contraseña?" (futuro)
- Divider "o"
- Botón "Crear cuenta" (secundario, redirige a /register)
- Footer con copyright

**Diseño:**
- Layout centrado con card
- Fondo con gradiente `--primary-color`
- Card blanca de 400px de ancho
- Sin sidebar/header del layout principal

**Comportamiento:**
1. Usuario introduce email + password
2. Click en "Iniciar sesión" → loading state en botón
3. Llamada a `authService.login()`
4. Si success:
   - Guardar user + companies en `useAuth()`
   - Establecer `activeCompany` (la que tenga `is_default=True` o la primera)
   - Redirigir a `/` (dashboard)
5. Si error:
   - Mostrar toast/mensaje: "Credenciales incorrectas"
   - Focus en input de password

---

#### 📄 `/register` — RegisterView.vue
**Propósito:** Crear cuenta nueva + primera empresa

**Elementos:**
- Logo centrado
- Título "Crear cuenta"
- Form con pasos visuales (stepper o todo junto):
  
  **Datos personales:**
  - Input first_name (requerido)
  - Input last_name (opcional)
  - Input email (type="email", requerido, validación de formato)
  - Input password (requerido, min 8 chars, mostrar requisitos)
  - Input confirm_password (debe coincidir)
  
  **Datos de empresa:**
  - Input company_name (requerido)
  - Text "Podrás configurar más detalles después"
  
  - Checkbox "Acepto los términos y condiciones" (requerido)
  - Botón "Crear cuenta" (primario, full-width)

- Link "¿Ya tienes cuenta? Inicia sesión"

**Diseño:**
- Similar a LoginView
- Card un poco más ancha (480px)
- Validación en tiempo real (visual feedback)

**Comportamiento:**
1. Validar formulario:
   - Email válido
   - Password ≥ 8 chars
   - Passwords coinciden
   - Términos aceptados
2. Deshabilitar botón → loading
3. Llamada a `authService.register({email, password, first_name, last_name, company_name})`
4. Si success:
   - Guardar user + company en state
   - Redirigir a `/welcome` (onboarding) o `/` (dashboard)
   - Mostrar toast: "¡Cuenta creada! Bienvenido a Sazed ERP"
5. Si error:
   - Mostrar mensaje específico:
     - "Ya existe una cuenta con este email"
     - "Error al crear la cuenta"

---

#### 📄 `/profile` — ProfileView.vue
**Propósito:** Ver y editar perfil del usuario

**Layout:** Dentro del layout principal (con sidebar)

**Secciones:**

**1. Header**
```
┌─────────────────────────────────────────────┐
│ [←] Mi Perfil                               │
└─────────────────────────────────────────────┘
```

**2. Card: Información personal**
```
┌─────────────────────────────────────────────┐
│  Avatar (circular, 80px)                    │
│  [Cambiar foto]                             │
│                                             │
│  Nombre             [Input: first_name   ]  │
│  Apellidos          [Input: last_name    ]  │
│  Email              email@example.com       │
│                     (no editable, gris)     │
│                                             │
│  Miembro desde      15 de enero, 2026       │
│                                             │
│  [Cancelar] [Guardar cambios]               │
└─────────────────────────────────────────────┘
```

**3. Card: Seguridad**
```
┌─────────────────────────────────────────────┐
│  Contraseña                                  │
│                                             │
│  [Cambiar contraseña] (botón secundario)    │
└─────────────────────────────────────────────┘
```

**4. Card: Empresas (read-only)**
```
┌─────────────────────────────────────────────┐
│  Mis empresas                               │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ [Logo] Acme Corp        [Activa]    │   │
│  │        Propietario                  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ [Logo] Otra Empresa Ltd             │   │
│  │        Editor                       │   │
│  │        [Cambiar a esta empresa]     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [+ Crear nueva empresa]                    │
└─────────────────────────────────────────────┘
```

**Comportamiento:**
- Cargar datos desde `useAuth().user`
- Al editar nombre/apellidos → `authService.updateProfile()`
- Al cambiar avatar → upload con FormData (multipart)
- Click en "Cambiar contraseña" → abrir modal `ChangePasswordModal`
- Click en "Cambiar a esta empresa" → `authService.switchCompany()` + reload + toast
- Click en "Crear nueva empresa" → abrir modal `CreateCompanyModal`

---

#### 📄 `/settings/company` — CompanySettingsView.vue
**Propósito:** Configuración de la empresa activa

**Layout:** Dentro del layout principal

**Tabs de navegación:**
```
[ General ] [ Facturación ] [ Miembros ] [ Plan ]
```

**Tab: General** (default)
```
┌─────────────────────────────────────────────┐
│  Logo de la empresa                         │
│  [Imagen actual o placeholder]              │
│  [Cambiar logo]                             │
│                                             │
│  Información básica                         │
│  Nombre comercial   [Input: name        ]  │
│  Razón social       [Input: legal_name  ]  │
│  CIF/NIF            [Input: tax_id      ]  │
│                                             │
│  Contacto                                   │
│  Email              [Input: email       ]  │
│  Teléfono           [Input: phone       ]  │
│  Sitio web          [Input: website     ]  │
│                                             │
│  Dirección                                  │
│  Dirección          [Input: address     ]  │
│  Ciudad             [Input: city        ]  │
│  Provincia          [Input: province    ]  │
│  Código postal      [Input: postal_code ]  │
│  País               [Select: country    ]  │
│                                             │
│  Branding                                   │
│  Color principal    [Color picker]          │
│                                             │
│  [Guardar cambios]                          │
└─────────────────────────────────────────────┘
```

**Tab: Facturación**
```
┌─────────────────────────────────────────────┐
│  Configuración de facturación                │
│                                             │
│  Divisa             [Select: EUR, USD...]  │
│  Inicio año fiscal  [Select: 1-12        ]  │
│  Prefijo facturas   [Input: FAC          ]  │
│                                             │
│  [Guardar cambios]                          │
└─────────────────────────────────────────────┘
```

**Tab: Miembros**
```
┌─────────────────────────────────────────────┐
│  Miembros del equipo         [+ Invitar]    │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ Avatar  Nombre          Rol      [⋮] │  │
│  │ [MC]    María Campos    Owner         │  │
│  │ [JR]    José Ruiz       Admin         │  │
│  │ [AL]    Ana López       Editor    [⋮] │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Menú contextual [⋮]:                       │
│  - Cambiar rol                              │
│  - Eliminar del equipo                      │
└─────────────────────────────────────────────┘
```

**Tab: Plan**
```
┌─────────────────────────────────────────────┐
│  Plan actual: Gratuito                       │
│                                             │
│  [ Card: Plan Free  ]  (actual)             │
│  [ Card: Plan Starter ]  [Actualizar]       │
│  [ Card: Plan Pro ]      [Actualizar]       │
└─────────────────────────────────────────────┘
```

**Permisos:**
- Solo `owner` y `admin` pueden acceder
- Solo `owner` puede eliminar empresa o cambiar plan
- `editor` y `viewer` ven mensaje "No tienes acceso a esta sección"

---

### 4.2 Componentes auxiliares

#### 🧩 CompanySwitcher.vue
**Ubicación:** En el header (topbar), reemplazando el avatar estático

**Diseño:**
```
┌────────────────────────────────────────────┐
│  [Logo empresa] Nombre empresa ▼           │
└────────────────────────────────────────────┘

Al hacer click → Dropdown:

┌────────────────────────────────────────────┐
│  Empresas                                  │
│  ────────────────────────────────────────  │
│  ● [Logo] Acme Corp                  ✓     │
│    [Logo] Otra Empresa Ltd                 │
│  ────────────────────────────────────────  │
│  ⚙️  Gestionar empresas                    │
│  ➕ Crear empresa                          │
│  ────────────────────────────────────────  │
│  👤 Mi perfil                              │
│  🚪 Cerrar sesión                          │
└────────────────────────────────────────────┘
```

**Props:**
- Ninguno (usa `useAuth()` internamente)

**Comportamiento:**
- Muestra empresa activa con check ✓
- Click en otra empresa → `switchCompany()` + reload
- Click en "Mi perfil" → navegar a `/profile`
- Click en "Cerrar sesión" → `logout()` + redirigir a `/login`

---

#### 🧩 ChangePasswordModal.vue
Modal para cambiar contraseña desde el perfil

**Campos:**
- Contraseña actual (password)
- Nueva contraseña (password, min 8 chars)
- Confirmar nueva contraseña (password)

**Validación:**
- Nueva contraseña ≠ actual
- Nueva contraseña = confirmar
- Mostrar indicador de fortaleza

---

#### 🧩 CreateCompanyModal.vue
Modal para crear empresa adicional

**Campos mínimos:**
- Nombre de la empresa (requerido)
- CIF/NIF (opcional)
- Email (opcional)

Al crear, el usuario se añade automáticamente como `owner`.

---

#### 🧩 InviteMemberModal.vue
Modal para invitar miembros a empresa

**Campos:**
- Email del usuario
- Rol (select: editor/admin/viewer)
- Mensaje personalizado (opcional)

---

#### 🧩 ProtectedRoute / middleware
Guard de Vue Router para proteger rutas privadas:

```javascript
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, fetchMe } = useAuth()
  
  // Rutas públicas
  if (to.meta.guest) {
    if (isAuthenticated.value) {
      // Ya autenticado, redirigir al dashboard
      return next('/')
    }
    return next()
  }
  
  // Rutas privadas
  if (to.meta.requiresAuth !== false) {
    if (!isAuthenticated.value) {
      // Intentar recuperar sesión
      try {
        await fetchMe()
        return next()
      } catch {
        // No autenticado, redirigir a login
        return next('/login')
      }
    }
  }
  
  next()
})
```

---

## 5. Flujos de usuario

### 5.1 Flujo: Primera vez (registro)

```
1. Usuario entra a la web → redirige a /login
2. Click en "Crear cuenta"
3. Rellenar formulario de registro
   - Nombre, email, password
   - Nombre de empresa
4. Submit → POST /api/auth/register/
5. Backend crea:
   - User
   - Company
   - Membership (role=owner, is_default=true)
6. Autenticación automática (cookie de sesión)
7. Redirigir a /home (dashboard)
8. Mostrar tour/onboarding (opcional, futuro)
```

### 5.2 Flujo: Login recurrente

```
1. Usuario entra a /login
2. Introduce email + password
3. Submit → POST /api/auth/login/
4. Backend valida credenciales
5. Establece cookie de sesión
6. Response con {user, company (default), role}
7. Frontend guarda en useAuth()
8. Redirigir a / (último destino o dashboard)
```

### 5.3 Flujo: Navegar con sesión activa

```
Al cargar la app:
1. Router guard verifica si hay usuario en state
2. Si no hay → llamar GET /api/auth/me/
3. Si response OK:
   - Guardar user + companies
   - Establecer activeCompany (la que tenga is_default=true)
   - Configurar X-Company header
   - Permitir acceso
4. Si response 401:
   - Borrar state
   - Redirigir a /login
```

### 5.4 Flujo: Cambiar de empresa

```
Usuario en dashboard, empresa A activa:
1. Click en CompanySwitcher dropdown
2. Seleccionar empresa B
3. POST /api/companies/switch/ {company_id: B}
4. Backend actualiza is_default
5. Frontend:
   - Actualizar activeCompany en state
   - Actualizar header X-Company
   - Recargar datos del módulo actual
   - Opcional: forzar reload completo (location.reload)
```

### 5.5 Flujo: Editar perfil

```
1. Usuario en /profile
2. Editar nombre/apellidos
3. Click en "Guardar cambios"
4. PATCH /api/auth/profile/
5. Actualizar state en useAuth()
6. Mostrar toast: "Perfil actualizado"
7. Actualizar avatar en CompanySwitcher
```

### 5.6 Flujo: Cambiar contraseña

```
1. En /profile, click "Cambiar contraseña"
2. Abrir ChangePasswordModal
3. Introducir:
   - Contraseña actual
   - Nueva contraseña (×2)
4. Submit → POST /api/auth/change-password/
5. Si success:
   - Cerrar modal
   - Toast: "Contraseña actualizada"
   - Sesión permanece activa
6. Si error "Contraseña actual incorrecta":
   - Mostrar error en el campo
```

### 5.7 Flujo: Invitar miembro

```
1. En /settings/company (tab Miembros)
2. Click "+ Invitar"
3. Introducir email + rol
4. POST /api/companies/{id}/members/
5. Backend:
   - Si usuario existe: añade Membership
   - Si no existe: crea User + Membership + envía email (futuro)
6. Refrescar lista de miembros
7. Toast: "Invitación enviada a email@example.com"
```

---

## 6. Estado global y servicios

### 6.1 useAuth() — Composable principal

**Estado:**
```javascript
{
  user: {
    id: 1,
    email: 'user@example.com',
    first_name: 'Juan',
    last_name: 'Pérez',
    full_name: 'Juan Pérez',
    initials: 'JP',
    avatar: 'http://...jpg',
    date_joined: '2026-01-15T10:00:00Z'
  },
  
  companies: [
    {
      id: 1,
      name: 'Acme Corp',
      slug: 'acme-corp',
      logo: 'http://...png',
      role: 'owner',
      is_default: true
    },
    {
      id: 2,
      name: 'My Side Project',
      slug: 'my-side-project',
      role: 'admin',
      is_default: false
    }
  ],
  
  activeCompany: { /* empresa con is_default=true */ },
  
  isLoading: false,
  isAuthenticated: true
}
```

**Métodos:**
```javascript
{
  // Auth
  login(email, password): Promise<void>
  register(data): Promise<void>
  logout(): Promise<void>
  
  // Session
  fetchMe(): Promise<void>  // Recuperar sesión activa
  
  // Company
  switchCompany(companyId): Promise<void>
  
  // Profile
  updateProfile(data): Promise<void>
  changePassword(current, newPass): Promise<void>
  uploadAvatar(file): Promise<void>
}
```

### 6.2 Persistencia de sesión

**Importante:** Django usa cookies HTTP-only para la sesión, por lo que:
- ❌ NO guardar nada en localStorage (no hay token JWT)
- ✅ Enviar `credentials: 'include'` en todos los fetch
- ✅ El backend valida la cookie automáticamente
- ✅ Al recargar la página, llamar a `GET /api/auth/me/` para recuperar el estado

### 6.3 Manejo de errores

**401 Unauthorized:**
- Sesión expirada o no autenticado
- Borrar state
- Redirigir a /login
- Mostrar toast: "Tu sesión ha expirado. Por favor, inicia sesión."

**403 Forbidden:**
- Usuario sin permisos para la acción
- Mostrar toast: "No tienes permiso para realizar esta acción"
- No redirigir

**400/422 Validation Error:**
- Mostrar errores específicos en el formulario

---

## 7. Rutas y navegación

### 7.1 Estructura de rutas propuesta

```javascript
// router/index.js
const routes = [
  // Rutas públicas (guest)
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: { guest: true, layout: 'empty' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterView.vue'),
    meta: { guest: true, layout: 'empty' }
  },
  
  // Rutas privadas (requieren auth)
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/auth/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    redirect: '/settings/company'
  },
  {
    path: '/settings/company',
    name: 'CompanySettings',
    component: () => import('../views/settings/CompanySettingsView.vue'),
    meta: {
      requiresAuth: true,
      requiresRole: ['owner', 'admin'] // Guard adicional
    }
  },
  
  // ... resto de rutas existentes (todas con requiresAuth: true)
  
  // Wildcard
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]
```

### 7.2 Navigation Guard

```javascript
// router/index.js
import { useAuth } from '@/composables/useAuth'

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isLoading, fetchMe, activeCompany } = useAuth()
  
  // Si está cargando, esperar
  if (isLoading.value) {
    await new Promise(resolve => {
      const unwatch = watch(isLoading, (loading) => {
        if (!loading) {
          unwatch()
          resolve()
        }
      })
    })
  }
  
  // Rutas públicas (login/register)
  if (to.meta.guest) {
    if (isAuthenticated.value) {
      return next('/') // Ya está autenticado
    }
    return next()
  }
  
  // Rutas privadas
  if (to.meta.requiresAuth !== false) {
    if (!isAuthenticated.value) {
      try {
        await fetchMe() // Intentar recuperar sesión
      } catch {
        return next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
      }
    }
    
    // Verificar rol si es necesario
    if (to.meta.requiresRole) {
      const membership = activeCompany.value
      if (!to.meta.requiresRole.includes(membership.role)) {
        return next('/') // Redirigir a home si no tiene permisos
      }
    }
  }
  
  next()
})
```

### 7.3 Layout condicional

Modificar `App.vue` para soportar layouts diferentes:

```vue
<template>
  <component :is="layout">
    <router-view />
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from './layouts/DefaultLayout.vue'
import EmptyLayout from './layouts/EmptyLayout.vue'

const route = useRoute()

const layout = computed(() => {
  return route.meta.layout === 'empty' ? EmptyLayout : DefaultLayout
})
</script>
```

**DefaultLayout.vue:** El layout actual de App.vue (sidebar + header)  
**EmptyLayout.vue:** Solo `<router-view />` (para login/register)

---

## 8. Consideraciones de diseño

### 8.1 Consistencia con sistema de diseño existente

**Colores:**
- Usar variables CSS de `style.css`:
  - `--primary-color` (#667eea) para CTA
  - `--text-primary`, `--text-secondary`
  - `--border-color`, `--border-radius`
  - Componentes reutilizables: `.btn`, `.input`, `.card`, `.badge`

**Iconos:**
- Usar `lucide-vue-next` (ya configurado)
- Ejemplos:
  - `User` para perfil
  - `Building2` para empresa
  - `LogOut` para cerrar sesión
  - `Settings` para configuración
  - `Users` para miembros

**Tipografía:**
- Mantener jerarquía existente
- Títulos: 24px (h2), 20px (h3)
- Body: 14px regular

### 8.2 Experiencia de usuario (UX)

**Feedback visual:**
- Loading states en botones (spinner + "Cargando...")
- Toasts para confirmaciones/errores (usar librería como `vue-toastification`)
- Validación inline en formularios (borde rojo + mensaje debajo)
- Deshabilitar botones durante peticiones

**Accesibilidad:**
- Labels en todos los inputs
- `aria-label` en botones de iconos
- Focus visible en elementos interactivos
- Errores con `role="alert"`

**Responsive:**
- Login/register: mobile-first (card 100% width en mobile)
- Dashboard: mantener diseño existente

### 8.3 Seguridad

**Frontend:**
- ✅ Validar inputs (formato email, longitud password)
- ✅ Sanitizar HTML si se renderiza contenido de usuario
- ❌ NO guardar contraseñas nunca (ni siquiera temporalmente)
- ✅ Usar HTTPS en producción

**Backend (ya implementado):**
- ✅ Passwords hasheados (Django usa PBKDF2)
- ✅ Cookies HTTP-only + SameSite
- ✅ CSRF protection
- ✅ Rate limiting (pendiente)

### 8.4 Gestión de errores comunes

| Error | Mensaje al usuario | Acción |
|-------|-------------------|--------|
| Credenciales incorrectas | "Email o contraseña incorrectos" | Focus en password |
| Email ya registrado | "Ya existe una cuenta con este email" | Focus en email |
| Sesión expirada | "Tu sesión ha expirado. Inicia sesión nuevamente." | Redirigir a /login |
| Sin permisos | "No tienes permiso para realizar esta acción" | Mantener en la misma vista |
| Error de red | "No se pudo conectar al servidor. Reintenta." | Botón "Reintentar" |
| Empresa no accesible | "No tienes acceso a esta empresa" | Revertir selección |

---

## 9. Plan de implementación

### Fase 1: Infraestructura base (1-2 días)
- [ ] Crear composable `useAuth()`
- [ ] Crear servicio `auth.js`
- [ ] Modificar `api.js` para soportar cookies y header X-Company
- [ ] Crear layouts `DefaultLayout.vue` y `EmptyLayout.vue`
- [ ] Configurar navigation guard en router
- [ ] Configurar librería de toasts

### Fase 2: Vistas de autenticación (2-3 días)
- [ ] Crear `LoginView.vue`
- [ ] Crear `RegisterView.vue`
- [ ] Validación de formularios
- [ ] Manejo de errores
- [ ] Estados de carga
- [ ] Estilos responsive

### Fase 3: Componente CompanySwitcher (1 día)
- [ ] Crear `CompanySwitcher.vue`
- [ ] Dropdown de empresas
- [ ] Switch de empresa
- [ ] Integrar en topbar de `App.vue`
- [ ] Menú de usuario (perfil + logout)

### Fase 4: Perfil de usuario (2 días)
- [ ] Crear `ProfileView.vue`
- [ ] Formulario de edición
- [ ] Crear `ChangePasswordModal.vue`
- [ ] Upload de avatar (multipart/form-data)
- [ ] Lista de empresas del usuario
- [ ] Integración con API

### Fase 5: Configuración de empresa (3 días)
- [ ] Crear `CompanySettingsView.vue`
- [ ] Tab: General (info + branding)
- [ ] Tab: Facturación
- [ ] Tab: Miembros (lista)
- [ ] Crear `CreateCompanyModal.vue`
- [ ] Crear `InviteMemberModal.vue`
- [ ] Permisos por rol

### Fase 6: Testing y refinamiento (1-2 días)
- [ ] Pruebas de flujos completos
- [ ] Manejo de edge cases
- [ ] Responsive en todas las vistas
- [ ] Accesibilidad (keyboard navigation)
- [ ] Mensajes de error claros
- [ ] Performance (lazy loading)

### Fase 7: Integración con módulos existentes (1 día)
- [ ] Añadir `requiresAuth: true` a todas las rutas existentes
- [ ] Verificar que X-Company se envíe en productos, clientes, facturas
- [ ] Testear cambio de empresa con datos reales
- [ ] Añadir botón "Configuración empresa" en sidebar

---

## 10. Checklist de completitud

### ✅ Backend (ya implementado)
- [x] Modelo User custom con email
- [x] Modelo Company multi-tenancy
- [x] Modelo Membership con roles
- [x] Endpoints de auth
- [x] Endpoints de perfil
- [x] Endpoints de companies
- [x] Middleware X-Company
- [x] Sesión Django HTTP-only cookies

### ❌ Frontend (por implementar)
- [ ] Composable useAuth()
- [ ] Servicio auth.js
- [ ] LoginView
- [ ] RegisterView
- [ ] ProfileView
- [ ] CompanySettingsView
- [ ] CompanySwitcher component
- [ ] ChangePasswordModal
- [ ] CreateCompanyModal
- [ ] InviteMemberModal
- [ ] Router guard
- [ ] Layouts condicionales
- [ ] Header X-Company en api.js
- [ ] Manejo de errores global
- [ ] Sistema de toasts
- [ ] Loading states

---

## Conclusión

Este sistema de autenticación y gestión de usuarios/empresa sigue los principios de:
- **Simplicidad:** Sesiones Django estándar, sin JWT complejo
- **Multi-tenancy robusto:** Toda la data scoped por empresa
- **Flexibilidad:** Un usuario puede pertenecer a múltiples empresas
- **Seguridad:** HTTP-only cookies, CSRF, passwords hasheados
- **UX coherente:** Integrado con el diseño existente de la app

La implementación total requiere aproximadamente **10-14 días de desarrollo** para un desarrollador familiarizado con Vue 3 y Django REST Framework.
