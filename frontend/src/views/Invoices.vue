<template>
  <div class="invoices-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Factures</h1>
          <span class="count-badge">{{ invoices.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="openPlansModal">
            <Repeat :size="18" />
            <span>Recurrents</span>
            <span v-if="activePlanCount" class="header-pill">{{ activePlanCount }}</span>
          </button>
          <button class="btn btn-secondary" :disabled="exporting" @click="handleExport">
            <Download :size="18" />
            <span>{{ exporting ? 'Exportant…' : 'Exportar' }}</span>
          </button>
          <button class="btn btn-primary" @click="openInvoiceForm()">
            <Plus :size="18" />
            <span>Nova factura</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- ===================== FILTERS BAR ===================== -->
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            type="text"
            class="input search-input"
            placeholder="Cerca per número o client…"
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">Tots els estats</option>
            <option value="draft">Esborrany</option>
            <option value="approved">Aprovada</option>
            <option value="partially_paid">Pagada parcialment</option>
            <option value="paid">Pagada</option>
            <option value="overdue">Vençuda</option>
            <option value="voided">Anul·lada</option>
            <option value="rectified">Rectificada</option>
          </select>
          <select class="select filter-select" v-model="customerFilter">
            <option value="all">Tots els clients</option>
            <option v-for="cust in customers" :key="cust" :value="cust">{{ cust }}</option>
          </select>
          <button class="btn btn-secondary" @click="sortInvoices">
            <ArrowUpDown :size="18" />
            <span>Ordenar</span>
          </button>
        </div>
      </div>

      <!-- ===================== BULK ACTIONS BAR ===================== -->
      <Transition name="slide-down">
        <div v-if="selectedInvoices.length > 0" class="bulk-actions-bar">
          <span class="bulk-count">{{ selectedInvoices.length }} seleccionades</span>
          <div class="bulk-buttons">
            <button class="btn btn-sm btn-secondary" @click="bulkApprove" title="Aprovar els esborranys seleccionats">
              <CheckCircle2 :size="16" />
              <span>Aprovar</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkSend" title="Enviar per correu">
              <Send :size="16" />
              <span>Enviar</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkExport" title="Exportar la selecció">
              <Download :size="16" />
              <span>Exportar</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkDelete" title="Eliminar els esborranys seleccionats" style="color: var(--error-color);">
              <Trash2 :size="16" />
              <span>Eliminar</span>
            </button>
          </div>
        </div>
      </Transition>

      <!-- ===================== TABLE ===================== -->
      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table invoices-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" class="checkbox" @change="toggleSelectAll" :checked="allSelected" />
                </th>
                <th class="col-number">Núm.</th>
                <th class="col-customer">Client</th>
                <th class="col-date">Data</th>
                <th class="col-due">Venciment</th>
                <th class="col-status">Estat</th>
                <th class="col-total">Total</th>
                <th class="col-balance">Saldo</th>
                <th class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="invoice in filteredInvoices"
                :key="invoice.id"
                class="table-row"
                @click="openDetail(invoice)"
              >
                <td class="col-checkbox" @click.stop>
                  <input type="checkbox" class="checkbox" v-model="selectedInvoices" :value="invoice.id" />
                </td>
                <td class="col-number">
                  <span class="invoice-number">{{ invoice.number || '—' }}</span>
                  <span v-if="invoice.type === 'CreditNote'" class="creditnote-hint">Nota de crèdit</span>
                </td>
                <td class="col-customer">
                  <div class="customer-cell" v-if="invoice.customer">
                    <div class="customer-avatar-sm" :style="{ background: invoice.customer.avatarColor }">
                      {{ invoice.customer.initials }}
                    </div>
                    <span class="customer-name">{{ invoice.customer.name }}</span>
                  </div>
                  <span v-else class="text-secondary">—</span>
                </td>
                <td class="col-date">
                  <span class="date-text">{{ formatDateShort(invoice.issueDate) }}</span>
                </td>
                <td class="col-due">
                  <span :class="['date-text', isOverdue(invoice) ? 'overdue-text' : '']">
                    {{ formatDateShort(invoice.dueDate) }}
                  </span>
                </td>
                <td class="col-status">
                  <span :class="['badge', statusBadgeClass(invoice)]">
                    {{ displayStatus(invoice) }}
                  </span>
                </td>
                <td class="col-total">
                  <span class="total-value">{{ formatCurrency(invoice.totalAmount) }}</span>
                </td>
                <td class="col-balance">
                  <span :class="['balance-value', invoice.balanceDue > 0 ? 'has-balance' : 'zero-balance']">
                    {{ formatCurrency(invoice.balanceDue) }}
                  </span>
                </td>
                <td class="col-actions" @click.stop>
                  <div class="actions-cell">
                    <button
                      v-if="invoice.status === 'Draft'"
                      class="btn-icon"
                      title="Editar"
                      @click="openInvoiceForm(invoice)"
                    >
                      <Pencil :size="16" />
                    </button>
                    <div class="dropdown-wrapper">
                      <button class="btn-icon" @click.stop="toggleDropdown(invoice.id)">
                        <MoreVertical :size="18" />
                      </button>
                      <Transition name="fade">
                        <div v-if="openDropdownId === invoice.id" class="dropdown-menu" @click.stop>
                          <button class="dropdown-item" @click="openDetail(invoice); closeDropdown()">
                            <Eye :size="16" />
                            <span>Veure</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item"
                            @click="openInvoiceForm(invoice); closeDropdown()"
                          >
                            <Pencil :size="16" />
                            <span>Editar</span>
                          </button>
                          <button class="dropdown-item" @click="duplicateInvoice(invoice); closeDropdown()">
                            <Copy :size="16" />
                            <span>Duplicar</span>
                          </button>
                          <button
                            v-if="invoice.type !== 'CreditNote'"
                            class="dropdown-item"
                            @click="openRecurrenceForm(invoice); closeDropdown()"
                          >
                            <Repeat :size="16" />
                            <span>Fer recurrent</span>
                          </button>
                          <div class="dropdown-divider"></div>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item"
                            @click="approveInvoice(invoice); closeDropdown()"
                          >
                            <CheckCircle2 :size="16" />
                            <span>Aprovar</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Approved' || invoice.status === 'PartiallyPaid'"
                            class="dropdown-item"
                            @click="openPaymentModal(invoice); closeDropdown()"
                          >
                            <Banknote :size="16" />
                            <span>Registrar pagament</span>
                          </button>
                          <button
                            v-if="invoice.status !== 'Draft' && invoice.status !== 'Voided'"
                            class="dropdown-item"
                            @click="sendInvoice(invoice); closeDropdown()"
                          >
                            <Send :size="16" />
                            <span>Enviar per correu</span>
                          </button>
                          <button class="dropdown-item" @click="downloadPdf(invoice); closeDropdown()">
                            <FileDown :size="16" />
                            <span>Descarregar PDF</span>
                          </button>
                          <div class="dropdown-divider"></div>
                          <button
                            v-if="['Approved','Paid','PartiallyPaid'].includes(invoice.status)"
                            class="dropdown-item"
                            @click="createRectifying(invoice); closeDropdown()"
                          >
                            <FileX :size="16" />
                            <span>Crear nota de crèdit</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Approved' && invoice.paidAmount === 0"
                            class="dropdown-item dropdown-item-danger"
                            @click="voidInvoice(invoice); closeDropdown()"
                          >
                            <Ban :size="16" />
                            <span>Anul·lar</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item dropdown-item-danger"
                            @click="deleteInvoice(invoice); closeDropdown()"
                          >
                            <Trash2 :size="16" />
                            <span>Eliminar</span>
                          </button>
                        </div>
                      </Transition>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="table-footer-info">
            Mostrant <strong>{{ filteredInvoices.length }}</strong> de <strong>{{ invoices.length }}</strong> factures
          </span>
          <div class="table-footer-summary">
            <span class="summary-item">
              Total: <strong>{{ formatCurrency(totalFiltered) }}</strong>
            </span>
            <span class="summary-item">
              Saldo: <strong :class="totalBalanceFiltered > 0 ? 'has-balance' : ''">{{ formatCurrency(totalBalanceFiltered) }}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===================== INVOICE DETAIL DRAWER ===================== -->
    <InvoiceDetailDrawer
      v-if="selectedInvoice"
      :invoice="selectedInvoice"
      :open="detailOpen"
      @close="closeDetail"
      @edit="(inv) => { closeDetail(); openInvoiceForm(inv) }"
      @approve="approveInvoice"
      @record-payment="openPaymentModal"
      @send="sendInvoice"
      @download-pdf="downloadPdf"
      @verifactu-submit="verifactuSubmit"
    />

    <!-- ===================== CREATE / EDIT MODAL ===================== -->
    <InvoiceFormModal
      :open="formModalOpen"
      :invoice="formInvoice"
      :invoices="invoices"
      :series-list="invoiceSeriesList"
      :customers="customersList"
      :preselected-customer-id="preselectedCustomerId"
      :preselected-line="preselectedLine"
      @close="closeInvoiceForm"
      @save="handleInvoiceSave"
      @customer-created="fetchCustomers"
    />

    <!-- ===================== PAYMENT MODAL ===================== -->
    <Transition name="fade">
      <div v-if="paymentModalOpen" class="modal-overlay" @click.self="closePaymentModal">
        <div class="modal-panel">
          <div class="modal-header">
            <h3>Registrar pagament</h3>
            <button class="btn-icon" @click="closePaymentModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Data</label>
              <input type="date" class="input" v-model="paymentForm.date" />
            </div>
            <div class="form-group">
              <label class="form-label">Import (EUR)</label>
              <input type="number" class="input" v-model.number="paymentForm.amount" min="0.01" :max="paymentInvoice?.balanceDue" step="0.01" />
              <span class="form-hint">Saldo pendent: {{ formatCurrency(paymentInvoice?.balanceDue) }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">Mètode</label>
              <select class="select" v-model="paymentForm.method">
                <option value="Transfer">Transferència</option>
                <option value="DirectDebit">Domiciliació</option>
                <option value="Card">Targeta</option>
                <option value="Cash">Efectiu</option>
                <option value="Other">Altres</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Referència</label>
              <input type="text" class="input" v-model="paymentForm.reference" placeholder="Núm. d'operació bancària" />
            </div>
            <div class="form-group">
              <label class="form-label">Notes</label>
              <textarea class="input" rows="2" v-model="paymentForm.notes" placeholder="Notes opcionals…"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closePaymentModal">Cancel·lar</button>
            <button class="btn btn-primary" @click="savePayment" :disabled="!paymentForm.amount || paymentForm.amount <= 0">
              <CheckCircle2 :size="18" />
              Desar pagament
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ===================== RECURRENCE MODALS ===================== -->
    <RecurrenceFormModal
      :open="recurrenceFormOpen"
      :source-invoice="recurrenceSource"
      :submitting="recurrenceSubmitting"
      @close="closeRecurrenceForm"
      @create="createRecurrence"
    />
    <RecurringPlansModal
      :open="plansModalOpen"
      :plans="plans"
      name-field="customer_name"
      @close="plansModalOpen = false"
      @run="runPlan"
      @toggle="togglePlan"
      @remove="removePlan"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  Plus, Search, ArrowUpDown, MoreVertical, Download,
  Pencil, Eye, Copy, CheckCircle2, Send,
  FileDown, Trash2, Ban, Banknote, FileX, X, Repeat
} from 'lucide-vue-next'
import InvoiceDetailDrawer from '@/components/InvoiceDetailDrawer.vue'
import InvoiceFormModal from '@/components/InvoiceFormModal.vue'
import RecurrenceFormModal from '@/components/RecurrenceFormModal.vue'
import RecurringPlansModal from '@/components/RecurringPlansModal.vue'
import invoicesApi from '@/services/invoices'
import customersApi from '@/services/customers'
import { saveBlob } from '@/services/api'
import { mapInvoiceFromApi, mapInvoiceDetailFromApi, mapInvoiceToApi, mapCustomerFromApi, parseDrfErrors } from '@/services/mappers'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const route = useRoute()
const loading = ref(false)
const exporting = ref(false)

async function handleExport() {
  if (exporting.value) return
  exporting.value = true
  try {
    const blob = await invoicesApi.export()
    const stamp = new Date().toISOString().slice(0, 10)
    saveBlob(blob, `factures-${stamp}.xlsx`)
    toast.success('Exportació generada')
  } catch (err) {
    console.error('Export failed:', err)
    toast.error(err.message || 'Error en exportar les factures')
  } finally {
    exporting.value = false
  }
}

/* ══════════════════════════════════════════
   LOAD SERIES FROM API
   ══════════════════════════════════════════ */
const invoiceSeriesList = ref([])

async function fetchSeries() {
  try {
    const data = await invoicesApi.getSeries()
    invoiceSeriesList.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    console.error('Failed to load series:', err)
    toast.error('Error en carregar les sèries de facturació')
  }
}

/* ══════════════════════════════════════════
   LOAD CUSTOMERS FROM API (for invoice form)
   ══════════════════════════════════════════ */
const customersList = ref([])

async function fetchCustomers() {
  try {
    const data = await customersApi.getAll()
    const items = Array.isArray(data) ? data : (data.results || [])
    customersList.value = items.map(mapCustomerFromApi)
  } catch (err) {
    console.error('Failed to load customers:', err)
    toast.error('Error en carregar els clients')
  }
}

/* ══════════════════════════════════════════
   LOAD INVOICES FROM API
   ══════════════════════════════════════════ */
async function fetchInvoices() {
  loading.value = true
  try {
    const data = await invoicesApi.getAll()
    const items = Array.isArray(data) ? data : data.results || []
    invoices.value = items.map(mapInvoiceFromApi)
  } catch (err) {
    console.error('Failed to load invoices:', err)
    toast.error('Error en carregar les factures')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await fetchInvoices()
  await fetchSeries()
  await fetchCustomers()
  fetchPlans()

  // Check if coming from Customers / Products page to create a new invoice
  if (route.query.newInvoice === 'true') {
    if (route.query.productName) {
      const taxN = parseFloat(route.query.productTax)
      preselectedLine.value = {
        description: route.query.productName,
        quantity: 1,
        unitPrice: parseFloat(route.query.productPrice) || 0,
        tax: [21, 10, 4].includes(taxN) ? `IVA ${taxN}%` : 'IVA 21%',
      }
    }
    let customerId = null
    if (route.query.customerId) {
      const id = parseInt(route.query.customerId)
      if (customersList.value.find(c => c.id === id)) customerId = id
    }
    openInvoiceForm(null, customerId)
  }
})

/* ══════════════════════════════════════════
   DRAWER STATE
   ══════════════════════════════════════════ */
const detailOpen = ref(false)
const selectedInvoice = ref(null)

async function openDetail(invoice) {
  try {
    const data = await invoicesApi.getById(invoice.id)
    selectedInvoice.value = mapInvoiceDetailFromApi(data)
    detailOpen.value = true
  } catch {
    selectedInvoice.value = invoice
    detailOpen.value = true
  }
  closeDropdown()
}

function closeDetail() {
  detailOpen.value = false
}

/* ══════════════════════════════════════════
   FORM MODAL STATE
   ══════════════════════════════════════════ */
const formModalOpen = ref(false)
const formInvoice = ref(null)
const preselectedCustomerId = ref(null)
const preselectedLine = ref(null)

function openInvoiceForm(invoice = null, customerId = null) {
  formInvoice.value = invoice
  preselectedCustomerId.value = customerId
  formModalOpen.value = true
}

function closeInvoiceForm() {
  formModalOpen.value = false
  formInvoice.value = null
  preselectedCustomerId.value = null
  preselectedLine.value = null
}

async function handleInvoiceSave(data) {
  const apiData = mapInvoiceToApi(data)
  try {
    if (formInvoice.value) {
      await invoicesApi.update(formInvoice.value.id, apiData)
      toast.success('Factura actualitzada')
    } else {
      const created = await invoicesApi.create(apiData)
      if (data.status === 'Approved' && created?.id) {
        await invoicesApi.approve(created.id)
        toast.success('Factura creada i aprovada')
      } else {
        toast.success('Factura creada')
      }
      if (data.recurrence && created?.id) {
        try {
          await invoicesApi.createRecurring({ source_invoice: created.id, ...data.recurrence })
          toast.success('Recurrència programada')
          await fetchPlans()
        } catch (err) {
          toast.error(err.data?.detail || err.message || 'Factura creada, però ha fallat la recurrència')
        }
      }
    }
    await fetchInvoices()
  } catch (err) {
    toast.error(parseDrfErrors(err.data) || err.message || 'Error en desar la factura')
  }
  formInvoice.value = null
}

/* ══════════════════════════════════════════
   PAYMENT MODAL STATE
   ══════════════════════════════════════════ */
const paymentModalOpen = ref(false)
const paymentInvoice = ref(null)
const paymentForm = ref({
  date: new Date().toISOString().split('T')[0],
  amount: 0,
  method: 'Transfer',
  reference: '',
  notes: ''
})

function openPaymentModal(invoice) {
  paymentInvoice.value = invoice
  paymentForm.value = {
    date: new Date().toISOString().split('T')[0],
    amount: invoice.balanceDue,
    method: 'Transfer',
    reference: '',
    notes: ''
  }
  paymentModalOpen.value = true
}

function closePaymentModal() {
  paymentModalOpen.value = false
  paymentInvoice.value = null
}

async function savePayment() {
  if (!paymentInvoice.value || !paymentForm.value.amount) return
  try {
    await invoicesApi.createPayment(paymentInvoice.value.id, {
      date: paymentForm.value.date,
      amount: paymentForm.value.amount,
      method: paymentForm.value.method,
      reference: paymentForm.value.reference || '',
      notes: paymentForm.value.notes || ''
    })
    toast.success('Pagament registrat')
    closePaymentModal()
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en registrar el pagament')
  }
}

/* ══════════════════════════════════════════
   RECURRENCE STATE
   ══════════════════════════════════════════ */
const plans = ref([])
const plansModalOpen = ref(false)
const recurrenceFormOpen = ref(false)
const recurrenceSource = ref(null)
const recurrenceSubmitting = ref(false)

const activePlanCount = computed(() => plans.value.filter(p => p.active).length)

async function fetchPlans() {
  try {
    const data = await invoicesApi.listRecurring()
    plans.value = Array.isArray(data) ? data : (data.results || [])
  } catch (err) {
    console.error('Failed to load recurring plans:', err)
  }
}

function openPlansModal() {
  plansModalOpen.value = true
  fetchPlans()
}

function openRecurrenceForm(invoice) {
  recurrenceSource.value = invoice
  recurrenceFormOpen.value = true
}

function closeRecurrenceForm() {
  recurrenceFormOpen.value = false
  recurrenceSource.value = null
}

async function createRecurrence(payload) {
  recurrenceSubmitting.value = true
  try {
    await invoicesApi.createRecurring(payload)
    toast.success('Recurrència creada')
    closeRecurrenceForm()
    await fetchPlans()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en crear la recurrència')
  } finally {
    recurrenceSubmitting.value = false
  }
}

async function runPlan(plan) {
  try {
    await invoicesApi.runRecurring(plan.id)
    toast.success('Factura generada')
    await Promise.all([fetchPlans(), fetchInvoices()])
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en generar la factura')
  }
}

async function togglePlan(plan) {
  try {
    await invoicesApi.updateRecurring(plan.id, { active: !plan.active })
    await fetchPlans()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en actualitzar el pla')
  }
}

async function removePlan(plan) {
  try {
    await invoicesApi.deleteRecurring(plan.id)
    toast.success('Recurrència eliminada')
    await fetchPlans()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en eliminar el pla')
  }
}

/* ══════════════════════════════════════════
   DROPDOWN STATE
   ══════════════════════════════════════════ */
const openDropdownId = ref(null)

function toggleDropdown(id) {
  openDropdownId.value = openDropdownId.value === id ? null : id
}

function closeDropdown() {
  openDropdownId.value = null
}

/* ══════════════════════════════════════════
   TABLE STATE
   ══════════════════════════════════════════ */
const searchQuery = ref('')
const statusFilter = ref('all')
const customerFilter = ref('all')
const selectedInvoices = ref([])
const sortAsc = ref(false)

/* ══════════════════════════════════════════
   ACTIONS (API)
   ══════════════════════════════════════════ */
async function approveInvoice(invoice) {
  if (invoice.status !== 'Draft') return
  try {
    await invoicesApi.approve(invoice.id)
    toast.success('Factura aprovada')
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en aprovar la factura')
  }
}

async function duplicateInvoice(invoice) {
  try {
    await invoicesApi.duplicate(invoice.id)
    toast.success('Factura duplicada')
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en duplicar la factura')
  }
}

async function deleteInvoice(invoice) {
  if (invoice.status !== 'Draft') return
  try {
    await invoicesApi.delete(invoice.id)
    invoices.value = invoices.value.filter(i => i.id !== invoice.id)
    selectedInvoices.value = selectedInvoices.value.filter(id => id !== invoice.id)
    toast.success('Factura eliminada')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en eliminar la factura')
  }
}

async function voidInvoice(invoice) {
  if (invoice.status !== 'Approved' || invoice.paidAmount > 0) return
  try {
    await invoicesApi.void(invoice.id)
    toast.success('Factura anul·lada')
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en anul·lar la factura')
  }
}

async function createRectifying(invoice) {
  try {
    await invoicesApi.rectify(invoice.id)
    toast.success('Nota de crèdit creada')
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en crear la nota de crèdit')
  }
}

async function sendInvoice(invoice) {
  try {
    await invoicesApi.send(invoice.id)
    toast.success('Factura enviada per correu')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en enviar la factura')
  }
}

async function downloadPdf(invoice) {
  try {
    const blob = await invoicesApi.downloadPdf(invoice.id)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${invoice.number || 'invoice'}.pdf`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en descarregar el PDF')
  }
}

async function verifactuSubmit(invoice) {
  try {
    const res = await invoicesApi.verifactuSubmit(invoice.id)
    toast.success(`VERI*FACTU enviat — CSV: ${res.csv || 'OK'}`)
    await fetchInvoices()
    if (selectedInvoice.value?.id === invoice.id) {
      selectedInvoice.value = { ...selectedInvoice.value, estadoAeat: res.estado || 'Aceptado', verifactuCsv: res.csv || '' }
    }
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en enviar a l\'AEAT')
  }
}

/* Bulk actions */
async function bulkApprove() {
  const draftIds = invoices.value
    .filter(i => selectedInvoices.value.includes(i.id) && i.status === 'Draft')
    .map(i => i.id)
  if (!draftIds.length) return
  try {
    await invoicesApi.bulkApprove(draftIds)
    toast.success(`${draftIds.length} factures aprovades`)
    selectedInvoices.value = []
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en l\'aprovació massiva')
  }
}

async function bulkSend() {
  const ids = invoices.value
    .filter(i => selectedInvoices.value.includes(i.id) && i.status !== 'Draft')
    .map(i => i.id)
  for (const id of ids) {
    try { await invoicesApi.send(id) } catch { /* skip */ }
  }
  toast.success('Factures enviades')
  selectedInvoices.value = []
}

async function bulkExport() {
  if (!selectedInvoices.value.length) return
  try {
    const blob = await invoicesApi.export({ ids: selectedInvoices.value.join(',') })
    const stamp = new Date().toISOString().slice(0, 10)
    saveBlob(blob, `factures-seleccio-${stamp}.xlsx`)
    toast.success(`${selectedInvoices.value.length} factures exportades`)
    selectedInvoices.value = []
  } catch (err) {
    console.error('Bulk export failed:', err)
    toast.error(err.message || 'Error en exportar les factures')
  }
}

async function bulkDelete() {
  const draftIds = invoices.value
    .filter(i => selectedInvoices.value.includes(i.id) && i.status === 'Draft')
    .map(i => i.id)
  if (!draftIds.length) return
  try {
    await invoicesApi.bulkDelete(draftIds)
    toast.success(`${draftIds.length} factures eliminades`)
    selectedInvoices.value = []
    await fetchInvoices()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en l\'eliminació massiva')
  }
}

/* ══════════════════════════════════════════
   INVOICES DATA (loaded from API)
   ══════════════════════════════════════════ */
const invoices = ref([])

/* ══════════════════════════════════════════
   COMPUTED
   ══════════════════════════════════════════ */
const customers = computed(() => {
  const names = [...new Set(invoices.value.map(i => i.customer?.name).filter(Boolean))]
  return names.sort()
})

const allSelected = computed(() => {
  return filteredInvoices.value.length > 0 && selectedInvoices.value.length === filteredInvoices.value.length
})

const filteredInvoices = computed(() => {
  let result = invoices.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(i =>
      (i.number && i.number.toLowerCase().includes(q)) ||
      i.customer.name.toLowerCase().includes(q) ||
      String(i.totalAmount).includes(q)
    )
  }

  if (statusFilter.value !== 'all') {
    if (statusFilter.value === 'overdue') {
      result = result.filter(i => isOverdue(i))
    } else if (statusFilter.value === 'partially_paid') {
      result = result.filter(i => i.status === 'PartiallyPaid')
    } else {
      result = result.filter(i => i.status.toLowerCase() === statusFilter.value)
    }
  }

  if (customerFilter.value !== 'all') {
    result = result.filter(i => i.customer.name === customerFilter.value)
  }

  // Sort by issue date
  result = [...result].sort((a, b) => {
    const dateA = new Date(a.issueDate)
    const dateB = new Date(b.issueDate)
    return sortAsc.value ? dateA - dateB : dateB - dateA
  })

  return result
})

const totalFiltered = computed(() => {
  return filteredInvoices.value.reduce((sum, i) => sum + i.totalAmount, 0)
})

const totalBalanceFiltered = computed(() => {
  return filteredInvoices.value.reduce((sum, i) => sum + i.balanceDue, 0)
})

/* ══════════════════════════════════════════
   ACTIONS
   ══════════════════════════════════════════ */
function toggleSelectAll() {
  if (allSelected.value) {
    selectedInvoices.value = []
  } else {
    selectedInvoices.value = filteredInvoices.value.map(i => i.id)
  }
}

function sortInvoices() {
  sortAsc.value = !sortAsc.value
}

/* ══════════════════════════════════════════
   HELPERS
   ══════════════════════════════════════════ */
function isOverdue(invoice) {
  if (!['Approved', 'PartiallyPaid'].includes(invoice.status)) return false
  return new Date(invoice.dueDate) < new Date()
}

function displayStatus(invoice) {
  if (isOverdue(invoice)) return 'Vençuda'
  const map = {
    Draft: 'Esborrany',
    Approved: 'Aprovada',
    PartiallyPaid: 'Parcial',
    Paid: 'Pagada',
    Voided: 'Anul·lada',
    Rectified: 'Rectificada'
  }
  return map[invoice.status] || invoice.status
}

function statusBadgeClass(invoice) {
  if (isOverdue(invoice)) return 'badge-error'
  const map = {
    Draft: 'badge-gray',
    Approved: 'badge-primary',
    PartiallyPaid: 'badge-warning',
    Paid: 'badge-success',
    Voided: 'badge-gray',
    Rectified: 'badge-gray'
  }
  return map[invoice.status] || 'badge-gray'
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDateShort(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ca-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.invoices-view {
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

.header-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 0.35rem;
  margin-left: 0.1rem;
  font-size: 0.6875rem;
  font-weight: 700;
  border-radius: 9px;
  background: var(--primary-color);
  color: white;
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
   BULK ACTIONS
   ============================ */
.bulk-actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--primary-light);
  border: 1px solid var(--primary-color);
  border-radius: var(--border-radius-sm);
  margin-bottom: 1rem;
}

.bulk-count {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--primary-color);
}

.bulk-buttons {
  display: flex;
  gap: 0.5rem;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
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

.invoices-table {
  min-width: 900px;
}

.invoices-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.invoices-table td {
  padding: 0.625rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.col-checkbox { width: 40px; text-align: center; }
.col-number { min-width: 140px; }
.col-customer { min-width: 180px; }
.col-date { width: 100px; }
.col-due { width: 100px; }
.col-status { width: 100px; }
.col-total { width: 110px; }
.col-balance { width: 110px; }
.col-actions { width: 80px; }

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
.invoice-number {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--primary-color);
  background: var(--primary-light);
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
}

.creditnote-hint {
  display: block;
  font-size: 0.625rem;
  color: var(--text-tertiary);
  margin-top: 2px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.customer-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.customer-avatar-sm {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
  flex-shrink: 0;
}

.customer-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.date-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.overdue-text {
  color: var(--error-color) !important;
  font-weight: 600;
}

.total-value {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.balance-value {
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.has-balance {
  color: var(--warning-color);
}

.zero-balance {
  color: var(--text-tertiary);
}

.actions-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
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

/* ============================
   DROPDOWN MENU
   ============================ */
.dropdown-wrapper {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  z-index: 50;
  min-width: 200px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-lg);
  padding: 0.375rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
  color: var(--text-primary);
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background var(--transition-fast);
  text-align: left;
}

.dropdown-item:hover {
  background: var(--bg-hover);
}

.dropdown-item-danger {
  color: var(--error-color);
}

.dropdown-item-danger:hover {
  background: var(--error-light);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0.25rem 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================
   TABLE FOOTER
   ============================ */
.table-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.table-footer-info {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.table-footer-summary {
  display: flex;
  gap: 1.5rem;
}

.summary-item {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.summary-item strong {
  color: var(--text-primary);
}

/* ============================
   PAYMENT MODAL
   ============================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-panel {
  width: 460px;
  max-width: 92vw;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.form-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
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
