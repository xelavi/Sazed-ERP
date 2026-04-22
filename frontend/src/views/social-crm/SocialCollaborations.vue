<template>
  <div class="collaborations-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Colaboraciones</h1>
          <span class="count-badge">{{ filtered.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="openMetrics"><Upload :size="18" /><span>Cargar métricas</span></button>
          <button class="btn btn-primary" @click="openForm"><Plus :size="18" /><span>Nueva colaboración</span></button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <select class="select" v-model="statusFilter">
          <option value="all">Todos los estados</option>
          <option v-for="(s, k) in COLLAB_STATUSES" :key="k" :value="k">{{ s.label }}</option>
        </select>
        <select class="select" v-model="campaignFilter">
          <option value="all">Todas las campañas</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select class="select" v-model="influencerFilter">
          <option value="all">Todos los influencers</option>
          <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Influencer</th>
                <th>Campaña</th>
                <th>Formato</th>
                <th>Publicación</th>
                <th class="text-right">Coste</th>
                <th>Código</th>
                <th>Estado</th>
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
                @click="$router.push('/social-crm/collaborations/' + c.id)">
                <td>
                  <div class="inf-cell">
                    <div class="small-avatar">{{ c.influencerName[0] }}</div>
                    <div>
                      <div class="inf-name">{{ c.influencerName }}</div>
                      <div class="inf-alias">{{ c.influencerAlias }}</div>
                    </div>
                  </div>
                </td>
                <td class="text-sm text-secondary">{{ c.campaignName }}</td>
                <td class="text-sm">{{ c.format }}</td>
                <td class="text-sm text-secondary">{{ formatDate(c.publishDate) }}</td>
                <td class="text-right">{{ formatCurrency(c.cost) }}</td>
                <td><code class="code-badge">{{ c.code }}</code></td>
                <td><span class="badge" :class="COLLAB_STATUSES[c.status].cls">{{ COLLAB_STATUSES[c.status].label }}</span></td>
                <td class="text-right">{{ formatNumber(c.clicks) }}</td>
                <td class="text-right">{{ c.conversions }}</td>
                <td class="text-right font-medium">{{ formatCurrency(c.sales) }}</td>
                <td @click.stop>
                  <div class="row-actions">
                    <button class="icon-btn" @click="$router.push('/social-crm/collaborations/' + c.id)" title="Ver detalle"><Eye :size="15" /></button>
                    <button class="icon-btn" title="Adjuntar evidencia"><Paperclip :size="15" /></button>
                    <button class="icon-btn" v-if="c.status === 'active'" title="Cerrar colaboración" @click.stop="closeCollab(c)"><CheckCircle :size="15" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New collaboration modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Nueva colaboración</h2>
          <button class="icon-btn" @click="showForm = false"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field">
              <label class="field-label">Influencer *</label>
              <select class="select full" v-model.number="form.influencerId">
                <option :value="null">Seleccionar...</option>
                <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.name }} ({{ i.alias }})</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Campaña *</label>
              <select class="select full" v-model.number="form.campaignId">
                <option :value="null">Seleccionar...</option>
                <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Formato pactado</label>
              <input class="input full" v-model="form.format" placeholder="Ej: Reel + 3 Stories" />
            </div>
            <div class="field">
              <label class="field-label">Coste (€)</label>
              <input class="input full" type="number" v-model.number="form.cost" />
            </div>
            <div class="field">
              <label class="field-label">Fecha publicación</label>
              <input class="input full" type="date" v-model="form.publishDate" />
            </div>
            <div class="field">
              <label class="field-label">Código descuento</label>
              <input class="input full" v-model="form.code" placeholder="CODIGO20" />
            </div>
            <div class="field full-width">
              <label class="field-label">Entregables</label>
              <textarea class="input full textarea" v-model="form.deliverables" rows="3" placeholder="Describa los entregables acordados..."></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showForm = false">Cancelar</button>
          <button class="btn btn-primary" @click="saveCollab">Crear colaboración</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Upload, Eye, Paperclip, CheckCircle, X } from 'lucide-vue-next'
import { socialCollaborations, socialCampaigns, socialInfluencers, COLLAB_STATUSES, formatNumber, formatCurrency, formatDate } from '@/services/socialCrmData'

const router   = useRouter()
const collabs  = ref([...socialCollaborations])
const statusFilter    = ref('all')
const campaignFilter  = ref('all')
const influencerFilter= ref('all')
const showForm = ref(false)
const form = reactive({ influencerId: null, campaignId: null, format: '', cost: 0, publishDate: '', code: '', deliverables: '' })

const filtered = computed(() => {
  let list = [...collabs.value]
  if (statusFilter.value !== 'all')     list = list.filter(c => c.status === statusFilter.value)
  if (campaignFilter.value !== 'all')   list = list.filter(c => c.campaignId === campaignFilter.value)
  if (influencerFilter.value !== 'all') list = list.filter(c => c.influencerId === influencerFilter.value)
  return list.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate))
})

function openForm() { Object.assign(form, { influencerId: null, campaignId: null, format: '', cost: 0, publishDate: '', code: '', deliverables: '' }); showForm.value = true }
function openMetrics() { router.push('/social-crm/metrics') }

function saveCollab() {
  if (!form.influencerId || !form.campaignId) return
  const inf = socialInfluencers.find(i => i.id === form.influencerId)
  const cam = socialCampaigns.find(c => c.id === form.campaignId)
  collabs.value.push({
    id: Date.now(),
    influencerId: form.influencerId, influencerName: inf?.name, influencerAlias: inf?.alias,
    campaignId: form.campaignId, campaignName: cam?.name,
    format: form.format, publishDate: form.publishDate, cost: form.cost,
    linkId: null, code: form.code, status: 'draft',
    clicks: 0, conversions: 0, sales: 0,
    deliverables: form.deliverables, reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0,
    evidences: [], expectedReach: 0, expectedClicks: 0, expectedConversions: 0, observations: '', recommendation: ''
  })
  showForm.value = false
}

function closeCollab(c) {
  if (confirm(`¿Cerrar la colaboración con ${c.influencerName}?`)) {
    const idx = collabs.value.findIndex(x => x.id === c.id)
    if (idx >= 0) collabs.value[idx].status = 'completed'
  }
}
</script>

<style scoped>
.collaborations-view { display: flex; flex-direction: column; height: 100%; }
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
.inf-cell { display: flex; align-items: center; gap: var(--spacing-sm); }
.small-avatar { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.78rem; flex-shrink: 0; }
.inf-name { font-weight: 600; font-size: 0.85rem; color: var(--text-primary); }
.inf-alias { font-size: 0.75rem; color: var(--text-secondary); }
.code-badge { background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; font-family: monospace; color: var(--text-primary); }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.text-secondary { color: var(--text-secondary); }
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
