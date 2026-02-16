# Copilot Instructions — ERP Web (TFG)

## Project Overview
Vue 3 SPA ERP system built with Vite, inspired by Uvodo's design. Sidebar-based layout with dashboard, product catalog, wallet/finances, and customer management modules.

## Tech Stack & Commands
- **Framework:** Vue 3 (Composition API with `<script setup>`) + Vue Router 4
- **Build:** Vite 7 — `npm run dev` (dev server), `npm run build` (production)
- **Icons:** `lucide-vue-next` — import as Vue components, never use emojis in UI
- **Styling:** CSS Variables design system in `src/style.css`, scoped `<style scoped>` per view
- **No state management library** — local `ref()` only for now

## Architecture

### Layout Structure
- `src/App.vue` — Root layout: fixed sidebar (260px, collapsible to 72px) + sticky header + `<router-view>` content area. Navigation defined as data-driven arrays (`menuItems`, `salesChannels`) rendered with `<component :is>` for icons.
- `src/style.css` — Global design system: CSS custom properties (`:root`), reusable component classes (`.btn`, `.card`, `.table`, `.badge`, `.input`), utility classes (`.flex`, `.gap-2`, `.text-sm`).
- `src/router/index.js` — All routes defined; most use `About.vue` as placeholder (marked with `// Placeholder` comments).

### Views Pattern
Each view in `src/views/` follows this structure:
```vue
<template>
  <div class="[name]-view">
    <div class="view-header">...</div>
    <div class="content-wrapper">...</div>
  </div>
</template>
<script setup>
import { IconName } from 'lucide-vue-next'
</script>
<style scoped>...</style>
```
- **Implemented:** `Home.vue`, `Products.vue`, `Wallet.vue`
- **Placeholder:** Collections, Inventory, Orders, Card, Payout, Customers, Marketing, OnlineStore, SellLink, Settings (all route to `About.vue`)

## Key Conventions

### Icons
Always use `lucide-vue-next` components. Import individually, pass `:size` prop:
```vue
import { Package, Wallet, Users } from 'lucide-vue-next'
<Package :size="20" />
```

### CSS Design Tokens
Use variables from `src/style.css` — never hardcode colors/spacing in views:
- Colors: `--primary-color` (#667eea), `--text-primary`, `--text-secondary`, `--border-color`
- Spacing: `--spacing-sm` through `--spacing-xl`
- Gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)` (primary brand gradient)
- Radius: `--border-radius` (12px), `--border-radius-sm` (8px)

### Component Classes
Use global `.btn`, `.btn-primary`, `.btn-secondary`, `.card`, `.card-header`, `.table`, `.badge-*`, `.input` classes from `style.css`. View-specific styles go in `<style scoped>`.

### Adding a New View
1. Create `src/views/NewView.vue` following the view pattern above
2. Update the placeholder route in `src/router/index.js` to lazy-import it
3. The sidebar navigation in `App.vue` is data-driven — add entries to `menuItems` or `salesChannels` arrays if needed

## Current State & Known Issues
- Many routes are placeholders pointing to `About.vue` — check `// Placeholder` comments in router
- `About.vue` still uses emoji icons instead of Lucide (not yet migrated)
- `src/style.css` has a broken `.input` rule (`padding: 0.625rem #e8eaed` — missing border shorthand) and duplicate `.card`/`#app` rules at the bottom that conflict with the ERP layout
- No backend/API — all data is hardcoded in component `<script setup>` blocks
- No tests configured
