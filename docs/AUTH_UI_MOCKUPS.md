# Mockups UI — Sistema de Autenticación

> **Fecha:** 2026-04-12  
> **Proyecto:** Sazed ERP  
> **Referencia:** [FRONTEND_AUTH_DESIGN.md](./FRONTEND_AUTH_DESIGN.md)

Este documento contiene mockups visuales en formato ASCII de todas las pantallas del sistema de autenticación.

---

## 🎨 Paleta de colores

```css
/* Del sistema de diseño existente */
--primary-color: #667eea
--primary-dark: #4f46e5
--bg-primary: #f9fafb
--text-primary: #111827
--text-secondary: #6b7280
--border-color: #e5e7eb
```

---

## 1. LoginView.vue — `/login`

### Desktop (1200px+)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                        [Fondo gradiente #667eea → #764ba2]                 │
│                                                                             │
│                             ╔═══════════════════════╗                       │
│                             ║                       ║                       │
│                             ║    ┌───────────┐     ║                       │
│                             ║    │ [Logo SVG]│     ║                       │
│                             ║    │  Sazed ERP│     ║                       │
│                             ║    └───────────┘     ║                       │
│                             ║                       ║                       │
│                             ║  Iniciar sesión       ║                       │
│                             ║  ────────────────     ║                       │
│                             ║                       ║                       │
│                             ║  Email                ║                       │
│                             ║  ┌─────────────────┐ ║                       │
│                             ║  │ user@example.com│ ║                       │
│                             ║  └─────────────────┘ ║                       │
│                             ║                       ║                       │
│                             ║  Contraseña           ║                       │
│                             ║  ┌─────────────────┐ ║                       │
│                             ║  │ ••••••••••••    │ ║                       │
│                             ║  └─────────────────┘ ║                       │
│                             ║  └─> ¿Olvidaste tu   ║                       │
│                             ║      contraseña?     ║                       │
│                             ║                       ║                       │
│                             ║  ┌─────────────────┐ ║                       │
│                             ║  │ Iniciar sesión  │ ║  (btn-primary)        │
│                             ║  └─────────────────┘ ║                       │
│                             ║                       ║                       │
│                             ║   ────── o ──────     ║                       │
│                             ║                       ║                       │
│                             ║  ┌─────────────────┐ ║                       │
│                             ║  │ Crear cuenta    │ ║  (btn-secondary)      │
│                             ║  └─────────────────┘ ║                       │
│                             ║                       ║                       │
│                             ╚═══════════════════════╝                       │
│                               (card 400px ancho)                            │
│                                                                             │
│                          © 2026 Sazed ERP                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mobile (320px - 768px)

```
┌──────────────────────────────┐
│ [Fondo gradiente]            │
│                              │
│   ┌────────────┐             │
│   │ [Logo]     │             │
│   │  Sazed ERP │             │
│   └────────────┘             │
│                              │
│  Iniciar sesión              │
│  ────────────────            │
│                              │
│  Email                       │
│  ┌────────────────────────┐ │
│  │ user@example.com       │ │
│  └────────────────────────┘ │
│                              │
│  Contraseña                  │
│  ┌────────────────────────┐ │
│  │ ••••••••••••           │ │
│  └────────────────────────┘ │
│  ¿Olvidaste tu contraseña?   │
│                              │
│  ┌────────────────────────┐ │
│  │ Iniciar sesión         │ │
│  └────────────────────────┘ │
│                              │
│   ────── o ──────            │
│                              │
│  ┌────────────────────────┐ │
│  │ Crear cuenta           │ │
│  └────────────────────────┘ │
│                              │
│  © 2026 Sazed ERP            │
│                              │
└──────────────────────────────┘
```

### Estados

**Loading state (durante login):**
```
┌─────────────────────┐
│  🔄 Iniciando...   │  (spinner + texto)
└─────────────────────┘
```

**Error state:**
```
Email
┌─────────────────┐
│ user@test.com   │
└─────────────────┘

Contraseña
┌─────────────────┐
│ ••••••••        │  (borde rojo)
└─────────────────┘
⚠️ Email o contraseña incorrectos
```

---

## 2. RegisterView.vue — `/register`

### Desktop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        [Fondo gradiente #667eea → #764ba2]                 │
│                                                                             │
│                        ╔═══════════════════════════╗                        │
│                        ║                           ║                        │
│                        ║   ┌────────────┐          ║                        │
│                        ║   │  [Logo]    │          ║                        │
│                        ║   └────────────┘          ║                        │
│                        ║                           ║                        │
│                        ║   Crear cuenta            ║                        │
│                        ║   ─────────────           ║                        │
│                        ║                           ║                        │
│                        ║   Datos personales        ║                        │
│                        ║   ═════════════           ║                        │
│                        ║                           ║                        │
│                        ║   Nombre *                ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ Juan                │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║                           ║                        │
│                        ║   Apellidos               ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ Pérez García        │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║                           ║                        │
│                        ║   Email *                 ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ juan@example.com    │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║                           ║                        │
│                        ║   Contraseña *            ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ ••••••••••••        │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║   ✓ Mínimo 8 caracteres   ║                        │
│                        ║                           ║                        │
│                        ║   Confirmar contraseña *  ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ ••••••••••••        │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║                           ║                        │
│                        ║   Datos de empresa        ║                        │
│                        ║   ══════════════          ║                        │
│                        ║                           ║                        │
│                        ║   Nombre de la empresa *  ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │ Mi Empresa SL       │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║   ℹ️  Podrás configurar   ║                        │
│                        ║      más detalles después ║                        │
│                        ║                           ║                        │
│                        ║   ☐ Acepto los términos   ║                        │
│                        ║      y condiciones        ║                        │
│                        ║                           ║                        │
│                        ║   ┌─────────────────────┐ ║                        │
│                        ║   │  Crear cuenta       │ ║                        │
│                        ║   └─────────────────────┘ ║                        │
│                        ║                           ║                        │
│                        ║   ¿Ya tienes cuenta?      ║                        │
│                        ║   Inicia sesión           ║                        │
│                        ║                           ║                        │
│                        ╚═══════════════════════════╝                        │
│                          (card 480px ancho)                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validaciones en tiempo real

**Email inválido:**
```
Email *
┌─────────────────┐
│ juan@test       │  (borde amarillo/warning)
└─────────────────┘
⚠️ Formato de email inválido
```

**Contraseñas no coinciden:**
```
Confirmar contraseña *
┌─────────────────┐
│ ••••••••        │  (borde rojo)
└─────────────────┘
❌ Las contraseñas no coinciden
```

**Email ya registrado (error del servidor):**
```
Email *
┌─────────────────┐
│ juan@test.com   │  (borde rojo)
└─────────────────┘
❌ Ya existe una cuenta con este email
```

---

## 3. ProfileView.vue — `/profile`

### Desktop (con sidebar del layout principal)

```
┌──────────┬──────────────────────────────────────────────────────────────────┐
│          │  ← Mi Perfil                                       [User icon]  │
│ SIDEBAR  │  ──────────────────────────────────────────────────────────────  │
│          │                                                                  │
│ [Home]   │  ┌────────────────────────────────────────────────────────────┐ │
│ [Catalog]│  │ Información personal                                       │ │
│ [Finance]│  │                                                            │ │
│ ...      │  │          ╔═══════╗                                         │ │
│          │  │          ║ [👤] ║  (Avatar circular 80px)                  │ │
│          │  │          ║  JP  ║                                          │ │
│          │  │          ╚═══════╝                                         │ │
│          │  │                                                            │ │
│          │  │          [📷 Cambiar foto]  (btn-ghost)                   │ │
│          │  │                                                            │ │
│          │  │  Nombre                                                    │ │
│          │  │  ┌──────────────────────────────────────┐                 │ │
│          │  │  │ Juan                                 │                 │ │
│          │  │  └──────────────────────────────────────┘                 │ │
│          │  │                                                            │ │
│          │  │  Apellidos                                                 │ │
│          │  │  ┌──────────────────────────────────────┐                 │ │
│          │  │  │ Pérez García                         │                 │ │
│          │  │  └──────────────────────────────────────┘                 │ │
│          │  │                                                            │ │
│          │  │  Email                                                     │ │
│          │  │  juan.perez@example.com  (texto gris, no editable)        │ │
│          │  │                                                            │ │
│          │  │  Miembro desde                                             │ │
│          │  │  15 de enero, 2026                                         │ │
│          │  │                                                            │ │
│          │  │  [Cancelar]  [Guardar cambios] (btn-primary)              │ │
│          │  │                                                            │ │
│          │  └────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
│          │  ┌────────────────────────────────────────────────────────────┐ │
│          │  │ Seguridad                                                  │ │
│          │  │                                                            │ │
│          │  │  Contraseña                                                │ │
│          │  │  •••••••• (oculta)                                         │ │
│          │  │                                                            │ │
│          │  │  [🔒 Cambiar contraseña]  (btn-secondary)                 │ │
│          │  │                                                            │ │
│          │  └────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
│          │  ┌────────────────────────────────────────────────────────────┐ │
│          │  │ Mis empresas                                    2 empresas │ │
│          │  │                                                            │ │
│          │  │  ┌──────────────────────────────────────────────────────┐ │ │
│          │  │  │ ┌────┐                                               │ │ │
│          │  │  │ │[🏢]│  Acme Corp               ✓ Activa             │ │ │
│          │  │  │ └────┘  Propietario                                  │ │ │
│          │  │  └──────────────────────────────────────────────────────┘ │ │
│          │  │                                                            │ │
│          │  │  ┌──────────────────────────────────────────────────────┐ │ │
│          │  │  │ ┌────┐                                               │ │ │
│          │  │  │ │[🏢]│  My Side Project                             │ │ │
│          │  │  │ └────┘  Editor                                       │ │ │
│          │  │  │         [→ Cambiar a esta empresa]  (link)           │ │ │
│          │  │  └──────────────────────────────────────────────────────┘ │ │
│          │  │                                                            │ │
│          │  │  [+ Crear nueva empresa]  (btn-ghost)                     │ │
│          │  │                                                            │ │
│          │  └────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
└──────────┴──────────────────────────────────────────────────────────────────┘
```

---

## 4. CompanySwitcher.vue — Componente en Header

### Estado cerrado (como aparece en el header)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ [☰] [🔍 Search...]          [?] [🔔] [🌐 EN] │ [🏢] Acme Corp  ▼  [A]    │
└────────────────────────────────────────────────────────────────────────────┘
                                                  └──────────────┘
                                                   CompanySwitcher
```

### Estado abierto (dropdown)

```
                               ┌──────────────────────────────────┐
                               │ Empresas                         │
                               │ ──────────────────────────────── │
                               │ ✓ [🏢] Acme Corp                │ (activa)
                               │    [🏢] My Side Project          │
                               │    [🏢] Cliente ABC              │
                               │ ──────────────────────────────── │
                               │ ⚙️  Gestionar empresas           │
                               │ ➕  Crear empresa                │
                               │ ──────────────────────────────── │
                               │ 👤  Mi perfil                    │
                               │ 🚪  Cerrar sesión                │
                               └──────────────────────────────────┘
```

**Hover states:**
- Empresa no activa: fondo gris claro
- "Mi perfil": fondo gris claro
- "Cerrar sesión": fondo rojo claro

**Click en empresa:**
- Mostrar loader: "Cambiando..."
- Fade out → reload → fade in

---

## 5. CompanySettingsView.vue — `/settings/company`

### Tab: General

```
┌──────────┬──────────────────────────────────────────────────────────────────┐
│          │  ⚙️ Configuración de empresa                                     │
│ SIDEBAR  │  ──────────────────────────────────────────────────────────────  │
│          │                                                                  │
│ [Home]   │  [ General ] [ Facturación ] [ Miembros ] [ Plan ]              │
│ [Catalog]│  ═══════════                                                     │
│ ...      │                                                                  │
│          │  ┌────────────────────────────────────────────────────────────┐ │
│          │  │ Logo de la empresa                                         │ │
│          │  │                                                            │ │
│          │  │  ┌─────────┐                                               │ │
│          │  │  │ [Imagen]│  (160x160px)                                  │ │
│          │  │  │ o [🏢]  │  (placeholder si no hay logo)                 │ │
│          │  │  └─────────┘                                               │ │
│          │  │                                                            │ │
│          │  │  [📷 Cambiar logo]  (btn-ghost)                           │ │
│          │  │                                                            │ │
│          │  │  Información básica                                        │ │
│          │  │  ───────────────────                                       │ │
│          │  │                                                            │ │
│          │  │  Nombre comercial *                                        │ │
│          │  │  ┌──────────────────────────────┐                         │ │
│          │  │  │ Acme Corp                    │                         │ │
│          │  │  └──────────────────────────────┘                         │ │
│          │  │                                                            │ │
│          │  │  Razón social                                              │ │
│          │  │  ┌──────────────────────────────┐                         │ │
│          │  │  │ Acme Corporation SL          │                         │ │
│          │  │  └──────────────────────────────┘                         │ │
│          │  │                                                            │ │
│          │  │  CIF/NIF                                                   │ │
│          │  │  ┌──────────────────────────────┐                         │ │
│          │  │  │ B12345678                    │                         │ │
│          │  │  └──────────────────────────────┘                         │ │
│          │  │                                                            │ │
│          │  │  Contacto                                                  │ │
│          │  │  ────────                                                  │ │
│          │  │                                                            │ │
│          │  │  Email  │  Teléfono  │  Sitio web                         │ │
│          │  │  ┌──────────┬─────────┬────────────────┐                  │ │
│          │  │  │ info@... │ +34 ... │ https://...    │                  │ │
│          │  │  └──────────┴─────────┴────────────────┘                  │ │
│          │  │                                                            │ │
│          │  │  Dirección                                                 │ │
│          │  │  ─────────                                                 │ │
│          │  │                                                            │ │
│          │  │  Dirección                                                 │ │
│          │  │  ┌──────────────────────────────┐                         │ │
│          │  │  │ Calle Mayor 1                │                         │ │
│          │  │  └──────────────────────────────┘                         │ │
│          │  │                                                            │ │
│          │  │  Ciudad  │  Provincia  │  Código postal                   │ │
│          │  │  ┌─────────┬──────────┬──────────┐                        │ │
│          │  │  │ Madrid  │ Madrid   │ 28001    │                        │ │
│          │  │  └─────────┴──────────┴──────────┘                        │ │
│          │  │                                                            │ │
│          │  │  País                                                      │ │
│          │  │  ┌──────────────────────────────┐                         │ │
│          │  │  │ España              ▼        │  (select)               │ │
│          │  │  └──────────────────────────────┘                         │ │
│          │  │                                                            │ │
│          │  │  Branding                                                  │ │
│          │  │  ────────                                                  │ │
│          │  │                                                            │ │
│          │  │  Color principal  ┌──┐ #667eea                            │ │
│          │  │                   └──┘  (color picker)                    │ │
│          │  │                                                            │ │
│          │  │  [Guardar cambios]                                         │ │
│          │  │                                                            │ │
│          │  └────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
└──────────┴──────────────────────────────────────────────────────────────────┘
```

### Tab: Miembros

```
┌──────────┬──────────────────────────────────────────────────────────────────┐
│          │  ⚙️ Configuración de empresa                                     │
│ SIDEBAR  │  ──────────────────────────────────────────────────────────────  │
│          │                                                                  │
│          │  [ General ] [ Facturación ] [ Miembros ] [ Plan ]              │
│          │                               ══════════                         │
│          │                                                                  │
│          │  ┌────────────────────────────────────────────────────────────┐ │
│          │  │ Miembros del equipo (3)                   [+ Invitar]      │ │
│          │  │                                                            │ │
│          │  │  ┌──────────┬───────────────────┬──────────┬────────────┐ │ │
│          │  │  │ Usuario  │ Email             │ Rol      │ Acciones   │ │ │
│          │  │  ├──────────┼───────────────────┼──────────┼────────────┤ │ │
│          │  │  │ [MC] MC  │ maria@acme.com    │ Owner    │    ─       │ │ │
│          │  │  │          │                   │          │            │ │ │
│          │  │  │ [JR] JR  │ jose@acme.com     │ Admin    │    ⋮       │ │ │
│          │  │  │          │                   │          │            │ │ │
│          │  │  │ [AL] AL  │ ana@acme.com      │ Editor   │    ⋮       │ │ │
│          │  │  │          │                   │          │            │ │ │
│          │  │  │ [TG] TG  │ tom@external.com  │ Viewer   │    ⋮       │ │ │
│          │  │  │          │                   │          │            │ │ │
│          │  │  └──────────┴───────────────────┴──────────┴────────────┘ │ │
│          │  │                                                            │ │
│          │  │  Menú contextual [⋮]:                                      │ │
│          │  │  ┌──────────────────────┐                                 │ │
│          │  │  │ Cambiar rol          │                                 │ │
│          │  │  │ Eliminar del equipo  │  (texto rojo)                   │ │
│          │  │  └──────────────────────┘                                 │ │
│          │  │                                                            │ │
│          │  └────────────────────────────────────────────────────────────┘ │
│          │                                                                  │
│          │  ℹ️  Roles:                                                     │
│          │  • Owner: Control total (solo hay uno)                          │
│          │  • Admin: Gestión completa excepto eliminar empresa             │
│          │  • Editor: Crear y editar datos                                 │
│          │  • Viewer: Solo lectura                                         │
│          │                                                                  │
└──────────┴──────────────────────────────────────────────────────────────────┘
```

**Permisos:**
- Solo `owner` y `admin` ven esta tab
- Solo `owner` puede eliminar miembros o cambiar el rol de admin
- `admin` puede invitar/eliminar editors y viewers

---

## 6. Modales

### ChangePasswordModal.vue

```
                    ┌─────────────────────────────────┐
                    │ Cambiar contraseña          [×] │
                    ├─────────────────────────────────┤
                    │                                 │
                    │  Contraseña actual              │
                    │  ┌────────────────────────────┐ │
                    │  │ •••••••••••                │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Nueva contraseña               │
                    │  ┌────────────────────────────┐ │
                    │  │ ••••••••••••               │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Fortaleza: ████████░░ Fuerte   │
                    │                                 │
                    │  Confirmar nueva contraseña     │
                    │  ┌────────────────────────────┐ │
                    │  │ ••••••••••••               │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  ✓ Mínimo 8 caracteres          │
                    │  ✓ Las contraseñas coinciden    │
                    │                                 │
                    │  [Cancelar]  [Guardar]          │
                    │                                 │
                    └─────────────────────────────────┘
```

### CreateCompanyModal.vue

```
                    ┌─────────────────────────────────┐
                    │ Crear nueva empresa         [×] │
                    ├─────────────────────────────────┤
                    │                                 │
                    │  Nombre de la empresa *         │
                    │  ┌────────────────────────────┐ │
                    │  │ Mi Nueva Empresa           │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  CIF/NIF                        │
                    │  ┌────────────────────────────┐ │
                    │  │ B87654321                  │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Email de contacto              │
                    │  ┌────────────────────────────┐ │
                    │  │ info@nueva.com             │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Divisa                         │
                    │  ┌────────────────────────────┐ │
                    │  │ EUR - Euro          ▼      │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  ℹ️  Podrás configurar más     │
                    │     detalles después            │
                    │                                 │
                    │  [Cancelar]  [Crear empresa]    │
                    │                                 │
                    └─────────────────────────────────┘
```

### InviteMemberModal.vue

```
                    ┌─────────────────────────────────┐
                    │ Invitar miembro             [×] │
                    ├─────────────────────────────────┤
                    │                                 │
                    │  Email *                        │
                    │  ┌────────────────────────────┐ │
                    │  │ nuevo@example.com          │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Rol *                          │
                    │  ┌────────────────────────────┐ │
                    │  │ Editor              ▼      │ │
                    │  └────────────────────────────┘ │
                    │                                 │
                    │  Opciones:                      │
                    │  • Editor: Crear y editar datos │
                    │  • Admin: Gestión completa      │
                    │  • Viewer: Solo lectura         │
                    │                                 │
                    │  ℹ️  Se enviará una invitación  │
                    │     al correo indicado          │
                    │                                 │
                    │  [Cancelar]  [Enviar invitación]│
                    │                                 │
                    └─────────────────────────────────┘
```

---

## 7. Toast Notifications

```
┌────────────────────────────────────────────┐
│ ✅ Sesión iniciada                         │  (verde)
│    Bienvenido, Juan                        │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ ❌ Credenciales incorrectas                │  (rojo)
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ 🔄 Cambiando empresa...                    │  (azul)
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ ✅ Perfil actualizado                      │  (verde)
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ 📧 Invitación enviada a user@example.com   │  (azul)
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ ⚠️  Tu sesión ha expirado                  │  (amarillo)
│    Por favor, inicia sesión nuevamente     │
└────────────────────────────────────────────┘
```

**Posición:** Top-right  
**Duración:** 4 segundos (auto-dismiss)  
**Con botón [×]** para cerrar manualmente

---

## 8. Loading States

### Skeleton loaders

**ProfileView cargando:**
```
┌────────────────────────────────────────────┐
│ Información personal                       │
│                                            │
│  ┌────────┐  (avatar placeholder)         │
│  │░░░░░░░░│                               │
│  └────────┘                               │
│                                            │
│  ░░░░░░░░░░░░░░░░  (nombre)               │
│  ░░░░░░░░░░░░░░░░░░░░░░  (apellidos)      │
│                                            │
│  ░░░░░░░░░░░░░░░░░░  (email)              │
│                                            │
└────────────────────────────────────────────┘
```

**Button loading:**
```
┌──────────────────────┐
│  🔄 Guardando...     │  (spinner animado)
└──────────────────────┘
```

---

## 9. Responsive Breakpoints

```css
/* Mobile: 320px - 767px */
- Stack vertical de formularios
- Sidebar colapsada por defecto
- Modales full-width
- Cards sin margen lateral

/* Tablet: 768px - 1023px */
- Formularios 2 columnas (algunos campos)
- Sidebar collapsible

/* Desktop: 1024px+ */
- Layout completo sidebar + content
- Formularios multi-columna
- Modales centrados con ancho fijo
```

---

## Conclusión

Estos mockups definen la estructura visual completa del sistema de autenticación. Todos los componentes siguen el sistema de diseño existente (colores, tipografía, espaciados) y están optimizados para:

- ✅ Claridad y usabilidad
- ✅ Feedback visual inmediato
- ✅ Responsive design
- ✅ Accesibilidad (labels, focus states)
- ✅ Estados de carga y error

La implementación debe respetar estos mockups pero puede ajustar espaciados y detalles menores según el flujo de desarrollo.
