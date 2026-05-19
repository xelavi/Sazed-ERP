<template>
  <div class="personnel-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Personal</h1>
          <span class="count-badge">{{ filteredMembers.length }}</span>
        </div>
        <div class="header-actions">
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
            <option value="owner">Propietario</option>
            <option value="admin">Administrador</option>
            <option value="editor">Editor</option>
            <option value="viewer">Solo lectura</option>
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
                  <span :class="['badge', roleBadgeClass(m.role)]">{{ roleLabel(m.role) }}</span>
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
              <select v-model="inviteForm.role" class="select">
                <option value="admin">Administrador</option>
                <option value="editor">Editor</option>
                <option value="viewer">Solo lectura</option>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import {
  Search, UserPlus, Pencil, Trash2, X,
} from 'lucide-vue-next'
import PersonnelDetailDrawer from '@/components/PersonnelDetailDrawer.vue'
import authApi from '@/services/auth'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const { activeCompany, activeRole, user: currentUser } = useAuth()
const toast = useToast()

const members = ref([])
const loading = ref(false)
const searchQuery = ref('')
const roleFilter = ref('all')

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

onMounted(fetchMembers)

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
    result = result.filter(m => m.role === roleFilter.value)
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
const inviteForm = reactive({ email: '', role: 'editor' })

async function handleInvite() {
  if (!inviteForm.email.trim()) return
  inviting.value = true
  try {
    await authApi.inviteMember(
      activeCompany.value.id,
      inviteForm.email.trim(),
      inviteForm.role,
    )
    toast.success('Invitación enviada')
    showInviteModal.value = false
    inviteForm.email = ''
    inviteForm.role = 'editor'
    await fetchMembers()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error al invitar')
  } finally {
    inviting.value = false
  }
}

/* ── Helpers ── */
function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Administrador', editor: 'Editor', viewer: 'Solo lectura' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[role] || 'badge-gray'
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
