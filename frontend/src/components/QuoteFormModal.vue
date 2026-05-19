<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <div class="modal-header">
            <h2 class="modal-title">
              {{ isEditing ? 'Edit quote' : (mode === 'purchase' ? 'New purchase quote' : 'New quote') }}
            </h2>
            <div class="modal-header-actions">
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">Cancel</button>
              <button class="btn btn-primary btn-sm" @click="handleSave">
                <Save :size="16" />
                <span>Save</span>
              </button>
            </div>
          </div>

          <div class="modal-body">
            <div class="modal-main">
              <section class="form-section">
                <h3 class="section-title">Quote details</h3>

                <div class="field">
                  <label class="field-label">Name <span class="required">*</span></label>
                  <input
                    class="input"
                    type="text"
                    placeholder="e.g. Servicios consultoría enero..."
                    v-model="form.name"
                  />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">{{ contactLabel }} <span class="required">*</span></label>
                    <select class="select" v-model="form.contactId">
                      <option value="">Select {{ contactLabel.toLowerCase() }}...</option>
                      <option v-for="c in contacts" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Status</label>
                    <select class="select" v-model="form.status">
                      <option value="Draft">Borrador</option>
                      <option value="Sent">{{ mode === 'purchase' ? 'Solicitado' : 'Enviado' }}</option>
                      <option value="Accepted">Aceptado</option>
                      <option value="Rejected">Rechazado</option>
                      <option value="Expired">Expirado</option>
                    </select>
                  </div>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Issue date <span class="required">*</span></label>
                    <input class="input" type="date" v-model="form.issueDate" />
                  </div>
                  <div class="field">
                    <label class="field-label">Valid until</label>
                    <input class="input" type="date" v-model="form.validUntil" />
                  </div>
                </div>
              </section>

              <section class="form-section">
                <h3 class="section-title">Items</h3>
                <p class="section-desc">Add products or services. Totals are calculated automatically.</p>

                <div class="lines-editor">
                  <div class="le-header">
                    <span class="le-h-desc">Description</span>
                    <span class="le-h-qty">Qty</span>
                    <span class="le-h-price">Price</span>
                    <span class="le-h-tax">Tax %</span>
                    <span class="le-h-subtotal">Subtotal</span>
                    <span class="le-h-actions"></span>
                  </div>

                  <div v-for="(line, idx) in form.lines" :key="idx" class="le-row">
                    <input class="input input-sm" type="text" placeholder="Item description..." v-model="line.description" />
                    <input class="input input-sm input-number" type="number" min="0" step="0.01" v-model.number="line.quantity" />
                    <input class="input input-sm input-number" type="number" min="0" step="0.01" v-model.number="line.unitPrice" />
                    <select class="select select-sm" v-model.number="line.taxPercent">
                      <option :value="0">0%</option>
                      <option :value="4">4%</option>
                      <option :value="10">10%</option>
                      <option :value="21">21%</option>
                    </select>
                    <span class="subtotal-value">{{ formatCurrency(calcLineSubtotal(line)) }}</span>
                    <button class="btn-icon-sm" @click="removeLine(idx)" title="Remove">
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </div>

                <button class="btn btn-secondary btn-sm add-line-btn" @click="addLine">
                  <Plus :size="16" />
                  <span>Add line</span>
                </button>
              </section>

              <section class="form-section">
                <h3 class="section-title">Notes</h3>
                <div class="field">
                  <label class="field-label">{{ mode === 'purchase' ? 'Provider notes' : 'Customer notes' }}</label>
                  <textarea class="input textarea" rows="2" v-model="form.contactNotes"></textarea>
                </div>
                <div class="field">
                  <label class="field-label">Internal notes</label>
                  <textarea class="input textarea" rows="2" v-model="form.internalNotes"></textarea>
                </div>
              </section>
            </div>

            <div class="modal-sidebar">
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Summary</h4>
                <div class="sidebar-totals">
                  <div class="sidebar-total-row">
                    <span>Subtotal</span>
                    <span>{{ formatCurrency(calcSubtotal) }}</span>
                  </div>
                  <div class="sidebar-total-row">
                    <span>Taxes</span>
                    <span>{{ formatCurrency(calcTotalTax) }}</span>
                  </div>
                  <div class="sidebar-total-row total-final-row">
                    <span>Total</span>
                    <span>{{ formatCurrency(calcTotal) }}</span>
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
import { ref, computed, watch } from 'vue'
import { Save, Plus, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  quote: { type: Object, default: null },
  contacts: { type: Array, default: () => [] },
  mode: { type: String, default: 'sales' }, // 'sales' | 'purchase'
  preselectedContactId: { type: [Number, String], default: null },
})

const emit = defineEmits(['close', 'save'])

const isEditing = computed(() => !!props.quote)
const contactLabel = computed(() => props.mode === 'purchase' ? 'Provider' : 'Customer')

const today = new Date().toISOString().split('T')[0]

const form = ref(emptyForm())

function emptyForm() {
  return {
    name: '',
    contactId: '',
    status: 'Draft',
    issueDate: today,
    validUntil: '',
    contactNotes: '',
    internalNotes: '',
    lines: [emptyLine()],
  }
}

function emptyLine() {
  return { description: '', quantity: 1, unitPrice: 0, taxPercent: 21 }
}

watch(() => props.open, (val) => {
  if (val) {
    if (props.quote) {
      const q = props.quote
      form.value = {
        name: q.name || '',
        contactId: q.customer?.id || q.provider?.id || '',
        status: q.status || 'Draft',
        issueDate: q.issueDate || today,
        validUntil: q.validUntil || '',
        contactNotes: (props.mode === 'purchase' ? q.providerNotes : q.customerNotes) || '',
        internalNotes: q.internalNotes || '',
        lines: (q.lines && q.lines.length > 0)
          ? q.lines.map(l => ({
              description: l.description,
              quantity: l.quantity,
              unitPrice: l.unitPrice,
              taxPercent: l.taxPercent || 0,
            }))
          : [emptyLine()],
      }
    } else {
      form.value = emptyForm()
      if (props.preselectedContactId) {
        form.value.contactId = props.preselectedContactId
      }
    }
  }
})

function addLine() { form.value.lines.push(emptyLine()) }
function removeLine(i) { form.value.lines.splice(i, 1) }

function calcLineSubtotal(line) {
  const gross = (line.quantity || 0) * (line.unitPrice || 0)
  return gross
}
const calcSubtotal = computed(() =>
  form.value.lines.reduce((sum, l) => sum + calcLineSubtotal(l), 0)
)
const calcTotalTax = computed(() =>
  form.value.lines.reduce((sum, l) => {
    const gross = (l.quantity || 0) * (l.unitPrice || 0)
    return sum + gross * (l.taxPercent || 0) / 100
  }, 0)
)
const calcTotal = computed(() => calcSubtotal.value + calcTotalTax.value)

function formatCurrency(v) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)
}

function handleSave() {
  if (!form.value.name?.trim() || !form.value.contactId || !form.value.issueDate) return
  const payload = {
    name: form.value.name,
    issueDate: form.value.issueDate,
    validUntil: form.value.validUntil || null,
    status: form.value.status,
    internalNotes: form.value.internalNotes,
    lines: form.value.lines
      .filter(l => l.description?.trim())
      .map((l, i) => ({
        position: i,
        description: l.description,
        quantity: l.quantity || 0,
        unitPrice: l.unitPrice || 0,
        taxPercent: l.taxPercent || 0,
      })),
  }
  if (props.mode === 'purchase') {
    payload.providerId = form.value.contactId
    payload.providerNotes = form.value.contactNotes
  } else {
    payload.customerId = form.value.contactId
    payload.customerNotes = form.value.contactNotes
  }
  emit('save', payload)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0, 0, 0, 0.4);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.modal-container {
  width: 1100px; max-width: 96vw; max-height: 92vh;
  background: white; border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column; overflow: hidden;
}
.modal-header {
  padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: space-between;
}
.modal-title { margin: 0; font-size: 1.125rem; font-weight: 700; }
.modal-header-actions { display: flex; gap: 0.5rem; }

.modal-body { display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; padding: 1.5rem; overflow-y: auto; }
.modal-main { display: flex; flex-direction: column; gap: 1.5rem; }
.modal-sidebar { display: flex; flex-direction: column; gap: 1rem; }

.form-section { display: flex; flex-direction: column; gap: 0.75rem; }
.section-title { margin: 0; font-size: 0.95rem; font-weight: 700; }
.section-desc { margin: 0; font-size: var(--font-size-xs); color: var(--text-secondary); }

.field { display: flex; flex-direction: column; gap: 0.375rem; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.field-label { font-size: var(--font-size-sm); font-weight: 600; }
.required { color: var(--error-color); }
.textarea { resize: vertical; min-height: 60px; }

.lines-editor {
  border: 1px solid var(--border-color); border-radius: var(--border-radius-sm);
  overflow: hidden;
}
.le-header, .le-row {
  display: grid;
  grid-template-columns: 2.5fr 0.7fr 0.9fr 0.7fr 1fr 36px;
  gap: 0.5rem; align-items: center;
  padding: 0.5rem 0.75rem;
}
.le-header {
  background: var(--bg-hover); font-size: 0.7rem;
  text-transform: uppercase; color: var(--text-secondary);
  font-weight: 600;
}
.le-row { border-top: 1px solid var(--border-color); }
.input-sm { padding: 0.4rem 0.5rem; font-size: var(--font-size-xs); }
.select-sm { padding: 0.4rem 0.5rem; font-size: var(--font-size-xs); }
.input-number { text-align: right; }
.subtotal-value { font-weight: 600; font-size: var(--font-size-sm); text-align: right; }
.btn-icon-sm {
  background: none; border: none; cursor: pointer;
  color: var(--text-tertiary); padding: 0.25rem; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
}
.btn-icon-sm:hover { background: var(--error-light); color: var(--error-color); }
.add-line-btn { margin-top: 0.75rem; align-self: flex-start; }

.sidebar-card {
  background: var(--bg-hover); border-radius: var(--border-radius-sm);
  padding: 1rem;
}
.sidebar-card-title { margin: 0 0 0.75rem; font-size: 0.875rem; font-weight: 700; }
.sidebar-totals { display: flex; flex-direction: column; gap: 0.4rem; }
.sidebar-total-row { display: flex; justify-content: space-between; font-size: var(--font-size-sm); }
.total-final-row {
  border-top: 1px solid var(--border-color);
  padding-top: 0.5rem; margin-top: 0.25rem;
  font-weight: 700; font-size: 1rem;
}
</style>
