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
                  <button class="btn-icon">
                    <MoreVertical :size="18" />
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
import { ref, computed } from 'vue'
import {
  Plus, Search, ArrowUpDown, Package, MoreVertical,
  Download, Globe, Store, Wrench, Pencil
} from 'lucide-vue-next'
import ProductDetailDrawer from '@/components/ProductDetailDrawer.vue'
import ProductFormModal from '@/components/ProductFormModal.vue'

/* ── Drawer state ── */
const detailOpen = ref(false)
const selectedProduct = ref(null)

function openDetail(product) {
  selectedProduct.value = product
  detailOpen.value = true
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

function handleProductSave(data) {
  console.log('Product saved:', data)
  // No persistence yet — just log
}

/* ── Table state ── */
const searchQuery = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const categoryFilter = ref('all')
const publishedFilter = ref('all')
const selectedProducts = ref([])
const sortAsc = ref(true)

/* ── Products data with full detail ── */
const products = ref([
  {
    id: 1,
    sku: 'ERP-001',
    name: 'Camiseta Algodón Orgánico',
    status: 'Active',
    type: 'Product',
    category: 'Clothing',
    stock: 245,
    reserved: 12,
    price: 29.99,
    priceFrom: null,
    hasVariants: true,
    variantsCount: 4,
    cost: 12.50,
    tax: '21% IVA',
    supplier: 'TextilSur S.L.',
    channels: ['Web', 'Marketplace'],
    updatedAt: '2026-02-15T10:30:00',
    image: null,
    detail: {
      description: 'Camiseta de algodón 100% orgánico certificado GOTS, corte regular, costuras reforzadas. Disponible en 4 tallas.',
      tags: ['Organic', 'T-Shirt', 'Summer'],
      unit: 'ud',
      sellable: true,
      purchasable: true,
      brand: 'EcoWear',
      gallery: ['front.jpg', 'back.jpg', 'detail.jpg'],
      priceExclTax: 24.79,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 29.99, from: '01/01/2026', to: null },
        { name: 'Wholesale', price: 22.00, from: '01/01/2026', to: null }
      ],
      minStock: 50,
      reorderPoint: 80,
      warehouse: 'Warehouse Madrid',
      location: 'A-12-03',
      lotTracking: false,
      stockMovements: [
        { date: '15/02/2026', type: 'Out', document: 'SO-2045', qty: -5, user: 'Ana G.' },
        { date: '14/02/2026', type: 'Out', document: 'SO-2038', qty: -12, user: 'Carlos M.' },
        { date: '10/02/2026', type: 'In', document: 'PO-1120', qty: 100, user: 'System' },
        { date: '02/02/2026', type: 'Adjust', document: 'ADJ-045', qty: -3, user: 'Ana G.' }
      ],
      attributes: [
        { name: 'Size', values: ['S', 'M', 'L', 'XL'] },
        { name: 'Color', values: ['White', 'Black', 'Navy'] }
      ],
      variants: [
        { name: 'S / White', sku: 'ERP-001-SW', price: 29.99, stock: 60, ean: '8412345000011' },
        { name: 'M / White', sku: 'ERP-001-MW', price: 29.99, stock: 75, ean: '8412345000028' },
        { name: 'L / Black', sku: 'ERP-001-LB', price: 29.99, stock: 55, ean: '8412345000035' },
        { name: 'XL / Navy', sku: 'ERP-001-XN', price: 29.99, stock: 55, ean: '8412345000042' }
      ],
      suppliers: [
        { name: 'TextilSur S.L.', sku: 'TS-CAM-ORG', price: 12.50, leadTime: '7 days', minOrder: 50, primary: true },
        { name: 'FabricWorld', sku: 'FW-0892', price: 13.80, leadTime: '14 days', minOrder: 100, primary: false }
      ],
      recentSales: [
        { document: 'SO-2045', customer: 'María López', date: '15/02/2026', qty: 5, unitPrice: 29.99, total: 149.95 },
        { document: 'SO-2038', customer: 'Retail BCN', date: '14/02/2026', qty: 12, unitPrice: 22.00, total: 264.00 },
        { document: 'SO-2011', customer: 'Pedro Ruiz', date: '08/02/2026', qty: 2, unitPrice: 29.99, total: 59.98 }
      ],
      returns: [
        { document: 'RET-012', customer: 'Pedro Ruiz', date: '12/02/2026', qty: 1, reason: 'Wrong size' }
      ],
      relatedProducts: ['Pantalón Chino Orgánico', 'Gorra Canvas'],
      weight: '0.18 kg',
      dimensions: '30 × 25 × 2 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [
        { name: 'GOTS_Certificate.pdf', size: '245 KB' },
        { name: 'Care_instructions.pdf', size: '120 KB' }
      ],
      notes: 'Restock before summer campaign. Confirm colors with supplier by March.',
      createdBy: 'Admin',
      createdAt: '15/09/2025',
      modifiedBy: 'Ana G.'
    }
  },
  {
    id: 2,
    sku: 'ERP-002',
    name: 'Zapatillas Running Pro',
    status: 'Active',
    type: 'Product',
    category: 'Footwear',
    stock: 58,
    reserved: 3,
    price: 89.95,
    priceFrom: 79.95,
    hasVariants: true,
    variantsCount: 6,
    cost: 35.00,
    tax: '21% IVA',
    supplier: 'SportGlobal Ltd.',
    channels: ['Web'],
    updatedAt: '2026-02-14T16:45:00',
    image: null,
    detail: {
      description: 'Zapatillas de running con amortiguación CloudFoam, upper de malla transpirable y suela de caucho continental.',
      tags: ['Running', 'Sport', 'Sneakers'],
      unit: 'pair',
      sellable: true,
      purchasable: true,
      brand: 'RunTech',
      gallery: ['side.jpg', 'sole.jpg'],
      priceExclTax: 74.34,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 89.95, from: '01/01/2026', to: null },
        { name: 'Staff', price: 65.00, from: '01/01/2026', to: null }
      ],
      minStock: 20,
      reorderPoint: 30,
      warehouse: 'Warehouse Madrid',
      location: 'B-04-01',
      lotTracking: false,
      stockMovements: [
        { date: '14/02/2026', type: 'Out', document: 'SO-2040', qty: -2, user: 'Carlos M.' },
        { date: '12/02/2026', type: 'In', document: 'PO-1118', qty: 30, user: 'System' }
      ],
      attributes: [
        { name: 'Size', values: ['39', '40', '41', '42', '43', '44'] },
        { name: 'Color', values: ['Black/Red', 'White/Blue'] }
      ],
      variants: [
        { name: '40 / Black-Red', sku: 'ERP-002-40BR', price: 89.95, stock: 10, ean: '8412345001001' },
        { name: '42 / Black-Red', sku: 'ERP-002-42BR', price: 89.95, stock: 12, ean: '8412345001002' },
        { name: '43 / White-Blue', sku: 'ERP-002-43WB', price: 89.95, stock: 8, ean: '8412345001003' },
        { name: '41 / White-Blue', sku: 'ERP-002-41WB', price: 79.95, stock: 10, ean: '8412345001004' },
        { name: '44 / Black-Red', sku: 'ERP-002-44BR', price: 89.95, stock: 9, ean: '8412345001005' },
        { name: '39 / White-Blue', sku: 'ERP-002-39WB', price: 79.95, stock: 9, ean: '8412345001006' }
      ],
      suppliers: [
        { name: 'SportGlobal Ltd.', sku: 'SG-RUN-PRO', price: 35.00, leadTime: '21 days', minOrder: 24, primary: true }
      ],
      recentSales: [
        { document: 'SO-2040', customer: 'Luis Fernández', date: '14/02/2026', qty: 2, unitPrice: 89.95, total: 179.90 }
      ],
      returns: [],
      relatedProducts: ['Calcetines Técnicos', 'Plantillas Running Gel'],
      weight: '0.62 kg',
      dimensions: '35 × 22 × 14 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [],
      notes: '',
      createdBy: 'Admin',
      createdAt: '20/10/2025',
      modifiedBy: 'Carlos M.'
    }
  },
  {
    id: 3,
    sku: 'ERP-003',
    name: 'Consultoría SEO Mensual',
    status: 'Active',
    type: 'Service',
    category: 'Services',
    stock: null,
    reserved: null,
    price: 450.00,
    priceFrom: null,
    hasVariants: false,
    variantsCount: 0,
    cost: 120.00,
    tax: '21% IVA',
    supplier: null,
    channels: ['Web'],
    updatedAt: '2026-02-13T09:15:00',
    image: null,
    detail: {
      description: 'Servicio mensual de consultoría SEO: auditoría técnica, keyword research, on-page optimization y reporting.',
      tags: ['SEO', 'Digital', 'Marketing'],
      unit: 'hour',
      sellable: true,
      purchasable: false,
      brand: null,
      gallery: [],
      priceExclTax: 371.90,
      currency: 'EUR',
      priceLists: [
        { name: 'Standard', price: 450.00, from: '01/01/2026', to: null }
      ],
      minStock: null,
      reorderPoint: null,
      warehouse: '—',
      location: null,
      lotTracking: false,
      stockMovements: [],
      attributes: [],
      variants: [],
      suppliers: [],
      recentSales: [
        { document: 'SO-2032', customer: 'Acme Corp.', date: '01/02/2026', qty: 1, unitPrice: 450.00, total: 450.00 },
        { document: 'SO-2010', customer: 'Acme Corp.', date: '01/01/2026', qty: 1, unitPrice: 450.00, total: 450.00 }
      ],
      returns: [],
      relatedProducts: ['Diseño de Logo Profesional'],
      weight: null,
      dimensions: null,
      shippingClass: null,
      digital: true,
      attachments: [
        { name: 'SEO_Service_Agreement.pdf', size: '310 KB' }
      ],
      notes: 'Recurring monthly service for Acme Corp. Auto-invoice on 1st.',
      createdBy: 'Admin',
      createdAt: '05/11/2025',
      modifiedBy: 'Admin'
    }
  },
  {
    id: 4,
    sku: 'ERP-004',
    name: 'Mochila Urbana 25L',
    status: 'Inactive',
    type: 'Product',
    category: 'Accessories',
    stock: 0,
    reserved: 0,
    price: 54.50,
    priceFrom: null,
    hasVariants: false,
    variantsCount: 0,
    cost: 22.00,
    tax: '21% IVA',
    supplier: 'BagCo Europa',
    channels: [],
    updatedAt: '2026-01-28T14:00:00',
    image: null,
    detail: {
      description: 'Mochila urbana 25L en poliéster reciclado, compartimento para portátil 15", bolsillo antirrobo trasero.',
      tags: ['Backpack', 'Urban', 'Eco'],
      unit: 'ud',
      sellable: true,
      purchasable: true,
      brand: 'UrbanPack',
      gallery: ['front.jpg'],
      priceExclTax: 45.04,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 54.50, from: '01/06/2025', to: null }
      ],
      minStock: 10,
      reorderPoint: 20,
      warehouse: 'Warehouse Madrid',
      location: 'C-01-05',
      lotTracking: false,
      stockMovements: [
        { date: '28/01/2026', type: 'Out', document: 'SO-1990', qty: -3, user: 'Ana G.' },
        { date: '15/01/2026', type: 'Adjust', document: 'ADJ-039', qty: -2, user: 'Admin' }
      ],
      attributes: [],
      variants: [],
      suppliers: [
        { name: 'BagCo Europa', sku: 'BC-URB25', price: 22.00, leadTime: '10 days', minOrder: 25, primary: true }
      ],
      recentSales: [
        { document: 'SO-1990', customer: 'Elena Vidal', date: '28/01/2026', qty: 3, unitPrice: 54.50, total: 163.50 }
      ],
      returns: [],
      relatedProducts: ['Botella Térmica 750ml'],
      weight: '0.75 kg',
      dimensions: '48 × 32 × 18 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [],
      notes: 'Out of stock — waiting on supplier restock. Set to Inactive.',
      createdBy: 'Admin',
      createdAt: '01/06/2025',
      modifiedBy: 'Ana G.'
    }
  },
  {
    id: 5,
    sku: 'ERP-005',
    name: 'Café Arábica Premium 1kg',
    status: 'Active',
    type: 'Product',
    category: 'Food & Drink',
    stock: 320,
    reserved: 45,
    price: 18.75,
    priceFrom: null,
    hasVariants: false,
    variantsCount: 0,
    cost: 7.80,
    tax: '10% IVA',
    supplier: 'CaféDirect',
    channels: ['Web', 'Marketplace'],
    updatedAt: '2026-02-15T08:20:00',
    image: null,
    detail: {
      description: 'Café arábica 100% de origen único (Colombia), tueste medio, grano entero. Paquete de 1 kg con válvula de desgasificación.',
      tags: ['Coffee', 'Organic', 'Premium'],
      unit: 'kg',
      sellable: true,
      purchasable: true,
      brand: 'CaféDirect',
      gallery: ['pack-front.jpg', 'beans-detail.jpg'],
      priceExclTax: 17.05,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 18.75, from: '01/01/2026', to: null },
        { name: 'HoReCa', price: 15.00, from: '01/01/2026', to: null }
      ],
      minStock: 100,
      reorderPoint: 150,
      warehouse: 'Warehouse Madrid',
      location: 'D-08-02',
      lotTracking: true,
      stockMovements: [
        { date: '15/02/2026', type: 'Out', document: 'SO-2044', qty: -20, user: 'System' },
        { date: '14/02/2026', type: 'Out', document: 'SO-2037', qty: -45, user: 'System' },
        { date: '10/02/2026', type: 'In', document: 'PO-1119', qty: 200, user: 'System' }
      ],
      attributes: [],
      variants: [],
      suppliers: [
        { name: 'CaféDirect', sku: 'CD-ARA-1KG', price: 7.80, leadTime: '5 days', minOrder: 50, primary: true }
      ],
      recentSales: [
        { document: 'SO-2044', customer: 'Bar El Centro', date: '15/02/2026', qty: 20, unitPrice: 15.00, total: 300.00 },
        { document: 'SO-2037', customer: 'Online Customer', date: '14/02/2026', qty: 3, unitPrice: 18.75, total: 56.25 }
      ],
      returns: [],
      relatedProducts: ['Café Descafeinado 1kg'],
      weight: '1.05 kg',
      dimensions: '28 × 12 × 8 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [
        { name: 'Origin_Certificate.pdf', size: '180 KB' }
      ],
      notes: 'Best seller. Lot tracking enabled — record expiry dates.',
      createdBy: 'Admin',
      createdAt: '10/08/2025',
      modifiedBy: 'System'
    }
  },
  {
    id: 6,
    sku: 'ERP-006',
    name: 'Auriculares Bluetooth NC',
    status: 'Active',
    type: 'Product',
    category: 'Electronics',
    stock: 14,
    reserved: 2,
    price: 129.00,
    priceFrom: null,
    hasVariants: true,
    variantsCount: 2,
    cost: 55.00,
    tax: '21% IVA',
    supplier: 'TechParts Asia',
    channels: ['Marketplace'],
    updatedAt: '2026-02-10T11:50:00',
    image: null,
    detail: {
      description: 'Auriculares over-ear Bluetooth 5.3 con cancelación de ruido activa (ANC), 40 h de batería, micrófono dual.',
      tags: ['Bluetooth', 'ANC', 'Headphones'],
      unit: 'ud',
      sellable: true,
      purchasable: true,
      brand: 'SoundMax',
      gallery: ['headphones-black.jpg', 'headphones-white.jpg'],
      priceExclTax: 106.61,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 129.00, from: '01/01/2026', to: null }
      ],
      minStock: 10,
      reorderPoint: 20,
      warehouse: 'Warehouse Madrid',
      location: 'A-02-07',
      lotTracking: true,
      stockMovements: [
        { date: '10/02/2026', type: 'Out', document: 'SO-2025', qty: -1, user: 'Carlos M.' },
        { date: '05/02/2026', type: 'In', document: 'PO-1115', qty: 10, user: 'System' }
      ],
      attributes: [
        { name: 'Color', values: ['Black', 'White'] }
      ],
      variants: [
        { name: 'Black', sku: 'ERP-006-BLK', price: 129.00, stock: 8, ean: '8412345002001' },
        { name: 'White', sku: 'ERP-006-WHT', price: 129.00, stock: 6, ean: '8412345002002' }
      ],
      suppliers: [
        { name: 'TechParts Asia', sku: 'TPA-BT-ANC40', price: 55.00, leadTime: '30 days', minOrder: 10, primary: true }
      ],
      recentSales: [
        { document: 'SO-2025', customer: 'Jorge Pérez', date: '10/02/2026', qty: 1, unitPrice: 129.00, total: 129.00 }
      ],
      returns: [],
      relatedProducts: ['Funda Auriculares', 'Cable USB-C 2m'],
      weight: '0.28 kg',
      dimensions: '20 × 18 × 8 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [
        { name: 'User_Manual_EN.pdf', size: '2.1 MB' }
      ],
      notes: 'Low stock alert! Reorder PO submitted 08/02.',
      createdBy: 'Carlos M.',
      createdAt: '01/12/2025',
      modifiedBy: 'Carlos M.'
    }
  },
  {
    id: 7,
    sku: 'ERP-007',
    name: 'Set Skincare Natural',
    status: 'Archived',
    type: 'Product',
    category: 'Beauty',
    stock: 3,
    reserved: 0,
    price: 42.00,
    priceFrom: null,
    hasVariants: false,
    variantsCount: 0,
    cost: 19.50,
    tax: '21% IVA',
    supplier: 'BioCosmética',
    channels: [],
    updatedAt: '2025-12-20T17:30:00',
    image: null,
    detail: {
      description: 'Set de skincare natural con crema hidratante, sérum vitamina C y limpiador facial. Ingredientes orgánicos certificados.',
      tags: ['Skincare', 'Natural', 'Gift Set'],
      unit: 'ud',
      sellable: false,
      purchasable: false,
      brand: 'BioCosmética',
      gallery: ['set-box.jpg'],
      priceExclTax: 34.71,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 42.00, from: '01/06/2025', to: '31/12/2025' }
      ],
      minStock: 5,
      reorderPoint: 10,
      warehouse: 'Warehouse Madrid',
      location: 'E-03-01',
      lotTracking: true,
      stockMovements: [
        { date: '20/12/2025', type: 'Adjust', document: 'ADJ-041', qty: -2, user: 'Admin' }
      ],
      attributes: [],
      variants: [],
      suppliers: [
        { name: 'BioCosmética', sku: 'BC-SKIN-SET', price: 19.50, leadTime: '7 days', minOrder: 20, primary: true }
      ],
      recentSales: [
        { document: 'SO-1945', customer: 'Laura Martín', date: '18/12/2025', qty: 2, unitPrice: 42.00, total: 84.00 }
      ],
      returns: [
        { document: 'RET-008', customer: 'Laura Martín', date: '22/12/2025', qty: 1, reason: 'Allergic reaction' }
      ],
      relatedProducts: [],
      weight: '0.45 kg',
      dimensions: '22 × 15 × 10 cm',
      shippingClass: 'Fragile',
      digital: false,
      attachments: [
        { name: 'INCI_List.pdf', size: '95 KB' }
      ],
      notes: 'Product archived — seasonal Christmas edition. Remaining 3 units to be sold at clearance.',
      createdBy: 'Admin',
      createdAt: '01/06/2025',
      modifiedBy: 'Admin'
    }
  },
  {
    id: 8,
    sku: 'ERP-008',
    name: 'Silla Ergonómica Oficina',
    status: 'Active',
    type: 'Product',
    category: 'Furniture',
    stock: 27,
    reserved: 5,
    price: 349.00,
    priceFrom: null,
    hasVariants: true,
    variantsCount: 3,
    cost: 145.00,
    tax: '21% IVA',
    supplier: 'MueblesPro',
    channels: ['Web'],
    updatedAt: '2026-02-12T13:10:00',
    image: null,
    detail: {
      description: 'Silla ergonómica de oficina con soporte lumbar ajustable, reposabrazos 4D, asiento de malla transpirable y base de aluminio.',
      tags: ['Office', 'Ergonomic', 'Chair'],
      unit: 'ud',
      sellable: true,
      purchasable: true,
      brand: 'ErgoPlus',
      gallery: ['chair-front.jpg', 'chair-side.jpg', 'chair-back.jpg'],
      priceExclTax: 288.43,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 349.00, from: '01/01/2026', to: null },
        { name: 'B2B', price: 295.00, from: '01/01/2026', to: null }
      ],
      minStock: 5,
      reorderPoint: 10,
      warehouse: 'Warehouse Madrid',
      location: 'F-01-01',
      lotTracking: false,
      stockMovements: [
        { date: '12/02/2026', type: 'Out', document: 'SO-2030', qty: -3, user: 'Ana G.' },
        { date: '01/02/2026', type: 'In', document: 'PO-1112', qty: 15, user: 'System' }
      ],
      attributes: [
        { name: 'Color', values: ['Black', 'Gray', 'Blue'] }
      ],
      variants: [
        { name: 'Black', sku: 'ERP-008-BLK', price: 349.00, stock: 12, ean: '8412345003001' },
        { name: 'Gray', sku: 'ERP-008-GRY', price: 349.00, stock: 10, ean: '8412345003002' },
        { name: 'Blue', sku: 'ERP-008-BLU', price: 349.00, stock: 5, ean: '8412345003003' }
      ],
      suppliers: [
        { name: 'MueblesPro', sku: 'MP-ERGO-V3', price: 145.00, leadTime: '14 days', minOrder: 5, primary: true }
      ],
      recentSales: [
        { document: 'SO-2030', customer: 'Oficinas Modernas S.L.', date: '12/02/2026', qty: 3, unitPrice: 295.00, total: 885.00 }
      ],
      returns: [],
      relatedProducts: ['Mesa Standing Desk', 'Reposapiés Ergonómico'],
      weight: '14.5 kg',
      dimensions: '68 × 68 × 120 cm',
      shippingClass: 'Bulky',
      digital: false,
      attachments: [
        { name: 'Assembly_Guide.pdf', size: '4.2 MB' },
        { name: 'Warranty_Card.pdf', size: '85 KB' }
      ],
      notes: 'Top margin product. Consider bundling with standing desk for Q2 promotion.',
      createdBy: 'Admin',
      createdAt: '15/09/2025',
      modifiedBy: 'Ana G.'
    }
  },
  {
    id: 9,
    sku: 'ERP-009',
    name: 'Diseño de Logo Profesional',
    status: 'Active',
    type: 'Service',
    category: 'Services',
    stock: null,
    reserved: null,
    price: 250.00,
    priceFrom: 150.00,
    hasVariants: true,
    variantsCount: 3,
    cost: 60.00,
    tax: '21% IVA',
    supplier: null,
    channels: ['Web'],
    updatedAt: '2026-02-08T10:00:00',
    image: null,
    detail: {
      description: 'Servicio de diseño de logotipo profesional: briefing, 3 conceptos, 2 rondas de revisión, entrega de archivos en AI, SVG, PNG y PDF.',
      tags: ['Design', 'Logo', 'Branding'],
      unit: 'project',
      sellable: true,
      purchasable: false,
      brand: null,
      gallery: [],
      priceExclTax: 206.61,
      currency: 'EUR',
      priceLists: [
        { name: 'Basic', price: 150.00, from: '01/01/2026', to: null },
        { name: 'Standard', price: 250.00, from: '01/01/2026', to: null },
        { name: 'Premium', price: 450.00, from: '01/01/2026', to: null }
      ],
      minStock: null,
      reorderPoint: null,
      warehouse: '—',
      location: null,
      lotTracking: false,
      stockMovements: [],
      attributes: [
        { name: 'Tier', values: ['Basic', 'Standard', 'Premium'] }
      ],
      variants: [
        { name: 'Basic', sku: 'ERP-009-BAS', price: 150.00, stock: null, ean: null },
        { name: 'Standard', sku: 'ERP-009-STD', price: 250.00, stock: null, ean: null },
        { name: 'Premium', sku: 'ERP-009-PRE', price: 450.00, stock: null, ean: null }
      ],
      suppliers: [],
      recentSales: [
        { document: 'SO-2022', customer: 'StartUp Tech', date: '08/02/2026', qty: 1, unitPrice: 250.00, total: 250.00 },
        { document: 'SO-2005', customer: 'Café Molino', date: '20/01/2026', qty: 1, unitPrice: 450.00, total: 450.00 }
      ],
      returns: [],
      relatedProducts: ['Consultoría SEO Mensual', 'Brand Guidelines Package'],
      weight: null,
      dimensions: null,
      shippingClass: null,
      digital: true,
      attachments: [],
      notes: '',
      createdBy: 'Admin',
      createdAt: '01/11/2025',
      modifiedBy: 'Admin'
    }
  },
  {
    id: 10,
    sku: 'ERP-010',
    name: 'Botella Térmica 750ml',
    status: 'Active',
    type: 'Product',
    category: 'Accessories',
    stock: 189,
    reserved: 0,
    price: 24.99,
    priceFrom: null,
    hasVariants: true,
    variantsCount: 5,
    cost: 8.20,
    tax: '21% IVA',
    supplier: 'EcoBottles',
    channels: ['Web', 'Marketplace'],
    updatedAt: '2026-02-14T09:40:00',
    image: null,
    detail: {
      description: 'Botella térmica de acero inoxidable 304, doble pared al vacío, 750 ml. Mantiene frío 24h y caliente 12h. Libre de BPA.',
      tags: ['Bottle', 'Eco', 'Thermal'],
      unit: 'ud',
      sellable: true,
      purchasable: true,
      brand: 'EcoBottles',
      gallery: ['bottle-colors.jpg'],
      priceExclTax: 20.65,
      currency: 'EUR',
      priceLists: [
        { name: 'Retail', price: 24.99, from: '01/01/2026', to: null },
        { name: 'Corporate Gifts', price: 19.99, from: '01/01/2026', to: null }
      ],
      minStock: 30,
      reorderPoint: 50,
      warehouse: 'Warehouse Madrid',
      location: 'C-02-08',
      lotTracking: false,
      stockMovements: [
        { date: '14/02/2026', type: 'Out', document: 'SO-2041', qty: -10, user: 'System' },
        { date: '10/02/2026', type: 'In', document: 'PO-1121', qty: 100, user: 'System' }
      ],
      attributes: [
        { name: 'Color', values: ['Midnight Black', 'Arctic White', 'Forest Green', 'Ocean Blue', 'Rose Gold'] }
      ],
      variants: [
        { name: 'Midnight Black', sku: 'ERP-010-MBK', price: 24.99, stock: 45, ean: '8412345004001' },
        { name: 'Arctic White', sku: 'ERP-010-AWT', price: 24.99, stock: 40, ean: '8412345004002' },
        { name: 'Forest Green', sku: 'ERP-010-FGR', price: 24.99, stock: 38, ean: '8412345004003' },
        { name: 'Ocean Blue', sku: 'ERP-010-OBL', price: 24.99, stock: 35, ean: '8412345004004' },
        { name: 'Rose Gold', sku: 'ERP-010-RGD', price: 24.99, stock: 31, ean: '8412345004005' }
      ],
      suppliers: [
        { name: 'EcoBottles', sku: 'EB-THERM-750', price: 8.20, leadTime: '10 days', minOrder: 50, primary: true },
        { name: 'SteelDrink Co.', sku: 'SD-750-SS', price: 9.10, leadTime: '7 days', minOrder: 25, primary: false }
      ],
      recentSales: [
        { document: 'SO-2041', customer: 'GymFit Centre', date: '14/02/2026', qty: 10, unitPrice: 19.99, total: 199.90 },
        { document: 'SO-2028', customer: 'Online Customer', date: '11/02/2026', qty: 2, unitPrice: 24.99, total: 49.98 }
      ],
      returns: [],
      relatedProducts: ['Mochila Urbana 25L', 'Tapa Deportiva Repuesto'],
      weight: '0.35 kg',
      dimensions: '27 × 7 × 7 cm',
      shippingClass: 'Standard',
      digital: false,
      attachments: [],
      notes: 'High margin product. Rose Gold best seller on Marketplace.',
      createdBy: 'Admin',
      createdAt: '01/07/2025',
      modifiedBy: 'System'
    }
  }
])

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
