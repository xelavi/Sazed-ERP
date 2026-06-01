<template>
  <div class="inbox-view">
    <div class="inbox-header">
      <div>
        <h1>Buzón</h1>
        <p class="view-subtitle">
          Notificaciones, mensajes e invitaciones
          <span v-if="unreadTotal > 0" class="unread-pill">{{ unreadTotal }} sin leer</span>
        </p>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary btn-sm" @click="markAllRead" :disabled="!unreadTotal">
          <CheckCheck :size="14" />
          Marcar todo leído
        </button>
        <button class="btn btn-primary" @click="openCompose()">
          <PenSquare :size="16" />
          Nuevo mensaje
        </button>
      </div>
    </div>

    <div class="inbox-toolbar">
      <div class="search-box">
        <Search :size="16" class="search-icon" />
        <input
          v-model="query"
          class="search-input"
          type="text"
          placeholder="Buscar por asunto, remitente o contenido…"
        />
      </div>
      <div class="filter-chips">
        <button
          v-for="f in filters"
          :key="f.id"
          class="chip"
          :class="{ active: activeFilter === f.id }"
          @click="activeFilter = f.id"
        >
          <component :is="f.icon" :size="14" />
          {{ f.label }}
          <span v-if="f.count" class="chip-count">{{ f.count }}</span>
        </button>
      </div>
    </div>

    <div class="inbox-body">
      <!-- List pane -->
      <aside class="inbox-list">
        <div v-if="loading && !filteredItems.length" class="empty-state">Cargando…</div>
        <div v-else-if="!filteredItems.length" class="empty-state">
          <Inbox :size="32" />
          <p>No hay nada por aquí.</p>
        </div>
        <button
          v-for="item in filteredItems"
          :key="item.key"
          class="inbox-item"
          :class="{ unread: item.unread, selected: selected && selected.key === item.key }"
          @click="openItem(item)"
        >
          <div class="item-icon" :class="`icon-${item.type}`">
            <component :is="iconFor(item)" :size="16" />
          </div>
          <div class="item-main">
            <div class="item-top">
              <span class="item-from">{{ item.from }}</span>
              <span class="item-time">{{ relativeTime(item.created_at) }}</span>
            </div>
            <p class="item-subject">{{ item.subject }}</p>
            <p class="item-preview">{{ item.preview }}</p>
          </div>
          <span v-if="item.unread" class="unread-dot" aria-label="No leído"></span>
        </button>
      </aside>

      <!-- Detail pane -->
      <section class="inbox-detail">
        <div v-if="!selected" class="detail-empty">
          <Mail :size="36" />
          <p>Selecciona un elemento para verlo aquí.</p>
        </div>

        <article v-else class="detail-card">
          <header class="detail-head">
            <div class="detail-head-top">
              <span class="badge-type" :class="`type-${selected.type}`">
                {{ typeLabel(selected.type) }}
              </span>
              <span class="detail-time">{{ formatDate(selected.created_at) }}</span>
            </div>
            <h2 class="detail-subject">{{ selected.subject }}</h2>
            <p class="detail-from">{{ selected.fromFull }}</p>
          </header>

          <div class="detail-body">
            <p v-for="(line, i) in (selected.body || '').split('\n')" :key="i">{{ line || ' ' }}</p>
          </div>

          <!-- Invitation actions -->
          <div v-if="selected.type === 'invitation' && selected.raw.status === 'pending'" class="detail-actions">
            <button class="btn btn-secondary" @click="rejectInvitation(selected)" :disabled="responding">
              <X :size="16" />
              Rechazar
            </button>
            <button class="btn btn-primary" @click="acceptInvitation(selected)" :disabled="responding">
              <Check :size="16" />
              Aceptar y unirme
            </button>
          </div>
          <div v-else-if="selected.type === 'invitation'" class="invitation-resolved">
            <span :class="['status-pill', `status-${selected.raw.status}`]">
              {{ statusLabel(selected.raw.status) }}
            </span>
          </div>

          <!-- Message reply -->
          <div v-if="selected.type === 'message'" class="detail-actions">
            <button class="btn btn-primary" @click="openCompose(selected)">
              <Reply :size="16" />
              Responder
            </button>
          </div>
        </article>
      </section>
    </div>

    <ComposeMessageModal
      v-if="showCompose"
      :reply-to="replyTo"
      @close="closeCompose"
      @sent="onMessageSent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Search, PenSquare, Inbox, Mail, CheckCheck, Reply,
  Bell, MessageSquare, Building2, Check, X,
} from 'lucide-vue-next'
import inboxApi from '@/services/inbox'
import { useAuth } from '@/composables/useAuth'
import { useInbox } from '@/composables/useInbox'
import { useToast } from '@/composables/useToast'
import ComposeMessageModal from '@/components/ComposeMessageModal.vue'

const { user } = useAuth()
const { refresh: refreshSummary } = useInbox()
const toast = useToast()

const notifications = ref([])
const messages = ref([])
const invitations = ref([])
const loading = ref(true)

const query = ref('')
const activeFilter = ref('all')
const selected = ref(null)
const responding = ref(false)

const showCompose = ref(false)
const replyTo = ref(null)

const unreadTotal = computed(() =>
  items.value.filter(i => i.unread).length,
)

const items = computed(() => {
  const list = []

  for (const n of notifications.value) {
    list.push({
      key: `n-${n.id}`,
      id: n.id,
      type: 'notification',
      subject: n.title,
      body: n.body,
      preview: previewOf(n.body),
      from: 'Sistema',
      fromFull: 'Notificación del sistema',
      unread: !n.read,
      created_at: n.created_at,
      raw: n,
    })
  }

  for (const m of messages.value) {
    const sender = m.sender || {}
    list.push({
      key: `m-${m.id}`,
      id: m.id,
      type: 'message',
      subject: m.subject,
      body: m.body,
      preview: previewOf(m.body),
      from: sender.full_name || sender.email || 'Desconocido',
      fromFull: `${sender.full_name || ''} <${sender.email || ''}>`,
      unread: !m.read,
      created_at: m.created_at,
      raw: m,
    })
  }

  for (const inv of invitations.value) {
    list.push({
      key: `i-${inv.id}`,
      id: inv.id,
      type: 'invitation',
      subject: `Invitación a unirse a ${inv.company_name}`,
      body: `${inv.inviter?.full_name || inv.inviter?.email || 'Un administrador'} te ha invitado a unirte a ${inv.company_name} como ${inv.role_label || roleLabel(inv.role)}.`,
      preview: `Rol propuesto: ${inv.role_label || roleLabel(inv.role)}`,
      from: inv.company_name,
      fromFull: `De ${inv.inviter?.full_name || inv.inviter?.email || 'administrador'}`,
      unread: inv.status === 'pending',
      created_at: inv.created_at,
      raw: inv,
    })
  }

  list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  return list
})

const filters = computed(() => [
  { id: 'all',          label: 'Todo',          icon: Inbox,         count: items.value.filter(i => i.unread).length },
  { id: 'unread',       label: 'Sin leer',      icon: Mail,          count: items.value.filter(i => i.unread).length },
  { id: 'message',      label: 'Mensajes',      icon: MessageSquare, count: messages.value.filter(m => !m.read).length },
  { id: 'notification', label: 'Sistema',       icon: Bell,          count: notifications.value.filter(n => !n.read).length },
  { id: 'invitation',   label: 'Invitaciones',  icon: Building2,     count: invitations.value.filter(i => i.status === 'pending').length },
])

const filteredItems = computed(() => {
  let list = items.value
  if (activeFilter.value === 'unread') {
    list = list.filter(i => i.unread)
  } else if (activeFilter.value !== 'all') {
    list = list.filter(i => i.type === activeFilter.value)
  }
  const q = query.value.trim().toLowerCase()
  if (q) {
    list = list.filter(i =>
      (i.subject || '').toLowerCase().includes(q)
      || (i.body || '').toLowerCase().includes(q)
      || (i.from || '').toLowerCase().includes(q),
    )
  }
  return list
})

function previewOf(text) {
  if (!text) return ''
  const flat = text.replace(/\s+/g, ' ').trim()
  return flat.length > 110 ? flat.slice(0, 110) + '…' : flat
}

function iconFor(item) {
  if (item.type === 'notification') return Bell
  if (item.type === 'invitation') return Building2
  return MessageSquare
}

function typeLabel(t) {
  return t === 'notification' ? 'Sistema'
    : t === 'invitation' ? 'Invitación'
    : 'Mensaje'
}

function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Administrador', editor: 'Editor', viewer: 'Solo lectura' }
  return map[role] || role
}

function statusLabel(status) {
  return status === 'accepted' ? 'Aceptada'
    : status === 'rejected' ? 'Rechazada'
    : 'Pendiente'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('es-ES', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function relativeTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const diff = (Date.now() - date.getTime()) / 1000
  if (diff < 60) return 'ahora'
  if (diff < 3600) return `${Math.floor(diff / 60)} min`
  if (diff < 86400) return `${Math.floor(diff / 3600)} h`
  if (diff < 604800) return `${Math.floor(diff / 86400)} d`
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}

async function openItem(item) {
  selected.value = item
  if (item.unread) {
    try {
      if (item.type === 'message') {
        await inboxApi.markMessageRead(item.id)
        const target = messages.value.find(m => m.id === item.id)
        if (target) target.read = true
      } else if (item.type === 'notification') {
        await inboxApi.markNotificationRead(item.id)
        const target = notifications.value.find(n => n.id === item.id)
        if (target) target.read = true
      }
      refreshSummary()
    } catch { /* silent */ }
  }
}

function openCompose(item = null) {
  if (item && item.type === 'message') {
    replyTo.value = {
      id: item.raw.id,
      recipient_id: item.raw.sender.id,
      recipient_name: item.raw.sender.full_name || item.raw.sender.email,
      subject: item.raw.subject,
    }
  } else {
    replyTo.value = null
  }
  showCompose.value = true
}

function closeCompose() {
  showCompose.value = false
  replyTo.value = null
}

async function onMessageSent() {
  closeCompose()
  await loadAll()
}

async function acceptInvitation(item) {
  responding.value = true
  try {
    const updated = await inboxApi.acceptInvitation(item.id)
    const idx = invitations.value.findIndex(i => i.id === item.id)
    if (idx >= 0) invitations.value[idx] = updated
    if (selected.value?.key === item.key) {
      selected.value = { ...selected.value, unread: false, raw: updated }
    }
    toast.success('Invitación aceptada')
    refreshSummary()
  } catch (err) {
    toast.error(err.message || 'Error al aceptar la invitación')
  } finally {
    responding.value = false
  }
}

async function rejectInvitation(item) {
  responding.value = true
  try {
    const updated = await inboxApi.rejectInvitation(item.id)
    const idx = invitations.value.findIndex(i => i.id === item.id)
    if (idx >= 0) invitations.value[idx] = updated
    if (selected.value?.key === item.key) {
      selected.value = { ...selected.value, unread: false, raw: updated }
    }
    toast.success('Invitación rechazada')
    refreshSummary()
  } catch (err) {
    toast.error(err.message || 'Error al rechazar la invitación')
  } finally {
    responding.value = false
  }
}

async function markAllRead() {
  try {
    await Promise.all([
      inboxApi.markAllMessagesRead(),
      inboxApi.markAllNotificationsRead(),
    ])
    notifications.value = notifications.value.map(n => ({ ...n, read: true }))
    messages.value = messages.value.map(m => ({ ...m, read: true }))
    refreshSummary()
    toast.success('Todo marcado como leído')
  } catch {
    toast.error('Error al actualizar')
  }
}

async function loadAll() {
  loading.value = true
  try {
    const [notifs, msgs, invs] = await Promise.all([
      inboxApi.listNotifications(),
      inboxApi.listMessages(),
      inboxApi.listInvitations(),
    ])
    notifications.value = notifs || []
    // Only show received messages (where current user is the recipient)
    messages.value = (msgs || []).filter(
      m => m.recipient && user.value && m.recipient.id === user.value.id,
    )
    invitations.value = (invs || []).filter(
      i => i.invitee && user.value && i.invitee.id === user.value.id,
    )
    refreshSummary()
  } catch {
    toast.error('No se pudo cargar el buzón')
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.inbox-view {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  height: 100%;
}

.inbox-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.inbox-header h1 { margin-bottom: 0.25rem; }

.view-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unread-pill {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  background: var(--primary-color);
  color: white;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Toolbar */
.inbox-toolbar {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 240px;
  max-width: 480px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.625rem 0.75rem 0.625rem 2.25rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
  background: white;
  transition: border-color var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.filter-chips {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 9999px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  font-family: var(--font-family);
  transition: all var(--transition-fast);
}

.chip:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.chip.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.chip-count {
  background: rgba(255, 255, 255, 0.25);
  padding: 0 0.375rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.chip:not(.active) .chip-count {
  background: var(--primary-light);
  color: var(--primary-color);
}

/* Body grid */
.inbox-body {
  display: grid;
  grid-template-columns: minmax(280px, 380px) 1fr;
  gap: var(--spacing-lg);
  flex: 1;
  min-height: 480px;
}

.inbox-list {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  background: white;
  overflow-y: auto;
  max-height: 70vh;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: var(--spacing-xl);
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

/* List item */
.inbox-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
  padding: 0.875rem 1rem;
  background: none;
  border: none;
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  text-align: left;
  font-family: var(--font-family);
  transition: background var(--transition-fast);
  position: relative;
}

.inbox-item:last-child { border-bottom: none; }

.inbox-item:hover {
  background: var(--bg-hover);
}

.inbox-item.selected {
  background: var(--primary-light);
}

.inbox-item.unread {
  background: linear-gradient(
    to right,
    rgba(102, 126, 234, 0.07),
    rgba(102, 126, 234, 0.02) 60%,
    transparent
  );
  box-shadow: inset 3px 0 0 var(--primary-color);
}

.inbox-item.unread.selected {
  background: var(--primary-light);
}

.item-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.item-icon.icon-message {
  background: rgba(102, 126, 234, 0.12);
  color: var(--primary-color);
}

.item-icon.icon-notification {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.item-icon.icon-invitation {
  background: rgba(16, 185, 129, 0.14);
  color: #047857;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.125rem;
}

.item-from {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inbox-item.unread .item-from { color: var(--primary-color); }

.item-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.item-subject {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin: 0 0 0.125rem;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inbox-item.unread .item-subject { font-weight: 700; }

.item-preview {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  flex-shrink: 0;
  margin-top: 0.375rem;
}

/* Detail */
.inbox-detail {
  display: flex;
  flex-direction: column;
}

.detail-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
  background: white;
  border: 1px dashed var(--border-color);
  border-radius: var(--border-radius-lg);
}

.detail-card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.detail-head-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.badge-type {
  display: inline-block;
  padding: 0.2rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.badge-type.type-message { background: rgba(102, 126, 234, 0.14); color: var(--primary-color); }
.badge-type.type-notification { background: rgba(245, 158, 11, 0.14); color: #b45309; }
.badge-type.type-invitation { background: rgba(16, 185, 129, 0.14); color: #047857; }

.detail-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.detail-subject {
  margin: 0 0 0.25rem;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.detail-from {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.detail-body {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-body p { margin: 0 0 0.5rem; }

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-md);
}

.invitation-resolved {
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-md);
}

.status-pill {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.status-accepted { background: rgba(16, 185, 129, 0.14); color: #047857; }
.status-rejected { background: rgba(239, 68, 68, 0.12); color: var(--error-color); }
.status-pending  { background: var(--bg-hover); color: var(--text-secondary); }

@media (max-width: 900px) {
  .inbox-body {
    grid-template-columns: 1fr;
  }
  .inbox-list { max-height: none; }
  .inbox-detail {
    display: none;
  }
  .inbox-detail.show-on-mobile {
    display: block;
  }
}
</style>
