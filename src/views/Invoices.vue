<template>
  <div class="invoices-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Invoices</h1>
          <span class="count-badge">{{ invoices.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Export</span>
          </button>
          <button class="btn btn-primary" @click="openInvoiceForm()">
            <Plus :size="18" />
            <span>New invoice</span>
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
            placeholder="Search by number, customer..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <select class="select filter-select" v-model="statusFilter">
            <option value="all">All statuses</option>
            <option value="draft">Draft</option>
            <option value="approved">Approved</option>
            <option value="partially_paid">Partially paid</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="voided">Voided</option>
            <option value="rectified">Rectified</option>
          </select>
          <select class="select filter-select" v-model="customerFilter">
            <option value="all">All customers</option>
            <option v-for="cust in customers" :key="cust" :value="cust">{{ cust }}</option>
          </select>
          <select class="select filter-select" v-model="seriesFilter">
            <option value="all">All series</option>
            <option v-for="s in seriesList" :key="s" :value="s">{{ s }}</option>
          </select>
          <button class="btn btn-secondary" @click="sortInvoices">
            <ArrowUpDown :size="18" />
            <span>Sort</span>
          </button>
        </div>
      </div>

      <!-- ===================== BULK ACTIONS BAR ===================== -->
      <Transition name="slide-down">
        <div v-if="selectedInvoices.length > 0" class="bulk-actions-bar">
          <span class="bulk-count">{{ selectedInvoices.length }} selected</span>
          <div class="bulk-buttons">
            <button class="btn btn-sm btn-secondary" @click="bulkApprove" title="Approve selected drafts">
              <CheckCircle2 :size="16" />
              <span>Approve</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkSend" title="Send by email">
              <Send :size="16" />
              <span>Send</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkExport" title="Export selected">
              <Download :size="16" />
              <span>Export</span>
            </button>
            <button class="btn btn-sm btn-secondary" @click="bulkDelete" title="Delete selected drafts" style="color: var(--error-color);">
              <Trash2 :size="16" />
              <span>Delete</span>
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
                <th class="col-number">Nº</th>
                <th class="col-customer">Customer</th>
                <th class="col-date">Date</th>
                <th class="col-due">Due date</th>
                <th class="col-status">Status</th>
                <th class="col-total">Total</th>
                <th class="col-balance">Balance</th>
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
                  <span v-if="invoice.type === 'CreditNote'" class="creditnote-hint">Credit note</span>
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
                      title="Edit"
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
                            <span>View</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item"
                            @click="openInvoiceForm(invoice); closeDropdown()"
                          >
                            <Pencil :size="16" />
                            <span>Edit</span>
                          </button>
                          <button class="dropdown-item" @click="duplicateInvoice(invoice); closeDropdown()">
                            <Copy :size="16" />
                            <span>Duplicate</span>
                          </button>
                          <div class="dropdown-divider"></div>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item"
                            @click="approveInvoice(invoice); closeDropdown()"
                          >
                            <CheckCircle2 :size="16" />
                            <span>Approve</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Approved' || invoice.status === 'PartiallyPaid'"
                            class="dropdown-item"
                            @click="openPaymentModal(invoice); closeDropdown()"
                          >
                            <Banknote :size="16" />
                            <span>Record payment</span>
                          </button>
                          <button
                            v-if="invoice.status !== 'Draft' && invoice.status !== 'Voided'"
                            class="dropdown-item"
                            @click="sendInvoice(invoice); closeDropdown()"
                          >
                            <Send :size="16" />
                            <span>Send by email</span>
                          </button>
                          <button class="dropdown-item" @click="downloadPdf(invoice); closeDropdown()">
                            <FileDown :size="16" />
                            <span>Download PDF</span>
                          </button>
                          <div class="dropdown-divider"></div>
                          <button
                            v-if="['Approved','Paid','PartiallyPaid'].includes(invoice.status)"
                            class="dropdown-item"
                            @click="createRectifying(invoice); closeDropdown()"
                          >
                            <FileX :size="16" />
                            <span>Create credit note</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Approved' && invoice.paidAmount === 0"
                            class="dropdown-item dropdown-item-danger"
                            @click="voidInvoice(invoice); closeDropdown()"
                          >
                            <Ban :size="16" />
                            <span>Void</span>
                          </button>
                          <button
                            v-if="invoice.status === 'Draft'"
                            class="dropdown-item dropdown-item-danger"
                            @click="deleteInvoice(invoice); closeDropdown()"
                          >
                            <Trash2 :size="16" />
                            <span>Delete</span>
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
            Showing <strong>{{ filteredInvoices.length }}</strong> of <strong>{{ invoices.length }}</strong> invoices
          </span>
          <div class="table-footer-summary">
            <span class="summary-item">
              Total: <strong>{{ formatCurrency(totalFiltered) }}</strong>
            </span>
            <span class="summary-item">
              Balance: <strong :class="totalBalanceFiltered > 0 ? 'has-balance' : ''">{{ formatCurrency(totalBalanceFiltered) }}</strong>
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
    />

    <!-- ===================== CREATE / EDIT MODAL ===================== -->
    <InvoiceFormModal
      :open="formModalOpen"
      :invoice="formInvoice"
      :invoices="invoices"
      @close="closeInvoiceForm"
      @save="handleInvoiceSave"
    />

    <!-- ===================== PAYMENT MODAL ===================== -->
    <Transition name="fade">
      <div v-if="paymentModalOpen" class="modal-overlay" @click.self="closePaymentModal">
        <div class="modal-panel">
          <div class="modal-header">
            <h3>Record payment</h3>
            <button class="btn-icon" @click="closePaymentModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Date</label>
              <input type="date" class="input" v-model="paymentForm.date" />
            </div>
            <div class="form-group">
              <label class="form-label">Amount (EUR)</label>
              <input type="number" class="input" v-model.number="paymentForm.amount" min="0.01" :max="paymentInvoice?.balanceDue" step="0.01" />
              <span class="form-hint">Balance due: {{ formatCurrency(paymentInvoice?.balanceDue) }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">Method</label>
              <select class="select" v-model="paymentForm.method">
                <option value="Transfer">Transfer</option>
                <option value="DirectDebit">Direct debit</option>
                <option value="Card">Card</option>
                <option value="Cash">Cash</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Reference</label>
              <input type="text" class="input" v-model="paymentForm.reference" placeholder="Bank operation nº" />
            </div>
            <div class="form-group">
              <label class="form-label">Notes</label>
              <textarea class="input" rows="2" v-model="paymentForm.notes" placeholder="Optional notes..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closePaymentModal">Cancel</button>
            <button class="btn btn-primary" @click="savePayment" :disabled="!paymentForm.amount || paymentForm.amount <= 0">
              <CheckCircle2 :size="18" />
              Save payment
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Plus, Search, ArrowUpDown, MoreVertical, Download,
  Pencil, Eye, Copy, CheckCircle2, Send,
  FileDown, Trash2, Ban, Banknote, FileX, X
} from 'lucide-vue-next'
import InvoiceDetailDrawer from '@/components/InvoiceDetailDrawer.vue'
import InvoiceFormModal from '@/components/InvoiceFormModal.vue'

/* ══════════════════════════════════════════
   DRAWER STATE
   ══════════════════════════════════════════ */
const detailOpen = ref(false)
const selectedInvoice = ref(null)

function openDetail(invoice) {
  selectedInvoice.value = invoice
  detailOpen.value = true
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

function openInvoiceForm(invoice = null) {
  formInvoice.value = invoice
  formModalOpen.value = true
}

function closeInvoiceForm() {
  formModalOpen.value = false
  formInvoice.value = null
}

function handleInvoiceSave(data) {
  if (formInvoice.value) {
    // Editing — update in place
    const idx = invoices.value.findIndex(i => i.id === formInvoice.value.id)
    if (idx !== -1) {
      invoices.value[idx] = data
    }
  } else {
    // Creating — prepend
    invoices.value.unshift(data)
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

function savePayment() {
  if (!paymentInvoice.value || !paymentForm.value.amount) return

  const inv = paymentInvoice.value
  const amt = Math.min(paymentForm.value.amount, inv.balanceDue)

  inv.payments.push({
    id: Date.now(),
    date: paymentForm.value.date,
    amount: amt,
    method: paymentForm.value.method,
    reference: paymentForm.value.reference || null,
    notes: paymentForm.value.notes || null
  })

  inv.paidAmount += amt
  inv.balanceDue = Math.max(0, inv.totalAmount - inv.paidAmount)

  if (inv.balanceDue === 0) {
    inv.status = 'Paid'
    inv.timeline.unshift({ type: 'paid', action: 'Invoice fully paid', actor: 'You', date: paymentForm.value.date })
  } else {
    inv.status = 'PartiallyPaid'
    inv.timeline.unshift({ type: 'payment', action: `Partial payment of ${formatCurrency(amt)}`, actor: 'You', date: paymentForm.value.date })
  }

  closePaymentModal()
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
const seriesFilter = ref('all')
const selectedInvoices = ref([])
const sortAsc = ref(false) // newest first by default

/* ══════════════════════════════════════════
   ACTIONS (mock)
   ══════════════════════════════════════════ */
function approveInvoice(invoice) {
  if (invoice.status !== 'Draft') return
  invoice.status = 'Approved'
  invoice.lockedAt = new Date().toISOString()
  // If totalAmount is 0, auto-mark as Paid
  if (invoice.totalAmount === 0) {
    invoice.status = 'Paid'
  }
  invoice.timeline.unshift({ type: 'approved', action: 'Invoice approved', actor: 'You', date: new Date().toISOString().split('T')[0] })
  console.log('Invoice approved:', invoice.number)
}

function duplicateInvoice(invoice) {
  const dup = JSON.parse(JSON.stringify(invoice))
  dup.id = Date.now()
  dup.number = null
  dup.status = 'Draft'
  dup.paidAmount = 0
  dup.balanceDue = dup.totalAmount
  dup.payments = []
  dup.lockedAt = null
  dup.timeline = [{ type: 'created', action: 'Draft created (duplicate)', actor: 'You', date: new Date().toISOString().split('T')[0] }]
  invoices.value.unshift(dup)
  console.log('Invoice duplicated from:', invoice.number)
}

function deleteInvoice(invoice) {
  if (invoice.status !== 'Draft') return
  invoices.value = invoices.value.filter(i => i.id !== invoice.id)
  selectedInvoices.value = selectedInvoices.value.filter(id => id !== invoice.id)
  console.log('Invoice deleted:', invoice.id)
}

function voidInvoice(invoice) {
  if (invoice.status !== 'Approved' || invoice.paidAmount > 0) return
  invoice.status = 'Voided'
  invoice.timeline.unshift({ type: 'voided', action: 'Invoice voided', actor: 'You', date: new Date().toISOString().split('T')[0] })
  console.log('Invoice voided:', invoice.number)
}

function createRectifying(invoice) {
  console.log('Create credit note for:', invoice.number)
  // TODO: opens editor with credit note type + rectifiedInvoiceId
}

function sendInvoice(invoice) {
  invoice.timeline.unshift({ type: 'sent', action: `Sent by email to ${invoice.customer?.email ?? '—'}`, actor: 'You', date: new Date().toISOString().split('T')[0] })
  console.log('Invoice sent:', invoice.number, '→', invoice.customer?.email)
}

function downloadPdf(invoice) {
  console.log('Download PDF:', invoice.number)
}

/* Bulk actions */
function bulkApprove() {
  invoices.value.filter(i => selectedInvoices.value.includes(i.id) && i.status === 'Draft')
    .forEach(i => approveInvoice(i))
  selectedInvoices.value = []
}

function bulkSend() {
  invoices.value.filter(i => selectedInvoices.value.includes(i.id) && i.status !== 'Draft')
    .forEach(i => sendInvoice(i))
  selectedInvoices.value = []
}

function bulkExport() {
  console.log('Export invoices:', selectedInvoices.value)
  selectedInvoices.value = []
}

function bulkDelete() {
  const drafts = invoices.value.filter(i => selectedInvoices.value.includes(i.id) && i.status === 'Draft').map(i => i.id)
  invoices.value = invoices.value.filter(i => !drafts.includes(i.id))
  selectedInvoices.value = []
}

/* ══════════════════════════════════════════
   INVOICES DATA
   ══════════════════════════════════════════ */
const invoices = ref([
  {
    id: 1,
    type: 'Standard',
    status: 'Paid',
    series: 'FAC',
    number: 'FAC-2026-0001',
    customer: {
      id: 1, name: 'Acme Corp.', vatId: 'B-12345678', email: 'contact@acmecorp.com',
      avatarColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', initials: 'AC'
    },
    issueDate: '2026-01-05',
    dueDate: '2026-02-04',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Camiseta Algodón Orgánico', quantity: 50, unitPrice: 22.00, discount: '5%', tax: 'IVA 21%', subtotal: 1045.00 },
      { id: 2, description: 'Gorra Canvas', quantity: 20, unitPrice: 14.50, discount: null, tax: 'IVA 21%', subtotal: 290.00 }
    ],
    subtotal: 1335.00,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 1335.00, amount: 280.35, isRetention: false }],
    totalTax: 280.35,
    totalAmount: 1615.35,
    paidAmount: 1615.35,
    balanceDue: 0,
    payments: [
      { id: 1, date: '2026-02-02', amount: 1615.35, method: 'Transfer', reference: 'OP-20260202-001' }
    ],
    customerNotes: 'Entrega en almacén central, horario 9-14h.',
    internalNotes: 'Cliente prioritario — descuento mayorista aplicado.',
    lockedAt: '2026-01-05T14:30:00',
    timeline: [
      { type: 'paid', action: 'Payment received — fully paid', actor: 'Ana G.', date: '2026-02-02' },
      { type: 'sent', action: 'Sent by email to contact@acmecorp.com', actor: 'Ana G.', date: '2026-01-05' },
      { type: 'approved', action: 'Invoice approved', actor: 'Ana G.', date: '2026-01-05' },
      { type: 'created', action: 'Draft created', actor: 'Carlos M.', date: '2026-01-05' }
    ]
  },
  {
    id: 2,
    type: 'Standard',
    status: 'Approved',
    series: 'FAC',
    number: 'FAC-2026-0002',
    customer: {
      id: 3, name: 'Oficinas Modernas S.L.', vatId: 'B-87654321', email: 'admin@oficinasmodernas.es',
      avatarColor: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)', initials: 'OM'
    },
    issueDate: '2026-01-15',
    dueDate: '2026-02-14',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Silla Ergonómica Oficina – Black', quantity: 3, unitPrice: 295.00, discount: null, tax: 'IVA 21%', subtotal: 885.00 },
      { id: 2, description: 'Mesa Standing Desk', quantity: 3, unitPrice: 420.00, discount: '10%', tax: 'IVA 21%', subtotal: 1134.00 }
    ],
    subtotal: 2019.00,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 2019.00, amount: 423.99, isRetention: false }],
    totalTax: 423.99,
    totalAmount: 2442.99,
    paidAmount: 0,
    balanceDue: 2442.99,
    payments: [],
    customerNotes: 'Montar en oficina planta 3. Contactar con Carlos Méndez.',
    internalNotes: '',
    lockedAt: '2026-01-15T11:00:00',
    timeline: [
      { type: 'sent', action: 'Sent by email to admin@oficinasmodernas.es', actor: 'Ana G.', date: '2026-01-15' },
      { type: 'approved', action: 'Invoice approved', actor: 'Ana G.', date: '2026-01-15' },
      { type: 'created', action: 'Draft created', actor: 'Carlos M.', date: '2026-01-14' }
    ]
  },
  {
    id: 3,
    type: 'Standard',
    status: 'PartiallyPaid',
    series: 'FAC',
    number: 'FAC-2026-0003',
    customer: {
      id: 7, name: 'Café Molino', vatId: 'B-11223344', email: 'info@cafemolino.es',
      avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #10B981 100%)', initials: 'CM'
    },
    issueDate: '2026-01-20',
    dueDate: '2026-02-19',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Café Arábica Premium 1kg', quantity: 100, unitPrice: 15.00, discount: null, tax: 'IVA 10%', subtotal: 1500.00 },
      { id: 2, description: 'Diseño de Logo Profesional – Standard', quantity: 1, unitPrice: 250.00, discount: null, tax: 'IVA 21%', subtotal: 250.00 }
    ],
    subtotal: 1750.00,
    discountAmount: 0,
    taxSummary: [
      { name: 'IVA 10%', base: 1500.00, amount: 150.00, isRetention: false },
      { name: 'IVA 21%', base: 250.00, amount: 52.50, isRetention: false }
    ],
    totalTax: 202.50,
    totalAmount: 1952.50,
    paidAmount: 1000.00,
    balanceDue: 952.50,
    payments: [
      { id: 1, date: '2026-02-01', amount: 1000.00, method: 'Transfer', reference: 'OP-CM-001' }
    ],
    customerNotes: '',
    internalNotes: 'Awaiting second payment. Follow up next week.',
    lockedAt: '2026-01-20T09:15:00',
    timeline: [
      { type: 'payment', action: 'Partial payment of 1.000,00 €', actor: 'Ana G.', date: '2026-02-01' },
      { type: 'sent', action: 'Sent by email to info@cafemolino.es', actor: 'Ana G.', date: '2026-01-20' },
      { type: 'approved', action: 'Invoice approved', actor: 'Ana G.', date: '2026-01-20' },
      { type: 'created', action: 'Draft created', actor: 'Ana G.', date: '2026-01-19' }
    ]
  },
  {
    id: 4,
    type: 'Standard',
    status: 'Draft',
    series: 'FAC',
    number: null,
    customer: {
      id: 9, name: 'Luis Fernández', vatId: null, email: 'lfernandez@outlook.com',
      avatarColor: 'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)', initials: 'LF'
    },
    issueDate: '2026-02-14',
    dueDate: '2026-03-16',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Zapatillas Running Pro – 42 Black/Red', quantity: 2, unitPrice: 89.95, discount: null, tax: 'IVA 21%', subtotal: 179.90 },
      { id: 2, description: 'Calcetines Técnicos', quantity: 4, unitPrice: 12.50, discount: '10%', tax: 'IVA 21%', subtotal: 45.00 }
    ],
    subtotal: 224.90,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 224.90, amount: 47.23, isRetention: false }],
    totalTax: 47.23,
    totalAmount: 272.13,
    paidAmount: 0,
    balanceDue: 272.13,
    payments: [],
    customerNotes: '',
    internalNotes: 'Pending approval. Customer requested express shipping.',
    lockedAt: null,
    timeline: [
      { type: 'created', action: 'Draft created', actor: 'Carlos M.', date: '2026-02-14' }
    ]
  },
  {
    id: 5,
    type: 'Standard',
    status: 'Approved',
    series: 'FAC',
    number: 'FAC-2026-0004',
    customer: {
      id: 10, name: 'TechParts Ibérica S.A.', vatId: 'A-99887766', email: 'ventas@techparts.es',
      avatarColor: 'linear-gradient(135deg, #667eea 0%, #10B981 100%)', initials: 'TI'
    },
    issueDate: '2026-02-01',
    dueDate: '2026-03-03',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Auriculares Bluetooth NC – Black', quantity: 5, unitPrice: 129.00, discount: null, tax: 'IVA 21%', subtotal: 645.00 }
    ],
    subtotal: 645.00,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 645.00, amount: 135.45, isRetention: false }],
    totalTax: 135.45,
    totalAmount: 780.45,
    paidAmount: 0,
    balanceDue: 780.45,
    payments: [],
    customerNotes: 'Enviar con albarán firmado.',
    internalNotes: '',
    lockedAt: '2026-02-01T16:00:00',
    timeline: [
      { type: 'approved', action: 'Invoice approved', actor: 'Ana G.', date: '2026-02-01' },
      { type: 'created', action: 'Draft created', actor: 'Carlos M.', date: '2026-02-01' }
    ]
  },
  {
    id: 6,
    type: 'Standard',
    status: 'Paid',
    series: 'SRV',
    number: 'SRV-2026-0001',
    customer: {
      id: 1, name: 'Acme Corp.', vatId: 'B-12345678', email: 'contact@acmecorp.com',
      avatarColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', initials: 'AC'
    },
    issueDate: '2026-01-01',
    dueDate: '2026-01-31',
    paymentMethod: 'Direct debit',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Consultoría SEO Mensual – Enero 2026', quantity: 1, unitPrice: 450.00, discount: null, tax: 'IVA 21%', subtotal: 450.00 }
    ],
    subtotal: 450.00,
    discountAmount: 0,
    taxSummary: [
      { name: 'IVA 21%', base: 450.00, amount: 94.50, isRetention: false },
      { name: 'IRPF -15%', base: 450.00, amount: 67.50, isRetention: true }
    ],
    totalTax: 94.50,
    totalAmount: 477.00,
    paidAmount: 477.00,
    balanceDue: 0,
    payments: [
      { id: 1, date: '2026-01-28', amount: 477.00, method: 'DirectDebit', reference: 'DD-ACM-2026-01' }
    ],
    customerNotes: 'Servicio recurrente mensual.',
    internalNotes: 'Auto-generated from recurring profile RP-001.',
    lockedAt: '2026-01-01T08:00:00',
    timeline: [
      { type: 'paid', action: 'Payment received via direct debit', actor: 'System', date: '2026-01-28' },
      { type: 'sent', action: 'Sent by email to contact@acmecorp.com', actor: 'System', date: '2026-01-01' },
      { type: 'approved', action: 'Auto-approved (recurring)', actor: 'System', date: '2026-01-01' },
      { type: 'created', action: 'Generated from recurring profile', actor: 'System', date: '2026-01-01' }
    ]
  },
  {
    id: 7,
    type: 'Standard',
    status: 'Voided',
    series: 'FAC',
    number: 'FAC-2026-0005',
    customer: {
      id: 12, name: 'Elena Vidal', vatId: null, email: 'elena.vidal@email.com',
      avatarColor: 'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)', initials: 'EV'
    },
    issueDate: '2026-02-05',
    dueDate: '2026-03-07',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Mochila Urbana 25L', quantity: 2, unitPrice: 54.50, discount: null, tax: 'IVA 21%', subtotal: 109.00 }
    ],
    subtotal: 109.00,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 109.00, amount: 22.89, isRetention: false }],
    totalTax: 22.89,
    totalAmount: 131.89,
    paidAmount: 0,
    balanceDue: 0,
    payments: [],
    customerNotes: '',
    internalNotes: 'Voided — customer cancelled order before shipment.',
    lockedAt: '2026-02-05T10:00:00',
    timeline: [
      { type: 'voided', action: 'Invoice voided', actor: 'Admin', date: '2026-02-06' },
      { type: 'approved', action: 'Invoice approved', actor: 'Ana G.', date: '2026-02-05' },
      { type: 'created', action: 'Draft created', actor: 'Ana G.', date: '2026-02-05' }
    ]
  },
  {
    id: 8,
    type: 'Standard',
    status: 'Draft',
    series: 'FAC',
    number: null,
    customer: {
      id: 2, name: 'María López', vatId: null, email: 'maria.lopez@email.com',
      avatarColor: 'linear-gradient(135deg, #EC4899 0%, #F59E0B 100%)', initials: 'ML'
    },
    issueDate: '2026-02-16',
    dueDate: '2026-03-18',
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Botella Térmica 750ml – Mint', quantity: 10, unitPrice: 24.99, discount: '15%', tax: 'IVA 21%', subtotal: 212.42 },
      { id: 2, description: 'Camiseta Algodón Orgánico – M/White', quantity: 5, unitPrice: 29.99, discount: null, tax: 'IVA 21%', subtotal: 149.95 }
    ],
    subtotal: 362.37,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: 362.37, amount: 76.10, isRetention: false }],
    totalTax: 76.10,
    totalAmount: 438.47,
    paidAmount: 0,
    balanceDue: 438.47,
    payments: [],
    customerNotes: '',
    internalNotes: 'Repeat customer — offer loyalty discount on next order.',
    lockedAt: null,
    timeline: [
      { type: 'created', action: 'Draft created', actor: 'Carlos M.', date: '2026-02-16' }
    ]
  },
  {
    id: 9,
    type: 'CreditNote',
    status: 'Approved',
    series: 'REC',
    number: 'REC-2026-0001',
    customer: {
      id: 4, name: 'Pedro Ruiz', vatId: null, email: 'pruiz@gmail.com',
      avatarColor: 'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)', initials: 'PR'
    },
    issueDate: '2026-02-12',
    dueDate: '2026-02-12',
    paymentMethod: 'Transfer',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Camiseta Algodón Orgánico – L/Black (return)', quantity: -1, unitPrice: 29.99, discount: null, tax: 'IVA 21%', subtotal: -29.99 }
    ],
    subtotal: -29.99,
    discountAmount: 0,
    taxSummary: [{ name: 'IVA 21%', base: -29.99, amount: -6.30, isRetention: false }],
    totalTax: -6.30,
    totalAmount: -36.29,
    paidAmount: -36.29,
    balanceDue: 0,
    payments: [
      { id: 1, date: '2026-02-13', amount: -36.29, method: 'Transfer', reference: 'REF-RET-012' }
    ],
    customerNotes: 'Rectifying invoice for return RET-012.',
    internalNotes: 'Linked to FAC-2026-0001, return reason: wrong size.',
    lockedAt: '2026-02-12T11:00:00',
    timeline: [
      { type: 'paid', action: 'Refund processed', actor: 'Ana G.', date: '2026-02-13' },
      { type: 'approved', action: 'Credit note approved', actor: 'Ana G.', date: '2026-02-12' },
      { type: 'created', action: 'Credit note created from FAC-2026-0001', actor: 'Ana G.', date: '2026-02-12' }
    ]
  },
  {
    id: 10,
    type: 'Standard',
    status: 'Approved',
    series: 'SRV',
    number: 'SRV-2026-0002',
    customer: {
      id: 1, name: 'Acme Corp.', vatId: 'B-12345678', email: 'contact@acmecorp.com',
      avatarColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', initials: 'AC'
    },
    issueDate: '2026-02-01',
    dueDate: '2026-02-28',
    paymentMethod: 'Direct debit',
    currency: 'EUR',
    lines: [
      { id: 1, description: 'Consultoría SEO Mensual – Febrero 2026', quantity: 1, unitPrice: 450.00, discount: null, tax: 'IVA 21%', subtotal: 450.00 }
    ],
    subtotal: 450.00,
    discountAmount: 0,
    taxSummary: [
      { name: 'IVA 21%', base: 450.00, amount: 94.50, isRetention: false },
      { name: 'IRPF -15%', base: 450.00, amount: 67.50, isRetention: true }
    ],
    totalTax: 94.50,
    totalAmount: 477.00,
    paidAmount: 0,
    balanceDue: 477.00,
    payments: [],
    customerNotes: 'Servicio recurrente mensual.',
    internalNotes: 'Auto-generated from recurring profile RP-001.',
    lockedAt: '2026-02-01T08:00:00',
    timeline: [
      { type: 'sent', action: 'Sent by email to contact@acmecorp.com', actor: 'System', date: '2026-02-01' },
      { type: 'approved', action: 'Auto-approved (recurring)', actor: 'System', date: '2026-02-01' },
      { type: 'created', action: 'Generated from recurring profile', actor: 'System', date: '2026-02-01' }
    ]
  }
])

/* ══════════════════════════════════════════
   COMPUTED
   ══════════════════════════════════════════ */
const customers = computed(() => {
  const names = [...new Set(invoices.value.map(i => i.customer?.name).filter(Boolean))]
  return names.sort()
})

const seriesList = computed(() => {
  const s = [...new Set(invoices.value.map(i => i.series))]
  return s.sort()
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

  if (seriesFilter.value !== 'all') {
    result = result.filter(i => i.series === seriesFilter.value)
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
  if (isOverdue(invoice)) return 'Overdue'
  const map = {
    Draft: 'Draft',
    Approved: 'Approved',
    PartiallyPaid: 'Partial',
    Paid: 'Paid',
    Voided: 'Voided',
    Rectified: 'Rectified'
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
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDateShort(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
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
