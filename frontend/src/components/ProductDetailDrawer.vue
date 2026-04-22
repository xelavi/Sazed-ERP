<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel">
          <!-- Drawer Header -->
          <div class="drawer-header">
            <div class="drawer-header-left">
              <div class="drawer-thumb">
                <img v-if="product.image" :src="product.image" :alt="product.name" />
                <Package v-else :size="28" class="image-placeholder-icon" />
              </div>
              <div>
                <h2 class="drawer-title">{{ product.name }}</h2>
                <div class="drawer-meta">
                  <span class="sku-text">{{ product.sku }}</span>
                  <span :class="['badge', statusBadgeClass(product.status)]">{{ product.status }}</span>
                </div>
              </div>
            </div>
            <div class="drawer-header-right">
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">
                <X :size="16" />
              </button>
            </div>
          </div>

          <!-- Tabs -->
          <nav class="drawer-tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              :class="['drawer-tab', { active: activeTab === tab.key }]"
              @click="activeTab = tab.key"
            >
              <component :is="tab.icon" :size="15" />
              <span>{{ tab.label }}</span>
            </button>
          </nav>

          <!-- Tab Content -->
          <div class="drawer-body">

            <!-- ========== A) GENERAL ========== -->
            <div v-if="activeTab === 'general'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><FileText :size="16" /> General Information</h3>
                <div class="detail-grid">
                  <div class="detail-field">
                    <label>Name</label>
                    <span>{{ product.name }}</span>
                  </div>
                  <div class="detail-field">
                    <label>SKU / Reference</label>
                    <span class="sku-text">{{ product.sku }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Type</label>
                    <div class="type-cell">
                      <component :is="product.type === 'Product' ? Package : Wrench" :size="14" />
                      <span>{{ product.type }}</span>
                    </div>
                  </div>
                  <div class="detail-field">
                    <label>Status</label>
                    <span :class="['badge', statusBadgeClass(product.status)]">{{ product.status }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Category</label>
                    <span>{{ product.category }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Tags</label>
                    <div class="tags-list">
                      <span v-for="tag in product.detail.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                    </div>
                  </div>
                  <div class="detail-field">
                    <label>Unit</label>
                    <span>{{ product.detail.unit }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Sellable / Purchasable</label>
                    <span>
                      <span :class="product.detail.sellable ? 'flag-yes' : 'flag-no'">{{ product.detail.sellable ? 'Sellable' : 'Not sellable' }}</span>
                      &nbsp;/&nbsp;
                      <span :class="product.detail.purchasable ? 'flag-yes' : 'flag-no'">{{ product.detail.purchasable ? 'Purchasable' : 'Not purchasable' }}</span>
                    </span>
                  </div>
                  <div class="detail-field">
                    <label>Brand</label>
                    <span>{{ product.detail.brand || '—' }}</span>
                  </div>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><FileText :size="16" /> Description</h3>
                <p class="description-text">{{ product.detail.description }}</p>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><ImageIcon :size="16" /> Images / Gallery</h3>
                <div class="gallery-grid">
                  <div v-for="(img, i) in product.detail.gallery" :key="i" class="gallery-item">
                    <ImageIcon :size="28" class="gallery-placeholder" />
                    <span class="gallery-label">{{ img }}</span>
                  </div>
                  <div v-if="!product.detail.gallery.length" class="empty-state-sm">
                    <ImageIcon :size="20" />
                    <span>No images uploaded</span>
                  </div>
                </div>
              </section>
            </div>

            <!-- ========== B) PRICES & TAXES ========== -->
            <div v-if="activeTab === 'prices'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><Receipt :size="16" /> Prices &amp; Taxes</h3>
                <div class="detail-grid">
                  <div class="detail-field">
                    <label>Sale Price (PVP)</label>
                    <span class="value-highlight">{{ formatCurrency(product.price) }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Price excl. tax</label>
                    <span>{{ formatCurrency(product.detail.priceExclTax) }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Purchase / Cost Price</label>
                    <span>{{ formatCurrency(product.cost) }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Tax (VAT)</label>
                    <span class="tax-tag">{{ product.tax }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Margin</label>
                    <span :class="['margin-value', marginClass(product)]">{{ calcMargin(product) }}%</span>
                  </div>
                  <div class="detail-field">
                    <label>Currency</label>
                    <span>{{ product.detail.currency }}</span>
                  </div>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><List :size="16" /> Price Lists</h3>
                <table class="mini-table">
                  <thead>
                    <tr>
                      <th>Price List</th>
                      <th>Price</th>
                      <th>Valid From</th>
                      <th>Valid To</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="pl in product.detail.priceLists" :key="pl.name">
                      <td>{{ pl.name }}</td>
                      <td class="font-semibold">{{ formatCurrency(pl.price) }}</td>
                      <td>{{ pl.from }}</td>
                      <td>{{ pl.to || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </section>
            </div>

            <!-- ========== C) INVENTORY ========== -->
            <div v-if="activeTab === 'inventory'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><Warehouse :size="16" /> Stock Overview</h3>
                <div class="stat-cards">
                  <div class="stat-card">
                    <span class="stat-label">Current Stock</span>
                    <span class="stat-value">{{ product.stock ?? '—' }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Reserved</span>
                    <span class="stat-value">{{ product.reserved ?? 0 }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Available</span>
                    <span class="stat-value stat-available">{{ product.stock != null ? product.stock - (product.reserved || 0) : '—' }}</span>
                  </div>
                  <div class="stat-card">
                    <span class="stat-label">Min. Stock</span>
                    <span class="stat-value">{{ product.detail.minStock ?? '—' }}</span>
                  </div>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><MapPin :size="16" /> Warehouse &amp; Location</h3>
                <div class="detail-grid">
                  <div class="detail-field">
                    <label>Warehouse</label>
                    <span>{{ product.detail.warehouse }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Location (Aisle/Shelf)</label>
                    <span>{{ product.detail.location || '—' }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Reorder Point</label>
                    <span>{{ product.detail.reorderPoint ?? '—' }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Lot / Serial Tracking</label>
                    <span :class="product.detail.lotTracking ? 'flag-yes' : 'flag-no'">{{ product.detail.lotTracking ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><History :size="16" /> Stock Movements</h3>
                <table class="mini-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Document</th>
                      <th>Qty</th>
                      <th>User</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(mov, i) in product.detail.stockMovements" :key="i">
                      <td>{{ mov.date }}</td>
                      <td>
                        <span :class="['badge', mov.type === 'In' ? 'badge-success' : mov.type === 'Out' ? 'badge-error' : 'badge-gray']">{{ mov.type }}</span>
                      </td>
                      <td>{{ mov.document }}</td>
                      <td :class="mov.qty > 0 ? 'text-success' : 'text-error'" class="font-semibold">{{ mov.qty > 0 ? '+' : '' }}{{ mov.qty }}</td>
                      <td>{{ mov.user }}</td>
                    </tr>
                  </tbody>
                </table>
              </section>
            </div>

            <!-- ========== D) VARIANTS ========== -->
            <div v-if="activeTab === 'variants'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><Layers :size="16" /> Attributes</h3>
                <div v-if="product.detail.attributes.length" class="attributes-list">
                  <div v-for="attr in product.detail.attributes" :key="attr.name" class="attribute-row">
                    <span class="attr-name">{{ attr.name }}</span>
                    <div class="attr-values">
                      <span v-for="v in attr.values" :key="v" class="attr-chip">{{ v }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state-sm">
                  <Layers :size="20" />
                  <span>No variants configured</span>
                </div>
              </section>

              <section v-if="product.detail.variants.length" class="detail-section">
                <h3 class="section-title"><Grid3x3 :size="16" /> Variant List</h3>
                <table class="mini-table">
                  <thead>
                    <tr>
                      <th>Variant</th>
                      <th>SKU</th>
                      <th>Price</th>
                      <th>Stock</th>
                      <th>EAN</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="v in product.detail.variants" :key="v.sku">
                      <td class="font-medium">{{ v.name }}</td>
                      <td><span class="sku-text">{{ v.sku }}</span></td>
                      <td>{{ formatCurrency(v.price) }}</td>
                      <td>{{ v.stock }}</td>
                      <td class="text-secondary">{{ v.ean || '—' }}</td>
                    </tr>
                  </tbody>
                </table>
              </section>
            </div>

            <!-- ========== E) PURCHASES / SUPPLIERS ========== -->
            <div v-if="activeTab === 'purchases'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><Truck :size="16" /> Suppliers</h3>
                <table v-if="product.detail.suppliers.length" class="mini-table">
                  <thead>
                    <tr>
                      <th>Supplier</th>
                      <th>Supplier SKU</th>
                      <th>Price</th>
                      <th>Lead Time</th>
                      <th>Min. Order</th>
                      <th>Primary</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in product.detail.suppliers" :key="s.name">
                      <td class="font-medium">{{ s.name }}</td>
                      <td><span class="sku-text">{{ s.sku }}</span></td>
                      <td>{{ formatCurrency(s.price) }}</td>
                      <td>{{ s.leadTime }}</td>
                      <td>{{ s.minOrder }}</td>
                      <td>
                        <span v-if="s.primary" class="flag-yes">Primary</span>
                        <span v-else class="flag-no">Alternative</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state-sm">
                  <Truck :size="20" />
                  <span>No suppliers linked</span>
                </div>
              </section>
            </div>

            <!-- ========== F) SALES ========== -->
            <div v-if="activeTab === 'sales'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><ShoppingCart :size="16" /> Recent Sales</h3>
                <table v-if="product.detail.recentSales.length" class="mini-table">
                  <thead>
                    <tr>
                      <th>Document</th>
                      <th>Customer</th>
                      <th>Date</th>
                      <th>Qty</th>
                      <th>Unit Price</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="sale in product.detail.recentSales" :key="sale.document">
                      <td class="font-medium">{{ sale.document }}</td>
                      <td>{{ sale.customer }}</td>
                      <td>{{ sale.date }}</td>
                      <td>{{ sale.qty }}</td>
                      <td>{{ formatCurrency(sale.unitPrice) }}</td>
                      <td class="font-semibold">{{ formatCurrency(sale.total) }}</td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state-sm">
                  <ShoppingCart :size="20" />
                  <span>No sales recorded yet</span>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><RotateCcw :size="16" /> Returns</h3>
                <table v-if="product.detail.returns.length" class="mini-table">
                  <thead>
                    <tr>
                      <th>Document</th>
                      <th>Customer</th>
                      <th>Date</th>
                      <th>Qty</th>
                      <th>Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="ret in product.detail.returns" :key="ret.document">
                      <td class="font-medium">{{ ret.document }}</td>
                      <td>{{ ret.customer }}</td>
                      <td>{{ ret.date }}</td>
                      <td>{{ ret.qty }}</td>
                      <td>{{ ret.reason }}</td>
                    </tr>
                  </tbody>
                </table>
                <div v-else class="empty-state-sm">
                  <RotateCcw :size="20" />
                  <span>No returns</span>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><Link :size="16" /> Related Products / Cross-sell</h3>
                <div v-if="product.detail.relatedProducts.length" class="related-chips">
                  <span v-for="rp in product.detail.relatedProducts" :key="rp" class="related-chip">{{ rp }}</span>
                </div>
                <div v-else class="empty-state-sm">
                  <Link :size="20" />
                  <span>No related products</span>
                </div>
              </section>
            </div>

            <!-- ========== G) LOGISTICS / SHIPPING ========== -->
            <div v-if="activeTab === 'logistics'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><PackageIcon :size="16" /> Shipping &amp; Dimensions</h3>
                <div class="detail-grid">
                  <div class="detail-field">
                    <label>Weight</label>
                    <span>{{ product.detail.weight || '—' }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Dimensions (L × W × H)</label>
                    <span>{{ product.detail.dimensions || '—' }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Shipping Class</label>
                    <span>{{ product.detail.shippingClass || '—' }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Digital Product</label>
                    <span :class="product.detail.digital ? 'flag-yes' : 'flag-no'">{{ product.detail.digital ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </section>
            </div>

            <!-- ========== I) ATTACHMENTS & AUDIT ========== -->
            <div v-if="activeTab === 'audit'" class="tab-content">
              <section class="detail-section">
                <h3 class="section-title"><Paperclip :size="16" /> Attachments</h3>
                <div v-if="product.detail.attachments.length" class="attachments-list">
                  <div v-for="file in product.detail.attachments" :key="file.name" class="attachment-row">
                    <FileText :size="16" class="attachment-icon" />
                    <div class="attachment-info">
                      <span class="attachment-name">{{ file.name }}</span>
                      <span class="attachment-size">{{ file.size }}</span>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state-sm">
                  <Paperclip :size="20" />
                  <span>No files attached</span>
                </div>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><StickyNote :size="16" /> Internal Notes</h3>
                <p class="description-text">{{ product.detail.notes || 'No notes yet.' }}</p>
              </section>

              <section class="detail-section">
                <h3 class="section-title"><History :size="16" /> Audit Trail</h3>
                <div class="detail-grid">
                  <div class="detail-field">
                    <label>Created by</label>
                    <span>{{ product.detail.createdBy }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Created at</label>
                    <span>{{ product.detail.createdAt }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Last modified by</label>
                    <span>{{ product.detail.modifiedBy }}</span>
                  </div>
                  <div class="detail-field">
                    <label>Last modified at</label>
                    <span>{{ formatDate(product.updatedAt) }}</span>
                  </div>
                </div>
              </section>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import {
  Package, Wrench, X,
  FileText, Receipt, Warehouse, Layers, Truck, ShoppingCart, Paperclip,
  ImageIcon, MapPin, History, Grid3x3, List,
  RotateCcw, Link, StickyNote,
  PackageIcon
} from 'lucide-vue-next'

/* ── Props & Emits ── */
const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  open: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])

/* ── Local state ── */
const activeTab = ref('general')

const tabs = [
  { key: 'general',   label: 'General',    icon: FileText },
  { key: 'prices',    label: 'Prices',     icon: Receipt },
  { key: 'inventory', label: 'Inventory',  icon: Warehouse },
  { key: 'variants',  label: 'Variants',   icon: Layers },
  { key: 'purchases', label: 'Purchases',  icon: Truck },
  { key: 'sales',     label: 'Sales',      icon: ShoppingCart },
  { key: 'logistics', label: 'Logistics',  icon: PackageIcon },
  { key: 'audit',     label: 'Audit',      icon: Paperclip }
]

/* Reset tab when drawer opens */
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    activeTab.value = 'general'
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

/* ── Helpers ── */
function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning', Archived: 'badge-gray' }
  return map[status] || 'badge-gray'
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
/* ============================
   DRAWER OVERLAY & PANEL
   ============================ */
.drawer-overlay {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(2px);
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 680px;
  max-width: 100vw;
  background: var(--bg-primary);
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

/* Drawer Header */
.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  flex-shrink: 0;
}

.drawer-header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.drawer-thumb {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  border: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--bg-secondary);
  flex-shrink: 0;
}

.drawer-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.drawer-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 380px;
}

.drawer-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.drawer-header-right {
  flex-shrink: 0;
}

/* Drawer Tabs */
.drawer-tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--border-color);
  padding: 0 1.5rem;
  background: var(--bg-primary);
  flex-shrink: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.drawer-tabs::-webkit-scrollbar {
  display: none;
}

.drawer-tab {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
}

.drawer-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.drawer-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  font-weight: 600;
}

/* Drawer Body */
.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* ============================
   DETAIL SECTIONS
   ============================ */
.tab-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.25rem;
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f0f2f5;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 2rem;
}

.detail-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-field label {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-field span {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.value-highlight {
  font-size: 1.125rem !important;
  font-weight: 700 !important;
  color: var(--text-primary) !important;
}

/* Shared cell styles used in drawer */
.sku-text {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.type-cell {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.image-placeholder-icon {
  color: var(--text-tertiary);
}

.tax-tag {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.margin-value { font-weight: 600; font-size: var(--font-size-sm); }
.margin-high { color: var(--success-color); }
.margin-mid { color: var(--primary-color); }
.margin-low { color: var(--warning-color); }

/* Description */
.description-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.65;
  margin: 0;
}

/* Tags */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.tag-chip {
  font-size: var(--font-size-xs);
  padding: 0.2rem 0.625rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 9999px;
  font-weight: 500;
}

/* Gallery */
.gallery-grid {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.gallery-item {
  width: 80px;
  height: 80px;
  border-radius: 8px;
  border: 1px dashed var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  background: var(--bg-secondary);
}

.gallery-placeholder {
  color: var(--text-tertiary);
}

.gallery-label {
  font-size: 0.625rem;
  color: var(--text-tertiary);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 72px;
  white-space: nowrap;
}

/* Flags */
.flag-yes {
  color: var(--success-color);
  font-weight: 500;
}

.flag-no {
  color: var(--text-tertiary);
  font-weight: 500;
}

/* ============================
   STAT CARDS (Inventory)
   ============================ */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

.stat-card {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-available {
  color: var(--success-color);
}

/* ============================
   MINI TABLE (inside drawer)
   ============================ */
.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-xs);
}

.mini-table th {
  text-align: left;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0.5rem 0.625rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.6875rem;
}

.mini-table td {
  padding: 0.5rem 0.625rem;
  color: var(--text-primary);
  border-bottom: 1px solid #f5f5f7;
}

.mini-table tbody tr:last-child td {
  border-bottom: none;
}

.mini-table tbody tr:hover {
  background: var(--bg-hover);
}

.text-success {
  color: var(--success-color);
}

.text-error {
  color: var(--error-color);
}

/* ============================
   ATTRIBUTES & VARIANTS
   ============================ */
.attributes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.attribute-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.attr-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  min-width: 80px;
}

.attr-values {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.attr-chip {
  font-size: var(--font-size-xs);
  padding: 0.2rem 0.625rem;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 9999px;
  border: 1px solid var(--border-color);
  font-weight: 500;
}

/* ============================
   RELATED PRODUCTS
   ============================ */
.related-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.related-chip {
  font-size: var(--font-size-xs);
  padding: 0.375rem 0.875rem;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--border-color);
  font-weight: 500;
  cursor: default;
}

/* ============================
   ATTACHMENTS
   ============================ */
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.attachment-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--border-radius-sm);
  background: var(--bg-secondary);
}

.attachment-icon {
  color: var(--primary-color);
  flex-shrink: 0;
}

.attachment-info {
  display: flex;
  flex-direction: column;
}

.attachment-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.attachment-size {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* ============================
   EMPTY STATE (small)
   ============================ */
.empty-state-sm {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

/* ============================
   DRAWER TRANSITION
   ============================ */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from {
  opacity: 0;
}

.drawer-enter-from .drawer-panel {
  transform: translateX(100%);
}

.drawer-leave-to {
  opacity: 0;
}

.drawer-leave-to .drawer-panel {
  transform: translateX(100%);
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .drawer-panel {
    width: 100vw;
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .drawer-title {
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }
}
</style>
