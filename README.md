# Sazed ERP - Sistema de Gestión Empresarial 🚀

Un sistema ERP web moderno y minimalista construido con Vue 3, diseñado para PyMEs y autónomos. Proyecto de Trabajo de Fin de Grado (TFG).

![Vue 3](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?logo=vite)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-MVP%20Development-orange)

---

## 📊 Estado Actual (Febrero 2026)

```
████████████░░░░░░░░ 60% Completado
```

### ✅ Módulos Implementados

| Módulo | Estado | Funcionalidad | Líneas |
|--------|--------|---------------|--------|
| **Dashboard** | ✅ Completo | KPIs, resumen de ventas, setup wizard | ~200 |
| **Productos** | ✅ Completo | CRUD, búsqueda, filtros, variantes, modales | ~800 |
| **Facturas** | ✅ Completo | Creación, estados (Draft→Paid), filtros avanzados | 2,142 |
| **Clientes** | ✅ Completo | CRUD, segmentación, tags, empresa/persona | 701 |
| **Wallet** | ✅ Completo | Balance, transacciones, historial | ~400 |

### 🚧 En Desarrollo (MVP Crítico)

- 📋 **Pedidos (Orders)** - Ciclo comercial completo
- 📦 **Inventario** - Control de stock y movimientos
- ⚙️ **Configuración** - Datos empresa, series, impuestos

### 📋 Planificado (Post-MVP)

- Presupuestos (Quotes)
- Albaranes de entrega
- Contabilidad básica (Gastos, P&L)
- Multi-usuario y roles
- Generación de PDFs
- Backend con Supabase

---

## 🌟 Características Destacadas

- 🎨 **Diseño Moderno** - UI/UX inspirado en Holded/Linear, diseño system consistente
- ⚡ **Rápido y Ligero** - Vue 3 Composition API + Vite para desarrollo ultra-rápido
- 🧩 **Modulares** - Componentes reutilizables, arquitectura escalable
- 🎯 **User-First** - Enfocado en simplicidad y usabilidad
- 🔓 **Open Source** - Código abierto, transparente, customizable
- 📱 **Responsive** - Funciona en desktop, tablet y mobile

## 🚀 Inicio Rápido

### Requisitos Previos

- Node.js 16+ 
- npm o yarn

### Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El servidor estará disponible en `http://localhost:5173`

## 📁 Estructura del Proyecto

```
TFG/
├── src/
│   ├── assets/          # Recursos estáticos
│   ├── components/      # Componentes reutilizables
│   ├── router/          # Configuración de rutas
│   ├── views/           # Páginas/Vistas
│   │   ├── Home.vue     # Dashboard principal
│   │   ├── Products.vue # Gestión de productos
│   │   ├── Wallet.vue   # Sistema de pagos
│   │   └── About.vue    # Información
│   ├── App.vue          # Componente raíz con layout
│   ├── main.js          # Punto de entrada
│   └── style.css        # Estilos globales y sistema de diseño
├── public/              # Archivos públicos
├── DESIGN_SYSTEM.md     # Documentación del sistema de diseño
└── README.md
```

## 🎨 Sistema de Diseño

El proyecto incluye un sistema de diseño completo basado en variables CSS. Consulta [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) para documentación detallada.

### Paleta de Colores

- **Primario:** `#6366f1` (Morado/Índigo)
- **Éxito:** `#10b981` (Verde)
- **Advertencia:** `#f59e0b` (Ámbar)
- **Error:** `#ef4444` (Rojo)

### Componentes Disponibles

- Botones (primario, secundario, ghost)
- Cards (tarjetas con header/body/footer)
- Inputs y formularios
- Tablas con hover
- Badges de estado
- Utilidades de espaciado y layout

## 🗺️ Rutas

| Ruta | Estado | Descripción |
|------|--------|-------------|
| `/` | ✅ | Dashboard principal con KPIs y setup wizard |
| `/products` | ✅ | Gestión completa de productos (CRUD + búsqueda) |
| `/customers` | ✅ | Gestión de clientes (empresa/persona, tags) |
| `/invoices` | ✅ | Facturación completa (estados, filtros, conversión) |
| `/wallet` | ✅ | Balance y transacciones |
| `/orders` | 🚧 | Pedidos (en desarrollo) |
| `/inventory` | 🚧 | Control de inventario (en desarrollo) |
| `/settings` | 🚧 | Configuración (en desarrollo) |
| `/collections` | 📋 | Colecciones de productos (placeholder) |
| `/marketin (puerto 5173)
npm run dev

# Build para producción
npm run build

# Preview de producción
npm run preview

# Tests (cuando estén configurados)
npm run test
npm run test:e2e
```

---

## 📚 Documentación del Proyecto

El proyecto incluye documentación exhaustiva en `/docs`:

- **[MVP_ANALYSIS.md](docs/MVP_ANALYSIS.md)** - Análisis completo del estado actual vs. Holded, gap analysis y roadmap estratégico
- **[MVP_ROADMAP.md](docs/MVP_ROADMAP.md)** - Hoja de ruta detallada por fases (8 semanas)
- **[FEATURE_COMPARISON.md](docs/FEATURE_COMPARISON.md)** - Matriz comparativa de features vs. competencia (Holded, Sage, Zoho)
- **[IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md)** - Checklist día a día para implementación MVP
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Guía completa del sistema de diseño (colores, componentes, utilities)
- **[specs/INVOICES_MODULE_SPEC.md](docs/specs/INVOICES_MODULE_SPEC.md)** - Especificación técnica del módulo de facturas (1048 líneas)

---

## 🎯 Próximos Pasos

### Esta Semana (Prioridad 1)
1. [ ] Implementar módulo **Orders** (Pedidos)
2. [ ] Implementar módulo **Inventory** (Inventario)
3. [ ] Implementar módulo **Settings** (Configuración)
4. [ ] Conectar flujo: Producto → Pedido → Factura → Stock

### Siguiente Semana (Prioridad 2)
1. [ ] Añadir validaciones y feedback visual (toasts, loading states)
2. [ ] Tests unitarios y E2E
3. [ ] Mejorar CRM (historial, notas)
4. [ ] Backend con Supabase (persistencia real)

### Futuro (Post-MVP)
- Presupuestos y albaranes
- Contabilidad básica (gastos, P&L)
- Multi-usuario con autenticación
- Generación de PDFs
- Integraciones (email, bancos, e-commerce)

---

## 🏆 Comparativa con ERPs del Mercado

| Feature | Sazed | Holded | Sage 50 |
|---------|-------|--------|---------|
| Productos | ✅ | ✅ | ✅ |
| Clientes | ✅ | ✅ | ✅ |
| Facturas | ✅ | ✅ | ✅ |
| Pedidos | 🚧 | ✅ | ✅ |
| Inventario | 🚧 | ✅ | ✅ |
| Contabilidad | ❌ | ✅ | ✅ |
| Multi-usuario | ❌ | ✅ | ✅ |
| Diseño moderno | ✅ | ✅ | ❌ |
| Open source | 🔮 | ❌ | ❌ |
| Precio | 0€ | 15-49€ | 40-80€ |

Ver **[comparativa completa](docs/FEATURE_COMPARISON.md)** con matriz detallada de 100+ features.

---

## 🎓 Contexto Académico

Este proyecto es un **Trabajo de Fin de Grado** que demuestra:

- ✅ Arquitectura frontend moderna (Vue 3, Composition API)
- ✅ Diseño de sistemas complejos (ERP multi-módulo)
- ✅ UX/UI design (sistema de diseño consistente)
- ✅ Modelado de datos (entidades relacionadas)
- 🚧 Testing automatizado (Vitest, Playwright)
- 🚧 Backend y persistencia (Supabase)
- 📋 Deploy y CI/CD (Vercel + GitHub Actions)

**Objetivo:** MVP funcional que cubra el ciclo comercial completo de una PyME (Producto → Pedido → Factura → Cobro → Inventario).

---

## 🤝 Contribuir

Este es un proyecto académico, pero las contribuciones son bienvenidas. Por favor:

1. Fork del repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Alex** - TFG 2026

- 📧 Email: [contacto]
- 🔗 LinkedIn: [perfil]
- 🐙 GitHub: [@usuario](https://github.com/usuario)

---

## 🙏 Agradecimientos

- Inspiración de diseño: [Holded](https://www.holded.com), [Linear](https://linear.app), [Notion](https://notion.so)
- Iconos: [Lucide](https://lucide.dev)
- Framework: [Vue.js](https://vuejs.org) + [Vite](https://vitejs.dev)

---

**⭐ Si te gusta el proyecto, dale una estrella en GitHub!** run dev

# Build para producción
npm run build

# Preview de producción
npm run preview
```

## 🎯 Próximas Funcionalidades

- [ ] Autenticación de usuarios
- [ ] Gestión de pedidos
- [ ] Reportes y analytics
- [ ] Exportación de datos
- [ ] Modo oscuro
- [ ] Multi-idioma
- [ ] Notificaciones en tiempo real

## 💡 Uso del Sistema de Diseño

### Ejemplo: Crear una nueva vista

```vue
<template>
  <div class="mi-vista">
    <div class="view-header">
      <h1 class="view-title">Mi Vista</h1>
      <button class="btn btn-primary">Acción</button>
    </div>

    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Título</h3>
      </div>
      <div class="card-body">
        <!-- Contenido -->
      </div>
    </div>
  </div>
</template>

<style scoped>
.mi-vista {
  max-width: 1200px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
}
</style>
```

## 🏗️ Arquitectura

### Componentes

- **App.vue**: Layout principal con sidebar navegable y header
- **Views**: Páginas individuales de la aplicación
- **Router**: Configuración de navegación SPA

### Estilos

- Variables CSS globales en `style.css`
- Scoped styles en cada componente
- Sistema de utilidades (flex, spacing, typography)

## 📱 Responsive Design

El layout se adapta automáticamente:
- **Desktop**: Sidebar expandido (240px)
- **Tablet/Mobile**: Sidebar colapsado (70px) al hacer clic en el toggle

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas de Desarrollo

### Layout Principal (App.vue)

El componente `App.vue` incluye:
- Sidebar colapsable con menú de navegación
- Submenús expandibles para Catalog y Finances
- Header superior con selector de idioma y menú de usuario
- Área de contenido principal para router-view

### Sistema de Variables CSS

Todas las variables están centralizadas en `style.css`:
- Colores (primarios, estados, fondos, textos)
- Espaciado (xs, sm, md, lg, xl)
- Tipografía (tamaños, pesos)
- Sombras y bordes
- Transiciones

### Convenciones de Código

- Componentes Vue con `<script setup>`
- Estilos scoped para componentes
- Variables CSS para valores reutilizables
- Clases de utilidad para layouts comunes

## 🙏 Agradecimientos

- Diseño inspirado en Uvodo
- Iconos: Emojis nativos
- Framework: Vue 3
- Build tool: Vite

---

**Nota:** Este es un proyecto de demostración/educativo para un sistema ERP web moderno.

# Sazed-ERP
