<template>
  <div class="profile-view">
    <div class="view-header">
      <h1>Mi cuenta</h1>
      <p class="view-subtitle">Gestiona tu perfil personal y preferencias</p>
    </div>

    <div class="content-wrapper">
      <!-- Personal Info Card -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h3 class="card-title">Información personal</h3>
            <p class="card-subtitle">Tu nombre y avatar visibles para tu equipo</p>
          </div>
          <button v-if="!editingProfile" class="btn btn-secondary btn-sm" @click="startEditProfile">
            <Pencil :size="14" />
            Editar
          </button>
        </div>

        <form v-if="editingProfile" @submit.prevent="saveProfile" class="profile-form">
          <div class="avatar-upload">
            <div class="avatar-preview" @click="$refs.avatarInput.click()">
              <img v-if="avatarPreview" :src="avatarPreview" alt="Avatar" />
              <span v-else class="avatar-initials">{{ user?.initials || '?' }}</span>
              <div class="avatar-overlay">
                <Camera :size="20" />
              </div>
            </div>
            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              class="hidden-input"
              @change="onAvatarChange"
            />
            <span class="text-xs text-tertiary">JPG, PNG. Máx 2 MB</span>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nombre <span class="required">*</span></label>
              <input v-model="profileForm.first_name" class="input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Apellidos</label>
              <input v-model="profileForm.last_name" class="input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input :value="user?.email" class="input" disabled />
            <span class="field-hint">El email no se puede cambiar</span>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-ghost" @click="cancelEditProfile">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="savingProfile">
              <span v-if="savingProfile" class="loading-spinner loading-spinner-sm"></span>
              {{ savingProfile ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </form>

        <div v-else class="profile-display">
          <div class="avatar-display">
            <img v-if="user?.avatar" :src="user.avatar" alt="Avatar" class="avatar-img" />
            <span v-else class="avatar-initials-lg">{{ user?.initials || '?' }}</span>
          </div>
          <div class="profile-info">
            <p class="profile-name">{{ user?.full_name || 'Sin nombre' }}</p>
            <p class="profile-email">{{ user?.email }}</p>
            <p class="profile-joined">Miembro desde {{ formatDate(user?.date_joined) }}</p>
          </div>
        </div>
      </div>

      <!-- Security Card -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Seguridad</h3>
          <p class="card-subtitle">Gestiona tu contraseña de acceso</p>
        </div>
        <div class="security-content">
          <div class="security-row">
            <div>
              <p class="security-label">Contraseña</p>
              <p class="security-detail">Última actualización desconocida</p>
            </div>
            <button class="btn btn-secondary btn-sm" @click="showPasswordModal = true">
              <Lock :size="14" />
              Cambiar contraseña
            </button>
          </div>
        </div>
      </div>

      <!-- Companies Card -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h3 class="card-title">Mis empresas</h3>
            <p class="card-subtitle">Empresas a las que perteneces</p>
          </div>
          <button class="btn btn-primary btn-sm" @click="showCreateCompanyModal = true">
            <Plus :size="14" />
            Crear empresa
          </button>
        </div>
        <div class="companies-list">
          <div
            v-for="company in companies"
            :key="company.id"
            class="company-row"
            :class="{ active: company.id === activeCompany?.id }"
          >
            <div class="company-info">
              <div class="company-logo-sm">
                <img v-if="company.logo" :src="company.logo" :alt="company.name" />
                <span v-else>{{ company.name?.charAt(0) }}</span>
              </div>
              <div>
                <p class="company-name">{{ company.name }}</p>
                <span class="badge" :class="roleBadgeClass(company.role)">{{ roleLabel(company.role) }}</span>
              </div>
            </div>
            <div class="company-actions">
              <span v-if="company.id === activeCompany?.id" class="badge badge-success">Activa</span>
              <button
                v-else
                class="btn btn-ghost btn-sm"
                @click="handleSwitch(company.id)"
                :disabled="switching"
              >
                Cambiar
              </button>
              <router-link
                v-if="company.role === 'owner' || company.role === 'admin'"
                :to="'/settings/company'"
                class="btn btn-ghost btn-sm"
              >
                <Settings :size="14" />
              </router-link>
            </div>
          </div>
          <p v-if="!companies.length" class="empty-text">No perteneces a ninguna empresa</p>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <Teleport to="body">
      <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Cambiar contraseña</h3>
            <button class="modal-close" @click="showPasswordModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleChangePassword" class="modal-body">
            <div class="form-group">
              <label class="form-label">Contraseña actual</label>
              <input
                v-model="passwordForm.current"
                type="password"
                class="input"
                required
                autocomplete="current-password"
              />
              <span v-if="passwordErrors.current" class="field-error">{{ passwordErrors.current }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">Nueva contraseña</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="input"
                required
                autocomplete="new-password"
                placeholder="Mínimo 8 caracteres"
              />
              <span v-if="passwordErrors.newPassword" class="field-error">{{ passwordErrors.newPassword }}</span>
            </div>
            <div class="form-group">
              <label class="form-label">Confirmar nueva contraseña</label>
              <input
                v-model="passwordForm.confirm"
                type="password"
                class="input"
                required
                autocomplete="new-password"
              />
              <span v-if="passwordErrors.confirm" class="field-error">{{ passwordErrors.confirm }}</span>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showPasswordModal = false">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="savingPassword">
                {{ savingPassword ? 'Guardando...' : 'Cambiar contraseña' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Create Company Modal -->
    <Teleport to="body">
      <div v-if="showCreateCompanyModal" class="modal-overlay" @click.self="showCreateCompanyModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Crear nueva empresa</h3>
            <button class="modal-close" @click="showCreateCompanyModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleCreateCompany" class="modal-body">
            <div class="form-group">
              <label class="form-label">Nombre de la empresa <span class="required">*</span></label>
              <input v-model="newCompanyForm.name" class="input" required placeholder="Mi Empresa SL" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">CIF / NIF</label>
                <input v-model="newCompanyForm.tax_id" class="input" placeholder="B12345678" />
              </div>
              <div class="form-group">
                <label class="form-label">Moneda</label>
                <select v-model="newCompanyForm.currency" class="select">
                  <option value="EUR">EUR - Euro</option>
                  <option value="USD">USD - Dólar</option>
                  <option value="GBP">GBP - Libra</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Email de contacto</label>
              <input v-model="newCompanyForm.email" type="email" class="input" placeholder="info@empresa.com" />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showCreateCompanyModal = false">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="creatingCompany">
                {{ creatingCompany ? 'Creando...' : 'Crear empresa' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Pencil, Camera, Lock, Plus, Settings, X } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'

const {
  user, companies, activeCompany,
  updateProfile, changePassword, switchCompany, fetchMe,
} = useAuth()
const toast = useToast()

// ── Profile editing ─────────────────────────
const editingProfile = ref(false)
const savingProfile = ref(false)
const profileForm = reactive({ first_name: '', last_name: '' })
const avatarFile = ref(null)
const avatarPreview = ref(null)

function startEditProfile() {
  profileForm.first_name = user.value?.first_name || ''
  profileForm.last_name = user.value?.last_name || ''
  avatarPreview.value = user.value?.avatar || null
  avatarFile.value = null
  editingProfile.value = true
}

function cancelEditProfile() {
  editingProfile.value = false
  avatarFile.value = null
  avatarPreview.value = null
}

function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    toast.error('La imagen no puede superar 2 MB')
    return
  }
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

async function saveProfile() {
  savingProfile.value = true
  try {
    const data = {
      first_name: profileForm.first_name.trim(),
      last_name: profileForm.last_name.trim(),
    }
    if (avatarFile.value) data.avatar = avatarFile.value
    await updateProfile(data)
    toast.success('Perfil actualizado')
    editingProfile.value = false
  } catch {
    toast.error('Error al actualizar el perfil')
  } finally {
    savingProfile.value = false
  }
}

// ── Password ────────────────────────────────
const showPasswordModal = ref(false)
const savingPassword = ref(false)
const passwordForm = reactive({ current: '', newPassword: '', confirm: '' })
const passwordErrors = reactive({})

async function handleChangePassword() {
  Object.keys(passwordErrors).forEach(k => delete passwordErrors[k])

  if (passwordForm.newPassword.length < 8) {
    passwordErrors.newPassword = 'Mínimo 8 caracteres'
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirm) {
    passwordErrors.confirm = 'Las contraseñas no coinciden'
    return
  }

  savingPassword.value = true
  try {
    await changePassword(passwordForm.current, passwordForm.newPassword)
    toast.success('Contraseña actualizada')
    showPasswordModal.value = false
    passwordForm.current = ''
    passwordForm.newPassword = ''
    passwordForm.confirm = ''
  } catch (err) {
    if (err.data?.current_password) {
      passwordErrors.current = Array.isArray(err.data.current_password)
        ? err.data.current_password[0]
        : err.data.current_password
    } else {
      toast.error(err.message || 'Error al cambiar la contraseña')
    }
  } finally {
    savingPassword.value = false
  }
}

// ── Companies ───────────────────────────────
const switching = ref(false)

async function handleSwitch(companyId) {
  switching.value = true
  try {
    await switchCompany(companyId)
    toast.success('Empresa cambiada')
  } catch {
    toast.error('Error al cambiar de empresa')
  } finally {
    switching.value = false
  }
}

// ── Create Company ──────────────────────────
const showCreateCompanyModal = ref(false)
const creatingCompany = ref(false)
const newCompanyForm = reactive({ name: '', tax_id: '', email: '', currency: 'EUR' })

async function handleCreateCompany() {
  if (!newCompanyForm.name.trim()) return
  creatingCompany.value = true
  try {
    await authApi.createCompany({
      name: newCompanyForm.name.trim(),
      tax_id: newCompanyForm.tax_id.trim(),
      email: newCompanyForm.email.trim(),
      currency: newCompanyForm.currency,
    })
    toast.success('Empresa creada')
    showCreateCompanyModal.value = false
    newCompanyForm.name = ''
    newCompanyForm.tax_id = ''
    newCompanyForm.email = ''
    newCompanyForm.currency = 'EUR'
    // Refresh companies list
    await fetchMe()
  } catch (err) {
    toast.error(err.message || 'Error al crear la empresa')
  } finally {
    creatingCompany.value = false
  }
}

// ── Helpers ─────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
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
.profile-view {
  max-width: 800px;
}

.view-header {
  margin-bottom: var(--spacing-xl);
}

.view-header h1 {
  margin-bottom: 0.25rem;
}

.view-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Profile display */
.profile-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.avatar-display {
  flex-shrink: 0;
}

.avatar-img {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-initials-lg {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.125rem;
}

.profile-email {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0 0 0.25rem;
}

.profile-joined {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
  margin: 0;
}

/* Profile form */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initials {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-tertiary);
}

.avatar-overlay {
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

.avatar-preview:hover .avatar-overlay {
  opacity: 1;
}

.hidden-input {
  display: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
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

.field-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--error-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

/* Security */
.security-content {
  padding: 0;
}

.security-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.security-label {
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 0.125rem;
  font-size: var(--font-size-sm);
}

.security-detail {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0;
}

/* Companies list */
.companies-list {
  display: flex;
  flex-direction: column;
}

.company-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 0;
  border-bottom: 1px solid var(--border-color);
}

.company-row:last-child {
  border-bottom: none;
}

.company-row.active {
  background: var(--primary-light);
  margin: 0 calc(var(--spacing-lg) * -1);
  padding-left: var(--spacing-lg);
  padding-right: var(--spacing-lg);
  border-radius: var(--border-radius-sm);
}

.company-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.company-logo-sm {
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-sm);
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

.company-logo-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.company-name {
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
  font-size: var(--font-size-sm);
}

.company-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.empty-text {
  text-align: center;
  color: var(--text-tertiary);
  padding: var(--spacing-lg);
  font-size: var(--font-size-sm);
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

.loading-spinner-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
}

@media (max-width: 640px) {
  .profile-display {
    flex-direction: column;
    text-align: center;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .security-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .company-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .company-actions {
    align-self: flex-end;
  }
}
</style>
