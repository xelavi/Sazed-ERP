<template>
  <div class="alerts-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Alertas</h1>
          <span class="count-badge pending-count">{{ pending.length }} pendientes</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="markAllReviewed">Marcar todas revisadas</button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <select class="select" v-model="severityFilter">
          <option value="all">Todas las gravedades</option>
          <option value="high">Alta</option>
          <option value="medium">Media</option>
          <option value="low">Baja</option>
        </select>
        <select class="select" v-model="statusFilter">
          <option value="all">Todos los estados</option>
          <option value="pending">Pendiente</option>
          <option value="reviewed">Revisada</option>
          <option value="assigned">Asignada</option>
        </select>
        <select class="select" v-model="typeFilter">
          <option value="all">Todos los tipos</option>
          <option v-for="(type, key) in ALERT_TYPES" :key="key" :value="key">{{ type.label }}</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Tipo</th>
                <th>Entidad afectada</th>
                <th>Descripción</th>
                <th>Gravedad</th>
                <th>Estado</th>
                <th>Responsable</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="alert in filtered" :key="alert.id"
                :class="['alert-row', `severity-${alert.severity}`, { reviewed: alert.status !== 'pending' }]">
                <td class="text-sm">{{ formatDate(alert.date) }}</td>
                <td><span class="type-badge">{{ ALERT_TYPES[alert.type]?.label || alert.type }}</span></td>
                <td class="text-sm font-medium">{{ alert.entity }}</td>
                <td class="desc-cell">{{ alert.description }}</td>
                <td>
                  <span :class="['sev-badge', `sev-${alert.severity}`]">
                    {{ { high: 'Alta', medium: 'Media', low: 'Baja' }[alert.severity] }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', statusBadge(alert.status)]">
                    {{ { pending: 'Pendiente', reviewed: 'Revisada', assigned: 'Asignada' }[alert.status] }}
                  </span>
                </td>
                <td class="text-sm">{{ alert.responsible || '—' }}</td>
                <td>
                  <div class="row-actions">
                    <button
                      v-if="alert.status === 'pending'"
                      class="icon-btn" title="Marcar revisada"
                      @click="markReviewed(alert.id)">
                      <Check :size="15" />
                    </button>
                    <button class="icon-btn" title="Asignar responsable" @click="assignAlert(alert)">
                      <UserPlus :size="15" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Assign modal -->
    <div v-if="assignTarget" class="modal-overlay" @click.self="assignTarget = null">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Asignar responsable</h2>
          <button class="icon-btn" @click="assignTarget = null"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="field"><label class="field-label">Alerta</label><p class="assign-desc">{{ assignTarget.description }}</p></div>
          <div class="field"><label class="field-label">Responsable *</label>
            <select class="select full" v-model="assignee">
              <option value="">Seleccionar persona</option>
              <option v-for="m in teamMembers" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="assignTarget = null">Cancelar</button>
          <button class="btn btn-primary" @click="confirmAssign">Asignar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Check, UserPlus, X } from 'lucide-vue-next'
import { socialAlerts, ALERT_TYPES, formatDate } from '@/services/socialCrmData'

const alerts        = ref(socialAlerts.map(a => ({ ...a })))
const severityFilter = ref('all')
const statusFilter  = ref('all')
const typeFilter    = ref('all')
const assignTarget  = ref(null)
const assignee      = ref('')

const teamMembers = ['María García', 'Laura Martínez', 'Carlos Ruiz', 'Ana López', 'David Sánchez']

const filtered = computed(() => {
  let list = [...alerts.value]
  if (severityFilter.value !== 'all') list = list.filter(a => a.severity === severityFilter.value)
  if (statusFilter.value  !== 'all') list = list.filter(a => a.status  === statusFilter.value)
  if (typeFilter.value    !== 'all') list = list.filter(a => a.type    === typeFilter.value)
  return list.sort((a, b) => {
    const sev = { high: 3, medium: 2, low: 1 }
    return sev[b.severity] - sev[a.severity] || new Date(b.date) - new Date(a.date)
  })
})

const pending = computed(() => alerts.value.filter(a => a.status === 'pending'))

function markReviewed(id) {
  const a = alerts.value.find(a => a.id === id)
  if (a) a.status = 'reviewed'
}
function markAllReviewed() {
  alerts.value.forEach(a => { if (a.status === 'pending') a.status = 'reviewed' })
}
function assignAlert(alert) { assignTarget.value = alert; assignee.value = '' }
function confirmAssign() {
  if (!assignee.value) return
  const a = alerts.value.find(x => x.id === assignTarget.value.id)
  if (a) { a.responsible = assignee.value; a.status = 'assigned' }
  assignTarget.value = null
}
function statusBadge(s) {
  return { pending: 'badge-warning', reviewed: 'badge-active', assigned: 'badge-info' }[s] || 'badge-inactive'
}
</script>

<style scoped>
.alerts-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.pending-count { background: #fef2f2; color: #DC2626; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.filters-bar { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.alert-row { transition: background 0.12s; }
.alert-row.severity-high   td:first-child { border-left: 3px solid #EF4444; }
.alert-row.severity-medium td:first-child { border-left: 3px solid #F59E0B; }
.alert-row.severity-low    td:first-child { border-left: 3px solid #3B82F6; }
.alert-row.reviewed { opacity: 0.65; }
.type-badge { font-size: 0.78rem; font-weight: 500; color: var(--text-secondary); }
.desc-cell { font-size: 0.85rem; color: var(--text-primary); max-width: 260px; }
.sev-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 700; }
.sev-high   { background: #fef2f2; color: #DC2626; }
.sev-medium { background: #fffbeb; color: #D97706; }
.sev-low    { background: #eff6ff; color: #2563EB; }
.font-medium { font-weight: 600; }
.text-sm { font-size: 0.85rem; }
.row-actions { display: flex; gap: 4px; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: none; background: none; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: background 0.15s; }
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: var(--spacing-md); }
.modal { background: var(--bg-primary); border-radius: var(--border-radius); width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.modal-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.modal-body { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-md); }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--spacing-sm); padding: var(--spacing-lg); border-top: 1px solid var(--border-color); }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.assign-desc { font-size: 0.875rem; color: var(--text-secondary); background: var(--bg-secondary); padding: var(--spacing-sm); border-radius: var(--border-radius-sm); margin: 0; }
.select.full { width: 100%; box-sizing: border-box; }
</style>
