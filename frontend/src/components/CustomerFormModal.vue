<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ isEditing ? 'Editar contacte' : 'Nou contacte' }}</h2>
            <button class="modal-close" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- ==================== MAIN COLUMN ==================== -->
            <div class="modal-main">

              <!-- ── Informació bàsica ── -->
              <section class="form-section">
                <h3 class="section-title">Informació bàsica</h3>
                <p class="section-desc">Dades principals del contacte. Les podràs utilitzar en factures i pressupostos.</p>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Tipus de contacte <span class="required">*</span></label>
                    <select class="select" v-model="form.type">
                      <option value="Company">Empresa</option>
                      <option value="Person">Persona</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Estat</label>
                    <select class="select" v-model="form.status">
                      <option value="Active">Actiu</option>
                      <option value="Inactive">Inactiu</option>
                    </select>
                  </div>
                </div>

                <div class="field">
                  <label class="field-label">{{ form.type === 'Company' ? 'Nom de l\'empresa' : 'Nom complet' }} <span class="required">*</span></label>
                  <input class="input" type="text" :placeholder="form.type === 'Company' ? 'Ex: Acme Corp.' : 'Ex: Maria López'" v-model="form.name" />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Correu electrònic <span class="required">*</span></label>
                    <input class="input" type="email" placeholder="correu@exemple.com" v-model="form.email" />
                  </div>
                  <div class="field">
                    <label class="field-label">Telèfon</label>
                    <input class="input" type="tel" placeholder="+34 600 000 000" v-model="form.phone" />
                  </div>
                </div>

                <div v-if="form.type === 'Company'" class="field">
                  <label class="field-label">NIF / CIF</label>
                  <input class="input" type="text" placeholder="Ex: B-12345678" v-model="form.vatId" />
                </div>

                <div class="field">
                  <label class="field-label">Web</label>
                  <input class="input" type="url" placeholder="https://www.exemple.com" v-model="form.website" />
                </div>
              </section>

              <!-- ── Adreça ── -->
              <section class="form-section">
                <h3 class="section-title">Adreça</h3>
                <p class="section-desc">Adreça fiscal del contacte per a documents i enviaments.</p>

                <div class="field">
                  <label class="field-label">Adreça</label>
                  <input class="input" type="text" placeholder="Carrer, número, pis…" v-model="form.address" />
                </div>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Ciutat</label>
                    <input class="input" type="text" placeholder="Barcelona" v-model="form.city" />
                  </div>
                  <div class="field">
                    <label class="field-label">Província</label>
                    <input class="input" type="text" placeholder="Barcelona" v-model="form.province" />
                  </div>
                  <div class="field">
                    <label class="field-label">C.P.</label>
                    <input class="input" type="text" placeholder="08001" v-model="form.postalCode" />
                  </div>
                </div>

                <div class="field">
                  <label class="field-label">País</label>
                  <select class="select" v-model="form.country">
                    <option value="España">Espanya</option>
                    <option value="Portugal">Portugal</option>
                    <option value="Francia">França</option>
                    <option value="Alemania">Alemanya</option>
                    <option value="Italia">Itàlia</option>
                    <option value="Reino Unido">Regne Unit</option>
                    <option value="Estados Unidos">Estats Units</option>
                  </select>
                </div>
              </section>

              <!-- ── Informació fiscal (només empresa) ── -->
              <section v-if="form.type === 'Company'" class="form-section">
                <h3 class="section-title">Informació fiscal</h3>
                <p class="section-desc">Dades fiscals i condicions de pagament per defecte.</p>

                <div class="field">
                  <label class="field-label">Raó social</label>
                  <input class="input" type="text" placeholder="Raó social completa" v-model="form.legalName" />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Forma de pagament</label>
                    <select class="select" v-model="form.paymentMethod">
                      <option value="Transferència 30 dies">Transferència 30 dies</option>
                      <option value="Transferència">Transferència</option>
                      <option value="Domiciliació">Domiciliació</option>
                      <option value="Targeta">Targeta</option>
                      <option value="Efectiu">Efectiu</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Compte bancari (IBAN)</label>
                    <input class="input" type="text" placeholder="ES00 0000 0000 0000 0000 0000" v-model="form.bankAccount" />
                  </div>
                </div>
              </section>

              <!-- ── Notes ── -->
              <section class="form-section">
                <h3 class="section-title">Notes internes</h3>
                <textarea class="input textarea" rows="3" placeholder="Afegeix notes internes sobre aquest contacte…" v-model="form.internalNotes"></textarea>
              </section>
            </div>

            <!-- ==================== SIDEBAR COLUMN ==================== -->
            <div class="modal-sidebar">

              <!-- ── Previsualització de l'avatar ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Previsualització</h4>
                <div class="avatar-preview">
                  <div class="preview-avatar" :style="{ background: previewGradient }">
                    {{ previewInitials }}
                  </div>
                  <span class="preview-name">{{ form.name || 'Nom del contacte' }}</span>
                  <span class="preview-email">{{ form.email || 'correu@exemple.com' }}</span>
                </div>
              </div>

              <!-- ── Etiquetes ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Etiquetes</h4>
                <p class="sidebar-card-desc">Organitza els teus contactes amb etiquetes personalitzades.</p>

                <div class="field">
                  <input class="input" type="text" placeholder="Cerca o crea etiquetes" v-model="tagInput" @keydown.enter.prevent="addTag" />
                  <div v-if="form.tags.length" class="tags-list">
                    <span v-for="(tag, i) in form.tags" :key="i" class="tag-chip">
                      {{ tag }}
                      <button class="tag-remove" @click="removeTag(i)">
                        <X :size="12" />
                      </button>
                    </span>
                  </div>
                </div>
              </div>

              <!-- ── Contactes vinculats ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Contactes vinculats</h4>
                <p class="sidebar-card-desc">Vincula amb altres empreses o persones del directori.</p>

                <div v-if="form.linkedContacts.length" class="tags-list" style="margin-bottom: 0.625rem;">
                  <span v-for="contact in form.linkedContacts" :key="contact.id" class="tag-chip">
                    {{ contact.name }}
                    <button class="tag-remove" @click="removeLinkedContact(contact.id)">
                      <X :size="12" />
                    </button>
                  </span>
                </div>

                <div class="linked-search-wrap">
                  <div class="linked-input-wrap">
                    <Search :size="14" class="linked-search-icon" />
                    <input
                      class="input linked-input"
                      type="text"
                      placeholder="Cerca un contacte…"
                      v-model="linkedSearchQuery"
                      @input="onLinkedSearch"
                      @focus="showLinkedDropdown = true"
                      @blur="onLinkedBlur"
                    />
                  </div>
                  <div v-if="showLinkedDropdown && linkedResults.length" class="linked-dropdown">
                    <button
                      v-for="c in linkedResults"
                      :key="c.id"
                      class="linked-option"
                      @mousedown.prevent="selectLinkedContact(c)"
                    >
                      <span class="linked-option-name">{{ c.name }}</span>
                      <span class="linked-option-email">{{ c.email }}</span>
                    </button>
                  </div>
                  <div v-else-if="showLinkedDropdown && linkedSearchQuery && !linkedResults.length" class="linked-dropdown">
                    <div class="linked-no-results">Cap resultat</div>
                  </div>
                </div>
              </div>

              <!-- ── Opcions ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Opcions</h4>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.isCustomer" />
                  <span>És client</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.isSupplier" />
                  <span>És proveïdor</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('close')">Descartar</button>
            <button class="btn btn-primary" @click="handleSave">
              <Check :size="18" />
              <span>Desar</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { X, Check, Search } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import customersApi from '@/services/customers'

const props = defineProps({
  open: { type: Boolean, default: false },
  customer: { type: Object, default: null }
})

const emit = defineEmits(['close', 'save'])

const isEditing = computed(() => !!props.customer)

/* ── Avatar gradients ── */
const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #EC4899 0%, #F59E0B 100%)',
  'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
  'linear-gradient(135deg, #F59E0B 0%, #EF4444 100%)',
  'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
  'linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%)',
  'linear-gradient(135deg, #3B82F6 0%, #06B6D4 100%)',
  'linear-gradient(135deg, #EF4444 0%, #F59E0B 100%)',
  'linear-gradient(135deg, #667eea 0%, #10B981 100%)',
  'linear-gradient(135deg, #06B6D4 0%, #10B981 100%)'
]

/* ── Default blank form ── */
function blankForm() {
  return {
    type: 'Company',
    status: 'Active',
    name: '',
    email: '',
    phone: '',
    vatId: '',
    website: '',
    address: '',
    city: '',
    province: '',
    postalCode: '',
    country: 'España',
    legalName: '',
    paymentMethod: 'Transferència 30 dies',
    bankAccount: '',
    internalNotes: '',
    tags: [],
    linkedContactIds: [],
    linkedContacts: [],
    isCustomer: true,
    isSupplier: false
  }
}

const form = reactive(blankForm())
const tagInput = ref('')

/* ── Linked contacts search ── */
const linkedSearchQuery = ref('')
const linkedResults = ref([])
const showLinkedDropdown = ref(false)
let linkedTimer = null

async function onLinkedSearch() {
  clearTimeout(linkedTimer)
  const q = linkedSearchQuery.value.trim()
  if (!q) { linkedResults.value = []; return }
  linkedTimer = setTimeout(async () => {
    try {
      const data = await customersApi.search(q)
      const items = Array.isArray(data) ? data : (data.results || [])
      linkedResults.value = items
        .filter(c => !form.linkedContactIds.includes(c.id))
        .filter(c => !props.customer || c.id !== props.customer.id)
        .slice(0, 8)
        .map(c => ({ id: c.id, name: c.name, email: c.email || '' }))
    } catch { linkedResults.value = [] }
  }, 280)
}

function selectLinkedContact(contact) {
  if (!form.linkedContactIds.includes(contact.id)) {
    form.linkedContactIds.push(contact.id)
    form.linkedContacts.push(contact)
  }
  linkedSearchQuery.value = ''
  linkedResults.value = []
  showLinkedDropdown.value = false
}

function removeLinkedContact(id) {
  const idx = form.linkedContactIds.indexOf(id)
  if (idx !== -1) { form.linkedContactIds.splice(idx, 1); form.linkedContacts.splice(idx, 1) }
}

function onLinkedBlur() {
  setTimeout(() => { showLinkedDropdown.value = false }, 180)
}

/* ── Preview ── */
const previewInitials = computed(() => {
  if (!form.name) return '?'
  const parts = form.name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return parts[0].substring(0, 2).toUpperCase()
})

const previewGradient = computed(() => {
  if (props.customer && props.customer.avatarColor) return props.customer.avatarColor
  const idx = form.name ? form.name.length % gradients.length : 0
  return gradients[idx]
})

/* ── Populate form when editing ── */
watch(() => props.open, (isOpen) => {
  if (isOpen && props.customer) {
    const c = props.customer
    Object.assign(form, {
      type: c.type,
      status: c.status,
      name: c.name,
      email: c.email,
      phone: c.detail?.phone || '',
      vatId: c.vatId || '',
      website: c.detail?.website || '',
      address: c.detail?.address || '',
      city: c.city,
      province: c.detail?.province || '',
      postalCode: c.detail?.postalCode || '',
      country: c.detail?.country || 'España',
      legalName: c.detail?.legalName || '',
      paymentMethod: c.detail?.paymentMethod || 'Transferència 30 dies',
      bankAccount: c.detail?.bankAccount || '',
      internalNotes: c.detail?.internalNotes || '',
      tags: [...(c.detail?.tags || [])],
      linkedContactIds: [...(c.detail?.linkedContactIds || [])],
      linkedContacts: [...(c.detail?.linkedContacts || [])],
      isCustomer: c.detail?.isCustomer ?? true,
      isSupplier: c.detail?.isSupplier ?? false
    })
  } else if (isOpen) {
    Object.assign(form, blankForm())
    tagInput.value = ''
    linkedSearchQuery.value = ''
    linkedResults.value = []
  }
})

/* ── Tags ── */
function addTag() {
  const val = tagInput.value.trim()
  if (val && !form.tags.includes(val)) {
    form.tags.push(val)
  }
  tagInput.value = ''
}

function removeTag(index) {
  form.tags.splice(index, 1)
}

/* ── Save ── */
function handleSave() {
  const errors = []
  if (!form.name.trim()) errors.push('El nom és obligatori')
  if (!form.email.trim()) errors.push('El correu electrònic és obligatori')
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.push('El correu electrònic no és vàlid')

  if (errors.length) {
    Swal.fire({
      icon: 'warning',
      title: 'Camps obligatoris',
      html: `<ul style="text-align:left;margin:0;padding-left:1.2em">${errors.map(e => `<li>${e}</li>`).join('')}</ul>`,
      confirmButtonText: 'OK',
      confirmButtonColor: '#667eea',
      customClass: { popup: 'swal-erp-popup' },
      backdrop: 'rgba(0,0,0,0.15)',
      target: document.body,
      heightAuto: false
    })
    return
  }

  const initials = previewInitials.value
  const avatarColor = previewGradient.value

  emit('save', { ...form, initials, avatarColor })
  emit('close')
}
</script>

<style scoped>
/* ============================
   OVERLAY & CONTAINER
   ============================ */
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
  max-width: 960px;
  max-height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px -12px rgba(0, 0, 0, 0.2);
}

/* ============================
   HEADER
   ============================ */
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

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-sm);
  border: none;
  background: none;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ============================
   BODY (scroll area)
   ============================ */
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

/* ============================
   FORM SECTIONS
   ============================ */
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

/* ============================
   FIELDS
   ============================ */
.field {
  margin-bottom: 1rem;
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

.required {
  color: var(--error-color);
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.field-row:last-child {
  margin-bottom: 0;
}

.field-row .field {
  margin-bottom: 0;
}

.field-row-3 {
  grid-template-columns: repeat(3, 1fr);
}

.textarea {
  resize: vertical;
  min-height: 72px;
  line-height: 1.5;
}

/* Toggle (checkbox + label) */
.toggle-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.toggle-field:last-child {
  margin-bottom: 0;
}

/* ============================
   SIDEBAR CARDS
   ============================ */
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
  margin: 0 0 0.25rem;
}

.sidebar-card-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0 0 1rem;
}

/* Avatar preview */
.avatar-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0 0.5rem;
}

.preview-avatar {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.preview-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
}

.preview-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  text-align: center;
}

/* Tags */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--primary-light);
  color: var(--primary-color);
  font-size: var(--font-size-xs);
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.tag-remove {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.tag-remove:hover {
  opacity: 1;
}

/* ============================
   LINKED CONTACTS
   ============================ */
.linked-search-wrap {
  position: relative;
}

.linked-input-wrap {
  position: relative;
}

.linked-search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.linked-input {
  padding-left: 2.25rem;
}

.linked-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  z-index: 200;
  max-height: 200px;
  overflow-y: auto;
}

.linked-option {
  display: flex;
  flex-direction: column;
  width: 100%;
  text-align: left;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  border-bottom: 1px solid #f5f5f7;
  cursor: pointer;
  transition: background var(--transition-fast);
  font-family: var(--font-family);
}

.linked-option:last-child {
  border-bottom: none;
}

.linked-option:hover {
  background: var(--bg-hover);
}

.linked-option-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.linked-option-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.linked-no-results {
  padding: 0.75rem;
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  text-align: center;
}

/* ============================
   FOOTER
   ============================ */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.75rem;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

/* ============================
   TRANSITION
   ============================ */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: translateY(16px) scale(0.97);
  opacity: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }

  .modal-body {
    flex-direction: column;
    padding: 1.25rem;
  }

  .modal-sidebar {
    width: 100%;
  }

  .field-row,
  .field-row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
