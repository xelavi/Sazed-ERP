<template>
  <div class="providers-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Providers</h1>
          <span class="count-badge">{{ providers.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Export</span>
          </button>
          <button class="btn btn-primary" @click="openProviderForm()">
            <Plus :size="18" />
            <span>Add provider</span>
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
          <button class="btn btn-secondary" @click="sortProviders">
            <ArrowUpDown :size="18" />
            <span>Sort</span>
          </button>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table providers-table">
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
              <tr v-for="provider in filteredProviders" :key="provider.id" class="table-row" @click="openDetail(provider)">
                <td class="col-checkbox" @click.stop>
                  <input type="checkbox" class="checkbox" v-model="selectedProviders" :value="provider.id" />
                </td>
                <td class="col-avatar">
                  <div class="provider-avatar" :style="{ background: provider.avatarColor }">
                    {{ provider.initials }}
                  </div>
                </td>
                <td class="col-name">
                  <span class="provider-name">{{ provider.name }}</span>
                  <span v-if="provider.type === 'Company' && provider.vatId" class="vat-hint">{{ provider.vatId }}</span>
                </td>
                <td class="col-type">
                  <span :class="['type-badge', provider.type === 'Company' ? 'type-company' : 'type-person']">
                    <Building2 v-if="provider.type === 'Company'" :size="12" />
                    <User v-else :size="12" />
                    {{ provider.type }}
                  </span>
                </td>
                <td class="col-email">
                  <span class="email-text">{{ provider.email }}</span>
                </td>
                <td class="col-city">
                  <span class="city-text">{{ provider.city }}</span>
                </td>
                <td class="col-linked">
                  <div v-if="provider.linked.length" class="linked-list">
                    <span class="linked-tag" v-for="link in provider.linked.slice(0, 2)" :key="link">{{ link }}</span>
                    <span v-if="provider.linked.length > 2" class="linked-more">+{{ provider.linked.length - 2 }}</span>
                  </div>
                  <span v-else class="text-tertiary">—</span>
                </td>
                <td class="col-status">
                  <span :class="['badge', statusBadgeClass(provider.status)]">
                    {{ provider.status }}
                  </span>
                </td>
                <td class="col-actions" @click.stop>
                  <button class="btn-icon" @click="openProviderForm(provider)">
                    <Pencil :size="16" />
                  </button>
                  <button class="btn-icon" title="Eliminar" @click="deleteProvider(provider)" style="color: var(--error-color);">
                    <Trash2 :size="16" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="table-footer-info">
            Showing <strong>{{ filteredProviders.length }}</strong> of <strong>{{ providers.length }}</strong> providers
          </span>
        </div>
      </div>
    </div>

    <ProviderDetailDrawer
      v-if="selectedProvider"
      :provider="selectedProvider"
      :open="detailOpen"
      @close="closeDetail"
      @edit="(p) => { closeDetail(); openProviderForm(p) }"
    />

    <ProviderFormModal
      :open="formModalOpen"
      :provider="formProvider"
      @close="closeProviderForm"
      @save="handleProviderSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Plus, Search, ArrowUpDown, Download,
  Building2, User, Pencil, Trash2
} from 'lucide-vue-next'
import ProviderDetailDrawer from '@/components/ProviderDetailDrawer.vue'
import ProviderFormModal from '@/components/ProviderFormModal.vue'
import providersApi from '@/services/providers'
import { mapProviderFromApi, mapProviderDetailFromApi, mapProviderToApi, parseDrfErrors } from '../services/mappers'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const loading = ref(false)

async function fetchProviders() {
  loading.value = true
  try {
    const data = await providersApi.getAll()
    const items = Array.isArray(data) ? data : data.results || []
    providers.value = items.map(mapProviderFromApi)
  } catch (err) {
    console.error('Failed to load providers:', err)
    toast.error('Error al cargar proveedores')
  } finally {
    loading.value = false
  }
}

onMounted(fetchProviders)

const detailOpen = ref(false)
const selectedProvider = ref(null)

async function openDetail(provider) {
  try {
    const data = await providersApi.getById(provider.id)
    selectedProvider.value = mapProviderDetailFromApi(data)
    detailOpen.value = true
  } catch {
    selectedProvider.value = provider
    detailOpen.value = true
  }
}

function closeDetail() {
  detailOpen.value = false
}

const formModalOpen = ref(false)
const formProvider = ref(null)

function openProviderForm(provider = null) {
  formProvider.value = provider
  formModalOpen.value = true
}

function closeProviderForm() {
  formModalOpen.value = false
  formProvider.value = null
}

async function handleProviderSave(formData) {
  const apiData = mapProviderToApi(formData)
  try {
    if (formProvider.value) {
      await providersApi.update(formProvider.value.id, apiData)
      toast.success('Proveedor actualizado')
    } else {
      await providersApi.create(apiData)
      toast.success('Proveedor creado')
    }
    await fetchProviders()
  } catch (err) {
    toast.error(parseDrfErrors(err.data) || err.message || 'Error al guardar proveedor')
  }
}

async function deleteProvider(provider) {
  try {
    await providersApi.delete(provider.id)
    providers.value = providers.value.filter(p => p.id !== provider.id)
    toast.success('Proveedor eliminado')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al eliminar proveedor')
  }
}

const searchQuery = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const cityFilter = ref('all')
const selectedProviders = ref([])
const sortAsc = ref(true)

const providers = ref([])

const cities = computed(() => {
  const c = [...new Set(providers.value.map(p => p.city))]
  return c.sort()
})

const allSelected = computed(() => {
  return filteredProviders.value.length > 0 && selectedProviders.value.length === filteredProviders.value.length
})

const filteredProviders = computed(() => {
  let result = providers.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(p =>
      p.name.toLowerCase().includes(q) ||
      p.email.toLowerCase().includes(q) ||
      (p.vatId && p.vatId.toLowerCase().includes(q))
    )
  }

  if (statusFilter.value !== 'all') {
    result = result.filter(p => p.status.toLowerCase() === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    result = result.filter(p => p.type.toLowerCase() === typeFilter.value)
  }

  if (cityFilter.value !== 'all') {
    result = result.filter(p => p.city === cityFilter.value)
  }

  return result
})

function toggleSelectAll() {
  if (allSelected.value) {
    selectedProviders.value = []
  } else {
    selectedProviders.value = filteredProviders.value.map(p => p.id)
  }
}

function sortProviders() {
  sortAsc.value = !sortAsc.value
  providers.value.sort((a, b) => {
    return sortAsc.value
      ? a.name.localeCompare(b.name)
      : b.name.localeCompare(a.name)
  })
}

function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning' }
  return map[status] || 'badge-gray'
}
</script>

<style scoped>
.providers-view {
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

.table-card {
  padding: 0;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.providers-table {
  min-width: 860px;
}

.providers-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.providers-table td {
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

.provider-avatar {
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

.provider-name {
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
