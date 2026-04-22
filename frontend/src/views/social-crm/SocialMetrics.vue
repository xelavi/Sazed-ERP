<template>
  <div class="metrics-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Carga manual de métricas</h1>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="two-col">
        <!-- Upload form -->
        <div class="card form-card">
          <div class="card-header"><h3 class="card-title">Introducir métricas</h3></div>
          <div class="form-body">
            <div class="field">
              <label class="field-label">Influencer *</label>
              <select class="select full" v-model.number="form.influencerId" @change="onInfluencerChange">
                <option :value="null">Seleccionar influencer...</option>
                <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.name }} ({{ i.alias }})</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Colaboración *</label>
              <select class="select full" v-model.number="form.collaborationId">
                <option :value="null">Seleccionar colaboración...</option>
                <option v-for="c in filteredCollabs" :key="c.id" :value="c.id">{{ c.campaignName }} — {{ formatDate(c.publishDate) }}</option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Descripción de la publicación</label>
              <input class="input full" v-model="form.publicationDesc" placeholder="Ej: TikTok #1 - Primavera" />
            </div>
            <div class="field">
              <label class="field-label">Fecha de publicación</label>
              <input class="input full" type="date" v-model="form.date" />
            </div>

            <div class="section-title">Métricas de alcance</div>
            <div class="metrics-grid-form">
              <div class="field" v-for="m in reachMetrics" :key="m.key">
                <label class="field-label">{{ m.label }}</label>
                <input class="input full" type="number" v-model.number="form[m.key]" placeholder="0" />
              </div>
            </div>

            <div class="section-title">Métricas de interacción</div>
            <div class="metrics-grid-form">
              <div class="field" v-for="m in interactionMetrics" :key="m.key">
                <label class="field-label">{{ m.label }}</label>
                <input class="input full" type="number" v-model.number="form[m.key]" placeholder="0" />
              </div>
            </div>

            <div class="section-title">Trazabilidad</div>
            <div class="traceability-grid">
              <div class="field">
                <label class="field-label">Fuente del dato</label>
                <select class="select full" v-model="form.source">
                  <option value="screenshot">Captura de pantalla</option>
                  <option value="api">API / Plataforma</option>
                  <option value="email">Email del influencer</option>
                  <option value="report">Informe PDF</option>
                  <option value="other">Otro</option>
                </select>
              </div>
              <div class="field">
                <label class="field-label">Estado validación</label>
                <select class="select full" v-model="form.status">
                  <option value="pending">Pendiente de validar</option>
                  <option value="validated">Validado</option>
                </select>
              </div>
            </div>

            <div class="section-title">Adjuntos</div>
            <div class="upload-zone">
              <Upload :size="24" />
              <span>Arrastra aquí capturas, PDFs o evidencias</span>
              <span class="upload-hint">PNG, JPG, PDF — máx. 10MB</span>
              <button class="btn btn-secondary btn-sm">Seleccionar archivos</button>
            </div>
          </div>
          <div class="card-footer">
            <button class="btn btn-secondary" @click="resetForm">Limpiar</button>
            <button class="btn btn-primary" @click="submitMetrics">
              <Save :size="18" />
              Guardar métricas
            </button>
          </div>
        </div>

        <!-- History -->
        <div class="card history-card">
          <div class="card-header">
            <h3 class="card-title">Historial de cargas</h3>
            <span class="count-badge">{{ history.length }}</span>
          </div>
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Influencer</th>
                  <th>Publicación</th>
                  <th>Cargado por</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in history" :key="h.id">
                  <td class="text-sm text-secondary">{{ formatDate(h.date) }}</td>
                  <td class="text-sm font-medium">{{ h.influencerName }}</td>
                  <td class="text-sm text-secondary">{{ h.publicationDesc }}</td>
                  <td class="text-sm text-secondary">{{ h.uploadedBy }}</td>
                  <td>
                    <span class="badge" :class="h.status === 'validated' ? 'badge-active' : 'badge-warning'">
                      {{ h.status === 'validated' ? 'Validado' : 'Pendiente' }}
                    </span>
                  </td>
                </tr>
                <tr v-if="!history.length"><td colspan="5" class="empty-cell">Sin cargas previas</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Upload, Save } from 'lucide-vue-next'
import { socialInfluencers, socialCollaborations, metricsHistory, formatDate } from '@/services/socialCrmData'

const history = ref([...metricsHistory])
const form = reactive({
  influencerId: null, collaborationId: null, publicationDesc: '', date: '',
  reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0,
  clicks: 0, conversions: 0, sales: 0,
  source: 'screenshot', status: 'pending'
})

const reachMetrics = [
  { key: 'reach', label: 'Alcance' }, { key: 'impressions', label: 'Impresiones' }, { key: 'views', label: 'Visualizaciones' }
]
const interactionMetrics = [
  { key: 'likes', label: 'Likes' }, { key: 'comments', label: 'Comentarios' }, { key: 'shares', label: 'Compartidos' },
  { key: 'clicks', label: 'Clics' }, { key: 'conversions', label: 'Conversiones' }, { key: 'sales', label: 'Ventas (€)' }
]

const filteredCollabs = computed(() =>
  form.influencerId
    ? socialCollaborations.filter(c => c.influencerId === form.influencerId)
    : socialCollaborations
)

function onInfluencerChange() { form.collaborationId = null }

function resetForm() {
  Object.assign(form, { influencerId: null, collaborationId: null, publicationDesc: '', date: '', reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0, clicks: 0, conversions: 0, sales: 0, source: 'screenshot', status: 'pending' })
}

function submitMetrics() {
  if (!form.influencerId || !form.collaborationId) { alert('Seleccione influencer y colaboración'); return }
  const inf = socialInfluencers.find(i => i.id === form.influencerId)
  history.value.unshift({
    id: Date.now(), date: form.date || new Date().toISOString().split('T')[0],
    influencerName: inf?.name, collaborationId: form.collaborationId,
    publicationDesc: form.publicationDesc || 'Sin descripción',
    uploadedBy: 'Usuario actual', status: form.status,
    reach: form.reach, impressions: form.impressions, views: form.views,
    likes: form.likes, comments: form.comments, shares: form.shares
  })
  resetForm()
  alert('Métricas guardadas correctamente')
}
</script>

<style scoped>
.metrics-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.two-col { display: grid; grid-template-columns: 420px 1fr; gap: var(--spacing-lg); align-items: start; }
@media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.form-body { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-md); }
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.input.full, .select.full { width: 100%; box-sizing: border-box; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.section-title { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.05em; margin-top: var(--spacing-sm); border-bottom: 1px solid var(--border-color); padding-bottom: 6px; }
.metrics-grid-form { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--spacing-sm); }
.traceability-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.upload-zone { border: 2px dashed var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-lg); display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm); color: var(--text-secondary); text-align: center; }
.upload-hint { font-size: 0.75rem; }
.btn-sm { padding: 6px 12px; font-size: 0.82rem; }
.card-footer { display: flex; justify-content: flex-end; gap: var(--spacing-sm); padding: var(--spacing-lg); border-top: 1px solid var(--border-color); }
.table-wrapper { overflow-x: auto; }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.text-secondary { color: var(--text-secondary); }
.empty-cell { text-align: center; padding: var(--spacing-lg); color: var(--text-secondary); font-size: 0.85rem; }
</style>
