<template>
  <div class="collab-detail-view">
    <div class="view-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/social-crm/collaborations" class="breadcrumb-link">Colaboraciones</router-link>
          <ChevronRight :size="16" class="breadcrumb-sep" />
          <span class="breadcrumb-current">{{ collab?.influencerName }}</span>
        </div>
        <div class="header-actions" v-if="collab">
          <span class="badge" :class="COLLAB_STATUSES[collab.status].cls">{{ COLLAB_STATUSES[collab.status].label }}</span>
          <button class="btn btn-secondary" @click="$router.push('/social-crm/metrics')"><Upload :size="18" /><span>Cargar métricas</span></button>
        </div>
      </div>
    </div>

    <div v-if="collab" class="content-wrapper">
      <div class="detail-grid">
        <!-- Deal data -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Datos del acuerdo</h3></div>
          <div class="info-body">
            <div class="info-row"><span class="info-key">Influencer</span>
              <span class="clickable-link" @click="$router.push('/social-crm/influencers/' + collab.influencerId)">
                {{ collab.influencerName }} ({{ collab.influencerAlias }})
              </span>
            </div>
            <div class="info-row"><span class="info-key">Campaña</span>
              <span class="clickable-link" @click="$router.push('/social-crm/campaigns/' + collab.campaignId)">
                {{ collab.campaignName }}
              </span>
            </div>
            <div class="info-row"><span class="info-key">Formato pactado</span><span>{{ collab.format }}</span></div>
            <div class="info-row"><span class="info-key">Entregables</span><span class="text-secondary">{{ collab.deliverables }}</span></div>
            <div class="info-row"><span class="info-key">Coste</span><span class="font-medium">{{ formatCurrency(collab.cost) }}</span></div>
            <div class="info-row"><span class="info-key">Fecha publicación</span><span>{{ formatDate(collab.publishDate) }}</span></div>
            <div class="info-row"><span class="info-key">Código descuento</span><code class="code-badge">{{ collab.code || '—' }}</code></div>
          </div>
        </div>

        <!-- Reported metrics -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Métricas reportadas</h3></div>
          <div class="metrics-grid">
            <div class="metric-item" v-for="m in collabMetrics" :key="m.field">
              <div class="metric-val">{{ formatNumber(collab[m.field]) || '—' }}</div>
              <div class="metric-label">{{ m.label }}</div>
            </div>
          </div>
        </div>

        <!-- Expected vs real -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Resultado esperado vs. real</h3></div>
          <div class="compare-grid">
            <div class="compare-item" v-for="m in compareItems" :key="m.label">
              <div class="compare-label">{{ m.label }}</div>
              <div class="compare-row">
                <div class="c-expected"><div class="c-num">{{ m.expected }}</div><div class="c-sub">Esperado</div></div>
                <div class="c-sep">vs</div>
                <div class="c-real"><div class="c-num" :class="m.real >= m.rawExpected ? 'pos' : 'neg'">{{ m.real }}</div><div class="c-sub">Real</div></div>
              </div>
            </div>
          </div>
          <div class="observations" v-if="collab.observations">
            <div class="obs-label">Observaciones</div>
            <div class="obs-text">{{ collab.observations }}</div>
          </div>
          <div class="recommendation" v-if="collab.recommendation">
            <div class="rec-label">Recomendación futura</div>
            <div class="rec-text">{{ collab.recommendation }}</div>
          </div>
        </div>

        <!-- Evidences -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Evidencias</h3>
            <button class="btn btn-secondary btn-sm"><Paperclip :size="15" /><span>Adjuntar</span></button>
          </div>
          <div class="evidences-list">
            <div v-for="(ev, i) in collab.evidences" :key="i" class="evidence-item">
              <FileImage :size="16" />
              <span>{{ ev }}</span>
              <button class="icon-btn-sm"><Download :size="13" /></button>
            </div>
            <div v-if="!collab.evidences.length" class="empty-cell">Sin evidencias adjuntas</div>
          </div>
          <div class="validation-banner" v-if="collab.status === 'completed'">
            <CheckCircle :size="16" />
            <span>Colaboración validada internamente</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <AlertCircle :size="40" />
      <p>Colaboración no encontrada.</p>
      <router-link to="/social-crm/collaborations" class="btn btn-secondary">Volver</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Upload, Paperclip, FileImage, Download, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { socialCollaborations, COLLAB_STATUSES, formatNumber, formatCurrency, formatDate } from '@/services/socialCrmData'

const route  = useRoute()
const collab = computed(() => socialCollaborations.find(c => c.id === Number(route.params.id)))

const collabMetrics = [
  { field: 'reach',        label: 'Alcance' },
  { field: 'impressions',  label: 'Impresiones' },
  { field: 'views',        label: 'Visualizaciones' },
  { field: 'likes',        label: 'Likes' },
  { field: 'comments',     label: 'Comentarios' },
  { field: 'shares',       label: 'Compartidos' },
  { field: 'clicks',       label: 'Clics' },
  { field: 'conversions',  label: 'Conversiones' },
  { field: 'sales',        label: 'Ventas (€)' },
]

const compareItems = computed(() => {
  if (!collab.value) return []
  return [
    { label: 'Alcance',      rawExpected: collab.value.expectedReach,       expected: formatNumber(collab.value.expectedReach),       real: formatNumber(collab.value.reach) },
    { label: 'Clics',        rawExpected: collab.value.expectedClicks,       expected: formatNumber(collab.value.expectedClicks),       real: formatNumber(collab.value.clicks) },
    { label: 'Conversiones', rawExpected: collab.value.expectedConversions,  expected: collab.value.expectedConversions,  real: collab.value.conversions },
  ]
})
</script>

<style scoped>
.collab-detail-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-md) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.breadcrumb { display: flex; align-items: center; gap: 6px; }
.breadcrumb-link { font-size: 0.875rem; color: var(--primary-color); text-decoration: none; }
.breadcrumb-sep { color: var(--text-secondary); }
.breadcrumb-current { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; }
.header-actions { display: flex; align-items: center; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.btn-sm { padding: 4px 10px; font-size: 0.8rem; display: flex; align-items: center; gap: 4px; }
.info-body { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: 10px; }
.info-row { display: flex; align-items: flex-start; gap: var(--spacing-md); }
.info-key { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); min-width: 130px; padding-top: 1px; text-transform: uppercase; }
.text-secondary { color: var(--text-secondary); font-size: 0.85rem; }
.font-medium { font-weight: 600; color: var(--text-primary); }
.clickable-link { color: var(--primary-color); cursor: pointer; font-size: 0.88rem; }
.clickable-link:hover { text-decoration: underline; }
.code-badge { background: var(--bg-secondary); padding: 2px 8px; border-radius: 4px; font-size: 0.82rem; font-family: monospace; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-sm); padding: var(--spacing-md); }
.metric-item { background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: var(--spacing-sm) var(--spacing-md); text-align: center; }
.metric-val { font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.metric-label { font-size: 0.72rem; color: var(--text-secondary); }
.compare-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-md); padding: var(--spacing-md) var(--spacing-lg); }
.compare-item { background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: var(--spacing-md); }
.compare-label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-bottom: var(--spacing-sm); }
.compare-row { display: flex; align-items: center; gap: var(--spacing-sm); }
.c-expected, .c-real { flex: 1; text-align: center; }
.c-sep { color: var(--text-secondary); font-size: 0.78rem; }
.c-num { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.c-num.pos { color: #10B981; }
.c-num.neg { color: #EF4444; }
.c-sub { font-size: 0.7rem; color: var(--text-secondary); }
.observations, .recommendation { padding: var(--spacing-md) var(--spacing-lg); border-top: 1px solid var(--border-color); }
.obs-label, .rec-label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px; }
.obs-text, .rec-text { font-size: 0.85rem; color: var(--text-primary); }
.evidences-list { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: 8px; }
.evidence-item { display: flex; align-items: center; gap: var(--spacing-sm); padding: 8px; background: var(--bg-secondary); border-radius: 6px; font-size: 0.85rem; color: var(--text-primary); }
.evidence-item span { flex: 1; }
.icon-btn-sm { width: 24px; height: 24px; border: none; background: none; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; justify-content: center; border-radius: 4px; }
.icon-btn-sm:hover { background: var(--border-color); }
.empty-cell { text-align: center; padding: var(--spacing-lg); color: var(--text-secondary); font-size: 0.85rem; }
.validation-banner { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-md) var(--spacing-lg); border-top: 1px solid var(--border-color); background: #f0fdf4; color: #10B981; font-size: 0.85rem; font-weight: 600; }
.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); height: 100%; color: var(--text-secondary); }
</style>
