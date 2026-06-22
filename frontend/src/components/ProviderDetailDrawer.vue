<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel">
          <!-- Header -->
          <div class="drawer-header">
            <div class="drawer-header-left">
              <div class="drawer-avatar" :style="{ background: provider.avatarColor }">
                {{ provider.initials }}
              </div>
              <div>
                <h2 class="drawer-title">{{ provider.name }}</h2>
                <div class="drawer-meta">
                  <span :class="['type-badge', provider.type === 'Company' ? 'type-company' : 'type-person']">
                    <Building2 v-if="provider.type === 'Company'" :size="12" />
                    <User v-else :size="12" />
                    {{ typeLabel(provider.type) }}
                  </span>
                  <span :class="['badge', statusBadgeClass(provider.status)]">{{ statusLabel(provider.status) }}</span>
                </div>
              </div>
            </div>
            <div class="drawer-header-right">
              <button class="btn btn-secondary btn-sm" @click="$emit('edit', provider)">
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

            <!-- ========== A) INFORMACIÓ ========== -->
            <div v-if="activeTab === 'info'" class="tab-content">
              <div class="detail-summary">
                <div class="summary-card">
                  <span class="summary-label">Total comprat</span>
                  <span class="summary-amount">{{ formatCurrency(provider.detail.totalPurchased) }}</span>
                </div>
                <div class="summary-card">
                  <span class="summary-label">Pendent</span>
                  <span :class="['summary-amount', provider.detail.pendingBalance > 0 ? 'has-balance' : 'zero-balance']">
                    {{ formatCurrency(provider.detail.pendingBalance) }}
                  </span>
                </div>
                <div class="summary-card">
                  <span class="summary-label">Documents</span>
                  <span class="summary-amount">{{ provider.detail.totalDocuments }}</span>
                </div>
              </div>

              <section class="detail-section">
                <h4 class="section-title">
                  <User :size="16" />
                  Informació de contacte
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Nom</span>
                  <span class="detail-value">{{ provider.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Correu electrònic</span>
                  <span class="detail-value">{{ provider.email }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Telèfon</span>
                  <span class="detail-value">{{ provider.detail.phone || '—' }}</span>
                </div>
                <div v-if="provider.type === 'Company'" class="detail-row">
                  <span class="detail-label">NIF / CIF</span>
                  <span class="detail-value">{{ provider.vatId || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Web</span>
                  <span class="detail-value">{{ provider.detail.website || '—' }}</span>
                </div>
              </section>

              <section class="detail-section">
                <h4 class="section-title">
                  <MapPin :size="16" />
                  Adreça
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Adreça</span>
                  <span class="detail-value">{{ provider.detail.address || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Ciutat</span>
                  <span class="detail-value">{{ provider.city }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Província</span>
                  <span class="detail-value">{{ provider.detail.province || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">C.P.</span>
                  <span class="detail-value">{{ provider.detail.postalCode || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">País</span>
                  <span class="detail-value">{{ provider.detail.country || 'Espanya' }}</span>
                </div>
              </section>

              <section v-if="provider.type === 'Company'" class="detail-section">
                <h4 class="section-title">
                  <FileText :size="16" />
                  Informació fiscal
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Raó social</span>
                  <span class="detail-value">{{ provider.detail.legalName || provider.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">NIF / CIF</span>
                  <span class="detail-value font-mono">{{ provider.vatId || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Forma de pagament</span>
                  <span class="detail-value">{{ provider.detail.paymentMethod || 'Transferència 30 dies' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Compte bancari</span>
                  <span class="detail-value font-mono">{{ provider.detail.bankAccount || '—' }}</span>
                </div>
              </section>

              <section class="detail-section">
                <h4 class="section-title">
                  <Users :size="16" />
                  Contactes vinculats
                </h4>
                <div v-if="provider.linked.length" class="linked-chips">
                  <span v-for="link in provider.linked" :key="link" class="linked-chip">{{ link }}</span>
                </div>
                <p v-else class="empty-hint">Sense contactes vinculats.</p>
              </section>

              <section class="detail-section">
                <h4 class="section-title">
                  <Tag :size="16" />
                  Etiquetes
                </h4>
                <div v-if="provider.detail.tags && provider.detail.tags.length" class="tags-list">
                  <span v-for="tag in provider.detail.tags" :key="tag" class="tag-chip">{{ tag }}</span>
                </div>
                <p v-else class="empty-hint">Sense etiquetes.</p>
              </section>
            </div>

            <!-- ========== B) NOTES ========== -->
            <div v-if="activeTab === 'notes'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <StickyNote :size="16" />
                    Notes
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewNote = !showNewNote">
                    <Plus :size="14" />
                    Nova nota
                  </button>
                </div>

                <div v-if="showNewNote" class="new-item-form">
                  <textarea
                    class="input textarea"
                    rows="3"
                    placeholder="Escriu una nota…"
                    v-model="newNote.content"
                  ></textarea>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewNote = false; newNote.content = ''">Cancel·lar</button>
                    <button class="btn btn-primary btn-sm" @click="addNote" :disabled="!newNote.content.trim()">
                      <Check :size="14" />
                      Desar
                    </button>
                  </div>
                </div>

                <div v-if="provider.detail.notes.length" class="items-list">
                  <div v-for="note in provider.detail.notes" :key="note.id" class="item-card">
                    <div class="item-card-header">
                      <span class="item-date">{{ formatDateShort(note.date) }}</span>
                      <span class="item-author">{{ note.author }}</span>
                    </div>
                    <p class="item-text">{{ note.content }}</p>
                  </div>
                </div>
                <p v-else-if="!showNewNote" class="empty-hint">No hi ha notes per a aquest proveïdor.</p>
              </section>
            </div>

            <!-- ========== C) COMANDES DE COMPRA ========== -->
            <div v-if="activeTab === 'orders'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <FileText :size="16" />
                    Comandes de compra
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewOrder = !showNewOrder">
                    <Plus :size="14" />
                    Nova comanda
                  </button>
                </div>

                <div v-if="showNewOrder" class="new-item-form">
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Concepte</label>
                      <input class="input" type="text" placeholder="Descripció de la comanda" v-model="newOrder.concept" />
                    </div>
                    <div class="field">
                      <label class="field-label">Import</label>
                      <div class="input-suffix">
                        <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="newOrder.totalAmount" />
                        <span class="suffix">€</span>
                      </div>
                    </div>
                  </div>
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Data</label>
                      <input class="input" type="date" v-model="newOrder.date" />
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Notes</label>
                    <textarea class="input textarea" rows="2" placeholder="Notes addicionals…" v-model="newOrder.notes"></textarea>
                  </div>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewOrder = false; resetNewOrder()">Cancel·lar</button>
                    <button class="btn btn-primary btn-sm" @click="addOrder" :disabled="!newOrder.concept.trim()">
                      <Check :size="14" />
                      Desar
                    </button>
                  </div>
                </div>

                <div v-if="provider.detail.purchaseOrders.length" class="items-list">
                  <div v-for="order in provider.detail.purchaseOrders" :key="order.id" class="item-card item-card-row">
                    <div class="item-card-main">
                      <span class="item-number">{{ order.number }}</span>
                      <span class="item-concept">{{ order.concept }}</span>
                      <span class="item-date">{{ formatDateShort(order.date) }}</span>
                    </div>
                    <div class="item-card-end">
                      <span class="item-amount">{{ formatCurrency(order.totalAmount) }}</span>
                      <span :class="['badge', orderBadgeClass(order.status)]">{{ orderStatusLabel(order.status) }}</span>
                    </div>
                  </div>
                </div>
                <p v-else-if="!showNewOrder" class="empty-hint">No hi ha comandes de compra per a aquest proveïdor.</p>
              </section>
            </div>

            <!-- ========== D) ACTIVITAT ========== -->
            <div v-if="activeTab === 'activity'" class="tab-content">
              <section class="detail-section">
                <div class="section-title-row">
                  <h4 class="section-title">
                    <CalendarDays :size="16" />
                    Activitat
                  </h4>
                  <button class="btn btn-sm btn-secondary" @click="showNewActivity = !showNewActivity">
                    <Plus :size="14" />
                    Nova activitat
                  </button>
                </div>

                <div v-if="showNewActivity" class="new-item-form">
                  <div class="field-row">
                    <div class="field">
                      <label class="field-label">Tipus</label>
                      <select class="select" v-model="newActivity.type">
                        <option value="Llamada">Trucada</option>
                        <option value="Reunión">Reunió</option>
                        <option value="Email">Email</option>
                        <option value="Tarea">Tasca</option>
                        <option value="Visita">Visita</option>
                      </select>
                    </div>
                    <div class="field">
                      <label class="field-label">Data</label>
                      <input class="input" type="date" v-model="newActivity.date" />
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Assumpte</label>
                    <input class="input" type="text" placeholder="Descripció de l'activitat" v-model="newActivity.subject" />
                  </div>
                  <div class="field">
                    <label class="field-label">Notes</label>
                    <textarea class="input textarea" rows="2" placeholder="Notes addicionals…" v-model="newActivity.notes"></textarea>
                  </div>
                  <div class="new-item-actions">
                    <button class="btn btn-secondary btn-sm" @click="showNewActivity = false; resetNewActivity()">Cancel·lar</button>
                    <button class="btn btn-primary btn-sm" @click="addActivity" :disabled="!newActivity.subject.trim()">
                      <Check :size="14" />
                      Desar
                    </button>
                  </div>
                </div>

                <div v-if="provider.detail.activities.length" class="timeline">
                  <div v-for="act in provider.detail.activities" :key="act.id" class="timeline-item">
                    <div :class="['timeline-dot', 'dot-' + act.type.toLowerCase()]"></div>
                    <div class="timeline-content">
                      <div class="timeline-header">
                        <span class="activity-type-tag" :style="{ background: activityColor(act.type) }">{{ activityLabel(act.type) }}</span>
                        <span class="timeline-meta">{{ formatDateShort(act.date) }}</span>
                      </div>
                      <span class="timeline-action">{{ act.subject }}</span>
                      <span v-if="act.notes" class="timeline-notes">{{ act.notes }}</span>
                    </div>
                  </div>
                </div>
                <p v-else-if="!showNewActivity" class="empty-hint">No hi ha activitat registrada.</p>
              </section>
            </div>

          </div>

          <!-- Footer -->
          <div class="drawer-footer">
            <button class="btn btn-secondary" @click="$emit('edit', provider)">
              <Pencil :size="18" />
              Editar
            </button>
            <button class="btn btn-primary" @click="$emit('new-quote', provider)">
              <FileText :size="18" />
              Nou pressupost
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
  StickyNote, Plus, Check, CalendarDays
} from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  provider: { type: Object, required: true }
})

defineEmits(['close', 'edit', 'new-quote'])

const tabs = [
  { key: 'info', label: 'Informació', icon: User },
  { key: 'notes', label: 'Notes', icon: StickyNote },
  { key: 'orders', label: 'Comandes de compra', icon: FileText },
  { key: 'activity', label: 'Activitat', icon: CalendarDays },
]

const activeTab = ref('info')

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
  props.provider.detail.notes.unshift(note)
  newNote.content = ''
  showNewNote.value = false
}

const showNewOrder = ref(false)
const newOrder = reactive({
  concept: '',
  totalAmount: null,
  date: new Date().toISOString().split('T')[0],
  notes: ''
})

function resetNewOrder() {
  Object.assign(newOrder, { concept: '', totalAmount: null, date: new Date().toISOString().split('T')[0], notes: '' })
}

function addOrder() {
  if (!newOrder.concept.trim()) return
  const orderCount = props.provider.detail.purchaseOrders.length + 1
  const order = {
    id: Date.now(),
    number: `OC-${String(orderCount).padStart(3, '0')}`,
    concept: newOrder.concept.trim(),
    totalAmount: newOrder.totalAmount || 0,
    balanceDue: newOrder.totalAmount || 0,
    date: newOrder.date,
    notes: newOrder.notes,
    status: 'Draft'
  }
  props.provider.detail.purchaseOrders.unshift(order)
  resetNewOrder()
  showNewOrder.value = false
}

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
  props.provider.detail.activities.unshift(activity)
  resetNewActivity()
  showNewActivity.value = false
}

function statusBadgeClass(status) {
  const map = { Active: 'badge-success', Inactive: 'badge-warning' }
  return map[status] || 'badge-gray'
}

/* ── Display labels (internal values stay unchanged) ── */
function statusLabel(status) {
  const map = { Active: 'Actiu', Inactive: 'Inactiu' }
  return map[status] || status
}

function typeLabel(type) {
  const map = { Company: 'Empresa', Person: 'Persona' }
  return map[type] || type
}

function activityLabel(type) {
  const map = { Llamada: 'Trucada', 'Reunión': 'Reunió', Email: 'Email', Tarea: 'Tasca', Visita: 'Visita' }
  return map[type] || type
}

function orderStatusLabel(status) {
  const map = {
    Draft: 'Esborrany', Approved: 'Aprovada', PartiallyPaid: 'Parcial',
    Paid: 'Pagada', Cancelled: 'Cancel·lada',
  }
  return map[status] || status
}

function orderBadgeClass(status) {
  const map = { Draft: 'badge-gray', Approved: 'badge-primary', PartiallyPaid: 'badge-warning', Paid: 'badge-success', Cancelled: 'badge-error' }
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
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDateShort(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ca-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
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

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 0.625rem;
  flex-wrap: wrap;
}

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

.empty-hint {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  font-style: italic;
  margin: 0;
}

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
