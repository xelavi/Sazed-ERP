# 🏗️ Arquitectura del Sistema - Sazed ERP

Documentación técnica de la arquitectura del sistema, flujos de datos y patrones de diseño.

---

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vue 3)                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │ Components │  │   Views    │  │   Router   │  │   Stores   ││
│  │ (Reusable) │  │  (Pages)   │  │ (Vue Router│  │  (Pinia)   ││
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘│
│         │               │                │               │       │
│         └───────────────┴────────────────┴───────────────┘       │
│                              │                                   │
│                    ┌─────────▼──────────┐                       │
│                    │   Composables      │                       │
│                    │  (Business Logic)  │                       │
│                    └─────────┬──────────┘                       │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   API Layer          │ ← Futuro: Supabase Client
                    │  (Supabase/REST)     │
                    └──────────┬───────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                     BACKEND (Supabase)                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │ PostgreSQL │  │    Auth    │  │  Storage   │  │  Realtime  ││
│  │    (DB)    │  │  (Users)   │  │  (Files)   │  │   (Live)   ││
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura de Directorios

```
src/
├── assets/                    # Recursos estáticos (imágenes, fuentes)
├── components/                # Componentes reutilizables
│   ├── common/                # Componentes genéricos (futuro)
│   │   ├── DataTable.vue
│   │   ├── FormModal.vue
│   │   ├── StatusBadge.vue
│   │   └── ConfirmDialog.vue
│   ├── ProductFormModal.vue   # Modal de productos
│   ├── ProductDetailDrawer.vue
│   └── ...                    # Otros componentes de módulos
├── composables/               # Lógica reutilizable (futuro)
│   ├── useFilters.js
│   ├── usePagination.js
│   ├── useApi.js
│   └── useToast.js
├── router/                    # Configuración de rutas
│   └── index.js
├── stores/                    # Estado global Pinia (futuro)
│   ├── auth.js
│   ├── settings.js
│   └── notifications.js
├── utils/                     # Funciones utilidad (futuro)
│   ├── formatters.js          # Formato de fechas, moneda, etc.
│   ├── validators.js          # Validaciones custom
│   └── constants.js           # Constantes globales
├── views/                     # Vistas/Páginas
│   ├── Home.vue               # Dashboard
│   ├── Products.vue           # Catálogo de productos
│   ├── Customers.vue          # CRM
│   ├── Orders.vue             # Pedidos (en desarrollo)
│   ├── Invoices.vue           # Facturación
│   ├── Inventory.vue          # Inventario (en desarrollo)
│   ├── Wallet.vue             # Tesorería
│   ├── Settings.vue           # Configuración (en desarrollo)
│   └── About.vue              # Placeholder
├── App.vue                    # Componente raíz (layout)
├── main.js                    # Punto de entrada
└── style.css                  # Sistema de diseño global
```

---

## 🔄 Flujos de Datos

### Flujo Comercial Completo

```
1. PRODUCTO
   ┌─────────────┐
   │  Product    │
   │  Catalog    │
   └──────┬──────┘
          │
          ├─→ Add to Order
          │
2. PEDIDO v
   ┌─────────────┐
   │   Order     │
   │  (Draft)    │
   └──────┬──────┘
          │
          ├─→ Confirm Order
          │
          ├─→ Complete Order
          │     ├─→ Update Inventory (Stock -n)
          │     └─→ Create Stock Movement (OUT)
          │
          ├─→ Convert to Invoice
          │
3. FACTURA v
   ┌─────────────┐
   │  Invoice    │
   │ (Approved)  │
   └──────┬──────┘
          │
          ├─→ Register Payment
          │
4. PAGO   v
   ┌─────────────┐
   │   Payment   │
   │  Received   │
   └──────┬──────┘
          │
          └─→ Update Wallet Balance
```

### Flujo de Inventario

```
┌─────────────────────────────────────────────────────────┐
│                    INVENTORY SYSTEM                      │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        v                  v                  v
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│  STOCK IN     │  │  STOCK OUT    │  │  ADJUSTMENT   │
│  (Purchase)   │  │  (Sale)       │  │  (Manual)     │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           v
                  ┌────────────────┐
                  │ Stock Movement │
                  │   (History)    │
                  └────────┬───────┘
                           │
                           v
                  ┌────────────────┐
                  │ Update Product │
                  │     Stock      │
                  └────────────────┘
```

---

## 🗃️ Modelo de Datos

### Entidades Principales

#### 1. Products
```javascript
{
  id: 'prod_001',
  name: 'Laptop HP',
  sku: 'LAP-HP-001',
  description: 'Laptop HP 15"...',
  category: 'Electronics',
  price: 799.99,
  cost: 600.00,
  taxRate: 21,
  unit: 'unit',
  status: 'active',
  image: 'https://...',
  tags: ['electronics', 'computers'],
  customFields: {},
  createdAt: '2026-01-15T10:00:00Z',
  updatedAt: '2026-02-10T14:30:00Z'
}
```

#### 2. Customers
```javascript
{
  id: 'cust_001',
  type: 'company' | 'person',
  name: 'Acme Corp',
  taxId: 'B12345678',
  email: 'contact@acme.com',
  phone: '+34 600 000 000',
  address: {
    street: 'Calle Mayor 1',
    city: 'Madrid',
    postalCode: '28001',
    country: 'ES'
  },
  tags: ['vip', 'tech'],
  totalInvoiced: 15000.00,
  pendingBalance: 2500.00,
  lastPurchase: '2026-02-15',
  status: 'active',
  notes: 'Cliente preferente',
  createdAt: '2025-06-10T09:00:00Z',
  updatedAt: '2026-02-15T16:45:00Z'
}
```

#### 3. Orders
```javascript
{
  id: 'ord_001',
  number: 'ORD-2026-0001',
  customerId: 'cust_001',
  customerName: 'Acme Corp',
  status: 'draft' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled',
  orderDate: '2026-02-15',
  deliveryDate: '2026-02-20',
  lines: [
    {
      id: 'line_001',
      productId: 'prod_001',
      productName: 'Laptop HP',
      quantity: 5,
      unitPrice: 799.99,
      discount: 0,
      taxRate: 21,
      subtotal: 3999.95,
      total: 4839.94
    }
  ],
  subtotal: 3999.95,
  taxAmount: 839.99,
  total: 4839.94,
  notes: 'Entrega urgente',
  invoiceId: null,  // Null si no convertido aún
  createdAt: '2026-02-15T10:00:00Z',
  updatedAt: '2026-02-15T10:00:00Z'
}
```

#### 4. Invoices
```javascript
{
  id: 'inv_001',
  number: 'FAC-2026-0042',
  series: 'FAC',
  customerId: 'cust_001',
  customerName: 'Acme Corp',
  customerTaxId: 'B12345678',
  customerAddress: {...},
  status: 'draft' | 'approved' | 'partially_paid' | 'paid' | 'overdue' | 'voided',
  issueDate: '2026-02-15',
  dueDate: '2026-03-15',
  lines: [...],  // Similar a Orders
  subtotal: 3999.95,
  taxAmount: 839.99,
  total: 4839.94,
  paidAmount: 0,
  pendingAmount: 4839.94,
  orderId: 'ord_001',  // Pedido origen
  paymentMethod: 'bank_transfer',
  notes: '',
  legalNotices: 'IVA incluido...',
  createdAt: '2026-02-15T11:00:00Z',
  updatedAt: '2026-02-15T11:00:00Z'
}
```

#### 5. InventoryItems
```javascript
{
  id: 'inv_item_001',
  productId: 'prod_001',
  productName: 'Laptop HP',
  sku: 'LAP-HP-001',
  currentStock: 25,
  minStock: 10,
  maxStock: 100,
  unitCost: 600.00,
  totalValue: 15000.00,  // currentStock × unitCost
  status: 'in_stock' | 'low_stock' | 'out_of_stock',
  lastMovement: '2026-02-15T10:00:00Z',
  updatedAt: '2026-02-15T10:00:00Z'
}
```

#### 6. StockMovements
```javascript
{
  id: 'mov_001',
  productId: 'prod_001',
  productName: 'Laptop HP',
  type: 'in' | 'out' | 'adjustment',
  reason: 'purchase' | 'sale' | 'return' | 'loss' | 'adjustment',
  quantity: 5,  // Positivo para IN, negativo para OUT
  previousStock: 20,
  newStock: 25,
  unitCost: 600.00,
  totalValue: 3000.00,
  reference: 'ord_001',  // ID relacionado (pedido, factura, etc.)
  referenceType: 'order',
  notes: 'Recepción mercancía proveedor X',
  createdBy: 'user_001',
  createdAt: '2026-02-15T10:00:00Z'
}
```

#### 7. Settings (Global)
```javascript
{
  id: 'settings_001',
  companyId: 'company_001',
  company: {
    name: 'Mi Empresa SL',
    taxId: 'B87654321',
    address: {...},
    logo: 'https://...',
    ...
  },
  invoiceSeries: [
    {
      id: 'series_001',
      prefix: 'FAC',
      nextNumber: 43,
      format: '{prefix}-{year}-{number:4}',
      resetYearly: true,
      isDefault: true
    }
  ],
  taxRates: [
    {
      id: 'tax_001',
      name: 'IVA General',
      type: 'vat',
      rate: 21,
      isDefault: true
    }
  ],
  paymentMethods: [
    {
      id: 'pm_001',
      name: 'Transferencia bancaria',
      type: 'bank_transfer',
      instructions: 'IBAN: ES00...',
      isActive: true
    }
  ],
  preferences: {
    currency: 'EUR',
    dateFormat: 'dd/mm/yyyy',
    locale: 'es-ES',
    timezone: 'Europe/Madrid'
  },
  updatedAt: '2026-02-15T10:00:00Z'
}
```

---

## 🔗 Relaciones entre Entidades

```
┌─────────────┐
│  Products   │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       v                 v
┌─────────────┐   ┌─────────────┐
│   Orders    │   │  Inventory  │
│   Lines     │   │    Items    │
└──────┬──────┘   └──────┬──────┘
       │                 │
       │                 v
       │          ┌─────────────┐
       │          │   Stock     │
       │          │ Movements   │
       │          └─────────────┘
       v
┌─────────────┐
│  Invoices   │
│   Lines     │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Payments   │
└──────┬──────┘
       │
       v
┌─────────────┐
│   Wallet    │
│Transactions │
└─────────────┘


┌─────────────┐
│  Customers  │
└──────┬──────┘
       │
       ├─────────────────┐
       v                 v
┌─────────────┐   ┌─────────────┐
│   Orders    │   │  Invoices   │
└─────────────┘   └─────────────┘
```

---

## 🎨 Patrones de Diseño

### 1. Component Pattern (Smart vs. Dumb)

#### Smart Components (Views)
- Conocen el estado global
- Manejan lógica de negocio
- Llaman APIs
- Coordinan componentes dumb

```vue
<!-- src/views/Products.vue -->
<script setup>
import { ref, computed } from 'vue'
import ProductFormModal from '@/components/ProductFormModal.vue'

const products = ref([...])  // Estado local
const searchQuery = ref('')

const filteredProducts = computed(() => {
  return products.value.filter(p => 
    p.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

function createProduct(data) {
  // Lógica de negocio
}
</script>
```

#### Dumb Components (Components)
- Solo reciben props
- Emiten eventos
- No conocen estado global
- Altamente reutilizables

```vue
<!-- src/components/StatusBadge.vue -->
<script setup>
defineProps({
  status: String,
  variant: String
})
</script>
```

---

### 2. Composables Pattern (Reusability)

```javascript
// src/composables/useFilters.js
export function useFilters(items, config) {
  const searchQuery = ref('')
  const filters = reactive({ ... })

  const filteredItems = computed(() => {
    let result = items.value
    
    // Búsqueda
    if (searchQuery.value) {
      result = result.filter(...)
    }
    
    // Filtros
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== 'all') {
        result = result.filter(...)
      }
    })
    
    return result
  })

  function clearFilters() {
    searchQuery.value = ''
    Object.keys(filters).forEach(k => filters[k] = 'all')
  }

  return {
    searchQuery,
    filters,
    filteredItems,
    clearFilters
  }
}
```

Uso:
```vue
<script setup>
import { useFilters } from '@/composables/useFilters'

const products = ref([...])
const { searchQuery, filters, filteredItems, clearFilters } = useFilters(products, {
  status: ['active', 'inactive'],
  category: ['electronics', 'clothing']
})
</script>
```

---

### 3. Store Pattern (Global State)

```javascript
// src/stores/auth.js
import { defineStore } from 'pinia'
import { supabase } from '@/lib/supabase'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    session: null,
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    userRole: (state) => state.user?.role || 'user'
  },

  actions: {
    async login(email, password) {
      this.loading = true
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password
        })
        if (error) throw error
        
        this.user = data.user
        this.session = data.session
      } catch (error) {
        console.error('Login error:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      await supabase.auth.signOut()
      this.user = null
      this.session = null
    }
  }
})
```

---

## 🔐 Seguridad & Autenticación (Futuro)

### Row Level Security (RLS) en Supabase

```sql
-- Tabla: products
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Política: Users solo ven productos de su empresa
CREATE POLICY "Users can view own company products"
  ON products FOR SELECT
  USING (company_id = auth.jwt() ->> 'company_id');

-- Política: Solo admin puede crear productos
CREATE POLICY "Only admin can create products"
  ON products FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM users
      WHERE users.id = auth.uid()
      AND users.role IN ('admin', 'owner')
    )
  );
```

### Middleware de Rutas

```javascript
// src/router/index.js
import { useAuthStore } from '@/stores/auth'

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Rutas públicas
  if (to.meta.public) {
    return next()
  }

  // Verificar autenticación
  if (!authStore.isAuthenticated) {
    return next('/login')
  }

  // Verificar rol
  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    return next('/unauthorized')
  }

  next()
})
```

---

## 📡 API Layer (Futuro con Supabase)

### Composable API Genérico

```javascript
// src/composables/useApi.js
import { ref } from 'vue'
import { supabase } from '@/lib/supabase'

export function useApi(table) {
  const data = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchAll(filters = {}) {
    loading.value = true
    error.value = null
    
    try {
      let query = supabase.from(table).select('*')
      
      // Aplicar filtros
      Object.entries(filters).forEach(([key, value]) => {
        if (value) query = query.eq(key, value)
      })
      
      const { data: result, error: err } = await query
      if (err) throw err
      
      data.value = result
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function create(item) {
    loading.value = true
    error.value = null
    
    try {
      const { data: result, error: err } = await supabase
        .from(table)
        .insert(item)
        .select()
        .single()
      
      if (err) throw err
      
      data.value.push(result)
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function update(id, updates) {
    loading.value = true
    error.value = null
    
    try {
      const { data: result, error: err } = await supabase
        .from(table)
        .update(updates)
        .eq('id', id)
        .select()
        .single()
      
      if (err) throw err
      
      const index = data.value.findIndex(item => item.id === id)
      if (index !== -1) data.value[index] = result
      
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function remove(id) {
    loading.value = true
    error.value = null
    
    try {
      const { error: err } = await supabase
        .from(table)
        .delete()
        .eq('id', id)
      
      if (err) throw err
      
      data.value = data.value.filter(item => item.id !== id)
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    fetchAll,
    create,
    update,
    remove
  }
}
```

Uso:
```vue
<script setup>
import { useApi } from '@/composables/useApi'

const { data: products, loading, fetchAll, create, update, remove } = useApi('products')

// Cargar todos los productos
await fetchAll()

// Crear producto
await create({ name: 'New Product', price: 99.99 })

// Actualizar producto
await update('prod_001', { price: 89.99 })

// Eliminar producto
await remove('prod_001')
</script>
```

---

## 🧪 Testing Strategy

### 1. Unit Tests (Vitest)
```javascript
// src/utils/formatters.test.js
import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate } from './formatters'

describe('formatCurrency', () => {
  it('formats number to EUR currency', () => {
    expect(formatCurrency(1234.56)).toBe('1.234,56 €')
  })

  it('handles zero', () => {
    expect(formatCurrency(0)).toBe('0,00 €')
  })

  it('handles negative numbers', () => {
    expect(formatCurrency(-100)).toBe('-100,00 €')
  })
})
```

### 2. Component Tests (Vitest + @vue/test-utils)
```javascript
// src/components/StatusBadge.test.js
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import StatusBadge from './StatusBadge.vue'

describe('StatusBadge', () => {
  it('renders correct class for status', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'paid', variant: 'success' }
    })
    
    expect(wrapper.classes()).toContain('badge-success')
    expect(wrapper.text()).toBe('Paid')
  })
})
```

### 3. E2E Tests (Playwright)
```javascript
// tests/e2e/orders-flow.spec.js
import { test, expect } from '@playwright/test'

test('complete order creation flow', async ({ page }) => {
  // Login
  await page.goto('http://localhost:5173/login')
  await page.fill('[name="email"]', 'demo@sazed.com')
  await page.fill('[name="password"]', 'demo1234')
  await page.click('button[type="submit"]')

  // Navigate to Orders
  await page.click('a[href="/orders"]')
  await expect(page).toHaveURL(/.*orders/)

  // Create new order
  await page.click('text=New order')
  await page.selectOption('[name="customer"]', 'cust_001')
  await page.click('text=Add product')
  await page.selectOption('[name="product"]', 'prod_001')
  await page.fill('[name="quantity"]', '5')
  await page.click('button:has-text("Save")')

  // Verify creation
  await expect(page.locator('text=Order created')).toBeVisible()
})
```

---

## 🚀 Build & Deploy

### Build Optimization

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'lucide': ['lucide-vue-next'],
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

### Vercel Deployment

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## 📊 Performance Targets

| Métrica | Target | Actual | Status |
|---------|--------|--------|--------|
| First Contentful Paint | < 1.5s | ? | ⚪ |
| Largest Contentful Paint | < 2.5s | ? | ⚪ |
| Time to Interactive | < 3.5s | ? | ⚪ |
| Cumulative Layout Shift | < 0.1 | ? | ⚪ |
| Lighthouse Score | > 90 | ? | ⚪ |
| Bundle Size (gzip) | < 200KB | ? | ⚪ |

---

**Última actualización:** 17 de febrero de 2026  
**Versión:** 1.0
