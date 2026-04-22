# ✅ Checklist de Implementación — Sistema de Autenticación

> **Proyecto:** Sazed ERP (TFG)  
> **Referencia:** [AUTH_SYSTEM_OVERVIEW.md](./AUTH_SYSTEM_OVERVIEW.md)

Este documento es una guía práctica paso a paso para implementar el sistema de autenticación.

---

## 📦 Fase 1: Infraestructura base (Día 1-2)

### 1.1 Dependencias

- [ ] Instalar librería de toasts  
  ```bash
  npm install vue-toastification@next
  ```

- [ ] Configurar toast en `main.js`  
  ```javascript
  import Toast from 'vue-toastification'
  import 'vue-toastification/dist/index.css'
  
  app.use(Toast, {
    position: 'top-right',
    timeout: 4000,
  })
  ```

### 1.2 Servicio de API

- [ ] Modificar `src/services/api.js`:
  - [ ] Añadir gestión de `activeCompanyId`
  - [ ] Añadir función `setActiveCompany(id)`
  - [ ] Añadir función `getActiveCompany()`
  - [ ] Modificar `apiFetch()` para:
    - [ ] Enviar `credentials: 'include'` siempre
    - [ ] Añadir header `X-Company` si no es ruta de auth/companies
    - [ ] Soportar FormData (no JSON.stringify si body es FormData)
    - [ ] Añadir header `X-CSRFToken` en peticiones POST/PUT/PATCH
    - [ ] Manejar error 401 → logout + redirigir a /login
    - [ ] Manejar error 403 → retry después de fetchMe()

### 1.3 Servicio de autenticación

- [ ] Crear `src/services/auth.js` con:
  - [ ] `login(email, password)`
  - [ ] `register(data)`
  - [ ] `logout()`
  - [ ] `me()`
  - [ ] `updateProfile(data)`
  - [ ] `changePassword(current, newPassword)`
  - [ ] `switchCompany(companyId)`

### 1.4 Composable useAuth

- [ ] Crear `src/composables/useAuth.js` con:
  - [ ] State: `user`, `companies`, `activeCompany`, `isLoading`, `isAuthenticated`
  - [ ] Métodos:
    - [ ] `login(email, password)`
    - [ ] `register(data)`
    - [ ] `logout()`
    - [ ] `fetchMe()` (con promise singleton para evitar múltiples llamadas)
    - [ ] `switchCompany(companyId)`
    - [ ] `updateProfile(data)`
    - [ ] `changePassword(current, newPassword)`
  - [ ] Al llamar `login()` o `fetchMe()`:
    - [ ] Guardar user + companies en state
    - [ ] Establecer activeCompany (is_default=true o primera)
    - [ ] Llamar a `setActiveCompany(id)` para configurar header

### 1.5 Layouts

- [ ] Crear `src/layouts/DefaultLayout.vue`:
  - [ ] Mover el contenido actual de `App.vue` (sidebar + header + router-view)

- [ ] Crear `src/layouts/EmptyLayout.vue`:
  - [ ] Solo `<router-view />` (sin sidebar/header)

- [ ] Modificar `src/App.vue`:
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

### 1.6 Router guard

- [ ] Modificar `src/router/index.js`:
  - [ ] Importar `useAuth()`
  - [ ] Añadir `router.beforeEach()` con lógica:
    - [ ] Si ruta tiene `meta.guest` y user autenticado → redirigir a '/'
    - [ ] Si ruta requiere auth y no hay user → llamar `fetchMe()`
    - [ ] Si `fetchMe()` falla (401) → redirigir a '/login?redirect=...'
    - [ ] Si ruta tiene `meta.requiresRole` → verificar rol del membership
  - [ ] Marcar todas las rutas existentes con `meta: { requiresAuth: true }`

### 1.7 Composable de validación

- [ ] Crear `src/composables/useFormValidation.js` con:
  - [ ] `errors` (ref)
  - [ ] `validateEmail(email)`
  - [ ] `validatePassword(password)`
  - [ ] `setError(field, message)`
  - [ ] `clearError(field)`
  - [ ] `clearAllErrors()`

---

## 🔐 Fase 2: Vistas de autenticación (Día 3-5)

### 2.1 LoginView

- [ ] Crear `src/views/auth/LoginView.vue`:
  - [ ] Layout: centrado, card con logo
  - [ ] Formulario:
    - [ ] Input email (type="email", required)
    - [ ] Input password (type="password", required)
    - [ ] Botón "Iniciar sesión" (primario, full-width)
    - [ ] Link "¿Olvidaste tu contraseña?" (futuro, disabled)
    - [ ] Divider "o"
    - [ ] Botón "Crear cuenta" (secundario, redirige a /register)
  - [ ] Validación:
    - [ ] Formato email válido
    - [ ] Password no vacío
  - [ ] Estados:
    - [ ] Loading durante submit (botón disabled + spinner)
    - [ ] Error: mostrar mensaje "Email o contraseña incorrectos"
  - [ ] Al éxito: redirigir a `?redirect=...` o '/'

- [ ] Añadir ruta en router:
  ```javascript
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: { guest: true, layout: 'empty' }
  }
  ```

- [ ] Estilos:
  - [ ] Fondo gradiente `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
  - [ ] Card blanca, 400px ancho, border-radius 12px, sombra
  - [ ] Logo centrado arriba
  - [ ] Usar clases `.input`, `.btn`, `.btn-primary` de `style.css`

### 2.2 RegisterView

- [ ] Crear `src/views/auth/RegisterView.vue`:
  - [ ] Layout similar a LoginView
  - [ ] Formulario:
    - [ ] Input first_name (required)
    - [ ] Input last_name (opcional)
    - [ ] Input email (required, validación formato)
    - [ ] Input password (required, min 8 chars, mostrar requisitos)
    - [ ] Input confirm_password (debe coincidir)
    - [ ] Input company_name (required)
    - [ ] Checkbox "Acepto términos" (required)
    - [ ] Botón "Crear cuenta"
    - [ ] Link "¿Ya tienes cuenta? Inicia sesión"
  - [ ] Validación en tiempo real:
    - [ ] Email válido (visual feedback)
    - [ ] Password ≥ 8 chars (checkmark verde)
    - [ ] Passwords coinciden
    - [ ] Términos aceptados
  - [ ] Errores del servidor:
    - [ ] "Ya existe una cuenta con este email"
    - [ ] Otros errores genéricos
  - [ ] Al éxito: redirigir a '/' + toast "¡Cuenta creada!"

- [ ] Añadir ruta en router:
  ```javascript
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterView.vue'),
    meta: { guest: true, layout: 'empty' }
  }
  ```

- [ ] Estilos: similar a LoginView pero card 480px ancho

---

## 👤 Fase 3: CompanySwitcher en header (Día 6)

### 3.1 Componente CompanySwitcher

- [ ] Crear `src/components/CompanySwitcher.vue`:
  - [ ] Botón trigger con:
    - [ ] Logo empresa (si existe) o icono `Building2`
    - [ ] Nombre empresa activa
    - [ ] Icono `ChevronDown`
    - [ ] Avatar usuario (iniciales)
  - [ ] Dropdown (mostrar con `v-if` o librería de dropdown):
    - [ ] Sección "Empresas"
    - [ ] Lista de companies con:
      - [ ] Logo + nombre
      - [ ] Checkmark ✓ en la activa
      - [ ] Click → `switchCompany(id)` + loading + reload
    - [ ] Divider
    - [ ] "⚙️ Gestionar empresas" → redirige a '/settings/company'
    - [ ] "➕ Crear empresa" → abre modal CreateCompanyModal
    - [ ] Divider
    - [ ] "👤 Mi perfil" → redirige a '/profile'
    - [ ] "🚪 Cerrar sesión" → logout() + redirige a '/login'
  - [ ] Hover states en items
  - [ ] Loading state al cambiar empresa

### 3.2 Integración en header

- [ ] Modificar `src/layouts/DefaultLayout.vue`:
  - [ ] Reemplazar el avatar estático actual con `<CompanySwitcher />`
  - [ ] Posición: top-right del header

---

## 📝 Fase 4: Perfil de usuario (Día 7-8)

### 4.1 ProfileView

- [ ] Crear `src/views/auth/ProfileView.vue`:
  - [ ] Header con botón "← Volver"
  - [ ] Card: Información personal
    - [ ] Avatar circular (80px)
    - [ ] Botón "📷 Cambiar foto" → input file hidden
    - [ ] Input first_name
    - [ ] Input last_name
    - [ ] Email (read-only, gris)
    - [ ] "Miembro desde" (fecha formateada)
    - [ ] Botones: [Cancelar] [Guardar cambios]
  - [ ] Card: Seguridad
    - [ ] Texto "Contraseña" con "••••••••"
    - [ ] Botón "🔒 Cambiar contraseña" → abre ChangePasswordModal
  - [ ] Card: Mis empresas
    - [ ] Lista de companies con:
      - [ ] Logo + nombre + rol
      - [ ] Badge "Activa" en la empresa activa
      - [ ] Botón "Cambiar a esta empresa" en las no activas
    - [ ] Botón "+ Crear nueva empresa" → abre CreateCompanyModal
  - [ ] Validación de formulario (nombre no vacío)
  - [ ] Upload de avatar:
    - [ ] Input file (accept="image/*")
    - [ ] Validar tamaño (max 2MB)
    - [ ] Validar tipo (solo imágenes)
    - [ ] Preview antes de subir (opcional)
    - [ ] PATCH /auth/profile/ con FormData

- [ ] Añadir ruta:
  ```javascript
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/auth/ProfileView.vue'),
    meta: { requiresAuth: true }
  }
  ```

### 4.2 ChangePasswordModal

- [ ] Crear `src/components/modals/ChangePasswordModal.vue`:
  - [ ] Input: Contraseña actual
  - [ ] Input: Nueva contraseña (mostrar indicador de fortaleza)
  - [ ] Input: Confirmar nueva contraseña
  - [ ] Validación:
    - [ ] Nueva ≠ actual
    - [ ] Nueva = confirmar
    - [ ] Nueva ≥ 8 chars
  - [ ] Checkmarks verdes para requisitos cumplidos
  - [ ] Botones: [Cancelar] [Guardar]
  - [ ] Loading state durante submit
  - [ ] Errores:
    - [ ] "Contraseña actual incorrecta"
  - [ ] Al éxito: cerrar modal + toast "Contraseña actualizada"

### 4.3 CreateCompanyModal

- [ ] Crear `src/components/modals/CreateCompanyModal.vue`:
  - [ ] Input: Nombre empresa (required)
  - [ ] Input: CIF/NIF (opcional)
  - [ ] Input: Email contacto (opcional)
  - [ ] Select: Divisa (EUR, USD...) (default: EUR)
  - [ ] Info: "Podrás configurar más detalles después"
  - [ ] Botones: [Cancelar] [Crear empresa]
  - [ ] Al éxito:
    - [ ] Añadir a la lista de companies en state
    - [ ] Opcionalmente cambiar a la nueva empresa
    - [ ] Toast "Empresa creada"

---

## ⚙️ Fase 5: Configuración de empresa (Día 9-11)

### 5.1 CompanySettingsView

- [ ] Crear `src/views/settings/CompanySettingsView.vue`:
  - [ ] Header: "⚙️ Configuración de empresa"
  - [ ] Tabs: [ General ] [ Facturación ] [ Miembros ] [ Plan ]
  - [ ] **Tab General:**
    - [ ] Upload logo (similar a avatar)
    - [ ] Inputs: name, legal_name, tax_id
    - [ ] Inputs: email, phone, website
    - [ ] Inputs: address, city, province, postal_code
    - [ ] Select: country
    - [ ] Color picker: primary_color
    - [ ] Botón "Guardar cambios"
    - [ ] PATCH /companies/{id}/
  - [ ] **Tab Facturación:**
    - [ ] Select: currency
    - [ ] Select: fiscal_year_start (1-12)
    - [ ] Input: invoice_prefix
    - [ ] Botón "Guardar cambios"
  - [ ] **Tab Miembros:**
    - [ ] Botón "+ Invitar" → abre InviteMemberModal
    - [ ] Tabla de members:
      - [ ] Columns: Avatar, Nombre, Email, Rol, Acciones
      - [ ] GET /companies/{id}/members/
      - [ ] Menú contextual [...]:
        - [ ] "Cambiar rol" → show modal o inline edit
        - [ ] "Eliminar del equipo" (texto rojo)
    - [ ] Info: descripción de roles
  - [ ] **Tab Plan:**
    - [ ] Cards de planes (Free, Starter, Pro)
    - [ ] Badge "Actual" en el plan activo
    - [ ] Botón "Actualizar" en otros planes (futuro)
  - [ ] Guard de permisos:
    - [ ] Solo owner/admin pueden acceder
    - [ ] Mostrar mensaje "No tienes permiso" si viewer/editor

- [ ] Añadir ruta:
  ```javascript
  {
    path: '/settings/company',
    name: 'CompanySettings',
    component: () => import('../views/settings/CompanySettingsView.vue'),
    meta: {
      requiresAuth: true,
      requiresRole: ['owner', 'admin']
    }
  }
  ```

### 5.2 InviteMemberModal

- [ ] Crear `src/components/modals/InviteMemberModal.vue`:
  - [ ] Input: Email (required, validación formato)
  - [ ] Select: Rol (editor, admin, viewer)
  - [ ] Descripción de cada rol
  - [ ] Info: "Se enviará una invitación al correo"
  - [ ] Botones: [Cancelar] [Enviar invitación]
  - [ ] POST /companies/{id}/members/ {email, role}
  - [ ] Al éxito:
    - [ ] Cerrar modal
    - [ ] Refrescar lista de miembros
    - [ ] Toast "Invitación enviada a email@example.com"

---

## 🧪 Fase 6: Testing y refinamiento (Día 12-13)

### 6.1 Testing manual

- [ ] **Flujo: Registro**
  - [ ] Crear cuenta con datos válidos
  - [ ] Verificar que se crea User + Company + Membership
  - [ ] Verificar redirección a dashboard
  - [ ] Verificar toast de éxito
  - [ ] Error: email ya existe

- [ ] **Flujo: Login**
  - [ ] Login con credenciales válidas
  - [ ] Verificar cookie en devtools
  - [ ] Verificar redirección
  - [ ] Error: credenciales incorrectas
  - [ ] Error: cuenta desactivada (manual en Django admin)

- [ ] **Flujo: Recuperación de sesión**
  - [ ] Login → recargar página
  - [ ] Verificar que sigue autenticado
  - [ ] Verificar que empresa activa se mantiene
  - [ ] Cerrar pestaña → volver → verificar sesión persiste
  - [ ] Logout → recargar → verificar redirige a /login

- [ ] **Flujo: Cambio de empresa**
  - [ ] Crear múltiples empresas
  - [ ] Cambiar entre empresas
  - [ ] Verificar que datos cambian (si hay productos/clientes creados por empresa)
  - [ ] Verificar header X-Company en devtools Network tab

- [ ] **Flujo: Editar perfil**
  - [ ] Cambiar nombre/apellidos
  - [ ] Subir avatar (jpg, png)
  - [ ] Error: archivo muy grande (>2MB)
  - [ ] Cambiar contraseña
  - [ ] Error: contraseña actual incorrecta

- [ ] **Flujo: Gestionar empresa**
  - [ ] Editar info general
  - [ ] Cambiar logo
  - [ ] Invitar miembro (email nuevo)
  - [ ] Invitar miembro (email existente)
  - [ ] Cambiar rol de miembro
  - [ ] Eliminar miembro
  - [ ] Error: solo owner puede eliminar admin

### 6.2 Testing de edge cases

- [ ] **Sesión expirada:**
  - [ ] Modificar SESSION_COOKIE_AGE a 1 minuto en Django
  - [ ] Login → esperar 1 min → hacer acción
  - [ ] Verificar que redirige a /login con toast "Sesión expirada"

- [ ] **Usuario eliminado de empresa:**
  - [ ] Usuario A en empresa X
  - [ ] Admin elimina a usuario A
  - [ ] Usuario A intenta acceder a datos
  - [ ] Verificar que detecta 403 y refresca companies

- [ ] **Usuario sin empresas:**
  - [ ] Eliminar todas memberships de un usuario
  - [ ] Usuario intenta acceder
  - [ ] Verificar que muestra mensaje "No perteneces a ninguna empresa"

- [ ] **Cambio de empresa con formulario abierto:**
  - [ ] Abrir modal de crear producto
  - [ ] Cambiar empresa
  - [ ] Verificar que modal se cierra (o pide confirmación si hay cambios)

### 6.3 Responsive testing

- [ ] **Mobile (320px - 767px):**
  - [ ] Login/register: card full-width
  - [ ] Sidebar colapsada por defecto
  - [ ] CompanySwitcher: dropdown adapta ancho
  - [ ] ProfileView: stack vertical
  - [ ] CompanySettingsView: tabs scroll horizontal

- [ ] **Tablet (768px - 1023px):**
  - [ ] Sidebar collapsible
  - [ ] Forms: algunas filas 2 columnas

- [ ] **Desktop (1024px+):**
  - [ ] Layout completo
  - [ ] Modales centrados con ancho fijo

### 6.4 Accesibilidad

- [ ] Todos los inputs tienen `<label for="...">`
- [ ] Botones de iconos tienen `aria-label`
- [ ] Focus visible en elementos interactivos
- [ ] Errores con `role="alert"`
- [ ] Navegación con teclado funciona (Tab, Enter, Escape)
- [ ] Contraste de colores adecuado (WCAG AA)

---

## 🔗 Fase 7: Integración con módulos existentes (Día 14)

### 7.1 Actualizar rutas existentes

- [ ] Marcar todas las rutas con `meta: { requiresAuth: true }`:
  - [ ] /products
  - [ ] /collections
  - [ ] /inventory
  - [ ] /orders
  - [ ] /invoices
  - [ ] /wallet
  - [ ] /customers
  - [ ] /marketing
  - [ ] /online-store
  - [ ] /sell-link

### 7.2 Verificar header X-Company

- [ ] Abrir devtools Network tab
- [ ] Navegar a módulos existentes (productos, clientes...)
- [ ] Verificar que peticiones tienen header `X-Company: {id}`
- [ ] Verificar que datos cargados corresponden a empresa activa

### 7.3 Botón de configuración en sidebar

- [ ] Añadir item en `menuItems` de DefaultLayout:
  ```javascript
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    route: '/settings/company'
  }
  ```

- [ ] Alternativamente, añadir botón en footer del sidebar

---

## 📋 Checklist final

### Funcionalidades core

- [ ] ✅ Login funciona y establece sesión
- [ ] ✅ Register crea usuario + empresa
- [ ] ✅ Logout cierra sesión
- [ ] ✅ Sesión persiste al recargar página
- [ ] ✅ CompanySwitcher muestra empresas del usuario
- [ ] ✅ Cambio de empresa actualiza datos
- [ ] ✅ Perfil de usuario editable
- [ ] ✅ Cambio de contraseña funciona
- [ ] ✅ Upload de avatar funciona
- [ ] ✅ Configuración de empresa editable (owner/admin)
- [ ] ✅ Invitar miembros funciona
- [ ] ✅ Gestión de miembros (cambiar rol, eliminar)

### Seguridad

- [ ] ✅ Cookies HTTP-only se establecen correctamente
- [ ] ✅ Header X-Company se envía en todas las peticiones de datos
- [ ] ✅ Router guard protege rutas privadas
- [ ] ✅ Permisos por rol verificados (settings solo owner/admin)
- [ ] ✅ CSRF token enviado en peticiones POST/PUT/PATCH
- [ ] ✅ Passwords nunca se guardan en localStorage

### UX

- [ ] ✅ Loading states en todos los botones
- [ ] ✅ Toasts informativos en todas las acciones
- [ ] ✅ Validación inline en formularios
- [ ] ✅ Errores claros y específicos
- [ ] ✅ Confirmaciones para acciones destructivas
- [ ] ✅ Responsive en mobile/tablet/desktop

### Performance

- [ ] ✅ Lazy loading de vistas
- [ ] ✅ No hay múltiples llamadas a fetchMe() simultáneas
- [ ] ✅ Avatar/logo optimizados (max 2MB, resize si es muy grande)

### Testing

- [ ] ✅ Todos los flujos principales testeados
- [ ] ✅ Edge cases cubiertos
- [ ] ✅ Accesibilidad verificada
- [ ] ✅ Responsive verificado

---

## 🎉 Completado

Si todos los items están marcados, el sistema de autenticación está **completo y listo para producción**.

**Próximos pasos:**
- Deploy a staging para testing real
- Documentar para otros desarrolladores
- Monitorear logs de errores
- Recoger feedback de usuarios beta

---

**Nota:** Este checklist debe revisarse durante la implementación. Algunos items pueden cambiar según necesidades emergentes o limitaciones técnicas descubiertas.
