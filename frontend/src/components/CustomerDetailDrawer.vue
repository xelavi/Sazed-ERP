<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel">
          <!-- Header -->
          <div class="drawer-header">
            <div class="drawer-header-left">
              <div class="drawer-avatar" :style="{ background: customer.avatarColor }">
                {{ customer.initials }}
              </div>
              <div>
                <h2 class="drawer-title">{{ customer.name }}</h2>
                <div class="drawer-meta">
                  <span :class="['type-badge', customer.type === 'Company' ? 'type-company' : 'type-person']">
                    <Building2 v-if="customer.type === 'Company'" :size="12" />
                    <User v-else :size="12" />
                    {{ customer.type }}
                  </span>
                  <span :class="['badge', statusBadgeClass(customer.status)]">{{ customer.status }}</span>
                </div>
              </div>
            </div>
            <div class="drawer-header-right">
              <button class="btn btn-secondary btn-sm" @click="$emit('edit', customer)">
                <Pencil :size="14" />
                <span>Editar</span>
              </button>
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">
                <X :size="16" />
              </button>
            </div>
          </div>

          <!-- Tabs -->
          <nav class="drawer-tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              :class="['drawer-tab', { active: activeTab === tab.key }]"
              @click="activeTab = tab.key"
            >
              <component :is="tab.icon" :size="15" />
              <span>{{ tab.label }}</span>
            </button>
          </nav>

          <!-- Tab Content -->
          <div class="drawer-body">

            <!-- ========== A) INFORMACIÓN ========== -->
            <div v-if="activeTab === 'info'" class="tab-content">
              <!-- Summary Cards -->
              <div class="detail-summary">
                <div class="summary-card">
                  <span class="summary-label">Total facturado</span>
                  <span class="summary-amount">{{ formatCurrency(customer.detail.totalInvoiced) }}</span>
                </div>
                <div class="summary-card">
                  <span class="summary-label">Pendiente</span>
                  <span :class="['summary-amount', customer.detail.pendingBalance > 0 ? 'has-balance' : 'zero-balance']">
                    {{ formatCurrency(customer.detail.pendingBalance) }}
                  </span>
                </div>
                <div class="summary-card">
                  <span class="summary-label">Documentos</span>
                  <span class="summary-amount">{{ customer.detail.totalDocuments }}</span>
                </div>
              </div>

              <!-- Contact info -->
              <section class="detail-section">
                <h4 class="section-title">
                  <User :size="16" />
                  Información de contacto
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Nombre</span>
                  <span class="detail-value">{{ customer.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Email</span>
                  <span class="detail-value">{{ customer.email }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Teléfono</span>
                  <span class="detail-value">{{ customer.detail.phone || '—' }}</span>
                </div>
                <div v-if="customer.type === 'Company'" class="detail-row">
                  <span class="detail-label">NIF / CIF</span>
                  <span class="detail-value">{{ customer.vatId || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Web</span>
                  <span class="detail-value">{{ customer.detail.website || '—' }}</span>
                </div>
              </section>

              <!-- Address -->
              <section class="detail-section">
                <h4 class="section-title">
                  <MapPin :size="16" />
                  Dirección
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Dirección</span>
                  <span class="detail-value">{{ customer.detail.address || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Ciudad</span>
                  <span class="detail-value">{{ customer.city }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Provincia</span>
                  <span class="detail-value">{{ customer.detail.province || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">C.P.</span>
                  <span class="detail-value">{{ customer.detail.postalCode || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">País</span>
                  <span class="detail-value">{{ customer.detail.country || 'España' }}</span>
                </div>
              </section>

              <!-- Fiscal info -->
              <section v-if="customer.type === 'Company'" class="detail-section">
                <h4 class="section-title">
                  <FileText :size="16" />
                  Información fiscal
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Razón social</span>
                  <span class="detail-value">{{ customer.detail.legalName || customer.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">NIF / CIF</span>
                  <span class="detail-value font-mono">{{ customer.vatId || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Forma de pago</span>
                  <span class="detail-value">{{ customer.detail.paymentMethod || 'Transferencia 30 días' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Cuenta bancaria</span>
                  <span class="detail-value font-mono">{{ customer.detail.bankAccount || '—' }}</span>
                </div>
              </section>

              <!-- Linked contacts -->
              <section class="detail-section">
                <h4 class="section-title">
                  <Users :size="16" />
                  Contactos vinculados
                </h4>
                <div v-if="customer.linked.length" class="linked-chips">
                  <span v-for="link in customer.linked" :key="link" class="linked-chip">{{ link }}</span>
                </div>
                <p v-else class="empty-hint">Sin contactos vinculados.</p>
              </section>

              <!-- Tags -->
              <section class="detail-section">
                <h4 class="section-title">
                  <Tag :size="16" />
                  Etiquetas
                </h4>
                <div v-if="customer.detail.tags && customer.detail.tags.length" class="tags-list">
                  <span v-for="tag in customer.detail.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>
                <p v-else class="empty-hint">Sin etiquetas.</p>
              </section>
            </div>

            <!-- ========== B) NOTAS ========== -->
            <div v-if="activeTab === 'notes'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <StickyNote :size="16" />
                    Notas
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewNote = !showNewNote">
                    <Plus :size="14" />
                    Nueva nota
                  </button>
                </div>

                <!-- New note form -->
                <div v-if="showNewNote" class="new-item-form">
                  <textarea
                    class="input textarea"
                    rows="3"
                    placeholder="Escribe una nota..."
                    v-model="newNote.content"
                  ></textarea>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewNote = false; newNote.content = ''">Cancelar</button>
                    <button class="btn btn-primary btn-sm" @click="addNote" :disabled="!newNote.content.trim()">
                      <Check :size="14" />
                      Guardar
                    </button>
                  </div>
                </div>

                <!-- Notes list -->
                <div v-if="customer.detail.notes.length" class="items-list">
                  <div v-for="note in customer.detail.notes" :key="note.id" class="item-card">
                    <div class="item-card-header">
                      <span class="item-date">{{ formatDateShort(note.date) }}</span>
                      <span class="item-author">{{ note.author }}</span>
                    </div>
                    <p class="item-text">{{ note.content }}</p>
                  </div>
                </div>
                <p v-else-if="!showNewNote" class="empty-hint">No hay notas para este contacto.</p>
              </section>
            </div>

            <!-- ========== C) PRESUPUESTOS ========== -->
            <div v-if="activeTab === 'quotes'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <FileText :size="16" />
                    Presupuestos
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewQuote = !showNewQuote">
                    <Plus :size="14" />
                    Nuevo presupuesto
                  </button>
                </div>

                <!-- New quote form -->
                <div v-if="showNewQuote" class="new-item-form">
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Concepto</label>
                      <input class="input" type="text" placeholder="Descripción del presupuesto" v-model="newQuote.concept" />
                    </div>
                    <div class="field">
                      <label class="field-label">Importe</label>
                      <div class="input-suffix">
                        <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="newQuote.amount" />
                        <span class="suffix">€</span>
                      </div>
                    </div>
                  </div>
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Fecha</label>
                      <input class="input" type="date" v-model="newQuote.date" />
                    </div>
                    <div class="field">
                      <label class="field-label">Validez (días)</label>
                      <input class="input" type="number" min="1" placeholder="30" v-model.number="newQuote.validDays" />
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Notas</label>
                    <textarea class="input textarea" rows="2" placeholder="Notas adicionales..." v-model="newQuote.notes"></textarea>
                  </div>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewQuote = false; resetNewQuote()">Cancelar</button>
                    <button class="btn btn-primary btn-sm" @click="addQuote" :disabled="!newQuote.concept.trim()">
                      <Check :size="14" />
                      Guardar
                    </button>
                  </div>
                </div>

                <!-- Quotes list -->
                <div v-if="customer.detail.quotes.length" class="items-list">
                  <div v-for="quote in customer.detail.quotes" :key="quote.id" class="item-card item-card-row">
                    <div class="item-card-main">
                      <span class="item-number">{{ quote.number }}</span>
                      <span class="item-concept">{{ quote.concept }}</span>
                      <span class="item-date">{{ formatDateShort(quote.date) }}</span>
                    </div>
                    <div class="item-card-end">
                      <span class="item-amount">{{ formatCurrency(quote.amount) }}</span>
                      <span :class="['badge', quoteBadgeClass(quote.status)]">{{ quote.status }}</span>
                    </div>
                  </div>
                </div>
                <p v-else-if="!showNewQuote" class="empty-hint">No hay presupuestos para este contacto.</p>
              </section>
            </div>

            <!-- ========== D) FACTURAS ========== -->
            <div v-if="activeTab === 'invoices'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <Receipt :size="16" />
                    Facturas
                  </h4>
                  <button class="btn btn-sm btn-primary" @click="$emit('new-invoice', customer)">
                    <Plus :size="14" />
                    Nueva factura
                  </button>
                </div>

                <!-- Invoices list -->
                <div v-if="customer.detail.invoices.length" class="items-list">
                  <div v-for="inv in customer.detail.invoices" :key="inv.id" class="item-card item-card-row">
                    <div class="item-card-main">
                      <span class="item-number">{{ inv.number }}</span>
                      <span class="item-date">{{ formatDateShort(inv.date) }}</span>
                    </div>
                    <div class="item-card-end">
                      <span class="item-amount">{{ formatCurrency(inv.amount) }}</span>
                      <span :class="['badge', invoiceBadgeClass(inv.status)]">{{ inv.status }}</span>
                    </div>
                  </div>
                </div>
                <p v-else class="empty-hint">No hay facturas para este contacto.</p>
              </section>
            </div>

            <!-- ========== E) ACTIVIDAD ========== -->
            <div v-if="activeTab === 'activity'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <CalendarDays :size="16" />
                    Actividad
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewActivity = !showNewActivity">
                    <Plus :size="14" />
                    Nueva actividad
                  </button>
                </div>

                <!-- New activity form -->
                <div v-if="showNewActivity" class="new-item-form">
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Tipo</label>
                      <select class="select" v-model="newActivity.type">
                        <option value="Llamada">Llamada</option>
                        <option value="Reunión">Reunión</option>
                        <option value="Email">Email</option>
                        <option value="Tarea">Tarea</option>
                        <option value="Visita">Visita</option>
                      </select>
                    </div>
                    <div class="field">
                      <label class="field-label">Fecha</label>
                      <input class="input" type="date" v-model="newActivity.date" />
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Asunto</label>
                    <input class="input" type="text" placeholder="Descripción de la actividad" v-model="newActivity.subject" />
                  </div>
                  <div class="field">
                    <label class="field-label">Notas</label>
                    <textarea class="input textarea" rows="2" placeholder="Notas adicionales..." v-model="newActivity.notes"></textarea>
                  </div>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewActivity = false; resetNewActivity()">Cancelar</button>
                    <button class="btn btn-primary btn-sm" @click="addActivity" :disabled="!newActivity.subject.trim()">
                      <Check :size="14" />
                      Guardar
                    </button>
                  </div>
                </div>

                <!-- Activity timeline -->
                <div v-if="customer.detail.activities.length" class="timeline">
                  <div v-for="act in customer.detail.activities" :key="act.id" class="timeline-item">
                    <div :class="['timeline-dot', 'dot-' + act.type.toLowerCase()]"></div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <span class="activity-type-tag" :style="{ background: activityColor(act.type) }">{{ act.type }}</span>
                        <span class="timeline-meta">{{ formatDateShort(act.date) }}</span>
                      </div>
                      <span class="timeline-action">{{ act.subject }}</span>
                      <span v-if="act.notes" class="timeline-notes">{{ act.notes }}</span>
                    </div>
                  </div>
                </div>
                <p v-else-if="!showNewActivity" class="empty-hint">No hay actividad registrada.</p>
              </section>
            </div>

            <!-- ========== F) COMPRAS ========== -->
            <div v-if="activeTab === 'purchases'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <ShoppingCart :size="16" />
                    Compras
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewPurchase = !showNewPurchase">
                    <Plus :size="14" />
                    Nueva compra
                  </button>
                </div>

                <!-- New purchase form -->
                <div v-if="showNewPurchase" class="new-item-form">
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Producto / Servicio</label>
                      <input class="input" type="text" placeholder="Nombre del producto" v-model="newPurchase.product" />
                    </div>
                    <div class="field">
                      <label class="field-label">Importe</label>
                      <div class="input-suffix">
                        <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="newPurchase.amount" />
                        <span class="suffix">€</span>
                      </div>
                    </div>
                  </div>
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Fecha</label>
                      <input class="input" type="date" v-model="newPurchase.date" />
                    </div>
                    <div class="field">
                      <label class="field-label">Cantidad</label>
                      <input class="input" type="number" min="1" placeholder="1" v-model.number="newPurchase.quantity" />
                    </div>
                  </div>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewPurchase = false; resetNewPurchase()">Cancelar</button>
                    <button class="btn btn-primary btn-sm" @click="addPurchase" :disabled="!newPurchase.product.trim()">
                      <Check :size="14" />
                      Guardar
                    </button>
                  </div>
                </div>

                <!-- Purchases list -->
                <div v-if="customer.detail.purchases.length" class="items-list">
                  <div v-for="purchase in customer.detail.purchases" :key="purchase.id" class="item-card item-card-row">
                    <div class="item-card-main">
                      <span class="item-concept">{{ purchase.product }}</span>
                      <span class="item-date">{{ formatDateShort(purchase.date) }} · Qty: {{ purchase.quantity }}</span>
                    </div>
                    <div class="item-card-end">
                      <span class="item-amount">{{ formatCurrency(purchase.amount) }}</span>
                      <span :class="['badge', purchaseBadgeClass(purchase.status)]">{{ purchase.status }}</span>
                    </div>
                  </div>
                </div>
                <p v-else-if="!showNewPurchase" class="empty-hint">No hay compras registradas.</p>
              </section>
            </div>

          </div>

          <!-- Footer -->
          <div class="drawer-footer">
            <button class="btn btn-secondary" @click="$emit('edit', customer)">
              <Pencil :size="18" />
              Editar
            </button>
            <button class="btn btn-primary" @click="$emit('new-invoice', customer)">
              <Receipt :size="18" />
              Nueva factura
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
  X, User, Building2, Pencil, FileText, MapPin, Users, Tag,
  StickyNote, Plus, Check, Receipt, CalendarDays, ShoppingCart,
  Clock
} from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  customer: { type: Object, required: true }
})

defineEmits(['close', 'edit', 'new-invoice'])

/* ── Tabs ── */
const tabs = [
  { key: 'info', label: 'Información', icon: User },
  { key: 'notes', label: 'Notas', icon: StickyNote },
  { key: 'quotes', label: 'Presupuestos', icon: FileText },
  { key: 'invoices', label: 'Facturas', icon: Receipt },
  { key: 'activity', label: 'Actividad', icon: CalendarDays },
  { key: 'purchases', label: 'Compras', icon: ShoppingCart }
]

const activeTab = ref('info')

/* ── New Note ── */
const showNewNote = ref(false)
const newNote = reactive({ content: '' })

function addNote() {
  if (!newNote.content.trim()) return
  const note = {
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    author: 'Admin',
    content: newNote.content.trim()
  }
  props.customer.detail.notes.unshift(note)
  newNote.content = ''
  showNewNote.value = false
}

/* ── New Quote ── */
const showNewQuote = ref(false)
const newQuote = reactive({
  concept: '',
  amount: null,
  date: new Date().toISOString().split('T')[0],
  validDays: 30,
  notes: ''
})

function resetNewQuote() {
  Object.assign(newQuote, { concept: '', amount: null, date: new Date().toISOString().split('T')[0], validDays: 30, notes: '' })
}

function addQuote() {
  if (!newQuote.concept.trim()) return
  const quoteCount = props.customer.detail.quotes.length + 1
  const quote = {
    id: Date.now(),
    number: `PRES-${String(quoteCount).padStart(3, '0')}`,
    concept: newQuote.concept.trim(),
    amount: newQuote.amount || 0,
    date: newQuote.date,
    validDays: newQuote.validDays || 30,
    notes: newQuote.notes,
    status: 'Borrador'
  }
  props.customer.detail.quotes.unshift(quote)
  resetNewQuote()
  showNewQuote.value = false
}

/* ── New Activity ── */
const showNewActivity = ref(false)
const newActivity = reactive({
  type: 'Llamada',
  date: new Date().toISOString().split('T')[0],
  subject: '',
  notes: ''
})

function resetNewActivity() {
  Object.assign(newActivity, { type: 'Llamada', date: new Date().toISOString().split('T')[0], subject: '', notes: '' })
}

function addActivity() {
  if (!newActivity.subject.trim()) return
  const activity = {
    id: Date.now(),
    type: newActivity.type,
    date: newActivity.date,
    subject: newActivity.subject.trim(),
    notes: newActivity.notes
  }
  props.customer.detail.activities.unshift(activity)
  resetNewActivity()
  showNewActivity.value = false
}

/* ── New Purchase ── */
const showNewPurchase = ref(false)
const newPurchase = reactive({
  product: '',
  amount: null,
  date: new Date().toISOString().split('T')[0],
  quantity: 1
})

function resetNewPurchase() {
  Object.assign(newPurchase, { product: '', amount: null, date: new Date().toISOString().split('T')[0], quantity: 1 })
}

function addPurchase() {
  if (!newPurchase.product.trim()) return
  const purchase = {
    id: Date.now(),
    product: newPurchase.product.trim(),
    amount: newPurchase.amount || 0,
    date: newPurchase.date,
    quantity: newPurchase.quantity || 1,
    status: 'Completada'
  }
  props.customer.detail.purchases.unshift(purchase)
  resetNewPurchase()
  showNewPurchase.value = false
}

/* ── Helpers ── */
function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning' }
  return map[status] || 'badge-gray'
}

function quoteBadgeClass(status) {
  const map = { Borrador: 'badge-gray', Enviado: 'badge-primary', Aceptado: 'badge-success', Rechazado: 'badge-error', Expirado: 'badge-warning' }
  return map[status] || 'badge-gray'
}

function invoiceBadgeClass(status) {
  const map = { Borrador: 'badge-gray', Aprobada: 'badge-primary', Pagada: 'badge-success', Parcial: 'badge-warning', Vencida: 'badge-error', Anulada: 'badge-gray' }
  return map[status] || 'badge-gray'
}

function purchaseBadgeClass(status) {
  const map = { Completada: 'badge-success', Pendiente: 'badge-warning', Cancelada: 'badge-error' }
  return map[status] || 'badge-gray'
}

function activityColor(type) {
  const map = {
    Llamada: 'rgba(59, 130, 246, 0.12)',
    Reunión: 'rgba(139, 92, 246, 0.12)',
    Email: 'rgba(16, 185, 129, 0.12)',
    Tarea: 'rgba(245, 158, 11, 0.12)',
    Visita: 'rgba(236, 72, 153, 0.12)'
  }
  return map[type] || 'rgba(100, 116, 139, 0.12)'
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
  width: 600px;
  max-width: 92vw;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.drawer-header-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-width: 0;
}

.drawer-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.drawer-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.drawer-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.drawer-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* ============================
   TABS
   ============================ */
.drawer-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  padding: 0 1.5rem;
  overflow-x: auto;
  flex-shrink: 0;
}

.drawer-tab {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.75rem 0.875rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  font-family: var(--font-family);
  color: var(--text-secondary);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.drawer-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.drawer-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
  font-weight: 600;
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

.has-balance { color: var(--warning-color); }
.zero-balance { color: var(--text-tertiary); }

/* ============================
   TYPE BADGES
   ============================ */
.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.2rem 0.5rem;
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

.font-mono {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ============================
   LINKED / TAGS
   ============================ */
.linked-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.linked-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  font-size: var(--font-size-xs);
  font-weight: 500;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 6px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  background: var(--primary-light);
  color: var(--primary-color);
  font-size: var(--font-size-xs);
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

/* ============================
   NEW ITEM FORMS
   ============================ */
.new-item-form {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 1rem;
  margin-bottom: 1rem;
}

.new-item-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.field {
  margin-bottom: 0.75rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.field-row .field {
  margin-bottom: 0;
}

.input-suffix {
  position: relative;
}

.input-suffix .input {
  padding-right: 2.25rem;
}

.suffix {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  pointer-events: none;
}

.textarea {
  resize: vertical;
  min-height: 64px;
  line-height: 1.5;
}

/* ============================
   ITEMS LIST
   ============================ */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-card {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  padding: 0.75rem 1rem;
}

.item-card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.item-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.item-card-main {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.item-card-end {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-shrink: 0;
}

.item-number {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--primary-color);
  font-family: 'JetBrains Mono', monospace;
}

.item-concept {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-date {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.item-author {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  font-weight: 500;
}

.item-amount {
  font-weight: 700;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.item-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin: 0;
  line-height: 1.5;
  white-space: pre-wrap;
}

/* ============================
   TIMELINE (Activity)
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
  margin-top: 4px;
}

.dot-llamada { background: #3b82f6; }
.dot-reunión { background: #8b5cf6; }
.dot-email { background: #10b981; }
.dot-tarea { background: #f59e0b; }
.dot-visita { background: #ec4899; }

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.activity-type-tag {
  display: inline-flex;
  padding: 0.125rem 0.5rem;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 4px;
  letter-spacing: 0.03em;
  color: var(--text-primary);
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

.timeline-notes {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  font-style: italic;
  line-height: 1.4;
}

/* ============================
   EMPTY STATE
   ============================ */
.empty-hint {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  font-style: italic;
  margin: 0;
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
  .drawer-tabs {
    padding: 0 1rem;
  }
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
