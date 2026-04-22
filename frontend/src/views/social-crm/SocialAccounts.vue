<template>
  <div class="social-accounts-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Cuentas sociales</h1>
          <span class="count-badge">{{ accounts.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="sync">
            <RefreshCw :size="18" />
            <span>Sincronizar</span>
          </button>
          <button class="btn btn-primary" @click="openForm()">
            <Plus :size="18" />
            <span>Añadir cuenta</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Red social</th>
                <th>Cuenta</th>
                <th>Usuario</th>
                <th>Estado</th>
                <th>Última sync.</th>
                <th class="text-right">Seguidores</th>
                <th class="text-right">Publicaciones</th>
                <th>Responsable</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="acc in accounts" :key="acc.id">
                <td>
                  <span class="platform-pill" :style="platformStyle(acc.platform)">
                    {{ getPlatform(acc.platform).label }}
                  </span>
                </td>
                <td class="font-medium">{{ acc.name }}</td>
                <td class="text-secondary">{{ acc.username }}</td>
                <td>
                  <span class="badge" :class="acc.status === 'connected' ? 'badge-active' : 'badge-error'">
                    {{ acc.status === 'connected' ? 'Conectada' : 'Desconectada' }}
                  </span>
                </td>
                <td class="text-secondary text-sm">{{ formatDate(acc.lastSync) }}</td>
                <td class="text-right font-medium">{{ formatNumber(acc.followers) }}</td>
                <td class="text-right">{{ acc.posts }}</td>
                <td class="text-secondary text-sm">{{ acc.responsible }}</td>
                <td>
                  <div class="row-actions">
                    <button class="icon-btn" @click="openForm(acc)" title="Editar">
                      <Pencil :size="15" />
                    </button>
                    <button class="icon-btn danger" @click="removeAccount(acc)" title="Eliminar">
                      <Trash2 :size="15" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">{{ editing ? 'Editar cuenta' : 'Nueva cuenta social' }}</h2>
          <button class="icon-btn" @click="closeForm"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Red social *</label>
              <select class="select full" v-model="form.platform">
                <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Nombre interno *</label>
              <input class="input full" v-model="form.name" placeholder="Ej: Marca Principal" />
            </div>
            <div class="field">
              <label class="field-label">Usuario / Handle *</label>
              <input class="input full" v-model="form.username" placeholder="@usuario" />
            </div>
            <div class="field">
              <label class="field-label">Token / API Key</label>
              <input class="input full" v-model="form.token" type="password" placeholder="••••••••" />
            </div>
            <div class="field">
              <label class="field-label">Responsable</label>
              <input class="input full" v-model="form.responsible" placeholder="Nombre del responsable" />
            </div>
            <div class="field full-width">
              <label class="field-label">Observaciones</label>
              <textarea class="input full textarea" v-model="form.observations" rows="3" placeholder="Notas internas..."></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeForm">Cancelar</button>
          <button class="btn btn-primary" @click="saveForm">{{ editing ? 'Guardar cambios' : 'Añadir cuenta' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Plus, RefreshCw, Pencil, Trash2, X } from 'lucide-vue-next'
import { socialAccounts, PLATFORMS, getPlatform, formatNumber, formatDate } from '@/services/socialCrmData'

const accounts = ref([...socialAccounts])
const showForm = ref(false)
const editing  = ref(null)
const form     = reactive({ platform: 'instagram', name: '', username: '', token: '', responsible: '', observations: '' })

function platformStyle(key) {
  const p = getPlatform(key)
  return { background: p.bg, color: p.color }
}

function openForm(acc = null) {
  if (acc) {
    editing.value = acc.id
    Object.assign(form, { platform: acc.platform, name: acc.name, username: acc.username, token: '', responsible: acc.responsible, observations: acc.observations })
  } else {
    editing.value = null
    Object.assign(form, { platform: 'instagram', name: '', username: '', token: '', responsible: '', observations: '' })
  }
  showForm.value = true
}

function closeForm() { showForm.value = false }

function saveForm() {
  if (!form.name || !form.username) return
  if (editing.value) {
    const idx = accounts.value.findIndex(a => a.id === editing.value)
    if (idx >= 0) Object.assign(accounts.value[idx], { platform: form.platform, name: form.name, username: form.username, responsible: form.responsible, observations: form.observations })
  } else {
    accounts.value.push({ id: Date.now(), platform: form.platform, name: form.name, username: form.username, status: 'connected', lastSync: new Date().toISOString(), followers: 0, posts: 0, responsible: form.responsible, observations: form.observations })
  }
  closeForm()
}

function removeAccount(acc) {
  if (confirm(`¿Eliminar la cuenta "${acc.name}"?`)) {
    accounts.value = accounts.value.filter(a => a.id !== acc.id)
  }
}

function sync() { alert('Sincronización iniciada (simulado)') }
</script>

<style scoped>
.social-accounts-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.platform-pill { font-size: 0.78rem; font-weight: 600; padding: 3px 10px; border-radius: 12px; white-space: nowrap; }
.font-medium { font-weight: 500; color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-sm { font-size: 0.85rem; }
.text-right { text-align: right; }
.row-actions { display: flex; gap: 4px; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: none; background: none; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: background 0.15s, color 0.15s; }
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.icon-btn.danger:hover { background: #fee2e2; color: #EF4444; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: var(--spacing-md); }
.modal { background: var(--bg-primary); border-radius: var(--border-radius); width: 100%; max-width: 560px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; max-height: 90vh; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.modal-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.modal-body { flex: 1; overflow-y: auto; padding: var(--spacing-lg); }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--spacing-sm); padding: var(--spacing-lg); border-top: 1px solid var(--border-color); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full-width { grid-column: 1 / 3; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.input.full, .select.full { width: 100%; box-sizing: border-box; }
.textarea { resize: vertical; font-family: inherit; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
</style>
