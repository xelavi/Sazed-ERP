# ERP Web - Sistema de Gestión Empresarial

Un sistema ERP web moderno, sencillo e intuitivo construido con Vue 3 y Vite, inspirado en el diseño de Uvodo.

![Vue 3](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vue.js)
![Vite](https://img.shields.io/badge/Vite-Latest-646CFF?logo=vite)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🌟 Características

- ✅ **Gestión de Productos** - Catálogo completo con búsqueda y filtros
- 💰 **Sistema de Wallet** - Control de pagos y balance
- 👥 **Gestión de Clientes** - CRM integrado
- 📊 **Dashboard Intuitivo** - Vista general del negocio
- 📦 **Control de Inventario** - Seguimiento de stock
- 🎨 **Diseño Moderno** - UI/UX inspirado en las mejores prácticas
- 📱 **Responsive** - Funciona en todos los dispositivos

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

| Ruta | Componente | Descripción |
|------|-----------|-------------|
| `/` | Home | Dashboard principal con pasos de configuración |
| `/products` | Products | Listado de productos con búsqueda |
| `/wallet` | Wallet | Sistema de pagos y balance |
| `/customers` | - | Gestión de clientes (placeholder) |
| `/settings` | - | Configuración (placeholder) |

## 🛠️ Scripts Disponibles

```bash
# Desarrollo
npm run dev

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
