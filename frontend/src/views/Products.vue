<template>
  <div class="products-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Products</h1>
          <span class="count-badge">{{ products.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Export</span>
          </button>
          <button class="btn btn-primary" @click="openProductForm()">
            <Plus :size="18" />
            <span>Create product</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            type="text"
            class="input search-input"
            placeholder="Search by name, SKU, category..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="archived">Archived</option>
          </select>
          <select class="select filter-select" v-model="typeFilter">
            <option value="all">All types</option>
            <option value="product">Product</option>
            <option value="service">Service</option>
          </select>
          <select class="select filter-select" v-model="categoryFilter">
            <option value="all">All categories</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <button class="btn btn-secondary" @click="togglePublishedFilter">
            <Globe :size="18" />
            <span>{{ publishedFilter === 'all' ? 'Published' : publishedFilter === 'yes' ? 'Published' : 'Unpublished' }}</span>
          </button>
          <button class="btn btn-secondary" @click="sortProducts">
            <ArrowUpDown :size="18" />
            <span>Sort</span>
          </button>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table products-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" class="checkbox" @change="toggleSelectAll" :checked="allSelected" />
                </th>
                <th class="col-image"></th>
                <th class="col-sku">SKU</th>
                <th class="col-name">Product</th>
                <th class="col-status">Status</th>
                <th class="col-type">Type</th>
                <th class="col-category">Category</th>
                <th class="col-stock">Stock</th>
                <th class="col-price">PVP</th>
                <th class="col-cost">Cost</th>
                <th class="col-margin">Margin</th>
                <th class="col-tax">Tax</th>
                <th class="col-supplier">Supplier</th>
                <th class="col-channel">Published</th>
                <th class="col-updated">Updated</th>
                <th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in filteredProducts" :key="product.id" class="table-row" @click="openDetail(product)">
                <td class="col-checkbox" @click.stop>
                  <input type="checkbox" class="checkbox" v-model="selectedProducts" :value="product.id" />
                </td>
                <td class="col-image">
                  <div class="product-thumb">
                    <img v-if="product.image" :src="product.image" :alt="product.name" />
                    <Package v-else :size="20" class="image-placeholder-icon" />
                  </div>
                </td>
                <td class="col-sku">
                  <span class="sku-text">{{ product.sku }}</span>
                </td>
                <td class="col-name">
                  <span class="product-name">{{ product.name }}</span>
                  <span v-if="product.hasVariants" class="variants-hint">{{ product.variantsCount }} variants</span>
                </td>
                <td class="col-status">
                  <span :class="['badge', statusBadgeClass(product.status)]">
                    {{ product.status }}
                  </span>
                </td>
                <td class="col-type">
                  <div class="type-cell">
                    <component :is="product.type === 'Product' ? Package : Wrench" :size="14" class="type-icon" />
                    <span>{{ product.type }}</span>
                  </div>
                </td>
                <td class="col-category">{{ product.category }}</td>
                <td class="col-stock">
                  <div class="stock-cell">
                    <span :class="['stock-value', stockClass(product)]">{{ product.stock }}</span>
                    <span v-if="product.reserved" class="stock-reserved">{{ product.reserved }} rsv</span>
                  </div>
                </td>
                <td class="col-price">
                  <div class="price-cell">
                    <span class="price-main">{{ formatCurrency(product.price) }}</span>
                    <span v-if="product.hasVariants && product.priceFrom" class="price-from">from {{ formatCurrency(product.priceFrom) }}</span>
                  </div>
                </td>
                <td class="col-cost">
                  <span class="cost-value">{{ formatCurrency(product.cost) }}</span>
                </td>
                <td class="col-margin">
                  <span :class="['margin-value', marginClass(product)]">
                    {{ calcMargin(product) }}%
                  </span>
                </td>
                <td class="col-tax">
                  <span class="tax-tag">{{ product.tax }}</span>
                </td>
                <td class="col-supplier">
                  <span class="supplier-text">{{ product.supplier || '—' }}</span>
                </td>
                <td class="col-channel">
                  <div class="channel-badges">
                    <span
                      v-for="ch in product.channels"
                      :key="ch"
                      :class="['channel-dot', ch === 'Web' ? 'channel-web' : 'channel-marketplace']"
                      :title="ch"
                    >
                      <Globe v-if="ch === 'Web'" :size="12" />
                      <Store v-else :size="12" />
                    </span>
                    <span v-if="!product.channels.length" class="text-tertiary">—</span>
                  </div>
                </td>
                <td class="col-updated">
                  <span class="updated-text">{{ formatDate(product.updatedAt) }}</span>
                </td>
                <td class="col-actions" @click.stop>
                  <button class="btn-icon" title="Editar" @click="openProductForm(product)">
                    <Pencil :size="16" />
                  </button>
                  <button class="btn-icon" title="Eliminar" @click="deleteProduct(product)" style="color: var(--error-color);">
                    <Trash2 :size="16" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="table-footer-info">
            Showing <strong>{{ filteredProducts.length }}</strong> of <strong>{{ products.length }}</strong> products
          </span>
        </div>
      </div>
    </div>

    <!-- ===================== PRODUCT DETAIL DRAWER ===================== -->
    <ProductDetailDrawer
      v-if="selectedProduct"
      :product="selectedProduct"
      :open="detailOpen"
      @close="closeDetail"
    />

    <!-- ===================== CREATE / EDIT MODAL ===================== -->
    <ProductFormModal
      :open="formModalOpen"
      :product="formProduct"
      @close="closeProductForm"
      @save="handleProductSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Plus, Search, ArrowUpDown, Package, MoreVertical,
  Download, Globe, Store, Wrench, Pencil, Trash2
} from 'lucide-vue-next'
import ProductDetailDrawer from '@/components/ProductDetailDrawer.vue'
import ProductFormModal from '@/components/ProductFormModal.vue'
import productsApi from '@/services/products'
import { mapProductFromApi, mapProductDetailFromApi, mapProductToApi, parseDrfErrors } from '../services/mappers'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const loading = ref(false)

/* ── Load products from API ── */
async function fetchProducts() {
  loading.value = true
  try {
    const data = await productsApi.getAll()
    const items = Array.isArray(data) ? data : data.results || []
    products.value = items.map(mapProductFromApi)
  } catch (err) {
    console.error('Failed to load products:', err)
    toast.error('Error al cargar productos')
  } finally {
    loading.value = false
  }
}

onMounted(fetchProducts)

/* ── Drawer state ── */
const detailOpen = ref(false)
const selectedProduct = ref(null)

async function openDetail(product) {
  try {
    const data = await productsApi.getById(product.id)
    selectedProduct.value = mapProductDetailFromApi(data)
    detailOpen.value = true
  } catch {
    selectedProduct.value = product
    detailOpen.value = true
  }
}

function closeDetail() {
  detailOpen.value = false
}

/* ── Form modal state ── */
const formModalOpen = ref(false)
const formProduct = ref(null)

function openProductForm(product = null) {
  formProduct.value = product
  formModalOpen.value = true
}

function closeProductForm() {
  formModalOpen.value = false
  formProduct.value = null
}

async function handleProductSave(data) {
  const apiData = mapProductToApi(data)
  try {
    if (formProduct.value) {
      await productsApi.update(formProduct.value.id, apiData)
      toast.success('Producto actualizado')
    } else {
      await productsApi.create(apiData)
      toast.success('Producto creado')
    }
    await fetchProducts()
  } catch (err) {
    toast.error(parseDrfErrors(err.data) || err.message || 'Error al guardar producto')
  }
}

async function deleteProduct(product) {
  try {
    await productsApi.delete(product.id)
    products.value = products.value.filter(p => p.id !== product.id)
    toast.success('Producto eliminado')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al eliminar producto')
  }
}

/* ── Table state ── */
const searchQuery = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const categoryFilter = ref('all')
const publishedFilter = ref('all')
const selectedProducts = ref([])
const sortAsc = ref(true)

/* ── Products data (loaded from API) ── */
const products = ref([])

/* ── Computed ── */
const categories = computed(() => {
  const cats = [...new Set(products.value.map(p => p.category))]
  return cats.sort()
})

const allSelected = computed(() => {
  return filteredProducts.value.length > 0 && selectedProducts.value.length === filteredProducts.value.length
})

const filteredProducts = computed(() => {
  let result = products.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.sku.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q) ||
      (p.supplier && p.supplier.toLowerCase().includes(q))
    )
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(p => p.status.toLowerCase() === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    result = result.filter(p => p.type.toLowerCase() === typeFilter.value)
  }

  if (categoryFilter.value !== 'all') {
    result = result.filter(p => p.category === categoryFilter.value)
  }

  if (publishedFilter.value !== 'all') {
    result = result.filter(p =>
      publishedFilter.value === 'yes' ? p.channels.length > 0 : p.channels.length === 0
    )
  }

  return result
})

/* ── Actions ── */
function toggleSelectAll() {
  if (allSelected.value) {
    selectedProducts.value = []
  } else {
    selectedProducts.value = filteredProducts.value.map(p => p.id)
  }
}

function togglePublishedFilter() {
  const states = ['all', 'yes', 'no']
  const idx = states.indexOf(publishedFilter.value)
  publishedFilter.value = states[(idx + 1) % states.length]
}

function sortProducts() {
  sortAsc.value = !sortAsc.value
  products.value.sort((a, b) => {
    return sortAsc.value
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  })
}

/* ── Helpers ── */
function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning', Archived: 'badge-gray' }
  return map[status] || 'badge-gray'
}

function stockClass(product) {
  if (product.stock === null) return 'stock-service'
  if (product.stock === 0) return 'stock-out'
  if (product.stock <= 15) return 'stock-low'
  return ''
}

function calcMargin(product) {
  if (!product.price || !product.cost) return '—'
  return (((product.price - product.cost) / product.price) * 100).toFixed(1)
}

function marginClass(product) {
  const m = parseFloat(calcMargin(product))
  if (isNaN(m)) return ''
  if (m >= 50) return 'margin-high'
  if (m >= 25) return 'margin-mid'
  return 'margin-low'
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now - d
  const diffDays = Math.floor(diffMs / 86400000)
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays}d ago`
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: '2-digit' })
}
</script>

<style scoped>
.products-view {
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.count-badge {
  background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%);
  color: var(--text-secondary);
  padding: 0.375rem 0.875rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 360px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-input {
  padding-left: 3rem;
}

.filter-actions {
  display: flex;
  gap: 0.625rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  width: auto;
  min-width: 140px;
  padding: 0.5rem 0.75rem;
  font-size: var(--font-size-xs);
}

/* ============================
   TABLE LAYOUT
   ============================ */
.table-card {
  padding: 0;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.products-table {
  min-width: 1280px;
}

.products-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.products-table td {
  padding: 0.625rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.col-checkbox { width: 40px; text-align: center; }
.col-image { width: 48px; }
.col-sku { width: 90px; }
.col-name { min-width: 180px; white-space: normal !important; }
.col-status { width: 90px; }
.col-type { width: 95px; }
.col-category { width: 100px; }
.col-stock { width: 100px; }
.col-price { width: 100px; }
.col-cost { width: 80px; }
.col-margin { width: 70px; }
.col-tax { width: 80px; }
.col-supplier { width: 120px; }
.col-channel { width: 80px; }
.col-updated { width: 90px; }
.col-actions { width: 40px; }

.table-row {
  transition: background var(--transition-fast);
  cursor: pointer;
}

.table-row:hover {
  background: var(--bg-hover);
}

/* ============================
   CELL STYLES
   ============================ */
.product-thumb {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.product-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder-icon {
  color: var(--text-tertiary);
}

.sku-text {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.product-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  display: block;
  line-height: 1.3;
}

.variants-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  display: block;
  margin-top: 1px;
}

.type-cell {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.type-icon {
  color: var(--text-tertiary);
}

.stock-cell {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stock-value {
  font-weight: 500;
  font-size: var(--font-size-sm);
}

.stock-out { color: var(--error-color); font-weight: 600; }
.stock-low { color: var(--warning-color); font-weight: 600; }
.stock-service { color: var(--text-tertiary); font-style: italic; font-weight: 400; }

.stock-reserved {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.price-cell {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.price-main {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.price-from {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.cost-value {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.margin-value { font-weight: 600; font-size: var(--font-size-sm); }
.margin-high { color: var(--success-color); }
.margin-mid { color: var(--primary-color); }
.margin-low { color: var(--warning-color); }

.tax-tag {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.supplier-text {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 110px;
  display: block;
}

.channel-badges {
  display: flex;
  gap: 0.375rem;
  align-items: center;
}

.channel-dot {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.channel-web { background: var(--primary-light); color: var(--primary-color); }
.channel-marketplace { background: var(--warning-light); color: var(--warning-color); }

.updated-text {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  color: var(--text-tertiary);
  border-radius: 6px;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #f0f2f5;
  color: var(--text-primary);
}

.table-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
}

.table-footer-info {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    gap: 1rem;
  }
  .view-title {
    font-size: 1.5rem;
  }
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box {
    max-width: 100%;
  }
  .filter-actions {
    flex-wrap: wrap;
  }
  .table-card {
    border-radius: 8px;
  }
}

@media (max-width: 480px) {
  .view-title {
    font-size: 1.25rem;
  }
  .header-actions .btn span {
    display: none;
  }
  .filter-actions .btn span {
    display: none;
  }
}
</style>
