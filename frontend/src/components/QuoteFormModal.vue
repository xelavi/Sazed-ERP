<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <div class="modal-header">
            <h2 class="modal-title">
              {{ isEditing ? 'Editar pressupost' : (mode === 'purchase' ? 'Nou pressupost de compra' : 'Nou pressupost') }}
            </h2>
            <div class="modal-header-actions">
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">Cancel·lar</button>
              <button class="btn btn-primary btn-sm" @click="handleSave">
                <Save :size="16" />
                <span>Desar</span>
              </button>
            </div>
          </div>

          <div class="modal-body">
            <div class="modal-main">
              <section class="form-section">
                <h3 class="section-title">Dades del pressupost</h3>

                <div class="field">
                  <label class="field-label">Nom <span class="required">*</span></label>
                  <input
                    class="input"
                    type="text"
                    placeholder="p. ex. Serveis de consultoria gener…"
                    v-model="form.name"
                  />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">{{ contactLabel }} <span class="required">*</span></label>
                    <select class="select" v-model="form.contactId">
                      <option value="">Selecciona {{ contactLabel.toLowerCase() }}…</option>
                      <option v-for="c in contactOptions" :key="c.id" :value="c.id">{{ c.name }}</option>
                      <option value="__new__">+ Crear {{ mode === 'purchase' ? 'un proveïdor' : 'un client' }} nou…</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Estat</label>
                    <select class="select" v-model="form.status">
                      <option value="Draft">Esborrany</option>
                      <option value="Sent">{{ mode === 'purchase' ? 'Sol·licitat' : 'Enviat' }}</option>
                      <option value="Accepted">Acceptat</option>
                      <option value="Rejected">Rebutjat</option>
                      <option value="Expired">Caducat</option>
                    </select>
                  </div>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Data d'emissió <span class="required">*</span></label>
                    <input class="input" type="date" v-model="form.issueDate" />
                  </div>
                  <div class="field">
                    <label class="field-label">Vàlid fins</label>
                    <input class="input" type="date" v-model="form.validUntil" />
                  </div>
                </div>
              </section>

              <section class="form-section">
                <h3 class="section-title">Línies</h3>
                <p class="section-desc">Afegeix productes o serveis. Els totals es calculen automàticament.</p>

                <div class="lines-editor">
                  <div class="le-header">
                    <span class="le-h-desc">Descripció</span>
                    <span class="le-h-qty">Qt.</span>
                    <span class="le-h-price">Preu</span>
                    <span class="le-h-tax">IVA %</span>
                    <span class="le-h-subtotal">Subtotal</span>
                    <span class="le-h-actions"></span>
                  </div>

                  <div v-for="(line, idx) in form.lines" :key="idx" class="le-row">
                    <ProductAutocomplete
                      v-model="line.description"
                      :products="products"
                      :linked-product-id="line.productId"
                      :price-mode="mode === 'purchase' ? 'purchase' : 'sale'"
                      placeholder="Producte o servei…"
                      @select="(p) => onProductSelect(line, p)"
                      @clear="onProductClear(line)"
                    />
                    <input class="input input-sm input-number" type="number" min="0" step="0.01" v-model.number="line.quantity" />
                    <input class="input input-sm input-number" type="number" min="0" step="0.01" v-model.number="line.unitPrice" />
                    <select class="select select-sm" v-model.number="line.taxPercent">
                      <option :value="0">0%</option>
                      <option :value="4">4%</option>
                      <option :value="10">10%</option>
                      <option :value="21">21%</option>
                    </select>
                    <span class="subtotal-value">{{ formatCurrency(calcLineSubtotal(line)) }}</span>
                    <button class="btn-icon-sm" @click="removeLine(idx)" title="Eliminar">
                      <Trash2 :size="14" />
                    </button>
                  </div>
                </div>

                <button class="btn btn-secondary btn-sm add-line-btn" @click="addLine">
                  <Plus :size="16" />
                  <span>Afegir línia</span>
                </button>
              </section>

              <section class="form-section">
                <h3 class="section-title">Notes</h3>
                <div class="field">
                  <label class="field-label">{{ mode === 'purchase' ? 'Notes del proveïdor' : 'Notes per al client' }}</label>
                  <textarea class="input textarea" rows="2" v-model="form.contactNotes"></textarea>
                </div>
                <div class="field">
                  <label class="field-label">Notes internes</label>
                  <textarea class="input textarea" rows="2" v-model="form.internalNotes"></textarea>
                </div>
              </section>
            </div>

            <div class="modal-sidebar">
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Resum</h4>
                <div class="sidebar-totals">
                  <div class="sidebar-total-row">
                    <span>Subtotal</span>
                    <span>{{ formatCurrency(calcSubtotal) }}</span>
                  </div>
                  <div class="sidebar-total-row">
                    <span>Impostos</span>
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

    <CustomerFormModal
      v-if="mode !== 'purchase'"
      :open="createContactOpen"
      @close="createContactOpen = false"
      @save="handleContactCreated"
    />
    <ProviderFormModal
      v-else
      :open="createContactOpen"
      @close="createContactOpen = false"
      @save="handleContactCreated"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Save, Plus, Trash2 } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import customersApi from '@/services/customers'
import providersApi from '@/services/providers'
import productsApi from '@/services/products'
import {
  mapCustomerFromApi, mapCustomerToApi,
  mapProviderFromApi, mapProviderToApi, mapProductFromApi
} from '@/services/mappers'
import { taxPercentFromProduct, priceForMode } from '@/services/productLine'
import CustomerFormModal from '@/components/CustomerFormModal.vue'
import ProviderFormModal from '@/components/ProviderFormModal.vue'
import ProductAutocomplete from '@/components/ProductAutocomplete.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  quote: { type: Object, default: null },
  contacts: { type: Array, default: () => [] },
  mode: { type: String, default: 'sales' }, // 'sales' | 'purchase'
  preselectedContactId: { type: [Number, String], default: null },
  preselectedLine: { type: Object, default: null },
})

const emit = defineEmits(['close', 'save', 'contact-created'])

const isEditing = computed(() => !!props.quote)
const contactLabel = computed(() => props.mode === 'purchase' ? 'Proveïdor' : 'Client')

/* ── Contact options + inline creation ── */
const extraContacts = ref([]) // contacts created inline from this modal

const contactOptions = computed(() => {
  if (!extraContacts.value.length) return props.contacts
  const ids = new Set(props.contacts.map(c => c.id))
  return [...props.contacts, ...extraContacts.value.filter(c => !ids.has(c.id))]
})

const createContactOpen = ref(false)

/* ── Product catalog (for line autocomplete) ── */
const products = ref([])

async function loadProducts() {
  try {
    const data = await productsApi.getAll({ page_size: 1000 })
    const items = Array.isArray(data) ? data : (data.results || [])
    products.value = items.map(mapProductFromApi).filter(p => p.status !== 'Archived')
  } catch (err) {
    console.error('[QuoteFormModal] failed to load products:', err)
    products.value = []
  }
}

/* Autorellena la línea al elegir un producto del catálogo. */
function onProductSelect(line, product) {
  line.productId = product.id
  line.unitPrice = priceForMode(product, props.mode === 'purchase' ? 'purchase' : 'sale')
  const pct = taxPercentFromProduct(product)
  if (pct !== null) line.taxPercent = pct
}

function onProductClear(line) {
  line.productId = null
}

async function handleContactCreated(formData) {
  try {
    let mapped
    if (props.mode === 'purchase') {
      const created = await providersApi.create(mapProviderToApi(formData))
      mapped = mapProviderFromApi(created)
    } else {
      const created = await customersApi.create(mapCustomerToApi(formData))
      mapped = mapCustomerFromApi(created)
    }
    extraContacts.value.push(mapped)
    form.value.contactId = mapped.id
    createContactOpen.value = false
    emit('contact-created', mapped)
  } catch (err) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: err.message || 'No s\'ha pogut crear el contacte',
      confirmButtonColor: '#667eea',
      customClass: { popup: 'swal-erp-popup' },
      target: document.body,
      heightAuto: false
    })
  }
}

const today = new Date().toISOString().split('T')[0]

const form = ref(emptyForm())

/* ── Open the inline "new contact" modal when sentinel option picked ── */
watch(() => form.value.contactId, (val, prev) => {
  if (val === '__new__') {
    form.value.contactId = prev === '__new__' ? '' : (prev ?? '')
    createContactOpen.value = true
  }
})

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
  return { productId: null, description: '', quantity: 1, unitPrice: 0, taxPercent: 21 }
}

watch(() => props.open, (val) => {
  if (val) {
    loadProducts()
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
              productId: l.productId || l.product || null,
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
      if (props.preselectedLine) {
        form.value.lines = [{ ...emptyLine(), ...props.preselectedLine }]
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
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)
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
        productId: l.productId || null,
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
