<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ isEditing ? 'Edit purchase invoice' : 'New purchase invoice' }}</h2>
            <div class="modal-header-actions">
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">Cancel</button>
              <button class="btn btn-secondary btn-sm" @click="handleSaveDraft">
                <Save :size="16" />
                <span>Save draft</span>
              </button>
              <div class="approve-btn-wrapper" :data-tooltip="approvalTooltip || undefined">
                <button class="btn btn-primary btn-sm" @click="handleSaveAndApprove">
                  <CheckCircle2 :size="16" />
                  <span>Save &amp; approve</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- MAIN COLUMN -->
            <div class="modal-main">

              <!-- Provider & dates -->
              <section class="form-section">
                <h3 class="section-title">Purchase invoice details</h3>
                <p class="section-desc">Set the provider, dates, and payment terms.</p>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Provider <span class="required">*</span></label>
                    <select
                      class="select"
                      :class="{ 'input-error': touched.provider && !form.providerId }"
                      v-model="form.providerId"
                      @blur="touched.provider = true"
                    >
                      <option value="">Select provider...</option>
                      <option v-for="p in providerOptions" :key="p.id" :value="p.id">{{ p.name }}</option>
                    </select>
                    <span v-if="touched.provider && !form.providerId" class="field-error">Provider is required</span>
                  </div>
                  <div class="field">
                    <label class="field-label">Series <span class="required">*</span></label>
                    <select
                      class="select"
                      :class="{ 'input-error': touched.series && !form.seriesId }"
                      v-model="form.seriesId"
                      @blur="touched.series = true"
                    >
                      <option :value="null" disabled>Select series...</option>
                      <option v-for="s in activeSeries" :key="s.id" :value="s.id">{{ s.prefix }} — {{ s.name }}</option>
                    </select>
                    <span v-if="touched.series && !form.seriesId" class="field-error">Series is required</span>
                  </div>
                </div>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Issue date <span class="required">*</span></label>
                    <input
                      class="input"
                      :class="{ 'input-error': touched.issueDate && !form.issueDate }"
                      type="date"
                      v-model="form.issueDate"
                      @blur="touched.issueDate = true"
                    />
                    <span v-if="touched.issueDate && !form.issueDate" class="field-error">Issue date is required</span>
                  </div>
                  <div class="field">
                    <label class="field-label">Due date <span class="required">*</span></label>
                    <input
                      class="input"
                      :class="{ 'input-error': touched.dueDate && !form.dueDate }"
                      type="date"
                      v-model="form.dueDate"
                      @blur="touched.dueDate = true"
                    />
                    <span v-if="touched.dueDate && !form.dueDate" class="field-error">Due date is required</span>
                  </div>
                  <div class="field">
                    <label class="field-label">Payment method</label>
                    <select class="select" v-model="form.paymentMethod">
                      <option value="Transfer 30 days">Transfer 30 days</option>
                      <option value="Transfer">Transfer</option>
                      <option value="Direct debit">Direct debit</option>
                      <option value="Card">Card</option>
                      <option value="Cash">Cash</option>
                    </select>
                  </div>
                </div>
              </section>

              <!-- Lines -->
              <section class="form-section">
                <h3 class="section-title">Invoice lines</h3>
                <p class="section-desc">Add products or services.</p>

                <div class="lines-editor">
                  <div class="le-header">
                    <span class="le-h-desc">Description</span>
                    <span class="le-h-qty">Qty</span>
                    <span class="le-h-price">Price</span>
                    <span class="le-h-discount">Disc.</span>
                    <span class="le-h-tax">Tax</span>
                    <span class="le-h-subtotal">Subtotal</span>
                    <span class="le-h-actions"></span>
                  </div>

                  <div v-for="(line, idx) in form.lines" :key="line.id" class="le-row">
                    <div class="le-cell-desc">
                      <input class="input input-sm" type="text" placeholder="Product or service..." v-model="line.description" />
                    </div>
                    <div class="le-cell-qty">
                      <input class="input input-sm input-number" type="number" min="0.01" step="1" v-model.number="line.quantity" />
                    </div>
                    <div class="le-cell-price">
                      <input class="input input-sm input-number" type="number" min="0" step="0.01" v-model.number="line.unitPrice" />
                    </div>
                    <div class="le-cell-discount">
                      <input class="input input-sm input-number" type="text" placeholder="0" v-model="line.discount" />
                    </div>
                    <div class="le-cell-tax">
                      <select class="select select-sm" v-model="line.tax">
                        <option value="IVA 21%">IVA 21%</option>
                        <option value="IVA 10%">IVA 10%</option>
                        <option value="IVA 4%">IVA 4%</option>
                        <option value="Exempt">Exempt</option>
                      </select>
                    </div>
                    <div class="le-cell-subtotal">
                      <span class="subtotal-value">{{ formatCurrency(calcLineSubtotal(line)) }}</span>
                    </div>
                    <div class="le-cell-actions">
                      <button class="btn-icon-sm" @click="removeLine(idx)" title="Remove line">
                        <Trash2 :size="14" />
                      </button>
                    </div>
                  </div>
                </div>

                <button class="btn btn-secondary btn-sm add-line-btn" @click="addLine">
                  <Plus :size="16" />
                  <span>Add line</span>
                </button>
              </section>

              <!-- Notes -->
              <section class="form-section">
                <h3 class="section-title">Notes</h3>
                <div class="field">
                  <label class="field-label">Provider notes</label>
                  <textarea class="input textarea" rows="2" placeholder="Visible on document..." v-model="form.providerNotes"></textarea>
                </div>
                <div class="field">
                  <label class="field-label">Internal notes</label>
                  <textarea class="input textarea" rows="2" placeholder="Internal use only..." v-model="form.internalNotes"></textarea>
                </div>
              </section>
            </div>

            <!-- SIDEBAR COLUMN -->
            <div class="modal-sidebar">
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Summary</h4>
                <div class="sidebar-totals">
                  <div class="sidebar-total-row">
                    <span>Subtotal</span>
                    <span>{{ formatCurrency(calcSubtotal) }}</span>
                  </div>
                  <div v-if="form.discountValue" class="sidebar-total-row">
                    <span>Discount</span>
                    <span class="discount-val">-{{ formatCurrency(calcDiscountAmount) }}</span>
                  </div>
                  <div v-for="tax in calcTaxSummary" :key="tax.name" class="sidebar-total-row">
                    <span>{{ tax.name }}</span>
                    <span :class="tax.isRetention ? 'retention-val' : ''">
                      {{ tax.isRetention ? '-' : '' }}{{ formatCurrency(tax.amount) }}
                    </span>
                  </div>
                  <div class="sidebar-total-row total-final-row">
                    <span>Total</span>
                    <span>{{ formatCurrency(calcTotal) }}</span>
                  </div>
                </div>
              </div>

              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Global discount</h4>
                <p class="sidebar-card-desc">Apply an additional discount on the subtotal.</p>
                <div class="field-row-inline">
                  <div class="field" style="flex:1">
                    <input class="input input-sm" type="number" min="0" step="0.01" placeholder="0" v-model.number="form.discountValue" />
                  </div>
                  <div class="field" style="width:90px">
                    <select class="select select-sm" v-model="form.discountType">
                      <option value="percent">%</option>
                      <option value="fixed">EUR</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Currency</h4>
                <select class="select select-sm" v-model="form.currency" disabled>
                  <option value="EUR">EUR — Euro</option>
                </select>
              </div>

              <div v-if="selectedProvider" class="sidebar-card">
                <h4 class="sidebar-card-title">Provider info</h4>
                <div class="provider-preview">
                  <div class="provider-avatar" :style="{ background: selectedProvider.avatarColor }">
                    {{ selectedProvider.initials }}
                  </div>
                  <div class="provider-preview-info">
                    <span class="provider-preview-name">{{ selectedProvider.name }}</span>
                    <span class="provider-preview-email">{{ selectedProvider.email }}</span>
                    <span v-if="selectedProvider.vatId" class="provider-preview-vat">{{ selectedProvider.vatId }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { Plus, Trash2, Save, CheckCircle2 } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import purchasesApi from '@/services/purchases'
import providersApi from '@/services/providers'
import { mapProviderFromApi } from '@/services/mappers'

const props = defineProps({
  open: { type: Boolean, default: false },
  invoice: { type: Object, default: null },
  invoices: { type: Array, default: () => [] },
  seriesList: { type: Array, default: () => [] },
  providers: { type: Array, default: () => [] },
  preselectedProviderId: { type: [Number, String], default: null },
})

const emit = defineEmits(['close', 'save'])

const isEditing = computed(() => !!props.invoice)

function findSeriesIdByPrefix(prefix) {
  if (!prefix || !activeSeries.value.length) return null
  return activeSeries.value.find(s => s.prefix === prefix)?.id || null
}

const touched = reactive({
  provider: false,
  series: false,
  issueDate: false,
  dueDate: false,
})

function markAllTouched() {
  Object.keys(touched).forEach(k => { touched[k] = true })
}

const fallbackSeriesList = ref([])
const activeSeries = computed(() =>
  props.seriesList.length > 0 ? props.seriesList : fallbackSeriesList.value
)

const fallbackProviders = ref([])

const providerOptions = computed(() =>
  props.providers.length > 0 ? props.providers : fallbackProviders.value
)

async function loadProviders() {
  try {
    const data = await providersApi.getAll()
    const items = Array.isArray(data) ? data : (data.results || [])
    fallbackProviders.value = items.map(mapProviderFromApi)
  } catch (err) {
    console.error('[PurchaseInvoiceFormModal] failed to load providers:', err)
    fallbackProviders.value = []
  }
}

const selectedProvider = computed(() => {
  if (!form.providerId) return null
  return providerOptions.value.find(p => p.id === form.providerId) || null
})

let lineCounter = 100

function blankLine() {
  return {
    id: lineCounter++,
    description: '',
    quantity: 1,
    unitPrice: 0,
    discount: '',
    tax: 'IVA 21%'
  }
}

function blankForm() {
  return {
    providerId: '',
    seriesId: null,
    issueDate: new Date().toISOString().split('T')[0],
    dueDate: getDefaultDueDate(),
    paymentMethod: 'Transfer 30 days',
    currency: 'EUR',
    lines: [blankLine()],
    discountType: 'percent',
    discountValue: null,
    providerNotes: '',
    internalNotes: ''
  }
}

function getDefaultDueDate() {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return d.toISOString().split('T')[0]
}

const form = reactive(blankForm())

watch(() => props.open, async (isOpen) => {
  Object.keys(touched).forEach(k => { touched[k] = false })

  if (!isOpen) return

  if (props.seriesList.length === 0) {
    try {
      const data = await purchasesApi.getSeries()
      const loaded = Array.isArray(data) ? data : (data.results || [])
      fallbackSeriesList.value = loaded
    } catch (err) {
      console.error('[PurchaseInvoiceFormModal] failed to load series:', err)
    }
  } else {
    fallbackSeriesList.value = []
  }

  if (props.providers.length === 0) {
    await loadProviders()
  } else {
    fallbackProviders.value = []
  }

  if (props.invoice) {
    const inv = props.invoice
    Object.assign(form, {
      providerId: inv.provider?.id || '',
      seriesId: inv.seriesId || findSeriesIdByPrefix(inv.series) || (activeSeries.value.find(s => s.is_default) || activeSeries.value[0])?.id || null,
      issueDate: inv.issueDate,
      dueDate: inv.dueDate,
      paymentMethod: inv.paymentMethod || 'Transfer 30 days',
      currency: inv.currency || 'EUR',
      lines: inv.lines.map(l => ({
        id: lineCounter++,
        description: l.description,
        quantity: l.quantity,
        unitPrice: l.unitPrice,
        discount: l.discount || '',
        tax: l.tax || 'IVA 21%'
      })),
      discountType: inv.discountType || 'percent',
      discountValue: inv.discountValue || null,
      providerNotes: inv.providerNotes || '',
      internalNotes: inv.internalNotes || ''
    })
  } else {
    Object.assign(form, blankForm())
    const def = activeSeries.value.find(s => s.is_default) || activeSeries.value[0]
    if (def) form.seriesId = def.id
    if (props.preselectedProviderId) {
      form.providerId = props.preselectedProviderId
    }
  }
})

function addLine() { form.lines.push(blankLine()) }

function removeLine(idx) {
  if (form.lines.length <= 1) return
  form.lines.splice(idx, 1)
}

function parseTaxPercent(taxStr) {
  if (!taxStr || taxStr === 'Exempt') return 0
  const match = taxStr.match(/([\d.]+)%/)
  return match ? parseFloat(match[1]) : 0
}

function parseDiscount(discountStr, base) {
  if (!discountStr) return 0
  const str = String(discountStr).trim()
  if (str.endsWith('%')) {
    const pct = parseFloat(str.replace('%', ''))
    return isNaN(pct) ? 0 : (base * pct / 100)
  }
  const val = parseFloat(str)
  return isNaN(val) ? 0 : val
}

function calcLineSubtotal(line) {
  const gross = (line.quantity || 0) * (line.unitPrice || 0)
  const disc = parseDiscount(line.discount, gross)
  return Math.max(0, gross - disc)
}

const calcSubtotal = computed(() => {
  return form.lines.reduce((sum, line) => sum + calcLineSubtotal(line), 0)
})

const calcDiscountAmount = computed(() => {
  if (!form.discountValue) return 0
  if (form.discountType === 'percent') return calcSubtotal.value * form.discountValue / 100
  return form.discountValue
})

const calcTaxBase = computed(() => calcSubtotal.value - calcDiscountAmount.value)

const calcTaxSummary = computed(() => {
  const groups = {}
  form.lines.forEach(line => {
    const sub = calcLineSubtotal(line)
    const ratio = calcSubtotal.value > 0 ? sub / calcSubtotal.value : 0
    const adjustedBase = sub - (calcDiscountAmount.value * ratio)
    const pct = parseTaxPercent(line.tax)
    const taxName = line.tax || 'Exempt'
    if (pct === 0) return
    if (!groups[taxName]) {
      groups[taxName] = { name: taxName, base: 0, amount: 0, isRetention: taxName.includes('IRPF') }
    }
    groups[taxName].base += adjustedBase
    groups[taxName].amount += adjustedBase * pct / 100
  })
  return Object.values(groups)
})

const calcTotalTax = computed(() => {
  return calcTaxSummary.value.filter(t => !t.isRetention).reduce((sum, t) => sum + t.amount, 0)
})

const calcTotalRetention = computed(() => {
  return calcTaxSummary.value.filter(t => t.isRetention).reduce((sum, t) => sum + t.amount, 0)
})

const calcTotal = computed(() => calcTaxBase.value + calcTotalTax.value - calcTotalRetention.value)

const approvalMissing = computed(() => {
  const missing = []
  if (!form.providerId) missing.push('Provider is required')
  if (!form.seriesId) missing.push('Series is required')
  if (!form.issueDate) missing.push('Issue date is required')
  if (!form.dueDate) missing.push('Due date is required')
  const validLines = form.lines.filter(l => l.description && l.quantity > 0 && l.unitPrice >= 0)
  if (validLines.length === 0) missing.push('At least 1 valid line')
  return missing
})

const approvalTooltip = computed(() => {
  if (!approvalMissing.value.length) return null
  return 'Requirements to approve:\n• ' + approvalMissing.value.join('\n• ')
})

function getValidationErrors(requireAll = false) {
  const errors = []
  if (!form.providerId) errors.push('Provider is required')
  if (!form.seriesId) errors.push('Series is required')
  if (!form.issueDate) errors.push('Issue date is required')
  if (!form.dueDate) errors.push('Due date is required')
  const validLines = form.lines.filter(l => l.description && l.quantity > 0 && l.unitPrice >= 0)
  if (requireAll && validLines.length === 0) errors.push('At least one line with description, quantity, and price is required')
  if (form.dueDate && form.issueDate && form.dueDate < form.issueDate) errors.push('Due date cannot be before issue date')
  return errors
}

function showValidationAlert(errors) {
  Swal.fire({
    icon: 'warning',
    title: 'Required fields missing',
    html: `<ul style="text-align:left;margin:0;padding-left:1.2em">${errors.map(e => `<li>${e}</li>`).join('')}</ul>`,
    confirmButtonText: 'OK',
    confirmButtonColor: '#667eea',
    customClass: { popup: 'swal-erp-popup' },
    backdrop: `rgba(0,0,0,0.15)`,
    target: document.body,
    heightAuto: false
  })
}

function buildInvoiceData(status) {
  const provider = selectedProvider.value
  return {
    id: props.invoice?.id || Date.now(),
    type: 'Standard',
    status,
    seriesId: form.seriesId,
    series: activeSeries.value.find(s => s.id === form.seriesId)?.prefix || '',
    number: status === 'Approved' ? generateNumber() : (props.invoice?.number || null),
    provider: provider ? {
      id: provider.id,
      name: provider.name,
      vatId: provider.vatId,
      email: provider.email,
      avatarColor: provider.avatarColor,
      initials: provider.initials
    } : props.invoice?.provider,
    issueDate: form.issueDate,
    dueDate: form.dueDate,
    paymentMethod: form.paymentMethod,
    currency: form.currency,
    lines: form.lines.filter(l => l.description).map(l => ({
      id: l.id,
      description: l.description,
      quantity: l.quantity,
      unitPrice: l.unitPrice,
      discount: l.discount || null,
      tax: l.tax,
      subtotal: calcLineSubtotal(l)
    })),
    subtotal: calcSubtotal.value,
    discountType: form.discountType,
    discountValue: form.discountValue,
    discountAmount: calcDiscountAmount.value,
    taxSummary: calcTaxSummary.value,
    totalTax: calcTotalTax.value,
    totalAmount: calcTotal.value,
    paidAmount: props.invoice?.paidAmount || 0,
    balanceDue: calcTotal.value - (props.invoice?.paidAmount || 0),
    payments: props.invoice?.payments || [],
    providerNotes: form.providerNotes,
    internalNotes: form.internalNotes,
    lockedAt: status === 'Approved' ? new Date().toISOString() : (props.invoice?.lockedAt || null),
    timeline: buildTimeline(status)
  }
}

function generateNumber() {
  const year = new Date().getFullYear()
  const prefix = activeSeries.value.find(s => s.id === form.seriesId)?.prefix || 'COMP'
  const existing = props.invoices.filter(i => i.series === prefix && i.number)
  const seq = existing.length + 1
  return `${prefix}-${year}-${String(seq).padStart(4, '0')}`
}

function buildTimeline(status) {
  const today = new Date().toISOString().split('T')[0]
  const existing = props.invoice?.timeline ? [...props.invoice.timeline] : []
  if (props.invoice) {
    existing.unshift({ type: 'created', action: 'Purchase invoice updated', actor: 'You', date: today })
  } else {
    existing.unshift({ type: 'created', action: 'Draft created', actor: 'You', date: today })
  }
  if (status === 'Approved') {
    existing.unshift({ type: 'approved', action: 'Purchase invoice approved', actor: 'You', date: today })
  }
  return existing
}

function handleSaveDraft() {
  markAllTouched()
  const errors = getValidationErrors(false)
  if (errors.length) { showValidationAlert(errors); return }
  const data = buildInvoiceData('Draft')
  emit('save', data)
  emit('close')
}

function handleSaveAndApprove() {
  markAllTouched()
  const errors = getValidationErrors(true)
  if (errors.length) { showValidationAlert(errors); return }
  const data = buildInvoiceData('Approved')
  if (data.totalAmount === 0) {
    data.status = 'Paid'
    data.timeline.unshift({ type: 'paid', action: 'Auto-paid (zero amount)', actor: 'You', date: new Date().toISOString().split('T')[0] })
  }
  emit('save', data)
  emit('close')
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 1060px;
  max-height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px -12px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.modal-body {
  display: flex;
  gap: 1.75rem;
  padding: 1.75rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.modal-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.modal-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}

.section-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0 0 1.25rem;
}

.field { margin-bottom: 1rem; }
.field:last-child { margin-bottom: 0; }

.field-label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.required { color: var(--error-color); }

.field-error {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--error-color);
  margin-top: 0.25rem;
}

.input-error, .select.input-error {
  border-color: var(--error-color) !important;
  outline-color: var(--error-color);
}

.approve-btn-wrapper { position: relative; }

.approve-btn-wrapper[data-tooltip]:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 10px);
  right: 0;
  background: #1e1e2e;
  color: #fff;
  font-size: 0.75rem;
  line-height: 1.6;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  white-space: pre-line;
  min-width: 220px;
  max-width: 300px;
  z-index: 9999;
  pointer-events: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.approve-btn-wrapper[data-tooltip]:hover::before {
  content: '';
  position: absolute;
  bottom: calc(100% + 4px);
  right: 18px;
  border: 6px solid transparent;
  border-top-color: #1e1e2e;
  z-index: 9999;
  pointer-events: none;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.field-row:last-child { margin-bottom: 0; }
.field-row .field { margin-bottom: 0; }
.field-row-3 { grid-template-columns: repeat(3, 1fr); }

.field-row-inline {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.textarea {
  resize: vertical;
  min-height: 56px;
  line-height: 1.5;
}

.input-sm { padding: 0.4rem 0.625rem; font-size: var(--font-size-sm); }
.select-sm { padding: 0.4rem 0.625rem; font-size: var(--font-size-sm); }
.input-number { text-align: right; }

.lines-editor {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.le-header {
  display: grid;
  grid-template-columns: 1fr 65px 90px 65px 110px 90px 36px;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  align-items: center;
}

.le-row {
  display: grid;
  grid-template-columns: 1fr 65px 90px 65px 110px 90px 36px;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-top: 1px solid var(--border-color);
  align-items: center;
  background: white;
  transition: background var(--transition-fast);
}

.le-row:first-child { border-top: none; }
.le-row:hover { background: var(--bg-hover); }

.le-cell-desc .input { width: 100%; }
.le-cell-qty .input { width: 100%; }
.le-cell-price .input { width: 100%; }
.le-cell-discount .input { width: 100%; }
.le-cell-tax .select { width: 100%; }

.subtotal-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  text-align: right;
  display: block;
}

.btn-icon-sm {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: none;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon-sm:hover {
  background: var(--error-light);
  color: var(--error-color);
}

.add-line-btn { margin-top: 0.25rem; }

.sidebar-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.25rem;
}

.sidebar-card-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.sidebar-card-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0 0 0.75rem;
}

.sidebar-totals {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-total-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  padding: 0.2rem 0;
}

.total-final-row {
  border-top: 1px solid var(--border-color);
  margin-top: 0.375rem;
  padding-top: 0.5rem;
  font-weight: 700;
  font-size: var(--font-size-base);
  color: var(--text-primary);
}

.discount-val { color: var(--error-color); }
.retention-val { color: var(--error-color); }

.provider-preview {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.provider-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.provider-preview-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.provider-preview-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.provider-preview-email {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.provider-preview-vat {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
}

.modal-enter-active, .modal-leave-active { transition: opacity 0.25s ease; }
.modal-enter-active .modal-container, .modal-leave-active .modal-container { transition: transform 0.25s ease, opacity 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-container, .modal-leave-to .modal-container { transform: translateY(16px) scale(0.97); opacity: 0; }

@media (max-width: 768px) {
  .modal-overlay { padding: 1rem; }
  .modal-body { flex-direction: column; padding: 1.25rem; }
  .modal-sidebar { width: 100%; }
  .field-row, .field-row-3 { grid-template-columns: 1fr; }
  .le-header, .le-row { grid-template-columns: 1fr 50px 70px 50px 90px 70px 30px; gap: 0.25rem; font-size: var(--font-size-xs); }
  .modal-header { flex-direction: column; gap: 0.75rem; align-items: flex-start; }
  .modal-header-actions { width: 100%; justify-content: flex-end; }
}
</style>
