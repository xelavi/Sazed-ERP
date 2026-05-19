<template>
  <div class="quotes-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Presupuestos de compra</h1>
          <span class="count-badge">{{ quotes.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openForm()">
            <Plus :size="18" />
            <span>Nuevo presupuesto</span>
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
            placeholder="Buscar por nombre, proveedor..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">Todos los estados</option>
            <option value="Draft">Borrador</option>
            <option value="Sent">Solicitado</option>
            <option value="Accepted">Aceptado</option>
            <option value="Rejected">Rechazado</option>
            <option value="Expired">Expirado</option>
            <option value="Converted">Convertido</option>
          </select>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Proveedor</th>
                <th>Fecha</th>
                <th>Válido hasta</th>
                <th>Estado</th>
                <th>Total</th>
                <th>Factura</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="q in filteredQuotes"
                :key="q.id"
                class="table-row"
                @click="openDetail(q)"
              >
                <td><strong>{{ q.name }}</strong></td>
                <td>
                  <div class="contact-cell" v-if="q.provider">
                    <div class="avatar-sm" :style="{ background: q.provider.avatarColor }">
                      {{ q.provider.initials }}
                    </div>
                    <span>{{ q.provider.name }}</span>
                  </div>
                </td>
                <td>{{ formatDate(q.issueDate) }}</td>
                <td>{{ formatDate(q.validUntil) }}</td>
                <td><span :class="['badge', statusBadgeClass(q.status)]">{{ statusLabel(q.status) }}</span></td>
                <td><strong>{{ formatCurrency(q.totalAmount) }}</strong></td>
                <td>
                  <span v-if="q.convertedInvoiceNumber" class="invoice-link">{{ q.convertedInvoiceNumber }}</span>
                  <span v-else-if="q.convertedInvoiceId" class="invoice-link">#{{ q.convertedInvoiceId }}</span>
                  <span v-else class="muted">—</span>
                </td>
                <td @click.stop>
                  <div class="actions-cell">
                    <button
                      v-if="q.status !== 'Converted'"
                      class="btn-icon"
                      title="Editar"
                      @click="openForm(q)"
                    >
                      <Pencil :size="16" />
                    </button>
                    <button
                      v-if="q.status !== 'Converted'"
                      class="btn-icon"
                      title="Convertir en factura"
                      @click="convertToInvoice(q)"
                    >
                      <FileText :size="16" />
                    </button>
                    <button class="btn-icon" title="Eliminar" @click="deleteQuote(q)">
                      <Trash2 :size="16" />
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filteredQuotes.length">
                <td colspan="8" class="empty-row">No hay presupuestos.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <Transition name="slide">
      <div v-if="detailOpen && selectedQuote" class="drawer-overlay" @click.self="closeDetail">
        <div class="drawer-panel">
          <div class="drawer-header">
            <div>
              <h2>{{ selectedQuote.name }}</h2>
              <span :class="['badge', statusBadgeClass(selectedQuote.status)]">{{ statusLabel(selectedQuote.status) }}</span>
            </div>
            <button class="btn-icon" @click="closeDetail"><X :size="20" /></button>
          </div>
          <div class="drawer-body">
            <div class="info-row"><span>Proveedor</span><strong>{{ selectedQuote.provider?.name }}</strong></div>
            <div class="info-row"><span>Fecha</span><strong>{{ formatDate(selectedQuote.issueDate) }}</strong></div>
            <div class="info-row"><span>Válido hasta</span><strong>{{ formatDate(selectedQuote.validUntil) }}</strong></div>

            <h3>Items</h3>
            <table class="table">
              <thead>
                <tr><th>Descripción</th><th>Cant.</th><th>Precio</th><th>IVA</th><th>Subtotal</th></tr>
              </thead>
              <tbody>
                <tr v-for="l in selectedQuote.lines" :key="l.id">
                  <td>{{ l.description }}</td>
                  <td>{{ l.quantity }}</td>
                  <td>{{ formatCurrency(l.unitPrice) }}</td>
                  <td>{{ l.taxPercent }}%</td>
                  <td>{{ formatCurrency(l.subtotal) }}</td>
                </tr>
              </tbody>
            </table>

            <div class="totals">
              <div class="info-row"><span>Subtotal</span><strong>{{ formatCurrency(selectedQuote.subtotal) }}</strong></div>
              <div class="info-row"><span>Impuestos</span><strong>{{ formatCurrency(selectedQuote.totalTax) }}</strong></div>
              <div class="info-row total"><span>Total</span><strong>{{ formatCurrency(selectedQuote.totalAmount) }}</strong></div>
            </div>

            <div v-if="selectedQuote.convertedInvoiceId" class="converted-info">
              Convertido en factura
              <strong>{{ selectedQuote.convertedInvoiceNumber || `#${selectedQuote.convertedInvoiceId}` }}</strong>
            </div>

            <div class="drawer-actions">
              <button
                v-if="selectedQuote.status !== 'Converted'"
                class="btn btn-primary"
                @click="convertToInvoice(selectedQuote)"
              >
                <FileText :size="16" />
                <span>Convertir en factura</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <QuoteFormModal
      :open="formOpen"
      :quote="formQuote"
      :contacts="providers"
      mode="purchase"
      @close="closeForm"
      @save="handleSave"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Search, Pencil, Trash2, FileText, X } from 'lucide-vue-next'
import QuoteFormModal from '@/components/QuoteFormModal.vue'
import quotesApi from '@/services/purchaseQuotes'
import providersApi from '@/services/providers'
import {
  mapPurchaseQuoteFromApi, mapPurchaseQuoteDetailFromApi, mapPurchaseQuoteToApi,
  mapProviderFromApi, parseDrfErrors,
} from '@/services/mappers'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const quotes = ref([])
const providers = ref([])
const searchQuery = ref('')
const statusFilter = ref('all')

async function fetchQuotes() {
  try {
    const data = await quotesApi.getAll()
    const items = Array.isArray(data) ? data : (data.results || [])
    quotes.value = items.map(mapPurchaseQuoteFromApi)
  } catch (err) {
    toast.error('Error al cargar presupuestos')
  }
}

async function fetchProviders() {
  try {
    const data = await providersApi.getAll()
    const items = Array.isArray(data) ? data : (data.results || [])
    providers.value = items.map(mapProviderFromApi)
  } catch (err) {
    toast.error('Error al cargar proveedores')
  }
}

onMounted(async () => {
  await fetchQuotes()
  await fetchProviders()
})

const filteredQuotes = computed(() => {
  let r = quotes.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    r = r.filter(x =>
      x.name?.toLowerCase().includes(q) ||
      x.provider?.name?.toLowerCase().includes(q)
    )
  }
  if (statusFilter.value !== 'all') {
    r = r.filter(x => x.status === statusFilter.value)
  }
  return r
})

const formOpen = ref(false)
const formQuote = ref(null)

function openForm(q = null) {
  formQuote.value = q
  formOpen.value = true
}

function closeForm() {
  formOpen.value = false
  formQuote.value = null
}

async function handleSave(formData) {
  const apiData = mapPurchaseQuoteToApi(formData)
  try {
    if (formQuote.value) {
      await quotesApi.update(formQuote.value.id, apiData)
      toast.success('Presupuesto actualizado')
    } else {
      await quotesApi.create(apiData)
      toast.success('Presupuesto creado')
    }
    closeForm()
    await fetchQuotes()
  } catch (err) {
    toast.error(parseDrfErrors(err.data) || err.message || 'Error al guardar')
  }
}

const detailOpen = ref(false)
const selectedQuote = ref(null)

async function openDetail(q) {
  try {
    const data = await quotesApi.getById(q.id)
    selectedQuote.value = mapPurchaseQuoteDetailFromApi(data)
    detailOpen.value = true
  } catch (err) {
    toast.error('Error al cargar el presupuesto')
  }
}

function closeDetail() {
  detailOpen.value = false
  selectedQuote.value = null
}

async function deleteQuote(q) {
  if (!confirm(`¿Eliminar presupuesto "${q.name}"?`)) return
  try {
    await quotesApi.delete(q.id)
    toast.success('Presupuesto eliminado')
    await fetchQuotes()
  } catch (err) {
    toast.error('Error al eliminar')
  }
}

async function convertToInvoice(q) {
  try {
    await quotesApi.convertToInvoice(q.id)
    toast.success('Presupuesto convertido en factura de compra (borrador)')
    closeDetail()
    await fetchQuotes()
  } catch (err) {
    toast.error(parseDrfErrors(err.data) || err.message || 'Error al convertir')
  }
}

function statusLabel(s) {
  return {
    Draft: 'Borrador', Sent: 'Solicitado', Accepted: 'Aceptado',
    Rejected: 'Rechazado', Expired: 'Expirado', Converted: 'Convertido',
  }[s] || s
}

function statusBadgeClass(s) {
  return {
    Draft: 'badge-gray', Sent: 'badge-primary', Accepted: 'badge-success',
    Rejected: 'badge-error', Expired: 'badge-warning', Converted: 'badge-success',
  }[s] || 'badge-gray'
}

function formatCurrency(v) {
  if (v === null || v === undefined) return '—'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v)
}
function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.quotes-view { width: 100%; }
.view-header { margin-bottom: 2rem; }
.header-content { display: flex; align-items: center; justify-content: space-between; }
.title-section { display: flex; align-items: center; gap: 0.875rem; }
.view-title { font-size: 2rem; font-weight: 700; color: var(--text-primary); }
.count-badge {
  background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%);
  color: var(--text-secondary);
  padding: 0.375rem 0.875rem; border-radius: 8px;
  font-size: 1rem; font-weight: 600;
}
.header-actions { display: flex; gap: 0.75rem; }
.filters-bar { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.search-box { position: relative; flex: 1; max-width: 360px; }
.search-icon {
  position: absolute; left: 1rem; top: 50%;
  transform: translateY(-50%); color: var(--text-tertiary);
}
.search-input { padding-left: 3rem; }
.filter-select { width: auto; min-width: 160px; }
.table-card { padding: 0; overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 0.75rem; border-bottom: 1px solid var(--border-color); text-align: left; }
.table th {
  font-size: 0.7rem; text-transform: uppercase;
  color: var(--text-secondary); font-weight: 600;
  background: var(--bg-hover);
}
.table-row { cursor: pointer; transition: background var(--transition-fast); }
.table-row:hover { background: var(--bg-hover); }
.contact-cell { display: flex; align-items: center; gap: 0.5rem; }
.avatar-sm {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 0.6rem; font-weight: 700;
}
.invoice-link { color: #059669; font-weight: 600; font-family: monospace; }
.muted { color: var(--text-tertiary); }
.actions-cell { display: flex; gap: 0.25rem; }
.btn-icon {
  background: none; border: none; cursor: pointer;
  color: var(--text-tertiary); padding: 0.375rem; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
}
.btn-icon:hover { background: var(--bg-hover); color: var(--text-primary); }
.empty-row { text-align: center; padding: 2rem; color: var(--text-tertiary); }

.drawer-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: flex-end;
}
.drawer-panel {
  width: 540px; max-width: 92vw; height: 100%;
  background: white; overflow-y: auto;
  display: flex; flex-direction: column;
}
.drawer-header {
  padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border-color);
  display: flex; align-items: flex-start; justify-content: space-between;
}
.drawer-header h2 { margin: 0 0 0.5rem; font-size: 1.125rem; }
.drawer-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
.drawer-body h3 { margin: 0.5rem 0 0.5rem; font-size: 0.875rem; }
.info-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); padding: 0.25rem 0; }
.info-row.total { border-top: 1px solid var(--border-color); margin-top: 0.5rem; padding-top: 0.5rem; font-size: 1rem; }
.totals { background: var(--bg-hover); padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; }
.converted-info {
  padding: 0.75rem; background: #ecfdf5; color: #065f46;
  border-radius: 6px; font-size: var(--font-size-sm);
}
.drawer-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }

.slide-enter-active, .slide-leave-active { transition: opacity 0.2s; }
.slide-enter-from, .slide-leave-to { opacity: 0; }
</style>
