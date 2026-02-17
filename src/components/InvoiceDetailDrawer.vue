<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel">
          <!-- Header -->
          <div class="drawer-header">
            <div class="drawer-title-row">
              <div>
                <h2 class="drawer-title">{{ invoice.number || 'Draft' }}</h2>
                <span :class="['badge', statusBadgeClass(invoice)]">
                  {{ displayStatus(invoice) }}
                </span>
              </div>
              <button class="btn-icon" @click="$emit('close')">
                <X :size="20" />
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="drawer-body">
            <!-- Summary cards -->
            <div class="detail-summary">
              <div class="summary-card">
                <span class="summary-label">Total</span>
                <span class="summary-amount">{{ formatCurrency(invoice.totalAmount) }}</span>
              </div>
              <div class="summary-card">
                <span class="summary-label">Paid</span>
                <span class="summary-amount paid-amount">{{ formatCurrency(invoice.paidAmount) }}</span>
              </div>
              <div class="summary-card">
                <span class="summary-label">Balance due</span>
                <span :class="['summary-amount', invoice.balanceDue > 0 ? 'has-balance' : 'zero-balance']">
                  {{ formatCurrency(invoice.balanceDue) }}
                </span>
              </div>
            </div>

            <!-- Payment progress -->
            <div class="payment-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: paymentPercent + '%' }"></div>
              </div>
              <span class="progress-label">{{ paymentPercent }}% collected</span>
            </div>

            <!-- Customer -->
            <div class="detail-section">
              <h4 class="section-title">
                <User :size="16" />
                Customer
              </h4>
              <div class="detail-row">
                <span class="detail-label">Name</span>
                <span class="detail-value">{{ invoice.customer.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">VAT ID</span>
                <span class="detail-value">{{ invoice.customer.vatId || '—' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Email</span>
                <span class="detail-value">{{ invoice.customer.email }}</span>
              </div>
            </div>

            <!-- Details -->
            <div class="detail-section">
              <h4 class="section-title">
                <FileText :size="16" />
                Details
              </h4>
              <div class="detail-row">
                <span class="detail-label">Series</span>
                <span class="detail-value">{{ invoice.series }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Issue date</span>
                <span class="detail-value">{{ formatDateShort(invoice.issueDate) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Due date</span>
                <span :class="['detail-value', isOverdue(invoice) ? 'overdue-text' : '']">
                  {{ formatDateShort(invoice.dueDate) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Payment method</span>
                <span class="detail-value">{{ invoice.paymentMethod }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Currency</span>
                <span class="detail-value">{{ invoice.currency }}</span>
              </div>
            </div>

            <!-- Lines -->
            <div class="detail-section">
              <h4 class="section-title">
                <ClipboardList :size="16" />
                Lines
              </h4>
              <div class="lines-table">
                <div class="lines-header">
                  <span class="lh-desc">Description</span>
                  <span class="lh-qty">Qty</span>
                  <span class="lh-price">Price</span>
                  <span class="lh-tax">Tax</span>
                  <span class="lh-subtotal">Subtotal</span>
                </div>
                <div v-for="line in invoice.lines" :key="line.id" class="line-row">
                  <span class="lr-desc">
                    {{ line.description }}
                    <small v-if="line.discount" class="line-discount">-{{ line.discount }}</small>
                  </span>
                  <span class="lr-qty">{{ line.quantity }}</span>
                  <span class="lr-price">{{ formatCurrency(line.unitPrice) }}</span>
                  <span class="lr-tax">{{ line.tax }}</span>
                  <span class="lr-subtotal">{{ formatCurrency(line.subtotal) }}</span>
                </div>
              </div>

              <!-- Totals -->
              <div class="totals-block">
                <div class="total-row">
                  <span>Subtotal</span>
                  <span>{{ formatCurrency(invoice.subtotal) }}</span>
                </div>
                <div v-if="invoice.discountAmount" class="total-row">
                  <span>Discount</span>
                  <span>-{{ formatCurrency(invoice.discountAmount) }}</span>
                </div>
                <div v-for="tax in invoice.taxSummary" :key="tax.name" class="total-row">
                  <span>{{ tax.name }}</span>
                  <span :class="tax.isRetention ? 'retention-amount' : ''">
                    {{ tax.isRetention ? '-' : '' }}{{ formatCurrency(tax.amount) }}
                  </span>
                </div>
                <div class="total-row total-final">
                  <span>Total</span>
                  <span>{{ formatCurrency(invoice.totalAmount) }}</span>
                </div>
              </div>
            </div>

            <!-- Payments -->
            <div class="detail-section">
              <div class="section-title-row">
                <h4 class="section-title">
                  <Banknote :size="16" />
                  Payments
                </h4>
                <button
                  v-if="invoice.status === 'Approved' || invoice.status === 'PartiallyPaid'"
                  class="btn btn-sm btn-secondary"
                  @click="$emit('record-payment', invoice)"
                >
                  <Plus :size="14" />
                  Add payment
                </button>
              </div>
              <div v-if="invoice.payments.length" class="payments-list">
                <div v-for="pay in invoice.payments" :key="pay.id" class="payment-item">
                  <div class="payment-info">
                    <span class="payment-date">{{ formatDateShort(pay.date) }}</span>
                    <span class="payment-method-tag">{{ pay.method }}</span>
                    <span v-if="pay.reference" class="payment-ref">{{ pay.reference }}</span>
                  </div>
                  <span class="payment-amount">{{ formatCurrency(pay.amount) }}</span>
                </div>
              </div>
              <p v-else class="empty-hint">No payments recorded yet.</p>
            </div>

            <!-- Notes -->
            <div v-if="invoice.customerNotes || invoice.internalNotes" class="detail-section">
              <h4 class="section-title">
                <StickyNote :size="16" />
                Notes
              </h4>
              <div v-if="invoice.customerNotes" class="note-block">
                <span class="note-label">Customer notes</span>
                <p class="note-text">{{ invoice.customerNotes }}</p>
              </div>
              <div v-if="invoice.internalNotes" class="note-block">
                <span class="note-label">Internal notes</span>
                <p class="note-text internal-note">{{ invoice.internalNotes }}</p>
              </div>
            </div>

            <!-- Timeline -->
            <div class="detail-section">
              <h4 class="section-title">
                <Clock :size="16" />
                Timeline
              </h4>
              <div class="timeline">
                <div v-for="(event, idx) in invoice.timeline" :key="idx" class="timeline-item">
                  <div :class="['timeline-dot', 'dot-' + event.type]"></div>
                  <div class="timeline-content">
                    <span class="timeline-action">{{ event.action }}</span>
                    <span class="timeline-meta">{{ event.actor }} · {{ formatDateShort(event.date) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer actions -->
          <div class="drawer-footer">
            <button
              v-if="invoice.status === 'Draft'"
              class="btn btn-secondary"
              @click="$emit('edit', invoice)"
            >
              <Pencil :size="18" />
              Edit
            </button>
            <button
              v-if="invoice.status === 'Draft'"
              class="btn btn-primary"
              @click="$emit('approve', invoice)"
            >
              <CheckCircle2 :size="18" />
              Approve
            </button>
            <button
              v-if="invoice.status === 'Approved' || invoice.status === 'PartiallyPaid'"
              class="btn btn-primary"
              @click="$emit('record-payment', invoice)"
            >
              <Banknote :size="18" />
              Record payment
            </button>
            <button class="btn btn-secondary" @click="$emit('download-pdf', invoice)">
              <FileDown :size="18" />
              PDF
            </button>
            <button
              v-if="invoice.status !== 'Draft' && invoice.status !== 'Voided'"
              class="btn btn-secondary"
              @click="$emit('send', invoice)"
            >
              <Send :size="18" />
              Send
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import {
  X, FileText, User, ClipboardList, Clock, StickyNote,
  Banknote, CheckCircle2, FileDown, Send, Plus, Pencil
} from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  invoice: { type: Object, required: true }
})

defineEmits(['close', 'edit', 'approve', 'record-payment', 'send', 'download-pdf'])

/* ── Helpers ── */
const paymentPercent = computed(() => {
  if (!props.invoice.totalAmount || props.invoice.totalAmount === 0) return 100
  const pct = Math.round((props.invoice.paidAmount / Math.abs(props.invoice.totalAmount)) * 100)
  return Math.min(100, Math.max(0, pct))
})

function isOverdue(invoice) {
  if (!['Approved', 'PartiallyPaid'].includes(invoice.status)) return false
  return new Date(invoice.dueDate) < new Date()
}

function displayStatus(invoice) {
  if (isOverdue(invoice)) return 'Overdue'
  const map = { Draft: 'Draft', Approved: 'Approved', PartiallyPaid: 'Partial', Paid: 'Paid', Voided: 'Voided', Rectified: 'Rectified' }
  return map[invoice.status] || invoice.status
}

function statusBadgeClass(invoice) {
  if (isOverdue(invoice)) return 'badge-error'
  const map = { Draft: 'badge-gray', Approved: 'badge-primary', PartiallyPaid: 'badge-warning', Paid: 'badge-success', Voided: 'badge-gray', Rectified: 'badge-gray' }
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
/* ============================
   DRAWER OVERLAY & PANEL
   ============================ */
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 540px;
  max-width: 90vw;
  background: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

/* ============================
   HEADER
   ============================ */
.drawer-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.drawer-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.drawer-title-row > div {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.drawer-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
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
   BODY (scrollable)
   ============================ */
.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

/* ============================
   FOOTER
   ============================ */
.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
}

/* ============================
   SUMMARY CARDS
   ============================ */
.detail-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.summary-card {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 500;
}

.summary-amount {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.paid-amount { color: var(--success-color); }
.has-balance { color: var(--warning-color); }
.zero-balance { color: var(--text-tertiary); }

/* ============================
   PAYMENT PROGRESS
   ============================ */
.payment-progress {
  margin-bottom: 1.5rem;
}

.progress-bar {
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.375rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.4s ease;
}

.progress-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* ============================
   DETAIL SECTIONS
   ============================ */
.detail-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f0f2f5;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
}

.section-title-row .section-title {
  margin-bottom: 0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.detail-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.detail-value {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.overdue-text {
  color: var(--error-color) !important;
  font-weight: 600;
}

/* ============================
   LINES TABLE
   ============================ */
.lines-table {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.lines-header {
  display: grid;
  grid-template-columns: 1fr 50px 80px 70px 80px;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--bg-secondary);
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.line-row {
  display: grid;
  grid-template-columns: 1fr 50px 80px 70px 80px;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  font-size: var(--font-size-sm);
  border-top: 1px solid var(--border-color);
  align-items: center;
}

.lr-desc {
  color: var(--text-primary);
  font-weight: 500;
  white-space: normal;
  line-height: 1.3;
}

.line-discount {
  display: inline-block;
  margin-left: 0.375rem;
  color: var(--error-color);
  font-size: var(--font-size-xs);
  font-weight: 400;
}

.lr-qty { color: var(--text-secondary); text-align: center; }
.lr-price { color: var(--text-secondary); text-align: right; }
.lr-tax { color: var(--text-tertiary); font-size: var(--font-size-xs); text-align: right; }
.lr-subtotal { color: var(--text-primary); font-weight: 600; text-align: right; }
.lh-qty { text-align: center; }
.lh-price, .lh-tax, .lh-subtotal { text-align: right; }

/* ============================
   TOTALS
   ============================ */
.totals-block {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  padding: 0.75rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.total-final {
  border-top: 1px solid var(--border-color);
  margin-top: 0.375rem;
  padding-top: 0.5rem;
  font-weight: 700;
  color: var(--text-primary);
  font-size: var(--font-size-base);
}

.retention-amount { color: var(--error-color); }

/* ============================
   PAYMENTS
   ============================ */
.payments-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.payment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
}

.payment-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.payment-date {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.payment-method-tag {
  display: inline-flex;
  padding: 0.125rem 0.5rem;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 4px;
  letter-spacing: 0.03em;
}

.payment-ref {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  font-family: 'JetBrains Mono', monospace;
}

.payment-amount {
  font-weight: 700;
  font-size: var(--font-size-sm);
  color: var(--success-color);
}

.empty-hint {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  font-style: italic;
  margin: 0;
}

/* ============================
   NOTES
   ============================ */
.note-block { margin-bottom: 0.75rem; }

.note-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.note-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin: 0;
  line-height: 1.5;
}

.internal-note {
  color: var(--text-secondary);
  font-style: italic;
}

/* ============================
   TIMELINE
   ============================ */
.timeline {
  display: flex;
  flex-direction: column;
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem 0;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 22px;
  bottom: -2px;
  width: 2px;
  background: var(--border-color);
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 2px;
}

.dot-created { background: var(--text-tertiary); }
.dot-approved { background: var(--primary-color); }
.dot-sent { background: var(--info-color); }
.dot-payment { background: var(--warning-color); }
.dot-paid { background: var(--success-color); }
.dot-voided { background: var(--error-color); }

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.timeline-action {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.timeline-meta {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* ============================
   TRANSITION
   ============================ */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from { opacity: 0; }
.drawer-enter-from .drawer-panel { transform: translateX(100%); }
.drawer-leave-to { opacity: 0; }
.drawer-leave-to .drawer-panel { transform: translateX(100%); }

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .drawer-panel {
    width: 100vw;
    max-width: 100vw;
  }
  .detail-summary {
    grid-template-columns: 1fr;
  }
}
</style>
