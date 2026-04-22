<template>
  <div class="reports-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Informes</h1>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="reports-layout">
        <!-- Left: selector -->
        <div class="selector-panel">
          <div class="card">
            <div class="card-header"><h3 class="card-title">Tipo de informe</h3></div>
            <div class="report-list">
              <div
                v-for="r in reportTypes" :key="r.id"
                :class="['report-item', { active: selectedReport === r.id }]"
                @click="selectedReport = r.id">
                <div class="report-icon-wrap" :style="{ background: r.colorBg }">
                  <component :is="r.icon" :size="18" :style="{ color: r.color }" />
                </div>
                <div class="report-info">
                  <div class="report-name">{{ r.name }}</div>
                  <div class="report-desc">{{ r.desc }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="card filters-card">
            <div class="card-header"><h3 class="card-title">Parámetros</h3></div>
            <div class="filters-body">
              <div class="field"><label class="field-label">Período</label>
                <select class="select full" v-model="params.period">
                  <option value="7d">Últimos 7 días</option>
                  <option value="30d">Últimos 30 días</option>
                  <option value="q1">Q1 2026</option>
                  <option value="q2">Q2 2026</option>
                  <option value="ytd">Año completo 2026</option>
                </select>
              </div>
              <div class="field"><label class="field-label">Red social</label>
                <select class="select full" v-model="params.platform">
                  <option value="all">Todas</option>
                  <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
                </select>
              </div>
              <div class="field"><label class="field-label">Campaña</label>
                <select class="select full" v-model="params.campaign">
                  <option value="all">Todas</option>
                  <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
              </div>
              <div class="field"><label class="field-label">Influencer</label>
                <select class="select full" v-model="params.influencer">
                  <option value="all">Todos</option>
                  <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
                </select>
              </div>
              <button class="btn btn-primary full-btn" @click="generatePreview">Generar vista previa</button>
            </div>
          </div>
        </div>

        <!-- Right: preview -->
        <div class="preview-panel">
          <div class="card preview-card" v-if="preview">
            <div class="preview-header">
              <div>
                <h2 class="preview-title">{{ currentReport?.name }}</h2>
                <p class="preview-meta">Generado el {{ today }} · Período: {{ periodLabel }}</p>
              </div>
              <div class="preview-actions">
                <button class="btn btn-secondary" @click="exportReport('pdf')"><FileDown :size="16" /><span>PDF</span></button>
                <button class="btn btn-secondary" @click="exportReport('excel')"><FileSpreadsheet :size="16" /><span>Excel</span></button>
                <button class="btn btn-secondary" @click="exportReport('csv')"><Download :size="16" /><span>CSV</span></button>
              </div>
            </div>

            <div class="preview-kpis">
              <div class="kpi-card" v-for="kpi in previewKPIs" :key="kpi.label">
                <div class="kpi-label">{{ kpi.label }}</div>
                <div class="kpi-value">{{ kpi.value }}</div>
              </div>
            </div>

            <div class="preview-sections">
              <div class="section-item" v-for="s in previewSections" :key="s">
                <CheckCircle :size="14" class="section-icon" />
                <span>{{ s }}</span>
              </div>
            </div>

            <div class="preview-placeholder">
              <BarChart2 :size="40" class="placeholder-icon" />
              <p>El informe completo incluye los gráficos y tablas listadas arriba.<br>Exporta para obtener el documento final.</p>
            </div>
          </div>

          <div class="empty-preview" v-else>
            <FileText :size="48" />
            <p>Selecciona un tipo de informe y configura los parámetros para generar la vista previa.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { BarChart2, FileText, FileDown, FileSpreadsheet, Download, CheckCircle, TrendingUp, Users, Megaphone, Link as LinkIcon, LayoutDashboard } from 'lucide-vue-next'
import { socialCampaigns, socialInfluencers, socialPosts, socialCollaborations, PLATFORMS, formatNumber, formatCurrency } from '@/services/socialCrmData'

const reportTypes = [
  { id: 'monthly',    name: 'Informe mensual',       desc: 'Resumen completo de actividad',  icon: LayoutDashboard, color: '#667eea', colorBg: '#eef2ff' },
  { id: 'campaign',   name: 'Por campaña',            desc: 'Rendimiento de una campaña',      icon: Megaphone,       color: '#10B981', colorBg: '#ecfdf5' },
  { id: 'influencer', name: 'Por influencer',         desc: 'Comparativa de colaboradores',    icon: Users,          color: '#F59E0B', colorBg: '#fffbeb' },
  { id: 'conversion', name: 'De conversión',          desc: 'Embudo y ROI por canal',          icon: TrendingUp,     color: '#EC4899', colorBg: '#fdf2f8' },
  { id: 'executive',  name: 'Ejecutivo',              desc: 'KPIs clave en una página',        icon: FileText,       color: '#6366F1', colorBg: '#eef2ff' },
]

const sectionsByType = {
  monthly:    ['Evolución de seguidores por red', 'Publicaciones y engagement', 'Top 5 posts', 'Resumen de campañas activas', 'Gasto e ingresos atribuidos'],
  campaign:   ['Ficha de la campaña', 'KPIs de rendimiento', 'Posts asociados', 'Colaboraciones', 'Embudo de conversión'],
  influencer: ['Tabla comparativa de influencers', 'Ranking por ventas', 'Coste por conversión', 'ROAS por colaborador'],
  conversion: ['Embudo agregado (clic → compra)', 'Revenue por canal', 'Análisis UTM', 'Comparativa campañas'],
  executive:  ['KPIs globales', 'Tendencia semanal', 'Top influencer', 'Alerta destacada', 'Próximos eventos'],
}

const selectedReport = ref('monthly')
const params = reactive({ period: '30d', platform: 'all', campaign: 'all', influencer: 'all' })
const preview = ref(false)
const today = new Date().toLocaleDateString('es-ES')
const currentReport = computed(() => reportTypes.find(r => r.id === selectedReport.value))
const periodLabel = computed(() => ({ '7d': 'Últimos 7 días', '30d': 'Últimos 30 días', 'q1': 'Q1 2026', 'q2': 'Q2 2026', 'ytd': 'Año 2026' }[params.period]))

const previewKPIs = computed(() => {
  const posts = socialPosts; const collabs = socialCollaborations
  const totalReach = posts.reduce((s,p) => s + p.reach, 0)
  const totalEng   = posts.reduce((s,p) => s + p.engagement, 0) / posts.length
  const totalSales = collabs.reduce((s,c) => s + c.sales, 0)
  const totalCost  = collabs.reduce((s,c) => s + c.cost, 0)
  return [
    { label: 'Alcance total', value: formatNumber(totalReach) },
    { label: 'Engagement medio', value: totalEng.toFixed(1) + '%' },
    { label: 'Ingresos atribuidos', value: formatCurrency(totalSales) },
    { label: 'Gasto', value: formatCurrency(totalCost) },
    { label: 'ROAS', value: totalCost ? (totalSales / totalCost).toFixed(2) + 'x' : '—' },
    { label: 'Posts analizados', value: posts.length },
  ]
})
const previewSections = computed(() => sectionsByType[selectedReport.value] || [])

function generatePreview() { preview.value = true }
function exportReport(format) { alert(`Exportando informe en formato ${format.toUpperCase()}... (simulado)`) }
</script>

<style scoped>
.reports-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.reports-layout { display: grid; grid-template-columns: 320px 1fr; gap: var(--spacing-lg); height: 100%; }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.report-list { padding: var(--spacing-sm); }
.report-item { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-sm) var(--spacing-md); border-radius: var(--border-radius-sm); cursor: pointer; transition: background 0.12s; }
.report-item:hover { background: var(--bg-secondary); }
.report-item.active { background: #eef2ff; border-left: 3px solid var(--primary-color); padding-left: calc(var(--spacing-md) - 3px); }
.report-icon-wrap { width: 36px; height: 36px; border-radius: var(--border-radius-sm); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.report-name { font-weight: 600; font-size: 0.875rem; color: var(--text-primary); }
.report-desc { font-size: 0.78rem; color: var(--text-secondary); }
.filters-card { margin-top: var(--spacing-md); }
.filters-body { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-md); }
.field { display: flex; flex-direction: column; gap: 4px; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.select.full, .input.full { width: 100%; box-sizing: border-box; padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.full-btn { width: 100%; justify-content: center; }
.preview-panel { display: flex; flex-direction: column; }
.preview-card { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-lg); }
.preview-header { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--spacing-md); }
.preview-title { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin: 0 0 4px; }
.preview-meta { font-size: 0.82rem; color: var(--text-secondary); margin: 0; }
.preview-actions { display: flex; gap: var(--spacing-sm); }
.preview-kpis { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: var(--spacing-md); }
.kpi-card { background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: var(--spacing-md); }
.kpi-label { font-size: 0.72rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; margin-bottom: 4px; }
.kpi-value { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.preview-sections { display: flex; flex-direction: column; gap: 8px; }
.section-item { display: flex; align-items: center; gap: var(--spacing-sm); font-size: 0.875rem; color: var(--text-primary); }
.section-icon { color: #10B981; flex-shrink: 0; }
.preview-placeholder { display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-xl); border: 2px dashed var(--border-color); border-radius: var(--border-radius-sm); color: var(--text-secondary); text-align: center; font-size: 0.875rem; }
.placeholder-icon { color: var(--text-secondary); }
.empty-preview { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); color: var(--text-secondary); text-align: center; height: 300px; font-size: 0.875rem; }
.selector-panel { display: flex; flex-direction: column; gap: var(--spacing-md); }
</style>
