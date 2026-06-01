<template>
  <div class="account-view">
    <div class="view-header">
      <h1>Gestión de cuenta</h1>
      <p class="view-subtitle">Tus datos personales y de seguridad</p>
    </div>

    <div class="content-wrapper">
      <!-- Personal Info Card -->
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h3 class="card-title">Información personal</h3>
            <p class="card-subtitle">Datos visibles para tu equipo</p>
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
            <label class="form-label">Teléfono</label>
            <input
              v-model="profileForm.phone"
              class="input"
              placeholder="+34 600 000 000"
              inputmode="tel"
            />
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

        <div v-if="!editingProfile" class="info-grid">
          <div class="info-row">
            <span class="info-label">Teléfono</span>
            <span class="info-value">{{ user?.phone || '—' }}</span>
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
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Pencil, Camera, Lock, X } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const {
  user,
  updateProfile, changePassword,
} = useAuth()
const toast = useToast()

const editingProfile = ref(false)
const savingProfile = ref(false)
const profileForm = reactive({ first_name: '', last_name: '', phone: '' })
const avatarFile = ref(null)
const avatarPreview = ref(null)

function startEditProfile() {
  profileForm.first_name = user.value?.first_name || ''
  profileForm.last_name = user.value?.last_name || ''
  profileForm.phone = user.value?.phone || ''
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
      phone: profileForm.phone.trim(),
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

// Password change
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

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })
}

</script>

<style scoped>
.account-view {
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

.profile-info { flex: 1; }

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

.info-grid {
  margin-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  padding: 0.25rem 0;
}

.info-label {
  color: var(--text-tertiary);
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

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

.hidden-input { display: none; }

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

.required { color: var(--error-color); }

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

.modal-header h3 { margin: 0; }

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
  .form-row { grid-template-columns: 1fr; }
  .security-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
