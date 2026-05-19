<template>
  <SocialHubLayout
    title="Atribución"
    subtitle="Trazabilidad de enlaces UTM, conversiones y reporting de ROI."
    :tabs="tabs"
    v-model="activeTab"
    :panel-open="!!panel.kind"
    @close-panel="closePanel"
  >
    <template #actions>
      <div class="hub-filter-group">
        <select v-model="periodFilter" class="hub-mini-select" aria-label="Periodo">
          <option value="7d">Últimos 7 días</option>
          <option value="30d">Últimos 30 días</option>
          <option value="90d">Últimos 3 meses</option>
          <option value="ytd">Año actual</option>
        </select>
        <select v-model="campaignFilter" class="hub-mini-select" aria-label="Campaña">
          <option value="all">Todas las campañas</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <button class="hub-btn hub-btn-primary" @click="onPrimaryAction">
        <component :is="primaryActionIcon" :size="15" />
        <span>{{ primaryActionLabel }}</span>
      </button>
    </template>

    <!-- ── KPI strip ─────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Ingresos atribuidos</div>
        <div class="kpi-val">{{ formatCurrency(kpis.totalRevenue) }}</div>
        <div class="kpi-sub">de {{ kpis.totalLinks }} enlaces activos</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Clics totales</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalClicks) }}</div>
        <div class="kpi-sub">{{ formatNumber(kpis.totalSessions) }} sesiones</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Compras</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalPurchases) }}</div>
        <div class="kpi-sub">conversión media {{ kpis.avgConversion.toFixed(2) }}%</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Mejor enlace</div>
        <div class="kpi-val kpi-val-sm">{{ kpis.topLink?.name || '—' }}</div>
        <div class="kpi-sub">{{ kpis.topLink ? formatCurrency(kpis.topLink.revenue) : '' }}</div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         TAB 1 · ENLACES
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'links'" class="tab-section">
      <div class="filters-row">
        <div class="search-input-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="linkSearch"
            class="filter-input search-input"
            placeholder="Buscar por nombre, UTM o influencer..."
          />
        </div>
        <select v-model="originFilter" class="filter-input">
          <option value="all">Todas las redes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select v-model="influencerFilter" class="filter-input">
          <option value="all">Todos los influencers</option>
          <option value="organic">Solo orgánico</option>
          <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
        </select>
        <select v-model="linkSort" class="filter-input">
          <option value="revenue">Mayor ingreso</option>
          <option value="clicks">Más clics</option>
          <option value="conversion">Mejor conversión</option>
        </select>
        <div class="result-count">{{ filteredLinks.length }} enlaces</div>
      </div>

      <!-- Funnel summary (aggregated) -->
      <div class="funnel-summary">
        <div class="funnel-step" v-for="(step, i) in aggregatedFunnel" :key="step.key">
          <div class="fs-num">{{ formatNumber(step.value) }}</div>
          <div class="fs-key">{{ step.label }}</div>
          <div class="fs-bar" :style="{ width: barWidth(step.value) + '%', background: funnelColors[i] }"></div>
          <div v-if="i > 0" class="fs-pct">
            <ArrowRight :size="11" />
            {{ ((step.value / aggregatedFunnel[i-1].value) * 100).toFixed(1) }}%
          </div>
        </div>
      </div>

      <div class="data-card">
        <div class="data-head head-links">
          <div class="th">Enlace</div>
          <div class="th">Origen</div>
          <div class="th">UTM</div>
          <div class="th th-num">Clics</div>
          <div class="th th-num">Compras</div>
          <div class="th th-num">Ingresos</div>
          <div class="th th-num">Conv.</div>
        </div>
        <div class="data-rows">
          <button
            v-for="lnk in filteredLinks"
            :key="lnk.id"
            class="data-row row-links"
            :class="{ active: panel.kind === 'link' && panel.id === lnk.id }"
            @click="openLink(lnk.id)"
          >
            <div class="cell cell-link">
              <div class="link-icon-box" :style="linkIconStyle(lnk.origin)">
                <LinkIcon :size="13" />
              </div>
              <div class="link-block">
                <div class="row-name">{{ lnk.name }}</div>
                <div class="row-alias">
                  {{ lnk.influencerName || 'Orgánico' }} · {{ lnk.campaignName }}
                </div>
              </div>
            </div>
            <div class="cell">
              <span class="platform-pill" :style="platformStyle(lnk.origin)">
                {{ getPlatform(lnk.origin).label }}
              </span>
            </div>
            <div class="cell">
              <code class="utm-chip">{{ lnk.utmCampaign }}</code>
            </div>
            <div class="cell cell-num font-mono">{{ formatNumber(lnk.clicks) }}</div>
            <div class="cell cell-num font-mono">{{ formatNumber(lnk.purchases) }}</div>
            <div class="cell cell-num font-mono cell-revenue">
              {{ formatCurrency(lnk.revenue) }}
            </div>
            <div class="cell cell-num">
              <span class="conv-pill" :class="convClass(lnk.conversion)">
                {{ lnk.conversion.toFixed(2) }}%
              </span>
            </div>
          </button>
          <div v-if="!filteredLinks.length" class="empty-row">
            <Frown :size="20" />
            <span>No hay enlaces con esos filtros.</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 2 · INFORMES
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'reports'" class="tab-section reports-tab">
      <div class="reports-grid">
        <!-- Report types -->
        <aside class="reports-sidebar">
          <h3 class="rs-title">Tipo de informe</h3>
          <div class="report-types">
            <button
              v-for="r in reportTypes"
              :key="r.id"
              class="report-type"
              :class="{ active: selectedReport === r.id }"
              @click="selectedReport = r.id"
            >
              <div class="rt-icon-wrap" :style="{ background: r.colorBg, color: r.color }">
                <component :is="r.icon" :size="16" />
              </div>
              <div class="rt-info">
                <div class="rt-name">{{ r.name }}</div>
                <div class="rt-desc">{{ r.desc }}</div>
              </div>
              <Check v-if="selectedReport === r.id" :size="14" class="rt-check" />
            </button>
          </div>
        </aside>

        <!-- Preview -->
        <div class="reports-preview">
          <header class="preview-head">
            <div class="preview-meta">
              <span class="preview-type">{{ currentReport.name }}</span>
              <span class="preview-period">Periodo: {{ periodLabel }}</span>
            </div>
            <div class="preview-exports">
              <button class="export-btn" @click="exportReport('pdf')">
                <FileDown :size="13" /> PDF
              </button>
              <button class="export-btn" @click="exportReport('excel')">
                <FileSpreadsheet :size="13" /> Excel
              </button>
              <button class="export-btn" @click="exportReport('csv')">
                <Download :size="13" /> CSV
              </button>
            </div>
          </header>

          <div class="preview-body">
            <h2 class="preview-title">{{ currentReport.name }}</h2>
            <p class="preview-sub">Generado el {{ today }}</p>

            <div class="preview-kpis">
              <div class="pk-cell" v-for="kpi in previewKPIs" :key="kpi.label">
                <div class="pk-key">{{ kpi.label }}</div>
                <div class="pk-val">{{ kpi.value }}</div>
              </div>
            </div>

            <div class="preview-sections">
              <h4 class="ps-title">Contenido del informe</h4>
              <ul class="ps-list">
                <li v-for="s in previewSections" :key="s">
                  <CheckCircle :size="13" />
                  <span>{{ s }}</span>
                </li>
              </ul>
            </div>

            <div class="preview-note">
              <Info :size="13" />
              <span>El export final incluye los gráficos, tablas y datos detallados listados arriba.</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Side panel ─────────────────────────────────────────── -->
    <template #panel>
      <LinkDetailPanel
        v-if="panel.kind === 'link'"
        :link-id="panel.id"
        @close="closePanel"
      />
    </template>
  </SocialHubLayout>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import {
  Search, Plus, Frown, Link as LinkIcon, ArrowRight,
  FileDown, FileSpreadsheet, Download, CheckCircle, Check, Info,
  LayoutDashboard, Megaphone, Users, TrendingUp, FileText,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'
import LinkDetailPanel from './LinkDetailPanel.vue'
import {
  socialLinks, socialCampaigns, socialInfluencers, socialPosts, socialCollaborations,
  PLATFORMS, getPlatform, formatNumber, formatCurrency,
} from '@/services/socialCrmData'

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('links')

const tabs = computed(() => [
  { key: 'links',   label: 'Enlaces UTM',  count: socialLinks.length },
  { key: 'reports', label: 'Informes' },
])

// ── Global filters ────────────────────────────────────────────
const periodFilter   = ref('30d')
const campaignFilter = ref('all')

// ── Links state ───────────────────────────────────────────────
const linkSearch       = ref('')
const originFilter     = ref('all')
const influencerFilter = ref('all')
const linkSort         = ref('revenue')

const filteredLinks = computed(() => {
  let list = [...socialLinks]
  if (campaignFilter.value !== 'all')   list = list.filter(l => l.campaignId === campaignFilter.value)
  if (originFilter.value !== 'all')     list = list.filter(l => l.origin === originFilter.value)
  if (influencerFilter.value === 'organic') list = list.filter(l => !l.influencerId)
  else if (influencerFilter.value !== 'all') list = list.filter(l => l.influencerId === influencerFilter.value)
  if (linkSearch.value) {
    const q = linkSearch.value.toLowerCase()
    list = list.filter(l =>
      l.name.toLowerCase().includes(q) ||
      l.utmCampaign.toLowerCase().includes(q) ||
      (l.influencerName || '').toLowerCase().includes(q)
    )
  }
  return list.sort((a, b) => {
    if (linkSort.value === 'revenue')    return b.revenue - a.revenue
    if (linkSort.value === 'clicks')     return b.clicks - a.clicks
    if (linkSort.value === 'conversion') return b.conversion - a.conversion
    return 0
  })
})

// ── Aggregated funnel for tab Enlaces ─────────────────────────
const aggregatedFunnel = computed(() => {
  const list = filteredLinks.value
  return [
    { key: 'clicks',    label: 'Clics',     value: list.reduce((s, l) => s + l.clicks, 0) },
    { key: 'sessions',  label: 'Sesiones',  value: list.reduce((s, l) => s + l.sessions, 0) },
    { key: 'carts',     label: 'Carritos',  value: list.reduce((s, l) => s + l.carts, 0) },
    { key: 'purchases', label: 'Compras',   value: list.reduce((s, l) => s + l.purchases, 0) },
  ]
})

const funnelColors = ['#667eea', '#764ba2', '#F59E0B', '#10B981']
function barWidth(val) {
  const max = aggregatedFunnel.value[0].value || 1
  return (val / max) * 100
}

// ── Reports state ─────────────────────────────────────────────
const reportTypes = [
  { id: 'monthly',    name: 'Informe mensual',  desc: 'Resumen completo de actividad',  icon: LayoutDashboard, color: '#667eea', colorBg: '#eef2ff' },
  { id: 'campaign',   name: 'Por campaña',      desc: 'Rendimiento de una campaña',     icon: Megaphone,       color: '#10B981', colorBg: '#ecfdf5' },
  { id: 'influencer', name: 'Por influencer',   desc: 'Comparativa de colaboradores',   icon: Users,           color: '#F59E0B', colorBg: '#fffbeb' },
  { id: 'conversion', name: 'De conversión',    desc: 'Embudo y ROI por canal',         icon: TrendingUp,      color: '#EC4899', colorBg: '#fdf2f8' },
  { id: 'executive',  name: 'Ejecutivo',        desc: 'KPIs clave en una página',       icon: FileText,        color: '#6366F1', colorBg: '#eef2ff' },
]

const sectionsByType = {
  monthly:    ['Evolución de seguidores por red', 'Publicaciones y engagement', 'Top 5 posts del periodo', 'Resumen de campañas activas', 'Gasto e ingresos atribuidos'],
  campaign:   ['Ficha de la campaña', 'KPIs de rendimiento', 'Posts asociados', 'Colaboraciones', 'Embudo de conversión'],
  influencer: ['Tabla comparativa de influencers', 'Ranking por ventas', 'Coste por conversión', 'ROAS por colaborador'],
  conversion: ['Embudo agregado (clic → compra)', 'Revenue por canal', 'Análisis UTM', 'Comparativa campañas'],
  executive:  ['KPIs globales', 'Tendencia semanal', 'Top influencer', 'Alerta destacada', 'Próximos eventos'],
}

const selectedReport = ref('monthly')
const today = new Date().toLocaleDateString('es-ES', { day: '2-digit', month: 'long', year: 'numeric' })
const currentReport = computed(() => reportTypes.find(r => r.id === selectedReport.value))
const periodLabel = computed(() => ({
  '7d': 'Últimos 7 días', '30d': 'Últimos 30 días',
  '90d': 'Últimos 3 meses', 'ytd': 'Año 2026',
}[periodFilter.value]))

const previewKPIs = computed(() => {
  const totalReach = socialPosts.reduce((s, p) => s + p.reach, 0)
  const totalEng = socialPosts.reduce((s, p) => s + p.engagement, 0) / socialPosts.length
  const totalSales = socialCollaborations.reduce((s, c) => s + c.sales, 0)
  const totalCost = socialCollaborations.reduce((s, c) => s + c.cost, 0)
  return [
    { label: 'Alcance total',       value: formatNumber(totalReach) },
    { label: 'Engagement medio',    value: totalEng.toFixed(1) + '%' },
    { label: 'Ingresos atribuidos', value: formatCurrency(totalSales) },
    { label: 'Gasto',               value: formatCurrency(totalCost) },
    { label: 'ROAS',                value: totalCost ? (totalSales / totalCost).toFixed(2) + 'x' : '—' },
    { label: 'Posts analizados',    value: socialPosts.length },
  ]
})

const previewSections = computed(() => sectionsByType[selectedReport.value] || [])

function exportReport(format) {
  alert(`Exportando ${currentReport.value.name} en formato ${format.toUpperCase()} (simulado)`)
}

// ── KPIs ──────────────────────────────────────────────────────
const kpis = computed(() => {
  const totalRevenue = socialLinks.reduce((s, l) => s + l.revenue, 0)
  const totalClicks = socialLinks.reduce((s, l) => s + l.clicks, 0)
  const totalSessions = socialLinks.reduce((s, l) => s + l.sessions, 0)
  const totalPurchases = socialLinks.reduce((s, l) => s + l.purchases, 0)
  const totalLinks = socialLinks.length
  const avgConversion = socialLinks.length
    ? socialLinks.reduce((s, l) => s + l.conversion, 0) / socialLinks.length
    : 0
  const topLink = [...socialLinks].sort((a, b) => b.revenue - a.revenue)[0]
  return { totalRevenue, totalClicks, totalSessions, totalPurchases, totalLinks, avgConversion, topLink }
})

// ── Side panel ────────────────────────────────────────────────
const panel = reactive({ kind: null, id: null })
function openLink(id) { panel.kind = 'link'; panel.id = id }
function closePanel() { panel.kind = null; panel.id = null }

// ── Primary action ────────────────────────────────────────────
const primaryActionLabel = computed(() => activeTab.value === 'links' ? 'Crear enlace' : 'Generar informe')
const primaryActionIcon = computed(() => activeTab.value === 'links' ? Plus : FileDown)
function onPrimaryAction() {
  if (activeTab.value === 'reports') exportReport('pdf')
  else alert('Abrir formulario de creación de enlace')
}

// ── Helpers ───────────────────────────────────────────────────
function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function linkIconStyle(key) {
  const p = getPlatform(key)
  return {
    background: `linear-gradient(135deg, ${p.color}cc, ${p.color}80)`,
    color: 'white',
  }
}
function convClass(v) { return v >= 5 ? 'conv-high' : v >= 2 ? 'conv-mid' : 'conv-low' }
</script>

<style scoped>
/* ── Header micro-controls ──────────────────────────── */
.hub-filter-group { display: flex; gap: 0.375rem; }
.hub-mini-select {
  padding: 0.4rem 0.625rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.8rem;
  cursor: pointer;
}
.hub-mini-select:hover { border-color: var(--primary-color); }

.hub-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--bg-primary);
  color: var(--text-primary);
}
.hub-btn-primary {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(102,126,234,0.30);
}
.hub-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }

/* ── KPI strip ──────────────────────────────────────── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}
.kpi-tile {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.875rem 1rem;
  position: relative;
  overflow: hidden;
}
.kpi-tile::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  opacity: 0.55;
}
.kpi-key {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}
.kpi-val {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  line-height: 1.05;
  font-feature-settings: "tnum";
}
.kpi-val-sm { font-size: 0.95rem; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kpi-sub { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.25rem; }

/* ── Filters row ────────────────────────────────────── */
.tab-section { display: flex; flex-direction: column; gap: 1rem; }
.filters-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }

.filter-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s ease;
}
.filter-input:hover { border-color: var(--primary-color); }
.filter-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }

.search-input-wrap { position: relative; flex: 1 1 280px; max-width: 360px; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { width: 100%; padding-left: 2rem; cursor: text; }
.result-count { margin-left: auto; font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; }

/* ── Funnel summary (aggregated horizontal funnel) ───── */
.funnel-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}
.funnel-step {
  position: relative;
  padding: 0.625rem 0.75rem 0.875rem;
  background: var(--bg-secondary);
  border-radius: 9px;
  overflow: hidden;
}
.fs-num {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.1;
}
.fs-key {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-top: 2px;
  margin-bottom: 0.5rem;
}
.fs-bar {
  height: 4px;
  border-radius: 2px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.fs-pct {
  position: absolute;
  top: 0.625rem;
  right: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--bg-primary);
  padding: 2px 6px;
  border-radius: 5px;
}

/* ── Links table ────────────────────────────────────── */
.data-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.data-head {
  display: grid;
  padding: 0.625rem 1.25rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
.head-links { grid-template-columns: 2.5fr 0.9fr 1.2fr 0.8fr 0.8fr 1fr 0.8fr; }
.th-num { text-align: right; }

.data-rows { display: flex; flex-direction: column; }
.data-row {
  display: grid;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-left: none;
  border-right: none;
  border-top: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  font-size: 0.85rem;
  transition: background 0.12s ease;
  align-items: center;
}
.row-links { grid-template-columns: 2.5fr 0.9fr 1.2fr 0.8fr 0.8fr 1fr 0.8fr; }
.data-row:last-child { border-bottom: none; }
.data-row:hover { background: var(--bg-secondary); }
.data-row.active { background: rgba(102,126,234,0.06); position: relative; }
.data-row.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}

.cell { display: flex; align-items: center; min-width: 0; }
.cell-link { gap: 0.625rem; }
.cell-num { justify-content: flex-end; text-align: right; }
.cell-revenue { font-weight: 700; color: var(--text-primary); }
.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.link-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(15,23,42,0.08);
}

.link-block { min-width: 0; flex: 1; }
.row-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 280px;
}
.row-alias {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.platform-pill {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.utm-chip {
  font-size: 0.7rem;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  background: var(--bg-secondary);
  padding: 2px 7px;
  border-radius: 5px;
  color: var(--text-primary);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.conv-pill {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  font-feature-settings: "tnum";
}
.conv-high { background: rgba(16,185,129,0.12); color: #10B981; }
.conv-mid  { background: rgba(245,158,11,0.12); color: #F59E0B; }
.conv-low  { background: rgba(239,68,68,0.10); color: #EF4444; }

.empty-row {
  padding: 2.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ── Reports tab ────────────────────────────────────── */
.reports-tab { gap: 0; }
.reports-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.25rem;
  align-items: start;
}

.reports-sidebar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  position: sticky;
  top: 0;
}
.rs-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--primary-color);
  margin: 0 0 0.25rem;
}

.report-types { display: flex; flex-direction: column; gap: 0.4rem; }
.report-type {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem 0.875rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: all 0.15s ease;
}
.report-type:hover {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.04);
}
.report-type.active {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.06);
  box-shadow: 0 0 0 3px rgba(102,126,234,0.10);
}
.rt-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.rt-info { min-width: 0; }
.rt-name { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); }
.rt-desc { font-size: 0.72rem; color: var(--text-secondary); margin-top: 1px; }
.rt-check { color: var(--primary-color); }

/* Preview */
.reports-preview {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.preview-head {
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(102,126,234,0.04), transparent);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.625rem;
}
.preview-meta { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.preview-type { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); }
.preview-period { font-size: 0.72rem; color: var(--text-secondary); }
.preview-exports { display: flex; gap: 0.375rem; }
.export-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.7rem;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}
.export-btn:hover { border-color: var(--primary-color); background: rgba(102,126,234,0.04); }

.preview-body { padding: 1.5rem 1.75rem 2rem; }
.preview-title {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}
.preview-sub { font-size: 0.825rem; color: var(--text-secondary); margin: 0 0 1.5rem; }

.preview-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.625rem;
  margin-bottom: 1.5rem;
}
.pk-cell {
  background: var(--bg-secondary);
  border-radius: 9px;
  padding: 0.625rem 0.75rem;
}
.pk-key { font-size: 0.66rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 600; letter-spacing: 0.05em; }
.pk-val { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-top: 2px; font-feature-settings: "tnum"; }

.preview-sections { background: var(--bg-secondary); border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 1rem; }
.ps-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
  margin: 0 0 0.625rem;
}
.ps-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.ps-list li { display: flex; align-items: center; gap: 0.5rem; font-size: 0.825rem; color: var(--text-primary); }
.ps-list svg { color: #10B981; flex-shrink: 0; }

.preview-note {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  background: rgba(102,126,234,0.06);
  border: 1px dashed rgba(102,126,234,0.3);
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.4;
}
.preview-note svg { color: var(--primary-color); flex-shrink: 0; margin-top: 1px; }

/* ── Responsive ────────────────────────────────────── */
@media (max-width: 1280px) {
  .head-links, .row-links { grid-template-columns: 2.2fr 0.9fr 1.1fr 0.7fr 0.7fr 1fr 0.7fr; }
}

@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .reports-grid { grid-template-columns: 1fr; }
  .reports-sidebar { position: static; }
  .funnel-summary { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
  .data-head { display: none; }
  .data-row {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 0.75rem;
    padding: 0.875rem 1rem;
  }
  .cell-link { grid-column: 1 / -1; }
  .cell:not(.cell-link) { font-size: 0.78rem; }
}

@media (max-width: 600px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
  .funnel-summary { grid-template-columns: 1fr; }
  .preview-body { padding: 1rem 1.25rem; }
}
</style>
