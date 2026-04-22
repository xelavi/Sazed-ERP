<template>
  <div class="company-settings-view">
    <div class="view-header">
      <div>
        <h1>Configuración de empresa</h1>
        <p class="view-subtitle">{{ activeCompany?.name }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" :size="16" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: General -->
    <div v-if="activeTab === 'general'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Datos generales</h3>
          <p class="card-subtitle">Información básica de la empresa</p>
        </div>
        <form @submit.prevent="saveGeneral" class="settings-form">
          <div class="form-group logo-group">
            <label class="form-label">Logo de la empresa</label>
            <div class="logo-upload">
              <div class="logo-preview" @click="$refs.logoInput.click()">
                <img v-if="logoPreview" :src="logoPreview" alt="Logo" />
                <Building2 v-else :size="28" class="logo-placeholder-icon" />
                <div class="logo-overlay">
                  <Camera :size="18" />
                </div>
              </div>
              <input
                ref="logoInput"
                type="file"
                accept="image/*"
                class="hidden-input"
                @change="onLogoChange"
              />
              <span class="text-xs text-tertiary">Recomendado: 256x256px, PNG o SVG</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nombre comercial <span class="required">*</span></label>
              <input v-model="generalForm.name" class="input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Razón social</label>
              <input v-model="generalForm.legal_name" class="input" placeholder="Empresa SL" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">CIF / NIF</label>
              <input v-model="generalForm.tax_id" class="input" placeholder="B12345678" />
            </div>
            <div class="form-group">
              <label class="form-label">Email de contacto</label>
              <input v-model="generalForm.email" type="email" class="input" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Teléfono</label>
              <input v-model="generalForm.phone" class="input" placeholder="+34 600 000 000" />
            </div>
            <div class="form-group">
              <label class="form-label">Sitio web</label>
              <input v-model="generalForm.website" class="input" placeholder="https://miempresa.com" />
            </div>
          </div>

          <div class="form-section-title">Dirección</div>

          <div class="form-group">
            <label class="form-label">Dirección</label>
            <input v-model="generalForm.address" class="input" placeholder="Calle Principal 1" />
          </div>

          <div class="form-row form-row-3">
            <div class="form-group">
              <label class="form-label">Ciudad</label>
              <input v-model="generalForm.city" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Provincia</label>
              <input v-model="generalForm.province" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Código postal</label>
              <input v-model="generalForm.postal_code" class="input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">País</label>
            <input v-model="generalForm.country" class="input" />
          </div>

          <div class="form-section-title">Personalización</div>

          <div class="form-group">
            <label class="form-label">Color principal</label>
            <div class="color-picker-row">
              <input type="color" v-model="generalForm.primary_color" class="color-input" />
              <input v-model="generalForm.primary_color" class="input color-text-input" maxlength="7" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingGeneral">
              {{ savingGeneral ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tab: Billing / Invoicing -->
    <div v-if="activeTab === 'billing'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Facturación</h3>
          <p class="card-subtitle">Configuración de moneda y numeración de facturas</p>
        </div>
        <form @submit.prevent="saveBilling" class="settings-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Moneda</label>
              <select v-model="billingForm.currency" class="select">
                <option value="EUR">EUR - Euro</option>
                <option value="USD">USD - Dólar</option>
                <option value="GBP">GBP - Libra</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Prefijo de factura</label>
              <input v-model="billingForm.invoice_prefix" class="input" placeholder="FAC" maxlength="10" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Inicio del año fiscal</label>
            <select v-model="billingForm.fiscal_year_start" class="select">
              <option v-for="(m, i) in months" :key="i" :value="i + 1">{{ m }}</option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingBilling">
              {{ savingBilling ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tab: Members -->
    <div v-if="activeTab === 'members'" class="tab-content">
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h3 class="card-title">Miembros</h3>
            <p class="card-subtitle">{{ members.length }} miembro{{ members.length !== 1 ? 's' : '' }}</p>
          </div>
          <button class="btn btn-primary btn-sm" @click="showInviteModal = true">
            <UserPlus :size="14" />
            Invitar
          </button>
        </div>
        <div class="members-table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Desde</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.id">
                <td>
                  <div class="member-cell">
                    <div class="member-avatar">
                      <img v-if="m.user?.avatar" :src="m.user.avatar" :alt="m.user.full_name" />
                      <span v-else>{{ m.user?.initials || '?' }}</span>
                    </div>
                    <div>
                      <p class="member-name">{{ m.user?.full_name || m.user?.email }}</p>
                      <p class="member-email">{{ m.user?.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="roleBadgeClass(m.role)">{{ roleLabel(m.role) }}</span>
                </td>
                <td class="text-sm text-secondary">{{ formatDate(m.joined_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="loadingMembers" class="loading-center">
            <div class="loading-spinner"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Plan -->
    <div v-if="activeTab === 'plan'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Plan actual</h3>
          <p class="card-subtitle">Gestiona tu suscripción</p>
        </div>
        <div class="plan-display">
          <div class="plan-badge">
            <Crown :size="20" />
            <span class="plan-name">{{ planLabel(activeCompany?.plan) }}</span>
          </div>
          <p class="plan-description">
            Estás usando el plan <strong>{{ planLabel(activeCompany?.plan) }}</strong>.
            Para cambiar de plan, contacta con soporte.
          </p>
        </div>
      </div>
    </div>

    <!-- Invite Member Modal -->
    <Teleport to="body">
      <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Invitar miembro</h3>
            <button class="modal-close" @click="showInviteModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleInvite" class="modal-body">
            <div class="form-group">
              <label class="form-label">Email del usuario <span class="required">*</span></label>
              <input v-model="inviteForm.email" type="email" class="input" required placeholder="usuario@email.com" />
            </div>
            <div class="form-group">
              <label class="form-label">Rol</label>
              <select v-model="inviteForm.role" class="select">
                <option value="admin">Administrador</option>
                <option value="editor">Editor</option>
                <option value="viewer">Solo lectura</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showInviteModal = false">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="inviting">
                {{ inviting ? 'Invitando...' : 'Enviar invitación' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import {
  Building2, Camera, UserPlus, Crown, X,
  Settings2, Receipt, Users, Sparkles,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'

const { activeCompany, activeRole } = useAuth()
const toast = useToast()

// ── Tabs ────────────────────────────────────
const tabs = [
  { id: 'general', label: 'General', icon: Settings2 },
  { id: 'billing', label: 'Facturación', icon: Receipt },
  { id: 'members', label: 'Miembros', icon: Users },
  { id: 'plan', label: 'Plan', icon: Sparkles },
]
const activeTab = ref('general')

// ── General settings ────────────────────────
const generalForm = reactive({
  name: '', legal_name: '', tax_id: '',
  email: '', phone: '', website: '',
  address: '', city: '', province: '', postal_code: '', country: '',
  primary_color: '#667eea',
})
const logoFile = ref(null)
const logoPreview = ref(null)
const savingGeneral = ref(false)

function loadCompanyData(company) {
  if (!company) return
  const fields = [
    'name', 'legal_name', 'tax_id', 'email', 'phone', 'website',
    'address', 'city', 'province', 'postal_code', 'country', 'primary_color',
  ]
  fields.forEach(f => { generalForm[f] = company[f] || '' })
  if (!generalForm.primary_color) generalForm.primary_color = '#667eea'
  logoPreview.value = company.logo || null

  billingForm.currency = company.currency || 'EUR'
  billingForm.invoice_prefix = company.invoice_prefix || 'FAC'
  billingForm.fiscal_year_start = company.fiscal_year_start || 1
}

function onLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    toast.error('La imagen no puede superar 2 MB')
    return
  }
  logoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

async function saveGeneral() {
  savingGeneral.value = true
  try {
    let payload
    if (logoFile.value) {
      payload = new FormData()
      Object.entries(generalForm).forEach(([k, v]) => payload.append(k, v))
      payload.append('logo', logoFile.value)
    } else {
      payload = { ...generalForm }
    }
    await authApi.updateCompany(activeCompany.value.id, payload)
    toast.success('Datos actualizados')
    logoFile.value = null
  } catch {
    toast.error('Error al guardar los datos')
  } finally {
    savingGeneral.value = false
  }
}

// ── Billing settings ────────────────────────
const billingForm = reactive({ currency: 'EUR', invoice_prefix: 'FAC', fiscal_year_start: 1 })
const savingBilling = ref(false)
const months = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

async function saveBilling() {
  savingBilling.value = true
  try {
    await authApi.updateCompany(activeCompany.value.id, {
      currency: billingForm.currency,
      invoice_prefix: billingForm.invoice_prefix,
      fiscal_year_start: billingForm.fiscal_year_start,
    })
    toast.success('Configuración de facturación actualizada')
  } catch {
    toast.error('Error al guardar')
  } finally {
    savingBilling.value = false
  }
}

// ── Members ─────────────────────────────────
const members = ref([])
const loadingMembers = ref(false)

async function fetchMembers() {
  if (!activeCompany.value) return
  loadingMembers.value = true
  try {
    const data = await authApi.getMembers(activeCompany.value.id)
    members.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    toast.error('Error al cargar miembros')
  } finally {
    loadingMembers.value = false
  }
}

// ── Invite ──────────────────────────────────
const showInviteModal = ref(false)
const inviting = ref(false)
const inviteForm = reactive({ email: '', role: 'editor' })

async function handleInvite() {
  if (!inviteForm.email.trim()) return
  inviting.value = true
  try {
    await authApi.inviteMember(activeCompany.value.id, inviteForm.email.trim(), inviteForm.role)
    toast.success('Invitación enviada')
    showInviteModal.value = false
    inviteForm.email = ''
    inviteForm.role = 'editor'
    await fetchMembers()
  } catch (err) {
    toast.error(err.message || 'Error al invitar')
  } finally {
    inviting.value = false
  }
}

// ── Helpers ─────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Admin', editor: 'Editor', viewer: 'Lector' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[role] || 'badge-gray'
}

function planLabel(plan) {
  const map = { free: 'Gratuito', starter: 'Starter', pro: 'Pro' }
  return map[plan] || 'Gratuito'
}

// ── Lifecycle ───────────────────────────────
watch(activeTab, (tab) => {
  if (tab === 'members' && !members.value.length) fetchMembers()
})

watch(activeCompany, (company) => {
  if (company) {
    loadCompanyData(company)
    if (activeTab.value === 'members') fetchMembers()
  }
}, { immediate: false })

onMounted(async () => {
  if (activeCompany.value) {
    // Fetch full company details
    try {
      const full = await authApi.getCompany(activeCompany.value.id)
      loadCompanyData(full)
    } catch {
      loadCompanyData(activeCompany.value)
    }
  }
})
</script>

<style scoped>
.company-settings-view {
  max-width: 800px;
}

.view-header {
  margin-bottom: var(--spacing-lg);
}

.view-header h1 {
  margin-bottom: 0.25rem;
}

.view-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: var(--spacing-lg);
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-family);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

/* Form styles */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-row-3 {
  grid-template-columns: 1fr 1fr 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--error-color);
}

.form-section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
}

/* Logo upload */
.logo-group {
  margin-bottom: 0.5rem;
}

.logo-upload {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-preview {
  width: 64px;
  height: 64px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--border-color);
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-placeholder-icon {
  color: var(--text-tertiary);
}

.logo-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.logo-preview:hover .logo-overlay {
  opacity: 1;
}

.hidden-input {
  display: none;
}

/* Color picker */
.color-picker-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-input {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  padding: 2px;
}

.color-text-input {
  max-width: 120px;
}

/* Members table */
.members-table-wrapper {
  overflow-x: auto;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 600;
  overflow: hidden;
  flex-shrink: 0;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-name {
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  font-size: var(--font-size-sm);
}

.member-email {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
  margin: 0;
}

.loading-center {
  display: flex;
  justify-content: center;
  padding: var(--spacing-xl);
}

/* Plan display */
.plan-display {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.plan-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 9999px;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.plan-name {
  font-size: var(--font-size-lg);
}

.plan-description {
  color: var(--text-secondary);
  max-width: 400px;
  margin: 0 auto;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9000;
  padding: var(--spacing-lg);
}

.modal-card {
  background: white;
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--border-radius-sm);
  display: flex;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

@media (max-width: 640px) {
  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .form-row,
  .form-row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
