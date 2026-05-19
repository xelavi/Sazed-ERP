<template>
  <div class="companies-view">
    <div class="view-header">
      <div>
        <h1>Gestión de empresas</h1>
        <p class="view-subtitle">Cambia entre empresas, crea nuevas o gestiona las que administras</p>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">
        <Plus :size="16" />
        Crear empresa
      </button>
    </div>

    <!-- Active company highlight -->
    <div v-if="activeCompany" class="active-card">
      <div class="active-card-head">
        <span class="active-tag">Empresa activa</span>
        <span class="active-role" :class="roleBadgeClass(activeRole)">{{ roleLabel(activeRole) }}</span>
      </div>
      <div class="active-card-body">
        <div class="active-logo">
          <img v-if="activeCompany.logo" :src="activeCompany.logo" :alt="activeCompany.name" />
          <Building2 v-else :size="32" />
        </div>
        <div class="active-info">
          <h2 class="active-name">{{ activeCompany.name }}</h2>
          <div class="active-meta">
            <span v-if="activeCompany.tax_id">CIF: {{ activeCompany.tax_id }}</span>
            <span v-if="activeCompany.email">{{ activeCompany.email }}</span>
            <span v-if="activeCompany.currency">{{ activeCompany.currency }}</span>
          </div>
        </div>
        <div class="active-actions">
          <button
            v-if="canManage(activeRole)"
            class="btn btn-secondary btn-sm"
            @click="showInviteModal = true"
          >
            <UserPlus :size="14" />
            Invitar
          </button>
          <router-link
            v-if="canManage(activeRole)"
            to="/settings/company"
            class="btn btn-secondary btn-sm"
          >
            <Settings :size="14" />
            Editar
          </router-link>
          <button
            v-if="isOwner(activeRole) && companies.length > 1"
            class="btn btn-ghost btn-sm btn-danger"
            @click="openDeleteModal(activeCompany)"
          >
            <Trash2 :size="14" />
            Eliminar
          </button>
        </div>
      </div>
    </div>

    <!-- Other companies -->
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Otras empresas</h3>
        <p class="card-subtitle">{{ otherCompanies.length }} empresa{{ otherCompanies.length === 1 ? '' : 's' }} adicional{{ otherCompanies.length === 1 ? '' : 'es' }}</p>
      </div>

      <div v-if="otherCompanies.length" class="companies-list">
        <div v-for="company in otherCompanies" :key="company.id" class="company-row">
          <div class="company-info">
            <div class="company-logo-sm">
              <img v-if="company.logo" :src="company.logo" :alt="company.name" />
              <span v-else>{{ company.name?.charAt(0) }}</span>
            </div>
            <div>
              <p class="company-name">{{ company.name }}</p>
              <span class="role-pill" :class="roleBadgeClass(company.role)">{{ roleLabel(company.role) }}</span>
            </div>
          </div>
          <div class="company-actions">
            <button
              class="btn btn-secondary btn-sm"
              @click="handleSwitch(company.id)"
              :disabled="switching"
            >
              Cambiar
            </button>
            <button
              v-if="isOwner(company.role)"
              class="btn btn-ghost btn-sm btn-danger"
              @click="openDeleteModal(company)"
              :title="'Eliminar ' + company.name"
            >
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
      </div>

      <p v-else class="empty-text">No perteneces a ninguna otra empresa todavía.</p>
    </div>

    <!-- Create company modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Crear nueva empresa</h3>
            <button class="modal-close" @click="showCreateModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleCreate" class="modal-body">
            <div class="form-group">
              <label class="form-label">Nombre de la empresa <span class="required">*</span></label>
              <input v-model="createForm.name" class="input" required placeholder="Mi Empresa SL" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">CIF / NIF</label>
                <input v-model="createForm.tax_id" class="input" placeholder="B12345678" />
              </div>
              <div class="form-group">
                <label class="form-label">Moneda</label>
                <select v-model="createForm.currency" class="select">
                  <option value="EUR">EUR - Euro</option>
                  <option value="USD">USD - Dólar</option>
                  <option value="GBP">GBP - Libra</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Email de contacto</label>
              <input v-model="createForm.email" type="email" class="input" placeholder="info@empresa.com" />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showCreateModal = false">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? 'Creando...' : 'Crear empresa' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Invite user modal -->
    <Teleport to="body">
      <div v-if="showInviteModal" class="modal-overlay" @click.self="closeInviteModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Invitar a {{ activeCompany?.name }}</h3>
            <button class="modal-close" @click="closeInviteModal">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleInvite" class="modal-body">
            <p class="modal-hint">
              El usuario recibirá la invitación en su buzón y podrá aceptarla o rechazarla.
              Debe tener cuenta registrada con ese correo.
            </p>
            <div class="form-group">
              <label class="form-label">Email del invitado <span class="required">*</span></label>
              <input
                v-model="inviteForm.email"
                type="email"
                class="input"
                required
                placeholder="persona@empresa.com"
              />
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
              <button type="button" class="btn btn-ghost" @click="closeInviteModal">Cancelar</button>
              <button type="submit" class="btn btn-primary" :disabled="inviting">
                {{ inviting ? 'Enviando…' : 'Enviar invitación' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete company modal -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="closeDeleteModal">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Eliminar empresa</h3>
            <button class="modal-close" @click="closeDeleteModal">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="danger-banner">
              <AlertTriangle :size="20" />
              <div>
                <p class="banner-title">Esta acción es irreversible</p>
                <p class="banner-detail">
                  Se eliminarán todos los datos de <strong>{{ deleteTarget.name }}</strong>:
                  productos, clientes, facturas, etc.
                </p>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">
                Escribe <strong>{{ deleteTarget.name }}</strong> para confirmar
              </label>
              <input
                v-model="deleteConfirm"
                class="input"
                :placeholder="deleteTarget.name"
                autocomplete="off"
              />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="closeDeleteModal">Cancelar</button>
              <button
                type="button"
                class="btn btn-danger"
                :disabled="!canConfirmDelete || deleting"
                @click="handleDelete"
              >
                {{ deleting ? 'Eliminando...' : 'Eliminar definitivamente' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Settings, Trash2, X, Building2, AlertTriangle, UserPlus } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'
import inboxApi from '@/services/inbox'

const router = useRouter()
const { companies, activeCompany, activeRole, switchCompany, fetchMe } = useAuth()
const toast = useToast()

const otherCompanies = computed(() =>
  companies.value.filter(c => c.id !== activeCompany.value?.id),
)

function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Administrador', editor: 'Editor', viewer: 'Solo lectura' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = {
    owner: 'role-owner',
    admin: 'role-admin',
    editor: 'role-editor',
    viewer: 'role-viewer',
  }
  return map[role] || 'role-viewer'
}

function canManage(role) {
  return role === 'owner' || role === 'admin'
}

function isOwner(role) {
  return role === 'owner'
}

// Switch
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

// Create
const showCreateModal = ref(false)
const creating = ref(false)
const createForm = reactive({ name: '', tax_id: '', email: '', currency: 'EUR' })

async function handleCreate() {
  if (!createForm.name.trim()) return
  creating.value = true
  try {
    await authApi.createCompany({
      name: createForm.name.trim(),
      tax_id: createForm.tax_id.trim(),
      email: createForm.email.trim(),
      currency: createForm.currency,
    })
    toast.success('Empresa creada')
    showCreateModal.value = false
    createForm.name = ''
    createForm.tax_id = ''
    createForm.email = ''
    createForm.currency = 'EUR'
    await fetchMe()
  } catch (err) {
    toast.error(err.message || 'Error al crear la empresa')
  } finally {
    creating.value = false
  }
}

// Invite
const showInviteModal = ref(false)
const inviting = ref(false)
const inviteForm = reactive({ email: '', role: 'editor' })

function closeInviteModal() {
  showInviteModal.value = false
  inviteForm.email = ''
  inviteForm.role = 'editor'
}

async function handleInvite() {
  if (!inviteForm.email.trim()) return
  inviting.value = true
  try {
    await inboxApi.createInvitation({
      email: inviteForm.email.trim(),
      role: inviteForm.role,
    })
    toast.success('Invitación enviada')
    closeInviteModal()
  } catch (err) {
    toast.error(err.message || err.data?.detail || 'Error al enviar la invitación')
  } finally {
    inviting.value = false
  }
}

// Delete
const deleteTarget = ref(null)
const deleteConfirm = ref('')
const deleting = ref(false)

const canConfirmDelete = computed(
  () => deleteTarget.value && deleteConfirm.value.trim() === deleteTarget.value.name,
)

function openDeleteModal(company) {
  deleteTarget.value = company
  deleteConfirm.value = ''
}

function closeDeleteModal() {
  deleteTarget.value = null
  deleteConfirm.value = ''
}

async function handleDelete() {
  if (!canConfirmDelete.value) return
  deleting.value = true
  const wasActive = deleteTarget.value.id === activeCompany.value?.id
  try {
    await authApi.deleteCompany(deleteTarget.value.id)
    toast.success('Empresa eliminada')
    closeDeleteModal()
    await fetchMe()
    if (wasActive && companies.value.length === 0) {
      router.push('/onboarding')
    }
  } catch (err) {
    toast.error(err.message || 'Error al eliminar la empresa')
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.companies-view {
  max-width: 960px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.view-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: 0;
}

.view-header h1 { margin-bottom: 0.25rem; }

.view-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
  max-width: 520px;
}

/* Active company card */
.active-card {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.06), rgba(118, 75, 162, 0.04));
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.active-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.active-tag {
  font-size: var(--font-size-xs);
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--primary-color);
}

.active-card-body {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.active-logo {
  width: 64px;
  height: 64px;
  border-radius: var(--border-radius);
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  color: var(--text-tertiary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.active-logo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.active-info { flex: 1; min-width: 0; }

.active-name {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.375rem;
}

.active-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.active-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Role pills */
.active-role,
.role-pill {
  display: inline-block;
  padding: 0.2rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.role-owner {
  background: rgba(102, 126, 234, 0.14);
  color: var(--primary-color);
}

.role-admin {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.role-editor {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.role-viewer {
  background: var(--bg-hover);
  color: var(--text-secondary);
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

.company-row:last-child { border-bottom: none; }

.company-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.company-logo-sm {
  width: 40px;
  height: 40px;
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
  margin: 0;
}

/* Danger button */
.btn-danger {
  background: var(--error-color);
  color: white;
  border: none;
}

.btn-danger:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-ghost.btn-danger {
  background: transparent;
  color: var(--error-color);
}

.btn-ghost.btn-danger:hover {
  background: var(--error-light);
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

.modal-hint {
  margin: 0;
  padding: 0.75rem 0.875rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

.danger-banner {
  display: flex;
  gap: 0.75rem;
  background: var(--error-light, rgba(239, 68, 68, 0.08));
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: 0.875rem 1rem;
  border-radius: var(--border-radius);
  color: var(--error-color);
}

.banner-title {
  margin: 0 0 0.25rem;
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.banner-detail {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}

@media (max-width: 720px) {
  .view-header {
    flex-direction: column;
    align-items: stretch;
  }
  .active-card-body { flex-direction: column; align-items: flex-start; }
  .active-actions { width: 100%; }
  .form-row { grid-template-columns: 1fr; }
  .company-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  .company-actions { align-self: flex-end; }
}
</style>
