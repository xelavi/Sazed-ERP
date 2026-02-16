<template>
  <div class="customers-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Customers</h1>
          <span class="count-badge">{{ customers.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Export</span>
          </button>
          <button class="btn btn-primary">
            <Plus :size="18" />
            <span>Add customer</span>
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
            placeholder="Search by name, email..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <div class="type-toggle">
            <button
              :class="['toggle-btn', { active: typeFilter === 'all' }]"
              @click="typeFilter = 'all'"
            >All</button>
            <button
              :class="['toggle-btn', { active: typeFilter === 'company' }]"
              @click="typeFilter = 'company'"
            >
              <Building2 :size="14" />
              Company
            </button>
            <button
              :class="['toggle-btn', { active: typeFilter === 'person' }]"
              @click="typeFilter = 'person'"
            >
              <User :size="14" />
              Person
            </button>
          </div>
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">All statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select class="select filter-select" v-model="cityFilter">
            <option value="all">All cities</option>
            <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
          </select>
          <button class="btn btn-secondary" @click="sortCustomers">
            <ArrowUpDown :size="18" />
            <span>Sort</span>
          </button>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table customers-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" class="checkbox" @change="toggleSelectAll" :checked="allSelected" />
                </th>
                <th class="col-avatar"></th>
                <th class="col-name">Name</th>
                <th class="col-type">Type</th>
                <th class="col-email">Email</th>
                <th class="col-city">City</th>
                <th class="col-linked">Linked</th>
                <th class="col-status">Status</th>
                <th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in filteredCustomers" :key="customer.id" class="table-row">
                <td class="col-checkbox" @click.stop>
                  <input type="checkbox" class="checkbox" v-model="selectedCustomers" :value="customer.id" />
                </td>
                <td class="col-avatar">
                  <div class="customer-avatar" :style="{ background: customer.avatarColor }">
                    {{ customer.initials }}
                  </div>
                </td>
                <td class="col-name">
                  <span class="customer-name">{{ customer.name }}</span>
                  <span v-if="customer.type === 'Company' && customer.vatId" class="vat-hint">{{ customer.vatId }}</span>
                </td>
                <td class="col-type">
                  <span :class="['type-badge', customer.type === 'Company' ? 'type-company' : 'type-person']">
                    <Building2 v-if="customer.type === 'Company'" :size="12" />
                    <User v-else :size="12" />
                    {{ customer.type }}
                  </span>
                </td>
                <td class="col-email">
                  <span class="email-text">{{ customer.email }}</span>
                </td>
                <td class="col-city">
                  <span class="city-text">{{ customer.city }}</span>
                </td>
                <td class="col-linked">
                  <div v-if="customer.linked.length" class="linked-list">
                    <span class="linked-tag" v-for="link in customer.linked.slice(0, 2)" :key="link">{{ link }}</span>
                    <span v-if="customer.linked.length > 2" class="linked-more">+{{ customer.linked.length - 2 }}</span>
                  </div>
                  <span v-else class="text-tertiary">—</span>
                </td>
                <td class="col-status">
                  <span :class="['badge', statusBadgeClass(customer.status)]">
                    {{ customer.status }}
                  </span>
                </td>
                <td class="col-actions" @click.stop>
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
            Showing <strong>{{ filteredCustomers.length }}</strong> of <strong>{{ customers.length }}</strong> customers
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Plus, Search, ArrowUpDown, MoreVertical, Download,
  Building2, User
} from 'lucide-vue-next'

/* ── Table state ── */
const searchQuery = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const cityFilter = ref('all')
const selectedCustomers = ref([])
const sortAsc = ref(true)

/* ── Customers data ── */
const customers = ref([
  {
    id: 1,
    name: 'Acme Corp.',
    type: 'Company',
    email: 'contact@acmecorp.com',
    city: 'Madrid',
    status: 'Active',
    vatId: 'B-12345678',
    avatarColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    initials: 'AC',
    linked: ['María López', 'Pedro Ruiz']
  },
  {
    id: 2,
    name: 'María López',
    type: 'Person',
    email: 'maria.lopez@email.com',
    city: 'Madrid',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EC4899 0%, #F59E0B 100%)',
    initials: 'ML',
    linked: ['Acme Corp.']
  },
  {
    id: 3,
    name: 'Oficinas Modernas S.L.',
    type: 'Company',
    email: 'admin@oficinasmodernas.es',
    city: 'Barcelona',
    status: 'Active',
    vatId: 'B-87654321',
    avatarColor: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
    initials: 'OM',
    linked: ['Carlos Méndez', 'Laura Martín', 'Elena Vidal']
  },
  {
    id: 4,
    name: 'Pedro Ruiz',
    type: 'Person',
    email: 'pruiz@gmail.com',
    city: 'Valencia',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
    initials: 'PR',
    linked: ['Acme Corp.']
  },
  {
    id: 5,
    name: 'Carlos Méndez',
    type: 'Person',
    email: 'carlos.mendez@oficinasmodernas.es',
    city: 'Barcelona',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
    initials: 'CM',
    linked: ['Oficinas Modernas S.L.']
  },
  {
    id: 6,
    name: 'Laura Martín',
    type: 'Person',
    email: 'laura.martin@email.com',
    city: 'Sevilla',
    status: 'Inactive',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%)',
    initials: 'LM',
    linked: ['Oficinas Modernas S.L.']
  },
  {
    id: 7,
    name: 'Café Molino',
    type: 'Company',
    email: 'info@cafemolino.es',
    city: 'Sevilla',
    status: 'Active',
    vatId: 'B-11223344',
    avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #10B981 100%)',
    initials: 'CM',
    linked: ['Jorge Pérez']
  },
  {
    id: 8,
    name: 'Jorge Pérez',
    type: 'Person',
    email: 'jorge.perez@cafemolino.es',
    city: 'Sevilla',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
    initials: 'JP',
    linked: ['Café Molino']
  },
  {
    id: 9,
    name: 'Luis Fernández',
    type: 'Person',
    email: 'lfernandez@outlook.com',
    city: 'Bilbao',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)',
    initials: 'LF',
    linked: []
  },
  {
    id: 10,
    name: 'TechParts Ibérica S.A.',
    type: 'Company',
    email: 'ventas@techparts.es',
    city: 'Madrid',
    status: 'Active',
    vatId: 'A-99887766',
    avatarColor: 'linear-gradient(135deg, #667eea 0%, #10B981 100%)',
    initials: 'TI',
    linked: ['Ana García']
  },
  {
    id: 11,
    name: 'Ana García',
    type: 'Person',
    email: 'ana.garcia@techparts.es',
    city: 'Madrid',
    status: 'Active',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%)',
    initials: 'AG',
    linked: ['TechParts Ibérica S.A.']
  },
  {
    id: 12,
    name: 'Elena Vidal',
    type: 'Person',
    email: 'elena.vidal@email.com',
    city: 'Zaragoza',
    status: 'Inactive',
    vatId: null,
    avatarColor: 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)',
    initials: 'EV',
    linked: ['Oficinas Modernas S.L.']
  }
])

/* ── Computed ── */
const cities = computed(() => {
  const c = [...new Set(customers.value.map(cu => cu.city))]
  return c.sort()
})

const allSelected = computed(() => {
  return filteredCustomers.value.length > 0 && selectedCustomers.value.length === filteredCustomers.value.length
})

const filteredCustomers = computed(() => {
  let result = customers.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.email.toLowerCase().includes(q) ||
      (c.vatId && c.vatId.toLowerCase().includes(q))
    )
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(c => c.status.toLowerCase() === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    result = result.filter(c => c.type.toLowerCase() === typeFilter.value)
  }

  if (cityFilter.value !== 'all') {
    result = result.filter(c => c.city === cityFilter.value)
  }

  return result
})

/* ── Actions ── */
function toggleSelectAll() {
  if (allSelected.value) {
    selectedCustomers.value = []
  } else {
    selectedCustomers.value = filteredCustomers.value.map(c => c.id)
  }
}

function sortCustomers() {
  sortAsc.value = !sortAsc.value
  customers.value.sort((a, b) => {
    return sortAsc.value
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  })
}

/* ── Helpers ── */
function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning' }
  return map[status] || 'badge-gray'
}
</script>

<style scoped>
.customers-view {
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

/* ============================
   FILTERS
   ============================ */
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
   TYPE TOGGLE (Company / Person)
   ============================ */
.type-toggle {
  display: inline-flex;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  background: white;
}

.toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  font-family: var(--font-family);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.toggle-btn:not(:last-child) {
  border-right: 1px solid var(--border-color);
}

.toggle-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.toggle-btn.active {
  background: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
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

.customers-table {
  min-width: 860px;
}

.customers-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.customers-table td {
  padding: 0.625rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.col-checkbox { width: 40px; text-align: center; }
.col-avatar { width: 48px; }
.col-name { min-width: 180px; white-space: normal !important; }
.col-type { width: 110px; }
.col-email { min-width: 180px; }
.col-city { width: 120px; }
.col-linked { min-width: 180px; }
.col-status { width: 90px; }
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
.customer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-xs);
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.customer-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  display: block;
  line-height: 1.3;
}

.vat-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  display: block;
  margin-top: 1px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  border-radius: 9999px;
  white-space: nowrap;
}

.type-company {
  background: var(--primary-light);
  color: var(--primary-color);
}

.type-person {
  background: #fdf2f8;
  color: #db2777;
}

.email-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.city-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.linked-list {
  display: flex;
  gap: 0.375rem;
  align-items: center;
  flex-wrap: wrap;
}

.linked-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 6px;
  white-space: nowrap;
}

.linked-more {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-weight: 600;
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
