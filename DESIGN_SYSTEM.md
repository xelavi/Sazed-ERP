# Sistema de Diseño ERP - Guía de Estilos

Este documento describe todos los estilos, componentes y utilidades disponibles en el sistema de diseño del ERP.

## 📋 Tabla de Contenidos
1. [Variables CSS](#variables-css)
2. [Componentes Reutilizables](#componentes-reutilizables)
3. [Utilidades](#utilidades)
4. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Variables CSS

### Colores Primarios
```css
--primary-color: #6366f1      /* Color principal (morado) */
--primary-dark: #4f46e5       /* Versión oscura */
--primary-light: #eef2ff      /* Versión clara para fondos */
```

### Colores de Fondo
```css
--bg-primary: #f9fafb         /* Fondo principal de la aplicación */
--bg-secondary: #f3f4f6       /* Fondo secundario */
--bg-hover: #f3f4f6           /* Estado hover */
--bg-dark: #1f2937            /* Fondo oscuro (footer sidebar) */
--sidebar-bg: #ffffff         /* Fondo del sidebar */
```

### Colores de Texto
```css
--text-primary: #111827       /* Texto principal */
--text-secondary: #6b7280     /* Texto secundario */
--text-tertiary: #9ca3af      /* Texto terciario */
```

### Estados
```css
--success-color: #10b981
--success-light: #d1fae5
--warning-color: #f59e0b
--warning-light: #fef3c7
--error-color: #ef4444
--error-light: #fee2e2
--info-color: #3b82f6
--info-light: #dbeafe
```

---

## Componentes Reutilizables

### Botones

#### Botón Primario
```html
<button class="btn btn-primary">
  <span>➕</span>
  Crear Producto
</button>
```

#### Botón Secundario
```html
<button class="btn btn-secondary">
  Acción Secundaria
</button>
```

#### Botón Ghost
```html
<button class="btn btn-ghost">
  Acción Sutil
</button>
```

#### Tamaños
```html
<button class="btn btn-primary btn-sm">Pequeño</button>
<button class="btn btn-primary">Normal</button>
<button class="btn btn-primary btn-lg">Grande</button>
```

### Tarjetas (Cards)

#### Tarjeta Básica
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Título de la Tarjeta</h3>
    <p class="card-subtitle">Subtítulo opcional</p>
  </div>
  <div class="card-body">
    <!-- Contenido -->
  </div>
  <div class="card-footer">
    <!-- Pie de tarjeta -->
  </div>
</div>
```

### Inputs

#### Input de Texto
```html
<input type="text" class="input" placeholder="Buscar..." />
```

#### Select
```html
<select class="select">
  <option>Opción 1</option>
  <option>Opción 2</option>
</select>
```

#### Checkbox
```html
<input type="checkbox" class="checkbox" />
```

### Badges

```html
<span class="badge badge-primary">Primario</span>
<span class="badge badge-success">Éxito</span>
<span class="badge badge-warning">Advertencia</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-gray">Neutral</span>
```

### Tablas

```html
<table class="table">
  <thead>
    <tr>
      <th>Columna 1</th>
      <th>Columna 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Dato 1</td>
      <td>Dato 2</td>
    </tr>
  </tbody>
</table>
```

---

## Utilidades

### Espaciado

#### Márgenes
```html
<div class="mt-1">Margen superior pequeño</div>
<div class="mt-2">Margen superior mediano</div>
<div class="mt-3">Margen superior grande</div>
<div class="mb-1">Margen inferior pequeño</div>
<div class="mb-2">Margen inferior mediano</div>
<div class="mb-3">Margen inferior grande</div>
```

#### Padding
```html
<div class="p-1">Padding pequeño</div>
<div class="p-2">Padding mediano</div>
<div class="p-3">Padding grande</div>
```

### Layout

#### Flexbox
```html
<div class="flex items-center justify-between gap-2">
  <span>Item 1</span>
  <span>Item 2</span>
</div>

<div class="flex flex-col gap-3">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### Tipografía

#### Tamaños
```html
<p class="text-xs">Texto extra pequeño</p>
<p class="text-sm">Texto pequeño</p>
<p class="text-base">Texto base</p>
<p class="text-lg">Texto grande</p>
<p class="text-xl">Texto extra grande</p>
```

#### Colores
```html
<p class="text-primary">Texto principal</p>
<p class="text-secondary">Texto secundario</p>
<p class="text-tertiary">Texto terciario</p>
```

#### Peso
```html
<p class="font-medium">Medio</p>
<p class="font-semibold">Semi-negrita</p>
<p class="font-bold">Negrita</p>
```

#### Alineación
```html
<p class="text-center">Centrado</p>
<p class="text-right">Derecha</p>
```

---

## Ejemplos de Uso

### Vista con Header y Filtros

```vue
<template>
  <div class="view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-content">
        <h1 class="view-title">
          Productos <span class="count">{{ products.length }}</span>
        </h1>
        <button class="btn btn-primary">
          <span>➕</span>
          Crear Producto
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" class="input search-input" placeholder="Buscar..." />
      </div>
      <button class="btn btn-secondary">Filtrar</button>
    </div>

    <!-- Contenido -->
    <div class="card">
      <!-- Tu contenido aquí -->
    </div>
  </div>
</template>

<style scoped>
.view {
  max-width: 1400px;
}

.view-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-input {
  padding-left: 2.75rem;
}
</style>
```

### Card con Estado Vacío

```vue
<template>
  <div class="card">
    <div class="card-header">
      <h3 class="card-title">Pagos Recientes</h3>
    </div>
    <div class="empty-state">
      <div class="empty-icon">💸</div>
      <h4 class="empty-title">No hay pagos recientes</h4>
      <p class="empty-text">Actualmente no hay pagos registrados.</p>
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-text {
  color: var(--text-secondary);
  font-size: 0.9375rem;
}
</style>
```

### Banner Informativo

```vue
<template>
  <div class="info-banner">
    <div class="banner-icon">💡</div>
    <div class="banner-content">
      <h3 class="banner-title">¡Comienza tus ventas!</h3>
      <p class="banner-text">
        Agrega productos o crea enlaces de pago para empezar.
      </p>
      <a href="#" class="banner-link">Ver más →</a>
    </div>
  </div>
</template>

<style scoped>
.info-banner {
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: 1.5rem;
  display: flex;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.banner-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.banner-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.banner-text {
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

.banner-link {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
}
</style>
```

---

## 🎨 Paleta de Colores Visual

- **Primario:** ![#6366f1](https://via.placeholder.com/15/6366f1/000000?text=+) `#6366f1`
- **Éxito:** ![#10b981](https://via.placeholder.com/15/10b981/000000?text=+) `#10b981`
- **Advertencia:** ![#f59e0b](https://via.placeholder.com/15/f59e0b/000000?text=+) `#f59e0b`
- **Error:** ![#ef4444](https://via.placeholder.com/15/ef4444/000000?text=+) `#ef4444`
- **Info:** ![#3b82f6](https://via.placeholder.com/15/3b82f6/000000?text=+) `#3b82f6`

---

## 📐 Espaciado Sistema

- **xs:** 0.25rem (4px)
- **sm:** 0.5rem (8px)
- **md:** 1rem (16px)
- **lg:** 1.5rem (24px)
- **xl:** 2rem (32px)

---

## 📱 Responsive Design

El sistema está diseñado para ser responsive. Usa las siguientes prácticas:

```css
/* Grid responsive */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

/* Media queries comunes */
@media (max-width: 768px) {
  .sidebar {
    width: 70px;
  }
}
```

---

## 💡 Mejores Prácticas

1. **Usa variables CSS** en lugar de colores hardcodeados
2. **Usa clases de utilidad** para espaciado y layout simple
3. **Crea componentes scoped** para estilos específicos
4. **Mantén consistencia** con el sistema de diseño
5. **Usa transiciones** para mejorar la experiencia: `transition: all var(--transition-base)`

---

## 🔧 Personalización

Para personalizar el tema, modifica las variables CSS en `style.css`:

```css
:root {
  --primary-color: #tu-color;
  /* ... otras variables */
}
```
