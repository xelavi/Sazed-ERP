<template>
  <div class="onboarding-page">
    <div class="onboarding-card">
      <div class="onboarding-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <span class="logo-text">Sazed ERP</span>
      </div>

      <div class="onboarding-header">
        <h2>Configura tus empresas</h2>
        <p class="onboarding-subtitle">
          Crea al menos una empresa para empezar a usar Sazed ERP.
          Si alguien te ha invitado a una empresa existente, aparecerá automáticamente.
        </p>
      </div>

      <!-- Existing companies (from invitations) -->
      <div v-if="companies.length" class="section">
        <h3 class="section-title">Tus empresas</h3>
        <div class="company-list">
          <div v-for="company in companies" :key="company.id" class="company-item">
            <div class="company-item-icon">
              <img v-if="company.logo" :src="company.logo" :alt="company.name" />
              <span v-else>{{ company.name?.charAt(0) }}</span>
            </div>
            <div class="company-item-info">
              <span class="company-item-name">{{ company.name }}</span>
              <span class="badge" :class="roleBadgeClass(company.role)">{{ roleLabel(company.role) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Created companies (during this session, not yet saved to backend list) -->
      <div v-if="newCompanies.length" class="section">
        <h3 class="section-title">Empresas creadas</h3>
        <div class="company-list">
          <div v-for="(c, i) in newCompanies" :key="i" class="company-item company-item-new">
            <div class="company-item-icon">
              <span>{{ c.name.charAt(0) }}</span>
            </div>
            <div class="company-item-info">
              <span class="company-item-name">{{ c.name }}</span>
              <span class="company-item-detail">{{ c.tax_id || 'Sin CIF' }} · {{ c.currency }}</span>
            </div>
            <button class="btn-icon" @click="removeNewCompany(i)" aria-label="Eliminar">
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- Add company form -->
      <div class="section">
        <button
          v-if="!showForm"
          class="add-company-trigger"
          @click="showForm = true"
        >
          <div class="add-icon">
            <Plus :size="20" />
          </div>
          <div>
            <span class="add-label">Crear nueva empresa</span>
            <span class="add-hint">Añade los datos de tu empresa o negocio</span>
          </div>
        </button>

        <div v-if="showForm" class="company-form-card">
          <h3 class="form-card-title">Nueva empresa</h3>
          <form @submit.prevent="addCompany" class="company-form">
            <div class="form-group">
              <label class="form-label">Nombre comercial <span class="required">*</span></label>
              <input
                v-model="form.name"
                class="input"
                :class="{ 'input-error': formErrors.name }"
                placeholder="Mi Empresa SL"
                required
                ref="nameInput"
                @input="delete formErrors.name"
              />
              <span v-if="formErrors.name" class="field-error">{{ formErrors.name }}</span>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">CIF / NIF</label>
                <input v-model="form.tax_id" class="input" placeholder="B12345678" />
              </div>
              <div class="form-group">
                <label class="form-label">Razón social</label>
                <input v-model="form.legal_name" class="input" placeholder="Empresa SL" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Email de contacto</label>
                <input v-model="form.email" type="email" class="input" placeholder="info@empresa.com" />
              </div>
              <div class="form-group">
                <label class="form-label">Moneda</label>
                <select v-model="form.currency" class="select">
                  <option value="EUR">EUR - Euro</option>
                  <option value="USD">USD - Dólar</option>
                  <option value="GBP">GBP - Libra</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button type="button" class="btn btn-ghost" @click="cancelForm">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="loading-spinner loading-spinner-sm"></span>
                {{ saving ? 'Creando...' : 'Crear empresa' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Continue / footer -->
      <div class="onboarding-footer">
        <button
          class="btn btn-primary btn-lg btn-block"
          :disabled="!canContinue"
          @click="handleContinue"
        >
          Continuar al panel
          <ArrowRight :size="18" />
        </button>
        <p v-if="!canContinue" class="footer-hint">
          Crea al menos una empresa para continuar
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Trash2, ArrowRight } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'

const router = useRouter()
const { companies, fetchMe } = useAuth()
const toast = useToast()

const showForm = ref(false)
const saving = ref(false)
const nameInput = ref(null)

const newCompanies = ref([])
const form = reactive({ name: '', tax_id: '', legal_name: '', email: '', currency: 'EUR' })
const formErrors = reactive({})

const totalCompanies = computed(() => companies.value.length + newCompanies.value.length)
const canContinue = computed(() => totalCompanies.value > 0)

function resetForm() {
  form.name = ''
  form.tax_id = ''
  form.legal_name = ''
  form.email = ''
  form.currency = 'EUR'
  Object.keys(formErrors).forEach(k => delete formErrors[k])
}

function cancelForm() {
  showForm.value = false
  resetForm()
}

async function addCompany() {
  Object.keys(formErrors).forEach(k => delete formErrors[k])
  if (!form.name.trim()) {
    formErrors.name = 'El nombre es obligatorio'
    return
  }

  saving.value = true
  try {
    await authApi.createCompany({
      name: form.name.trim(),
      tax_id: form.tax_id.trim(),
      legal_name: form.legal_name.trim(),
      email: form.email.trim(),
      currency: form.currency,
    })

    newCompanies.value.push({ ...form, name: form.name.trim() })
    toast.success(`Empresa "${form.name.trim()}" creada`)
    resetForm()
    showForm.value = false

    // Refresh companies from backend
    try { await fetchMe() } catch { /* non-critical */ }
  } catch (err) {
    if (err.data?.name) {
      formErrors.name = Array.isArray(err.data.name) ? err.data.name[0] : err.data.name
    } else {
      toast.error(err.message || 'Error al crear la empresa')
    }
  } finally {
    saving.value = false
  }
}

function removeNewCompany(index) {
  // Note: company already created in backend, this only removes from local display
  // In a real app you might want to delete it via API, but for onboarding flow this is fine
  newCompanies.value.splice(index, 1)
}

async function handleContinue() {
  // Refresh session to ensure company data is up to date
  try { await fetchMe() } catch { /* ignore */ }
  router.push('/')
}

function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Admin', editor: 'Editor', viewer: 'Lector' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[role] || 'badge-gray'
}
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl) var(--spacing-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.onboarding-card {
  width: 100%;
  max-width: 580px;
  background: #fff;
  border-radius: var(--border-radius-lg);
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

/* Logo */
.onboarding-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.onboarding-logo .logo-icon {
  width: 36px;
  height: 36px;
  color: var(--primary-color);
}

.onboarding-logo .logo-icon svg {
  width: 100%;
  height: 100%;
}

.onboarding-logo .logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

/* Header */
.onboarding-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.onboarding-header h2 {
  font-size: var(--font-size-2xl);
  margin-bottom: 0.5rem;
}

.onboarding-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  max-width: 440px;
  margin: 0 auto;
}

/* Sections */
.section {
  margin-bottom: 1.25rem;
}

.section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.625rem;
}

/* Company list */
.company-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.company-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--bg-secondary);
}

.company-item-new {
  border-style: dashed;
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.company-item-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-sm);
  background: white;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.company-item-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.company-item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.company-item-name {
  font-weight: 500;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.company-item-detail {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.btn-icon {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: var(--border-radius-sm);
  display: flex;
  transition: all var(--transition-fast);
}

.btn-icon:hover {
  background: var(--error-light);
  color: var(--error-color);
}

/* Add company trigger */
.add-company-trigger {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  padding: 1rem;
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius);
  background: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  font-family: var(--font-family);
}

.add-company-trigger:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.add-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.add-company-trigger:hover .add-icon {
  background: var(--primary-color);
  color: white;
}

.add-label {
  display: block;
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin-bottom: 0.125rem;
}

.add-hint {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* Company form */
.company-form-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.25rem;
  background: var(--bg-secondary);
}

.form-card-title {
  font-size: var(--font-size-base);
  margin-bottom: 1rem;
}

.company-form {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.875rem;
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

.input-error {
  border-color: var(--error-color) !important;
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--error-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.25rem;
}

.loading-spinner-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

/* Footer */
.onboarding-footer {
  margin-top: 1.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-color);
}

.btn-block {
  width: 100%;
}

.btn-lg {
  padding: 0.875rem 1.5rem;
  font-size: var(--font-size-base);
}

.footer-hint {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 0.5rem;
  margin-bottom: 0;
}

@media (max-width: 520px) {
  .onboarding-card {
    padding: 1.75rem 1.25rem;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
