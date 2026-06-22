<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="open" class="drawer-overlay" @click.self="$emit('close')">
        <div class="drawer-panel">
          <!-- Header -->
          <div class="drawer-header">
            <div class="drawer-header-left">
              <div class="drawer-avatar" :style="{ background: avatarColor }">
                <img v-if="member.user?.avatar" :src="member.user.avatar" :alt="member.user.full_name" />
                <span v-else>{{ member.user?.initials || '?' }}</span>
              </div>
              <div>
                <h2 class="drawer-title">{{ member.user?.full_name || member.user?.email }}</h2>
                <div class="drawer-meta">
                  <span :class="['badge', currentRoleBadgeClass()]">
                    {{ currentRoleLabel() }}
                  </span>
                  <span v-if="isSelf" class="self-tag">Tu</span>
                </div>
              </div>
            </div>
            <div class="drawer-header-right">
              <button
                v-if="canManage && !isEditing"
                class="btn btn-secondary btn-sm"
                @click="startEdit"
              >
                <Pencil :size="14" />
                <span>Editar</span>
              </button>
              <button class="btn btn-secondary btn-sm" @click="$emit('close')">
                <X :size="16" />
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="drawer-body">

            <!-- ────── READ-ONLY VIEW ────── -->
            <div v-if="!isEditing">
              <section class="detail-section">
                <h4 class="section-title">
                  <User :size="16" />
                  Informació personal
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Nom</span>
                  <span class="detail-value">{{ member.user?.first_name || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Cognoms</span>
                  <span class="detail-value">{{ member.user?.last_name || '—' }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Correu electrònic</span>
                  <span class="detail-value">{{ member.user?.email }}</span>
                </div>
              </section>

              <section class="detail-section">
                <h4 class="section-title">
                  <Shield :size="16" />
                  Accés i rol
                </h4>
                <div class="detail-row">
                  <span class="detail-label">Rol a l'empresa</span>
                  <span :class="['badge', currentRoleBadgeClass()]">
                    {{ currentRoleLabel() }}
                  </span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">A l'empresa des de</span>
                  <span class="detail-value">{{ formatDate(member.joined_at) }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Empresa</span>
                  <span class="detail-value">{{ member.company_name }}</span>
                </div>
              </section>

              <section v-if="!canManage" class="readonly-hint">
                <Lock :size="14" />
                <span>Només els administradors poden editar les dades del personal.</span>
              </section>
            </div>

            <!-- ────── EDIT VIEW (admins only) ────── -->
            <form v-else class="edit-form" @submit.prevent="save">
              <section class="detail-section">
                <h4 class="section-title">
                  <User :size="16" />
                  Informació personal
                </h4>
                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Nom</label>
                    <input class="input" type="text" v-model="form.first_name" />
                  </div>
                  <div class="field">
                    <label class="field-label">Cognoms</label>
                    <input class="input" type="text" v-model="form.last_name" />
                  </div>
                </div>
                <div class="field">
                  <label class="field-label">Correu electrònic</label>
                  <input class="input" type="email" :value="member.user?.email" disabled />
                  <span class="field-hint">El correu electrònic no es pot modificar.</span>
                </div>
              </section>

              <section class="detail-section">
                <h4 class="section-title">
                  <Shield :size="16" />
                  Rol a l'empresa
                </h4>
                <div class="field">
                  <label class="field-label">Rol</label>
                  <select
                    class="select"
                    v-model="form.roleToken"
                    :disabled="isOwner || isSelf"
                  >
                    <option v-if="isOwner" value="builtin:owner">Propietari</option>
                    <optgroup label="Rols base">
                      <option
                        v-for="opt in builtinRoleOptions"
                        :key="opt.value"
                        :value="opt.value"
                      >{{ opt.label }}</option>
                    </optgroup>
                    <optgroup v-if="customRoles.length" label="Rols personalitzats">
                      <option
                        v-for="r in customRoles"
                        :key="r.id"
                        :value="`custom:${r.id}`"
                      >{{ r.name }}</option>
                    </optgroup>
                  </select>
                  <span v-if="isOwner" class="field-hint">
                    El rol del propietari no es pot canviar.
                  </span>
                  <span v-else-if="isSelf" class="field-hint">
                    No pots canviar el teu propi rol.
                  </span>
                  <span v-else class="field-hint">
                    Els rols personalitzats defineixen a quins mòduls accedeix l'empleat.
                  </span>
                </div>
              </section>

              <div class="edit-actions">
                <button type="button" class="btn btn-secondary" @click="cancelEdit">
                  Cancel·lar
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <Check :size="16" />
                  {{ saving ? 'Desant…' : 'Desar canvis' }}
                </button>
              </div>
            </form>

          </div>

          <!-- Footer -->
          <div v-if="canManage && !isEditing" class="drawer-footer">
            <button
              v-if="!isSelf && member.role !== 'owner'"
              class="btn btn-secondary danger-btn"
              @click="$emit('delete', member)"
            >
              <Trash2 :size="16" />
              Eliminar empleat
            </button>
            <button class="btn btn-primary" @click="startEdit">
              <Pencil :size="16" />
              Editar
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { X, User, Pencil, Shield, Lock, Check, Trash2 } from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  member: { type: Object, required: true },
  canManage: { type: Boolean, default: false },
  currentUserId: { type: [Number, String], default: null },
  customRoles: { type: Array, default: () => [] },
})

const emit = defineEmits(['close', 'save', 'delete'])

const isEditing = ref(false)
const saving = ref(false)

// Role is selected as a token: 'builtin:<role>' or 'custom:<id>'.
const form = reactive({
  first_name: '',
  last_name: '',
  roleToken: 'builtin:viewer',
})

const isSelf = computed(() =>
  props.currentUserId != null && props.member.user?.id === props.currentUserId
)

const isOwner = computed(() => props.member.role === 'owner')

function tokenForMember(m) {
  if (m?.custom_role && !['owner', 'admin'].includes(m.role)) {
    return `custom:${m.custom_role}`
  }
  return `builtin:${m?.role || 'viewer'}`
}

const builtinRoleOptions = [
  { value: 'builtin:admin', label: 'Administrador' },
  { value: 'builtin:editor', label: 'Editor' },
  { value: 'builtin:viewer', label: 'Només lectura' },
]

const avatarColors = ['#667eea', '#f97316', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4', '#f59e0b']
const avatarColor = computed(() => {
  const id = props.member.user?.id ?? props.member.id ?? 0
  return avatarColors[id % avatarColors.length]
})

watch(
  () => props.member,
  (m) => {
    if (!m) return
    form.first_name = m.user?.first_name || ''
    form.last_name = m.user?.last_name || ''
    form.roleToken = tokenForMember(m)
    isEditing.value = false
  },
  { immediate: true, deep: true },
)

watch(() => props.open, (val) => {
  if (!val) isEditing.value = false
})

function startEdit() {
  if (!props.canManage) return
  form.first_name = props.member.user?.first_name || ''
  form.last_name = props.member.user?.last_name || ''
  form.roleToken = tokenForMember(props.member)
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
}

function save() {
  if (!props.canManage) return
  saving.value = true
  const payload = {
    first_name: form.first_name,
    last_name: form.last_name,
  }
  // Role changes are only sent for non-owners, not for yourself, and only
  // when the selection actually changed.
  if (!isOwner.value && !isSelf.value && form.roleToken !== tokenForMember(props.member)) {
    const [kind, value] = form.roleToken.split(':')
    if (kind === 'custom') {
      payload.custom_role = Number(value)
    } else {
      payload.role = value
      payload.custom_role = null
    }
  }
  emit('save', payload)
  // Parent updates the member prop on success → watcher resets isEditing.
  // Release the loading flag after a short tick so the button doesn't appear stuck.
  setTimeout(() => {
    saving.value = false
    isEditing.value = false
  }, 300)
}

/* ── Helpers ── */
function currentRoleLabel() {
  if (props.member?.role_label) return props.member.role_label
  const map = { owner: 'Propietari', admin: 'Administrador', editor: 'Editor', viewer: 'Només lectura' }
  return map[props.member?.role] || props.member?.role
}

function currentRoleBadgeClass() {
  if (props.member?.custom_role && !['owner', 'admin'].includes(props.member.role)) {
    return 'badge-primary'
  }
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[props.member?.role] || 'badge-gray'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ca-ES', {
    day: 'numeric', month: 'long', year: 'numeric',
  })
}
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: flex-end;
}

.drawer-panel {
  width: 560px;
  max-width: 92vw;
  background: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: -8px 0 24px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.drawer-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.drawer-header-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  min-width: 0;
}

.drawer-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: var(--font-size-sm);
  font-weight: 700;
  flex-shrink: 0;
  letter-spacing: 0.02em;
  overflow: hidden;
}

.drawer-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.drawer-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.drawer-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.375rem;
}

.self-tag {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
  padding: 0.125rem 0.5rem;
  border-radius: 6px;
}

.drawer-header-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.drawer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  gap: 0.625rem;
  flex-wrap: wrap;
}

.danger-btn {
  color: var(--error-color);
}

.danger-btn:hover {
  background: #fef2f2;
}

.detail-section {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #f0f2f5;
}

.detail-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.detail-label {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.detail-value {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.readonly-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  padding: 0.75rem 1rem;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: 1rem;
}

/* Edit form */
.edit-form .field {
  margin-bottom: 0.875rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 0.875rem;
}

.field-row .field {
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

.field-hint {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 0.375rem;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.5rem;
}

/* Transition */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-active .drawer-panel,
.drawer-leave-active .drawer-panel {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-enter-from { opacity: 0; }
.drawer-enter-from .drawer-panel { transform: translateX(100%); }
.drawer-leave-to { opacity: 0; }
.drawer-leave-to .drawer-panel { transform: translateX(100%); }

@media (max-width: 768px) {
  .drawer-panel {
    width: 100vw;
    max-width: 100vw;
  }
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
