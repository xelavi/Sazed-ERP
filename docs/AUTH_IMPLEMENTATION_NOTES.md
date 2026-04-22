# Consideraciones Técnicas — Implementación de Autenticación

> **Proyecto:** Sazed ERP (TFG)  
> **Fecha:** 2026-04-12  
> **Referencias:**  
> - [FRONTEND_AUTH_DESIGN.md](./FRONTEND_AUTH_DESIGN.md)  
> - [AUTH_UI_MOCKUPS.md](./AUTH_UI_MOCKUPS.md)  
> - [BACKEND_DESIGN.md](./BACKEND_DESIGN.md)

Este documento aborda detalles técnicos específicos y decisiones de implementación críticas.

---

## 📋 Tabla de contenidos

1. [Autenticación basada en sesiones vs JWT](#autenticación-basada-en-sesiones-vs-jwt)
2. [Gestión del header X-Company](#gestión-del-header-x-company)
3. [Persistencia y recuperación de sesión](#persistencia-y-recuperación-de-sesión)
4. [Manejo de CORS y cookies](#manejo-de-cors-y-cookies)
5. [Validación de formularios](#validación-de-formularios)
6. [Upload de archivos (avatar/logo)](#upload-de-archivos-avatarlogo)
7. [Optimización de rendimiento](#optimización-de-rendimiento)
8. [Testing y depuración](#testing-y-depuración)
9. [Seguridad](#seguridad)
10. [Edge cases y escenarios especiales](#edge-cases-y-escenarios-especiales)

---

## 1. Autenticación basada en sesiones vs JWT

### ¿Por qué sesiones Django?

El backend usa **autenticación de sesión de Django** (no JWT). Esto significa:

✅ **Ventajas:**
- Cookie HTTP-only automática (no hackeable con XSS)
- CSRF protection incluida
- Sesión gestionada por Django (redis/db)
- Logout real (invalida sesión server-side)
- Menos complejidad en el frontend

❌ **Desventajas:**
- No funciona con apps móviles nativas (solo web)
- Requiere sticky sessions en load balancers
- Cookie debe enviarse en todas las peticiones

### Implicaciones para el frontend:

```javascript
// SIEMPRE enviar cookies en fetch
fetch(url, {
  credentials: 'include', // ⚠️ CRÍTICO
  // ...
})
```

**Sin `credentials: 'include'`, la cookie no se envía y el usuario aparece como no autenticado.**

### Configuración de Django (ya implementada):

```python
# settings.py
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_HTTPONLY = True  # JavaScript no puede leer la cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF
SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
```

---

## 2. Gestión del header X-Company

### ¿Por qué X-Company?

Django tiene un **middleware** que:
1. Lee el header `X-Company: {company_id}` de cada request
2. Busca la `Membership` del usuario con esa empresa
3. Inyecta `request.company` y `request.membership` en el contexto
4. Si no hay header, usa la empresa por defecto (`is_default=True`)

**Todos los datos** (productos, clientes, facturas) están scoped por `request.company`.

### Implementación en `api.js`:

```javascript
// src/services/api.js
let activeCompanyId = null

export function setActiveCompany(companyId) {
  activeCompanyId = companyId
  // También guardar en sessionStorage para recuperar después de refresh
  if (companyId) {
    sessionStorage.setItem('activeCompanyId', companyId)
  } else {
    sessionStorage.removeItem('activeCompanyId')
  }
}

export function getActiveCompany() {
  return activeCompanyId || sessionStorage.getItem('activeCompanyId')
}

async function apiFetch(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  // IMPORTANTE: No añadir X-Company en endpoints de auth/companies
  const exemptPaths = ['/auth/', '/companies/']
  const needsCompanyHeader = !exemptPaths.some(path => endpoint.startsWith(path))
  
  if (needsCompanyHeader && activeCompanyId) {
    headers['X-Company'] = activeCompanyId
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    credentials: 'include', // ⚠️ CRÍTICO
    headers,
    ...options,
  })
  
  // ...
}
```

### Flujo de recuperación de empresa activa:

```javascript
// En useAuth.js, después de login o fetchMe:
async function fetchMe() {
  const data = await authService.me()
  
  user.value = data.user
  companies.value = data.companies
  
  // Establecer empresa activa
  const saved = sessionStorage.getItem('activeCompanyId')
  const defaultCompany = data.companies.find(c => c.is_default) || data.companies[0]
  
  if (saved && data.companies.some(c => c.id === parseInt(saved))) {
    // Usuario tiene acceso a la empresa guardada
    activeCompany.value = data.companies.find(c => c.id === parseInt(saved))
  } else {
    // Usar la default
    activeCompany.value = defaultCompany
  }
  
  setActiveCompany(activeCompany.value.id)
}
```

### ⚠️ Problema: Cambio de empresa

Al cambiar de empresa, los datos cargados en las vistas (productos, clientes) **pertenecen a la empresa anterior**. Opciones:

**Opción A: Reload completo**
```javascript
async function switchCompany(companyId) {
  await authService.switchCompany(companyId)
  setActiveCompany(companyId)
  // Recargar página completa
  window.location.reload()
}
```

**Opción B: Reactive reload (más elegante)**
```javascript
// En cada módulo (productos, clientes, etc.), watch la empresa activa
watch(activeCompany, () => {
  loadProducts() // Recargar datos
})
```

**Recomendación:** Opción A para MVP (más simple), Opción B para versión final.

---

## 3. Persistencia y recuperación de sesión

### Problema:

Usuario recarga la página → pierde el estado de `useAuth()` → necesita volver a cargar la sesión.

### Solución: Auto-recuperación en router guard

```javascript
// router/index.js
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, isLoading, fetchMe } = useAuth()
  
  // Skip para rutas públicas
  if (to.meta.guest) {
    return next()
  }
  
  // Si no está autenticado, intentar recuperar sesión
  if (!isAuthenticated.value && !isLoading.value) {
    isLoading.value = true
    try {
      await fetchMe()
      isLoading.value = false
      return next()
    } catch (error) {
      isLoading.value = false
      // No hay sesión válida, redirigir a login
      return next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  }
  
  next()
})
```

### Flujo completo:

```
1. Usuario entra a /products
2. Router guard detecta que no hay user en state
3. Llama a GET /api/auth/me/
4. Django valida la cookie de sesión
5. Si válida:
   - Response: {user, companies}
   - Guardar en state
   - Continuar navegación
6. Si inválida (401):
   - Redirigir a /login?redirect=/products
```

### ⚠️ Evitar múltiples llamadas a fetchMe()

Problema: Si el usuario recarga rápido múltiples veces, podría disparar varias peticiones paralelas a `/api/auth/me/`.

**Solución: Promise singleton**

```javascript
// useAuth.js
let fetchMePromise = null

async function fetchMe() {
  // Si ya hay una petición en curso, devolver la misma promise
  if (fetchMePromise) {
    return fetchMePromise
  }
  
  isLoading.value = true
  
  fetchMePromise = authService.me()
    .then(data => {
      user.value = data.user
      companies.value = data.companies
      // ... configurar activeCompany
    })
    .catch(error => {
      user.value = null
      companies.value = []
      activeCompany.value = null
      throw error
    })
    .finally(() => {
      isLoading.value = false
      fetchMePromise = null
    })
  
  return fetchMePromise
}
```

---

## 4. Manejo de CORS y cookies

### Configuración del backend (settings.py):

```python
# Django CORS
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
    'https://erp.sazed.com',  # Producción
]

CORS_ALLOW_CREDENTIALS = True  # ⚠️ CRÍTICO para cookies

# Django session
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = True  # Solo en producción (HTTPS)
```

### Frontend (Vite):

```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
}
```

**En desarrollo:**
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Proxy de Vite redirige `/api/*` al backend

**En producción:**
- Frontend: Servido como static files por Django o por CDN con mismo dominio
- Backend: Mismo dominio o subdomain (ej: `app.sazed.com` → `api.sazed.com`)

### ⚠️ Problema común: Cookie no se guarda

**Síntomas:**
- Login parece exitoso pero siguientes peticiones devuelven 401
- Cookie no aparece en DevTools → Application → Cookies

**Causas:**
1. Falta `credentials: 'include'` en fetch
2. Backend no tiene `CORS_ALLOW_CREDENTIALS = True`
3. Frontend y backend en dominios distintos SIN configurar CORS
4. Cookie con `Secure=True` pero usando HTTP (no HTTPS)

**Debug:**
```javascript
// Ver si la cookie se establece
console.log(document.cookie) // ⚠️ Si es HTTP-only, NO aparecerá aquí (normal)

// Verificar en Network tab:
// - Response headers de /api/auth/login/
// - Debe tener: Set-Cookie: sessionid=xxx; HttpOnly; SameSite=Lax
```

---

## 5. Validación de formularios

### Pattern reusable:

```javascript
// useFormValidation.js
export function useFormValidation() {
  const errors = ref({})
  
  function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return regex.test(email)
  }
  
  function validatePassword(password) {
    return password.length >= 8
  }
  
  function setError(field, message) {
    errors.value[field] = message
  }
  
  function clearError(field) {
    delete errors.value[field]
  }
  
  function clearAllErrors() {
    errors.value = {}
  }
  
  return {
    errors: readonly(errors),
    validateEmail,
    validatePassword,
    setError,
    clearError,
    clearAllErrors,
  }
}
```

### Uso en LoginView:

```vue
<script setup>
import { ref } from 'vue'
import { useFormValidation } from '@/composables/useFormValidation'
import { useAuth } from '@/composables/useAuth'

const { login } = useAuth()
const { errors, validateEmail, setError, clearAllErrors } = useFormValidation()

const form = ref({
  email: '',
  password: '',
})

const isSubmitting = ref(false)

async function handleSubmit() {
  clearAllErrors()
  
  // Validación local
  if (!validateEmail(form.value.email)) {
    setError('email', 'Formato de email inválido')
    return
  }
  
  if (!form.value.password) {
    setError('password', 'La contraseña es requerida')
    return
  }
  
  isSubmitting.value = true
  
  try {
    await login(form.value.email, form.value.password)
    // Redirigir (el guard ya lo hace)
  } catch (error) {
    if (error.message.includes('Credenciales')) {
      setError('password', 'Email o contraseña incorrectos')
    } else {
      setError('general', 'Error al iniciar sesión. Reintenta.')
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>Email</label>
      <input 
        v-model="form.email" 
        type="email" 
        :class="{ 'input-error': errors.email }"
        @input="clearError('email')"
      />
      <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
    </div>
    
    <div class="form-group">
      <label>Contraseña</label>
      <input 
        v-model="form.password" 
        type="password"
        :class="{ 'input-error': errors.password }"
        @input="clearError('password')"
      />
      <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
    </div>
    
    <button type="submit" :disabled="isSubmitting" class="btn btn-primary">
      <span v-if="isSubmitting">Iniciando...</span>
      <span v-else>Iniciar sesión</span>
    </button>
  </form>
</template>
```

---

## 6. Upload de archivos (avatar/logo)

Django REST Framework requiere `multipart/form-data` para archivos.

### Frontend:

```javascript
// authService.js
async uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)
  
  // NO enviar Content-Type: application/json
  return apiFetch('/auth/profile/', {
    method: 'PATCH',
    body: formData,
    // ⚠️ NO incluir headers: { 'Content-Type': ... }
    // El browser establece automáticamente multipart/form-data con boundary
  })
}
```

### Modificar `apiFetch` para soportar FormData:

```javascript
async function apiFetch(endpoint, options = {}) {
  const headers = { ...options.headers }
  
  // Solo añadir Content-Type si NO es FormData
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  
  if (needsCompanyHeader && activeCompanyId) {
    headers['X-Company'] = activeCompanyId
  }
  
  const config = {
    credentials: 'include',
    headers,
    ...options,
  }
  
  // Solo JSON.stringify si no es FormData
  if (config.body && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body)
  }
  
  // ...
}
```

### Componente de upload:

```vue
<template>
  <div class="avatar-upload">
    <img v-if="avatarUrl" :src="avatarUrl" alt="Avatar" />
    <div v-else class="avatar-placeholder">{{ initials }}</div>
    
    <input 
      ref="fileInput" 
      type="file" 
      accept="image/*" 
      @change="handleFileChange"
      style="display: none"
    />
    
    <button @click="$refs.fileInput.click()" class="btn btn-ghost">
      📷 Cambiar foto
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { user, updateProfile } = useAuth()
const fileInput = ref(null)
const avatarUrl = computed(() => user.value?.avatar)
const initials = computed(() => user.value?.initials)

async function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  // Validar tamaño (max 2MB)
  if (file.size > 2 * 1024 * 1024) {
    alert('El archivo debe ser menor a 2MB')
    return
  }
  
  // Validar tipo
  if (!file.type.startsWith('image/')) {
    alert('Solo se permiten imágenes')
    return
  }
  
  try {
    await updateProfile({ avatar: file })
    // Mostrar toast: "Avatar actualizado"
  } catch (error) {
    // Mostrar error
  }
}
</script>
```

---

## 7. Optimización de rendimiento

### Lazy loading de vistas:

```javascript
// router/index.js
{
  path: '/profile',
  component: () => import('../views/auth/ProfileView.vue')
  // No se carga hasta que el usuario navega a /profile
}
```

### Prefetch de datos críticos:

```javascript
// Al hacer login, pre-cargar algunos datos frecuentes
async function login(email, password) {
  const data = await authService.login(email, password)
  user.value = data.user
  companies.value = data.companies
  activeCompany.value = data.company
  
  setActiveCompany(data.company.id)
  
  // Pre-cargar dashboard stats (opcional)
  // dashboardService.getStats()
}
```

### Debounce en validación de email:

```javascript
import { debounce } from 'lodash-es'

const checkEmailAvailability = debounce(async (email) => {
  // Llamada a backend para verificar si el email ya existe
  const available = await authService.checkEmail(email)
  if (!available) {
    setError('email', 'Ya existe una cuenta con este email')
  }
}, 500)
```

### Optimizar re-renders:

```vue
<script setup>
import { computed, readonly } from 'vue'

const { user } = useAuth()

// ✅ No reactive si no es necesario
const userName = computed(() => user.value?.full_name)

// ❌ Evitar esto:
// const userName = ref(user.value?.full_name) // No se actualiza si user cambia
</script>
```

---

## 8. Testing y depuración

### Logging para debugging:

```javascript
// api.js
async function apiFetch(endpoint, options = {}) {
  console.log(`[API] ${options.method || 'GET'} ${endpoint}`, {
    headers,
    body: options.body,
  })
  
  try {
    const response = await fetch(url, config)
    console.log(`[API] Response ${response.status}`, await response.clone().json())
    // ...
  } catch (error) {
    console.error(`[API] Error ${endpoint}`, error)
    throw error
  }
}
```

### Simulación de errores:

```javascript
// Para testear UI de errores
if (import.meta.env.DEV && email === 'test-error@test.com') {
  throw new Error('Simulated error')
}
```

### Tests unitarios (opcional):

```javascript
// useAuth.test.js
import { describe, it, expect, vi } from 'vitest'
import { useAuth } from '@/composables/useAuth'

describe('useAuth', () => {
  it('should login successfully', async () => {
    const { login, isAuthenticated } = useAuth()
    
    vi.mock('@/services/auth', () => ({
      authService: {
        login: vi.fn().mockResolvedValue({
          user: { email: 'test@test.com' },
          company: { id: 1 },
        })
      }
    }))
    
    await login('test@test.com', 'password')
    
    expect(isAuthenticated.value).toBe(true)
  })
})
```

### Testing manual en desarrollo:

```bash
# Backend
cd backend
python manage.py runserver

# Frontend
cd frontend
npm run dev

# Abrir: http://localhost:5173/login
# Crear cuenta de prueba
# Verificar cookie en DevTools
# Recargar página → verificar que persiste sesión
```

---

## 9. Seguridad

### XSS (Cross-Site Scripting):

**Vue protege automáticamente** contra XSS al renderizar `{{ }}`. Pero:

```vue
<!-- ❌ PELIGROSO -->
<div v-html="user.name"></div>

<!-- ✅ SEGURO -->
<div>{{ user.name }}</div>
```

### CSRF (Cross-Site Request Forgery):

Django incluye CSRF protection. Para que funcione:

```python
# Django settings (ya configurado)
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
]
```

**En el frontend con cookies de sesión:**
Django envía un token CSRF en la cookie `csrftoken`. Debemos:

```javascript
// api.js
function getCsrfToken() {
  const cookies = document.cookie.split(';')
  const csrfCookie = cookies.find(c => c.trim().startsWith('csrftoken='))
  return csrfCookie ? csrfCookie.split('=')[1] : null
}

async function apiFetch(endpoint, options = {}) {
  const headers = { ...options.headers }
  
  // Añadir CSRF token en peticiones no-GET
  if (options.method && options.method !== 'GET') {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }
  
  // ...
}
```

**Otra opción (más simple):** Decorar vistas de Django con `@csrf_exempt` para endpoints de API (solo si usas session auth).

### Rate limiting:

Proteger endpoints sensibles (login, register) con:

```python
# Django (django-ratelimit)
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    # ...
```

### Content Security Policy (CSP):

```python
# settings.py
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 10. Edge cases y escenarios especiales

### 1. Usuario eliminado de empresa mientras está logueado

**Escenario:** Admin elimina a un usuario de la empresa activa.

**Comportamiento esperado:**
- Siguiente request con `X-Company: {old_company_id}` → 403 Forbidden
- Frontend detecta 403
- Llamar a `fetchMe()` para refrescar lista de empresas
- Si ya no tiene acceso a ninguna empresa → crear wizard "Crea tu primera empresa"
- Si tiene otras empresas → cambiar a otra automáticamente

**Implementación:**

```javascript
// api.js
async function apiFetch(endpoint, options = {}) {
  // ...
  
  if (response.status === 403 && headers['X-Company']) {
    // Puede ser que ya no tenga acceso a esta empresa
    const { fetchMe, switchToFirstAvailable } = useAuth()
    await fetchMe()
    await switchToFirstAvailable()
    
    // Reintentar la petición
    return apiFetch(endpoint, options)
  }
  
  // ...
}
```

### 2. Sesión expirada durante navegación

**Escenario:** Usuario deja la pestaña abierta 24h, la sesión expira, hace click en algo.

**Comportamiento esperado:**
- Request → 401
- Mostrar toast: "Tu sesión ha expirado"
- Redirigir a `/login?redirect={current_path}`

**Implementación:**

```javascript
// api.js
if (response.status === 401) {
  const { logout } = useAuth()
  logout(false) // No llamar a /api/auth/logout/ (ya está deslogueado)
  
  // Redirigir
  router.push({
    path: '/login',
    query: { redirect: router.currentRoute.value.fullPath }
  })
  
  throw new Error('Sesión expirada')
}
```

### 3. Usuario intenta acceder a Settings sin permisos

**Escenario:** Usuario con rol `viewer` intenta ir a `/settings/company`.

**Comportamiento esperado:**
- Router guard verifica `to.meta.requiresRole`
- Usuario no tiene rol suficiente
- Mostrar toast: "No tienes permiso para acceder a esta sección"
- Redirigir a `/`

**Implementación:**

```javascript
// router guard
if (to.meta.requiresRole) {
  const { activeCompany } = useAuth()
  const role = activeCompany.value?.role
  
  if (!to.meta.requiresRole.includes(role)) {
    showToast('No tienes permiso para acceder a esta sección', 'warning')
    return next('/')
  }
}
```

### 4. Creación de empresa duplicada (slug collision)

**Escenario:** Dos usuarios crean empresas con el mismo nombre simultáneamente.

**Backend:** Ya maneja esto añadiendo `-1`, `-2` al slug.

**Frontend:** No requiere handling especial, el backend devuelve el slug único.

### 5. Cambio de empresa durante edición de formulario

**Escenario:** Usuario edita un producto, cambia de empresa, datos se mezclan.

**Solución:**
- Detectar si hay cambios no guardados
- Mostrar modal de confirmación: "Tienes cambios sin guardar. ¿Deseas cambiar de empresa?"
- Si acepta: descartar cambios + cambiar
- Si cancela: mantener empresa actual

**Implementación:**

```javascript
// CompanySwitcher.vue
async function handleSwitchCompany(companyId) {
  if (hasUnsavedChanges.value) {
    const confirmed = await showConfirmDialog(
      '¿Cambiar de empresa?',
      'Tienes cambios sin guardar que se perderán.'
    )
    if (!confirmed) return
  }
  
  await switchCompany(companyId)
}
```

### 6. Usuario sin empresas (eliminado de todas)

**Escenario:** Usuario es eliminado de todas sus empresas.

**Comportamiento esperado:**
- `fetchMe()` devuelve `companies: []`
- Mostrar vista especial: "No perteneces a ninguna empresa"
- CTA: "Crear mi primera empresa"

**Implementación:**

```vue
<!-- App.vue -->
<template>
  <EmptyLayout v-if="!hasCompanies">
    <NoCompaniesView />
  </EmptyLayout>
  <DefaultLayout v-else>
    <router-view />
  </DefaultLayout>
</template>

<script setup>
const { companies } = useAuth()
const hasCompanies = computed(() => companies.value.length > 0)
</script>
```

---

## Conclusión técnica

La implementación de este sistema de autenticación requiere atención especial en:

1. **Gestión de cookies HTTP-only** con `credentials: 'include'`
2. **Header X-Company dinámico** en todas las peticiones (excepto auth/companies)
3. **Recuperación de sesión** en cada recarga de página
4. **Manejo de errores 401/403** con lógica de re-autenticación
5. **FormData para uploads** de archivos
6. **Validación robusta** de formularios
7. **Edge cases** de multi-tenancy (eliminación, cambios de empresa)

Siguiendo estas consideraciones, el sistema será robusto, seguro y mantenible.
