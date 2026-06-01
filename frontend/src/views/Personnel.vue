<template>
  <div class="personnel-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Personal</h1>
          <span class="count-badge">{{ filteredMembers.length }}</span>
        </div>
        <div class="header-actions">
          <button v-if="canManage" class="btn btn-secondary" @click="openRolesModal">
            <Shield :size="18" />
            <span>Gestionar roles</span>
          </button>
          <button v-if="canManage" class="btn btn-primary" @click="showInviteModal = true">
            <UserPlus :size="18" />
            <span>Invitar empleado</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="18" class="search-icon" />
          <input
            type="text"
            class="input search-input"
            placeholder="Buscar por nombre, email..."
            v-model="searchQuery"
          />
        </div>
        <div class="filter-actions">
          <select class="select filter-select" v-model="roleFilter">
            <option value="all">Todos los roles</option>
            <option v-for="opt in roleFilterOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table personnel-table">
            <thead>
              <tr>
                <th class="col-avatar"></th>
                <th class="col-name">Nombre</th>
                <th class="col-email">Email</th>
                <th class="col-role">Rol</th>
                <th class="col-joined">En la empresa desde</th>
                <th v-if="canManage" class="col-actions"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="m in filteredMembers"
                :key="m.id"
                class="table-row"
                @click="openDetail(m)"
              >
                <td class="col-avatar">
                  <div class="member-avatar" :style="{ background: avatarColor(m) }">
                    <img v-if="m.user?.avatar" :src="m.user.avatar" :alt="m.user.full_name" />
                    <span v-else>{{ m.user?.initials || '?' }}</span>
                  </div>
                </td>
                <td class="col-name">
                  <span class="member-name">{{ m.user?.full_name || '—' }}</span>
                </td>
                <td class="col-email">
                  <span class="email-text">{{ m.user?.email }}</span>
                </td>
                <td class="col-role">
                  <span :class="['badge', roleBadgeClass(m)]">{{ roleLabel(m) }}</span>
                </td>
                <td class="col-joined">
                  <span class="joined-text">{{ formatDate(m.joined_at) }}</span>
                </td>
                <td v-if="canManage" class="col-actions" @click.stop>
                  <button class="btn-icon" title="Editar" @click="openDetail(m)">
                    <Pencil :size="16" />
                  </button>
                  <button
                    v-if="!m.is_owner && m.user?.id !== currentUser?.id"
                    class="btn-icon"
                    title="Eliminar"
                    @click="confirmDelete(m)"
                    style="color: var(--error-color);"
                  >
                    <Trash2 :size="16" />
                  </button>
                </td>
              </tr>
              <tr v-if="!loading && !filteredMembers.length">
                <td :colspan="canManage ? 6 : 5" class="empty-row">
                  No hay empleados que coincidan con la búsqueda.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="table-footer">
          <span class="table-footer-info">
            Mostrando <strong>{{ filteredMembers.length }}</strong> de
            <strong>{{ members.length }}</strong> empleados
          </span>
        </div>
      </div>
    </div>

    <PersonnelDetailDrawer
      v-if="selectedMember"
      :open="detailOpen"
      :member="selectedMember"
      :can-manage="canManage"
      :current-user-id="currentUser?.id"
      :custom-roles="customRoles"
      @close="closeDetail"
      @save="handleSave"
      @delete="confirmDelete"
    />

    <Teleport to="body">
      <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Invitar empleado</h3>
            <button class="modal-close" @click="showInviteModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleInvite" class="modal-body">
            <div class="form-group">
              <label class="form-label">Email del usuario <span class="required">*</span></label>
              <input
                v-model="inviteForm.email"
                type="email"
                class="input"
                required
                placeholder="usuario@email.com"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Rol</label>
              <select v-model="inviteForm.roleToken" class="select">
                <optgroup label="Roles base">
                  <option value="builtin:admin">Administrador</option>
                  <option value="builtin:editor">Editor</option>
                  <option value="builtin:viewer">Solo lectura</option>
                </optgroup>
                <optgroup v-if="customRoles.length" label="Roles personalizados">
                  <option
                    v-for="r in customRoles"
                    :key="r.id"
                    :value="`custom:${r.id}`"
                  >{{ r.name }}</option>
                </optgroup>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-secondary" @click="showInviteModal = false">
                Cancelar
              </button>
              <button type="submit" class="btn btn-primary" :disabled="inviting">
                {{ inviting ? 'Invitando...' : 'Enviar invitación' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Roles management modal -->
    <Teleport to="body">
      <div v-if="showRolesModal" class="modal-overlay" @click.self="showRolesModal = false">
        <div class="modal-card roles-card">
          <div class="modal-header">
            <h3>Gestionar roles</h3>
            <button class="modal-close" @click="showRolesModal = false">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body roles-body">
            <!-- Existing roles -->
            <div class="roles-list">
              <p class="roles-section-label">Roles personalizados</p>
              <p v-if="!customRoles.length" class="roles-empty">
                Aún no has creado ningún rol. Crea uno para definir a qué módulos accede cada empleado.
              </p>
              <div
                v-for="r in customRoles"
                :key="r.id"
                :class="['role-chip', { active: editingRoleId === r.id }]"
              >
                <div class="role-chip-info" @click="editRole(r)">
                  <span class="role-chip-name">{{ r.name }}</span>
                  <span class="role-chip-meta">{{ r.members_count }} empleado(s)</span>
                </div>
                <div class="role-chip-actions">
                  <button class="btn-icon" title="Editar" @click="editRole(r)">
                    <Pencil :size="14" />
                  </button>
                  <button
                    class="btn-icon"
                    title="Eliminar"
                    style="color: var(--error-color);"
                    @click="deleteRole(r)"
                  >
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
            </div>

            <!-- Role editor -->
            <div class="role-editor">
              <p class="roles-section-label">
                {{ editingRoleId ? 'Editar rol' : 'Nuevo rol' }}
                <button
                  v-if="editingRoleId"
                  class="link-btn"
                  type="button"
                  @click="resetRoleForm"
                >
                  <Plus :size="14" /> Crear otro
                </button>
              </p>
              <div class="form-group">
                <label class="form-label">Nombre del rol <span class="required">*</span></label>
                <input
                  v-model="roleForm.name"
                  type="text"
                  class="input"
                  placeholder="Ej. Comercial, Almacén, Contabilidad…"
                />
              </div>

              <div class="form-group">
                <label class="form-label">Permisos por módulo</label>
                <div class="perm-grid">
                  <div v-for="mod in modules" :key="mod.key" class="perm-row">
                    <span class="perm-module">{{ mod.label }}</span>
                    <div class="perm-options">
                      <label
                        v-for="opt in PERMISSION_OPTIONS"
                        :key="opt.value"
                        :class="['perm-opt', { selected: roleForm.permissions[mod.key] === opt.value }]"
                      >
                        <input
                          type="radio"
                          :name="`perm-${mod.key}`"
                          :value="opt.value"
                          v-model="roleForm.permissions[mod.key]"
                        />
                        {{ opt.label }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              <div class="modal-actions">
                <button type="button" class="btn btn-secondary" @click="showRolesModal = false">
                  Cerrar
                </button>
                <button type="button" class="btn btn-primary" :disabled="savingRole" @click="saveRole">
                  {{ savingRole ? 'Guardando...' : (editingRoleId ? 'Guardar cambios' : 'Crear rol') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import {
  Search, UserPlus, Pencil, Trash2, X, Shield, Plus,
} from 'lucide-vue-next'
import PersonnelDetailDrawer from '@/components/PersonnelDetailDrawer.vue'
import authApi from '@/services/auth'
import inboxApi from '@/services/inbox'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const { activeCompany, activeRole, user: currentUser } = useAuth()
const toast = useToast()

const members = ref([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('all')

// Custom roles + the module catalog (loaded from the backend).
const customRoles = ref([])
const modules = ref([])

const BUILTIN_ROLES = [
  { value: 'owner', label: 'Propietario' },
  { value: 'admin', label: 'Administrador' },
  { value: 'editor', label: 'Editor' },
  { value: 'viewer', label: 'Solo lectura' },
]

const PERMISSION_OPTIONS = [
  { value: 'none', label: 'Sin acceso' },
  { value: 'view', label: 'Ver' },
  { value: 'edit', label: 'Editar' },
]

const canManage = computed(() => ['owner', 'admin'].includes(activeRole.value))

async function fetchMembers() {
  if (!activeCompany.value) return
  loading.value = true
  try {
    const data = await authApi.getMembers(activeCompany.value.id)
    const list = Array.isArray(data) ? data : data.results || []
    members.value = list.map(m => ({
      ...m,
      is_owner: m.role === 'owner',
    }))
  } catch {
    toast.error('Error al cargar el personal')
  } finally {
    loading.value = false
  }
}

async function fetchRoles() {
  if (!activeCompany.value) return
  try {
    const data = await authApi.getRoles(activeCompany.value.id)
    customRoles.value = data.roles || []
    modules.value = data.modules || []
  } catch {
    /* non-critical — the roles UI just stays empty */
  }
}

onMounted(() => {
  fetchMembers()
  fetchRoles()
})

const filteredMembers = computed(() => {
  let result = members.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(m =>
      (m.user?.full_name || '').toLowerCase().includes(q) ||
      (m.user?.email || '').toLowerCase().includes(q)
    )
  }
  if (roleFilter.value !== 'all') {
    result = result.filter(m => memberMatchesFilter(m, roleFilter.value))
  }
  return result
})

/* ── Detail drawer ── */
const detailOpen = ref(false)
const selectedMember = ref(null)

function openDetail(member) {
  selectedMember.value = member
  detailOpen.value = true
}

function closeDetail() {
  detailOpen.value = false
}

async function handleSave(payload) {
  if (!canManage.value || !selectedMember.value) return
  try {
    const updated = await authApi.updateMember(
      activeCompany.value.id,
      selectedMember.value.id,
      payload,
    )
    const idx = members.value.findIndex(m => m.id === selectedMember.value.id)
    if (idx !== -1) {
      members.value[idx] = { ...updated, is_owner: updated.role === 'owner' }
      selectedMember.value = members.value[idx]
    }
    toast.success('Empleado actualizado')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al actualizar')
  }
}

async function confirmDelete(member) {
  if (!canManage.value) return
  if (member.is_owner) {
    toast.error('No puedes eliminar al propietario')
    return
  }
  if (member.user?.id === currentUser.value?.id) {
    toast.error('No puedes eliminarte a ti mismo')
    return
  }
  const name = member.user?.full_name || member.user?.email
  if (!confirm(`¿Eliminar a ${name} de la empresa?`)) return
  try {
    await authApi.removeMember(activeCompany.value.id, member.id)
    members.value = members.value.filter(m => m.id !== member.id)
    if (selectedMember.value?.id === member.id) closeDetail()
    toast.success('Empleado eliminado')
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al eliminar')
  }
}

/* ── Invite ── */
const showInviteModal = ref(false)
const inviting = ref(false)
const inviteForm = reactive({ email: '', roleToken: 'builtin:editor' })

async function handleInvite() {
  if (!inviteForm.email.trim()) return
  inviting.value = true
  const [kind, value] = inviteForm.roleToken.split(':')
  const payload = { email: inviteForm.email.trim() }
  if (kind === 'custom') {
    payload.custom_role = Number(value)
  } else {
    payload.role = value
  }
  try {
    // Sends an invitation to the user's inbox; they choose to accept or reject.
    // The invitation is scoped to the active company via the X-Company header.
    await inboxApi.createInvitation(payload)
    toast.success('Invitación enviada. El usuario la verá en su buzón.')
    showInviteModal.value = false
    inviteForm.email = ''
    inviteForm.roleToken = 'builtin:editor'
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al invitar')
  } finally {
    inviting.value = false
  }
}

/* ── Roles management ── */
const showRolesModal = ref(false)
const savingRole = ref(false)
const editingRoleId = ref(null)  // null = creating a new role
const roleForm = reactive({ name: '', permissions: {} })

function blankPermissions() {
  const perms = {}
  modules.value.forEach(m => { perms[m.key] = 'none' })
  return perms
}

function openRolesModal() {
  showRolesModal.value = true
  resetRoleForm()
}

function resetRoleForm() {
  editingRoleId.value = null
  roleForm.name = ''
  roleForm.permissions = blankPermissions()
}

function editRole(role) {
  editingRoleId.value = role.id
  roleForm.name = role.name
  roleForm.permissions = { ...blankPermissions(), ...(role.permissions || {}) }
}

async function saveRole() {
  if (!roleForm.name.trim()) {
    toast.error('El rol necesita un nombre')
    return
  }
  savingRole.value = true
  const payload = { name: roleForm.name.trim(), permissions: { ...roleForm.permissions } }
  try {
    if (editingRoleId.value) {
      await authApi.updateRole(activeCompany.value.id, editingRoleId.value, payload)
      toast.success('Rol actualizado')
    } else {
      await authApi.createRole(activeCompany.value.id, payload)
      toast.success('Rol creado')
    }
    await fetchRoles()
    await fetchMembers()
    resetRoleForm()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al guardar el rol')
  } finally {
    savingRole.value = false
  }
}

async function deleteRole(role) {
  if (!confirm(`¿Eliminar el rol "${role.name}"? Los empleados con este rol pasarán a su rol base.`)) return
  try {
    await authApi.deleteRole(activeCompany.value.id, role.id)
    toast.success('Rol eliminado')
    if (editingRoleId.value === role.id) resetRoleForm()
    await fetchRoles()
    await fetchMembers()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al eliminar el rol')
  }
}

/* ── Helpers ── */
const roleFilterOptions = computed(() => [
  ...BUILTIN_ROLES,
  ...customRoles.value.map(r => ({ value: `custom:${r.id}`, label: r.name })),
])

function memberMatchesFilter(m, filter) {
  if (filter === 'all') return true
  if (filter.startsWith('custom:')) {
    return String(m.custom_role) === filter.slice(7)
  }
  // Builtin filter: match the base role, but exclude members that carry a
  // custom role (those are listed under their custom-role filter instead).
  return m.role === filter && !m.custom_role
}

function roleLabel(member) {
  // Prefer the label computed by the backend (handles custom roles).
  if (member?.role_label) return member.role_label
  const map = { owner: 'Propietario', admin: 'Administrador', editor: 'Editor', viewer: 'Solo lectura' }
  return map[member?.role] || member?.role
}

function roleBadgeClass(member) {
  if (member?.custom_role && !['owner', 'admin'].includes(member.role)) {
    return 'badge-primary'
  }
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[member?.role] || 'badge-gray'
}

const avatarColors = ['#667eea', '#f97316', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4', '#f59e0b']
function avatarColor(member) {
  const id = member.user?.id ?? member.id ?? 0
  return avatarColors[id % avatarColors.length]
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}
</script>

<style scoped>
.personnel-view {
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.count-badge {
  background: linear-gradient(135deg, #f0f2f5 0%, #e8eaed 100%);
  color: var(--text-secondary);
  padding: 0.375rem 0.875rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Filters */
.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 360px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
}

.search-input {
  padding-left: 3rem;
}

.filter-actions {
  display: flex;
  gap: 0.625rem;
  align-items: center;
}

.filter-select {
  width: auto;
  min-width: 160px;
  padding: 0.5rem 0.75rem;
  font-size: var(--font-size-xs);
}

/* Table */
.table-card {
  padding: 0;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.personnel-table {
  min-width: 720px;
}

.personnel-table th {
  font-size: 0.6875rem;
  padding: 0.625rem 0.75rem;
  white-space: nowrap;
  user-select: none;
}

.personnel-table td {
  padding: 0.625rem 0.75rem;
  vertical-align: middle;
  white-space: nowrap;
}

.col-avatar { width: 48px; }
.col-name { min-width: 200px; white-space: normal !important; }
.col-email { min-width: 220px; }
.col-role { width: 140px; }
.col-joined { width: 160px; }
.col-actions { width: 80px; text-align: right; }

.table-row {
  transition: background var(--transition-fast);
  cursor: pointer;
}

.table-row:hover {
  background: var(--bg-hover);
}

.member-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-xs);
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
  overflow: hidden;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-name {
  font-weight: 500;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  display: block;
  line-height: 1.3;
}

.email-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.joined-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.375rem;
  color: var(--text-tertiary);
  border-radius: 6px;
  transition: all var(--transition-base);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #f0f2f5;
  color: var(--text-primary);
}

.empty-row {
  text-align: center;
  padding: 2rem !important;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

.table-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--border-color);
}

.table-footer-info {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* Invite modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.modal-card {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 700;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 0.25rem;
  border-radius: 6px;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: 1.25rem 1.5rem 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

/* Roles modal */
.roles-card {
  max-width: 720px;
}

.roles-body {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 1.5rem;
  max-height: 70vh;
  overflow-y: auto;
}

.roles-section-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
  margin: 0 0 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.roles-empty {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  line-height: 1.5;
}

.role-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all var(--transition-fast);
}

.role-chip.active {
  border-color: var(--primary-color, #667eea);
  background: var(--bg-hover);
}

.role-chip-info {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  min-width: 0;
}

.role-chip-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.role-chip-meta {
  font-size: 0.6875rem;
  color: var(--text-tertiary);
}

.role-chip-actions {
  display: flex;
  gap: 0.125rem;
  flex-shrink: 0;
}

.role-editor {
  border-left: 1px solid var(--border-color);
  padding-left: 1.5rem;
}

.link-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--primary-color, #667eea);
  font-size: var(--font-size-xs);
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  text-transform: none;
  letter-spacing: 0;
}

.perm-grid {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.perm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.375rem 0;
}

.perm-module {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.perm-options {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.perm-opt {
  font-size: 0.6875rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  user-select: none;
  transition: all var(--transition-fast);
}

.perm-opt.selected {
  background: var(--primary-color, #667eea);
  border-color: var(--primary-color, #667eea);
  color: white;
}

.perm-opt input {
  display: none;
}

@media (max-width: 768px) {
  .roles-body {
    grid-template-columns: 1fr;
  }
  .role-editor {
    border-left: none;
    border-top: 1px solid var(--border-color);
    padding-left: 0;
    padding-top: 1.25rem;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    gap: 1rem;
  }
  .view-title {
    font-size: 1.5rem;
  }
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .search-box {
    max-width: 100%;
  }
}
</style>
