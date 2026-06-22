<template>
  <div class="companies-view">
    <div class="view-header">
      <div>
        <h1>Gestió d'empreses</h1>
        <p class="view-subtitle">Canvia entre empreses, crea'n de noves o gestiona les que administres</p>
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
            Convidar
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
            v-if="canManage(activeRole)"
            class="btn btn-secondary btn-sm"
            @click="handleOpenOdoo(activeCompany.id)"
            :disabled="openingOdoo"
            title="Obre el mòdul de comptabilitat a Odoo"
          >
            <BookOpen :size="14" />
            Comptabilitat
          </button>
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
        <h3 class="card-title">Altres empreses</h3>
        <p class="card-subtitle">{{ otherCompanies.length }} {{ otherCompanies.length === 1 ? 'empresa addicional' : 'empreses addicionals' }}</p>
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
              Canviar
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

      <p v-else class="empty-text">Encara no pertanys a cap altra empresa.</p>
    </div>

    <!-- Create company modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Crear una empresa nova</h3>
            <button class="modal-close" @click="showCreateModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleCreate" class="modal-body">
            <div class="form-group">
              <label class="form-label">Nom de l'empresa <span class="required">*</span></label>
              <input v-model="createForm.name" class="input" required placeholder="La meva empresa SL" />
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
                  <option value="USD">USD - Dòlar</option>
                  <option value="GBP">GBP - Lliura</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Correu de contacte</label>
              <input v-model="createForm.email" type="email" class="input" placeholder="info@empresa.com" />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showCreateModal = false">Cancel·lar</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? 'Creant…' : 'Crear empresa' }}
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
            <h3>Convidar a {{ activeCompany?.name }}</h3>
            <button class="modal-close" @click="closeInviteModal">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleInvite" class="modal-body">
            <p class="modal-hint">
              L'usuari rebrà la invitació a la seva bústia i la podrà acceptar o rebutjar.
              Ha de tenir un compte registrat amb aquest correu.
            </p>
            <div class="form-group">
              <label class="form-label">Correu de la persona convidada <span class="required">*</span></label>
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
                <option value="viewer">Només lectura</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="closeInviteModal">Cancel·lar</button>
              <button type="submit" class="btn btn-primary" :disabled="inviting">
                {{ inviting ? 'Enviant…' : 'Enviar invitació' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Provisioning progress modal -->
    <Teleport to="body">
      <div v-if="provisioningJob" class="modal-overlay">
        <div class="modal-card provisioning-card">
          <div class="modal-header">
            <h3>Configurant la comptabilitat a Odoo</h3>
          </div>
          <div class="modal-body">
            <div v-if="provisioningJob.status === 'pending' || provisioningJob.status === 'running'" class="prov-state prov-running">
              <Loader2 :size="32" class="prov-spin" />
              <p class="prov-title">
                {{ provisioningJob.status === 'pending' ? 'A la cua…' : 'Creant la base de dades i els mòduls comptables…' }}
              </p>
              <p class="prov-subtitle">
                Això pot trigar 1–3 minuts. Pots tancar aquesta finestra i tornar més tard;
                el procés continua en segon pla.
              </p>
            </div>
            <div v-else-if="provisioningJob.status === 'done'" class="prov-state prov-done">
              <CheckCircle2 :size="32" />
              <p class="prov-title">Comptabilitat a punt!</p>
              <p class="prov-subtitle">
                Base de dades Odoo <code>{{ provisioningJob.database_name }}</code> creada
                i connectada amb l'empresa.
              </p>
            </div>
            <div v-else class="prov-state prov-failed">
              <AlertTriangle :size="32" />
              <p class="prov-title">No s'ha pogut configurar Odoo</p>
              <p class="prov-error">{{ provisioningJob.error_message }}</p>
              <p class="prov-subtitle">
                Pots tornar-ho a provar més tard des de Configuració → Integracions.
                Mentrestant, l'empresa funciona sense comptabilitat.
              </p>
            </div>

            <details v-if="provisioningJob.logs" class="prov-logs">
              <summary>Veure detalls tècnics</summary>
              <pre>{{ provisioningJob.logs }}</pre>
            </details>

            <div class="modal-actions">
              <button
                v-if="provisioningJob.status === 'done'"
                class="btn btn-primary"
                @click="handleOpenOdoo(provisioningJob.company); provisioningJob = null"
              >
                <BookOpen :size="14" /> Obrir la comptabilitat
              </button>
              <button class="btn btn-ghost" @click="provisioningJob = null">
                Tancar
              </button>
            </div>
          </div>
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
                <p class="banner-title">Aquesta acció és irreversible</p>
                <p class="banner-detail">
                  S'eliminaran totes les dades de <strong>{{ deleteTarget.name }}</strong>:
                  productes, clients, factures, etc.
                </p>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">
                Escriu <strong>{{ deleteTarget.name }}</strong> per confirmar
              </label>
              <input
                v-model="deleteConfirm"
                class="input"
                :placeholder="deleteTarget.name"
                autocomplete="off"
              />
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="closeDeleteModal">Cancel·lar</button>
              <button
                type="button"
                class="btn btn-danger"
                :disabled="!canConfirmDelete || deleting"
                @click="handleDelete"
              >
                {{ deleting ? 'Eliminant…' : 'Eliminar definitivament' }}
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
import { Plus, Settings, Trash2, X, Building2, AlertTriangle, UserPlus, BookOpen, Loader2, CheckCircle2 } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'
import inboxApi from '@/services/inbox'
import odooApi from '@/services/odoo'

const router = useRouter()
const { companies, activeCompany, activeRole, switchCompany, fetchMe } = useAuth()
const toast = useToast()

const otherCompanies = computed(() =>
  companies.value.filter(c => c.id !== activeCompany.value?.id),
)

function roleLabel(role) {
  const map = { owner: 'Propietari', admin: 'Administrador', editor: 'Editor', viewer: 'Només lectura' }
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
    toast.success('Empresa canviada')
  } catch {
    toast.error('Error en canviar d\'empresa')
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
    const newCompany = await authApi.createCompany({
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
    // Arrancar el seguimiento del provisioning Odoo (no bloquea la UI).
    if (newCompany?.id) trackProvisioning(newCompany.id)
  } catch (err) {
    toast.error(err.message || 'Error en crear l\'empresa')
  } finally {
    creating.value = false
  }
}

// Odoo provisioning (creación automática de BD tras crear Company)
const provisioningJob = ref(null)

async function trackProvisioning(companyId) {
  try {
    // Primer poll inmediato para mostrar el modal cuanto antes.
    provisioningJob.value = await odooApi.getProvisioningStatus(companyId)
    const finalJob = await odooApi.waitForProvisioning(companyId, {
      intervalMs: 4000,
      timeoutMs: 5 * 60 * 1000,
      onProgress: (job) => { provisioningJob.value = job },
    })
    provisioningJob.value = finalJob
    if (finalJob.status === 'done') {
      toast.success('Comptabilitat d\'Odoo configurada')
    } else {
      toast.error('La configuració d\'Odoo ha fallat. Revisa els detalls.')
    }
  } catch (err) {
    toast.error(err.message || 'No s\'ha pogut seguir el progrés d\'Odoo')
  }
}

// Botón "Abrir contabilidad" → SSO + nueva pestaña
const openingOdoo = ref(false)
async function handleOpenOdoo(companyId) {
  openingOdoo.value = true
  try {
    await odooApi.openOdooForCompany(companyId)
  } catch (err) {
    toast.error(err.message || 'No s\'ha pogut obrir Odoo')
  } finally {
    openingOdoo.value = false
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
    toast.success('Invitació enviada')
    closeInviteModal()
  } catch (err) {
    toast.error(err.message || err.data?.detail || 'Error en enviar la invitació')
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
    toast.error(err.message || 'Error en eliminar l\'empresa')
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

/* Provisioning modal */
.provisioning-card {
  max-width: 520px;
}

.prov-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.5rem;
  padding: 0.5rem 0 1rem;
}

.prov-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0.25rem 0 0;
}

.prov-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
  max-width: 380px;
  line-height: 1.5;
}

.prov-error {
  font-size: var(--font-size-sm);
  color: var(--error-color);
  background: var(--error-light, rgba(239, 68, 68, 0.08));
  padding: 0.625rem 0.875rem;
  border-radius: var(--border-radius);
  margin: 0.5rem 0;
  max-width: 100%;
  word-break: break-word;
  text-align: left;
}

.prov-running { color: var(--primary-color); }
.prov-done { color: #047857; }
.prov-failed { color: var(--error-color); }

.prov-spin {
  animation: prov-spin 1s linear infinite;
}

@keyframes prov-spin {
  to { transform: rotate(360deg); }
}

.prov-logs {
  margin-top: 1rem;
  font-size: var(--font-size-xs);
}

.prov-logs summary {
  cursor: pointer;
  color: var(--text-tertiary);
  user-select: none;
}

.prov-logs pre {
  margin-top: 0.5rem;
  background: var(--bg-secondary);
  padding: 0.75rem;
  border-radius: var(--border-radius-sm);
  max-height: 200px;
  overflow: auto;
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
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
