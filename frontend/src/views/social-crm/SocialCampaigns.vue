<template>
  <div class="social-campaigns-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Campañas</h1>
          <span class="count-badge">{{ filtered.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openForm">
            <Plus :size="18" /><span>Nueva campaña</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <select class="select" v-model="statusFilter">
          <option value="all">Todos los estados</option>
          <option v-for="(s, k) in CAMPAIGN_STATUSES" :key="k" :value="k">{{ s.label }}</option>
        </select>
        <select class="select" v-model="objectiveFilter">
          <option value="all">Todos los objetivos</option>
          <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Objetivo</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Estado</th>
                <th class="text-right">Presupuesto</th>
                <th class="text-right">Posts</th>
                <th class="text-right">Influencers</th>
                <th class="text-right">Clics</th>
                <th class="text-right">Conversiones</th>
                <th class="text-right">Ventas</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="c in filtered" :key="c.id"
                class="clickable-row"
                @click="$router.push('/social-crm/campaigns/' + c.id)">
                <td class="font-medium">{{ c.name }}</td>
                <td><span class="badge badge-info">{{ c.objective }}</span></td>
                <td class="text-sm text-secondary">{{ formatDate(c.startDate) }}</td>
                <td class="text-sm text-secondary">{{ formatDate(c.endDate) }}</td>
                <td><span class="badge" :class="CAMPAIGN_STATUSES[c.status].cls">{{ CAMPAIGN_STATUSES[c.status].label }}</span></td>
                <td class="text-right">{{ formatCurrency(c.budget) }}</td>
                <td class="text-right">{{ c.posts }}</td>
                <td class="text-right">{{ c.influencers }}</td>
                <td class="text-right">{{ formatNumber(c.clicks) }}</td>
                <td class="text-right">{{ formatNumber(c.conversions) }}</td>
                <td class="text-right font-medium">{{ formatCurrency(c.sales) }}</td>
                <td @click.stop>
                  <div class="row-actions">
                    <button class="icon-btn" @click="$router.push('/social-crm/campaigns/' + c.id)" title="Ver detalle"><Eye :size="15" /></button>
                    <button class="icon-btn" title="Editar"><Pencil :size="15" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create campaign modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Nueva campaña</h2>
          <button class="icon-btn" @click="showForm = false"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field full-width">
              <label class="field-label">Nombre *</label>
              <input class="input full" v-model="form.name" placeholder="Nombre de la campaña" />
            </div>
            <div class="field">
              <label class="field-label">Objetivo *</label>
              <select class="select full" v-model="form.objective">
                <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Presupuesto (€)</label>
              <input class="input full" type="number" v-model.number="form.budget" placeholder="0.00" />
            </div>
            <div class="field">
              <label class="field-label">Fecha inicio</label>
              <input class="input full" type="date" v-model="form.startDate" />
            </div>
            <div class="field">
              <label class="field-label">Fecha fin</label>
              <input class="input full" type="date" v-model="form.endDate" />
            </div>
            <div class="field">
              <label class="field-label">Responsable</label>
              <input class="input full" v-model="form.responsible" placeholder="Nombre" />
            </div>
            <div class="field full-width">
              <label class="field-label">Descripción</label>
              <textarea class="input full textarea" v-model="form.description" rows="3"></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showForm = false">Cancelar</button>
          <button class="btn btn-primary" @click="saveCampaign">Crear campaña</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus, Eye, Pencil, X } from 'lucide-vue-next'
import { socialCampaigns, CAMPAIGN_STATUSES, CAMPAIGN_OBJECTIVES, formatNumber, formatCurrency, formatDate } from '@/services/socialCrmData'

const campaigns     = ref([...socialCampaigns])
const statusFilter  = ref('all')
const objectiveFilter = ref('all')
const showForm      = ref(false)
const form = reactive({ name: '', objective: 'Awareness', budget: 0, startDate: '', endDate: '', responsible: '', description: '' })

const filtered = computed(() => {
  let list = [...campaigns.value]
  if (statusFilter.value !== 'all')    list = list.filter(c => c.status === statusFilter.value)
  if (objectiveFilter.value !== 'all') list = list.filter(c => c.objective === objectiveFilter.value)
  return list.sort((a, b) => new Date(b.startDate) - new Date(a.startDate))
})

function openForm() { Object.assign(form, { name: '', objective: 'Awareness', budget: 0, startDate: '', endDate: '', responsible: '', description: '' }); showForm.value = true }

function saveCampaign() {
  if (!form.name) return
  campaigns.value.push({ id: Date.now(), ...form, status: 'draft', posts: 0, influencers: 0, clicks: 0, conversions: 0, sales: 0, reach: 0, impressions: 0, engagement: 0, cost: 0, roas: 0, timeline: [] })
  showForm.value = false
}
</script>

<style scoped>
.social-campaigns-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.filters-bar { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.clickable-row { cursor: pointer; transition: background 0.12s; }
.clickable-row:hover { background: var(--bg-secondary); }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-sm { font-size: 0.85rem; }
.text-right { text-align: right; }
.row-actions { display: flex; gap: 4px; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: none; background: none; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: background 0.15s; }
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
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
</style>
