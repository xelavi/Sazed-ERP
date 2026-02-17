<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ isEditing ? 'Editar contacto' : 'Nuevo contacto' }}</h2>
            <button class="modal-close" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- ==================== MAIN COLUMN ==================== -->
            <div class="modal-main">

              <!-- ── Información básica ── -->
              <section class="form-section">
                <h3 class="section-title">Información básica</h3>
                <p class="section-desc">Datos principales del contacto. Podrás utilizarlos en facturas y presupuestos.</p>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Tipo de contacto <span class="required">*</span></label>
                    <select class="select" v-model="form.type">
                      <option value="Company">Empresa</option>
                      <option value="Person">Persona</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Estado</label>
                    <select class="select" v-model="form.status">
                      <option value="Active">Activo</option>
                      <option value="Inactive">Inactivo</option>
                    </select>
                  </div>
                </div>

                <div class="field">
                  <label class="field-label">{{ form.type === 'Company' ? 'Nombre de la empresa' : 'Nombre completo' }} <span class="required">*</span></label>
                  <input class="input" type="text" :placeholder="form.type === 'Company' ? 'Ej: Acme Corp.' : 'Ej: María López'" v-model="form.name" />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Email <span class="required">*</span></label>
                    <input class="input" type="email" placeholder="correo@ejemplo.com" v-model="form.email" />
                  </div>
                  <div class="field">
                    <label class="field-label">Teléfono</label>
                    <input class="input" type="tel" placeholder="+34 600 000 000" v-model="form.phone" />
                  </div>
                </div>

                <div v-if="form.type === 'Company'" class="field">
                  <label class="field-label">NIF / CIF</label>
                  <input class="input" type="text" placeholder="Ej: B-12345678" v-model="form.vatId" />
                </div>

                <div class="field">
                  <label class="field-label">Web</label>
                  <input class="input" type="url" placeholder="https://www.ejemplo.com" v-model="form.website" />
                </div>
              </section>

              <!-- ── Dirección ── -->
              <section class="form-section">
                <h3 class="section-title">Dirección</h3>
                <p class="section-desc">Dirección fiscal del contacto para documentos y envíos.</p>

                <div class="field">
                  <label class="field-label">Dirección</label>
                  <input class="input" type="text" placeholder="Calle, número, piso..." v-model="form.address" />
                </div>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Ciudad</label>
                    <input class="input" type="text" placeholder="Madrid" v-model="form.city" />
                  </div>
                  <div class="field">
                    <label class="field-label">Provincia</label>
                    <input class="input" type="text" placeholder="Madrid" v-model="form.province" />
                  </div>
                  <div class="field">
                    <label class="field-label">C.P.</label>
                    <input class="input" type="text" placeholder="28001" v-model="form.postalCode" />
                  </div>
                </div>

                <div class="field">
                  <label class="field-label">País</label>
                  <select class="select" v-model="form.country">
                    <option value="España">España</option>
                    <option value="Portugal">Portugal</option>
                    <option value="Francia">Francia</option>
                    <option value="Alemania">Alemania</option>
                    <option value="Italia">Italia</option>
                    <option value="Reino Unido">Reino Unido</option>
                    <option value="Estados Unidos">Estados Unidos</option>
                  </select>
                </div>
              </section>

              <!-- ── Información fiscal (Company only) ── -->
              <section v-if="form.type === 'Company'" class="form-section">
                <h3 class="section-title">Información fiscal</h3>
                <p class="section-desc">Datos fiscales y condiciones de pago por defecto.</p>

                <div class="field">
                  <label class="field-label">Razón social</label>
                  <input class="input" type="text" placeholder="Razón social completa" v-model="form.legalName" />
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Forma de pago</label>
                    <select class="select" v-model="form.paymentMethod">
                      <option value="Transferencia 30 días">Transferencia 30 días</option>
                      <option value="Transferencia">Transferencia</option>
                      <option value="Domiciliación">Domiciliación</option>
                      <option value="Tarjeta">Tarjeta</option>
                      <option value="Efectivo">Efectivo</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Cuenta bancaria (IBAN)</label>
                    <input class="input" type="text" placeholder="ES00 0000 0000 0000 0000 0000" v-model="form.bankAccount" />
                  </div>
                </div>
              </section>

              <!-- ── Notas ── -->
              <section class="form-section">
                <h3 class="section-title">Notas internas</h3>
                <textarea class="input textarea" rows="3" placeholder="Añade notas internas sobre este contacto..." v-model="form.internalNotes"></textarea>
              </section>
            </div>

            <!-- ==================== SIDEBAR COLUMN ==================== -->
            <div class="modal-sidebar">

              <!-- ── Avatar Preview ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Preview</h4>
                <div class="avatar-preview">
                  <div class="preview-avatar" :style="{ background: previewGradient }">
                    {{ previewInitials }}
                  </div>
                  <span class="preview-name">{{ form.name || 'Nombre del contacto' }}</span>
                  <span class="preview-email">{{ form.email || 'email@ejemplo.com' }}</span>
                </div>
              </div>

              <!-- ── Etiquetas ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Etiquetas</h4>
                <p class="sidebar-card-desc">Organiza tus contactos con etiquetas personalizadas.</p>

                <div class="field">
                  <input class="input" type="text" placeholder="Busca o crea tags" v-model="tagInput" @keydown.enter.prevent="addTag" />
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

              <!-- ── Contacto vinculado ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Contacto vinculado</h4>
                <p class="sidebar-card-desc">Vincula este contacto con una empresa o persona.</p>

                <div class="field">
                  <input class="input" type="text" placeholder="Busca un contacto..." v-model="form.linkedContact" />
                </div>
              </div>

              <!-- ── Opciones ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Opciones</h4>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.isCustomer" />
                  <span>Es cliente</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.isSupplier" />
                  <span>Es proveedor</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('close')">Descartar</button>
            <button class="btn btn-primary" @click="handleSave">
              <Check :size="18" />
              <span>Guardar</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { X, Check } from 'lucide-vue-next'
import Swal from 'sweetalert2'

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
    paymentMethod: 'Transferencia 30 días',
    bankAccount: '',
    internalNotes: '',
    tags: [],
    linkedContact: '',
    isCustomer: true,
    isSupplier: false
  }
}

const form = reactive(blankForm())
const tagInput = ref('')

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
      paymentMethod: c.detail?.paymentMethod || 'Transferencia 30 días',
      bankAccount: c.detail?.bankAccount || '',
      internalNotes: c.detail?.internalNotes || '',
      tags: [...(c.detail?.tags || [])],
      linkedContact: '',
      isCustomer: c.detail?.isCustomer ?? true,
      isSupplier: c.detail?.isSupplier ?? false
    })
  } else if (isOpen) {
    Object.assign(form, blankForm())
    tagInput.value = ''
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
  if (!form.name.trim()) errors.push('El nombre es obligatorio')
  if (!form.email.trim()) errors.push('El email es obligatorio')
  if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.push('El email no es válido')

  if (errors.length) {
    Swal.fire({
      icon: 'warning',
      title: 'Campos obligatorios',
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
