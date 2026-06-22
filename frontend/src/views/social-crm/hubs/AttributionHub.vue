<template>
  <SocialHubLayout
    title="Atribución"
    subtitle="Traçabilitat d'enllaços UTM, conversions i reporting de ROI."
    :tabs="tabs"
    v-model="activeTab"
    :panel-open="!!panel.kind"
    @close-panel="closePanel"
  >
    <template #actions>
      <button v-if="activeTab === 'links'" class="hub-btn hub-btn-primary" @click="onPrimaryAction">
        <Plus :size="15" />
        <span>Crear enllaç</span>
      </button>
    </template>

    <!-- ── KPI strip ─────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Ingressos atribuïts</div>
        <div class="kpi-val">{{ formatCurrency(kpis.totalRevenue) }}</div>
        <div class="kpi-sub">de {{ kpis.totalLinks }} enllaços actius</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Clics totals</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalClicks) }}</div>
        <div class="kpi-sub">{{ formatNumber(kpis.totalSessions) }} sessions</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Compres</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalPurchases) }}</div>
        <div class="kpi-sub">conversió mitjana {{ kpis.avgConversion.toFixed(2) }}%</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Millor enllaç</div>
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
            placeholder="Cerca per nom, UTM o influencer..."
          />
        </div>
        <select v-model="campaignFilter" class="filter-input">
          <option value="all">Totes les campanyes</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="originFilter" class="filter-input">
          <option value="all">Totes les xarxes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select v-model="influencerFilter" class="filter-input">
          <option value="all">Tots els influencers</option>
          <option value="organic">Només orgànic</option>
          <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
        </select>
        <select v-model="linkSort" class="filter-input">
          <option value="revenue">Major ingrés</option>
          <option value="clicks">Més clics</option>
          <option value="conversion">Millor conversió</option>
        </select>
        <div class="result-count">{{ filteredLinks.length }} enllaços</div>
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
          <div class="th">Enllaç</div>
          <div class="th">Origen</div>
          <div class="th">UTM</div>
          <div class="th th-num">Clics</div>
          <div class="th th-num">Compres</div>
          <div class="th th-num">Ingressos</div>
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
                  {{ lnk.influencerName || 'Orgànic' }} · {{ lnk.campaignName }}
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
            <span>No hi ha enllaços amb aquests filtres.</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 2 · INFORMES
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'reports'" class="tab-section">
      <div class="data-card">
        <div class="report-list">
          <div
            v-for="r in reportTypes"
            :key="r.id"
            class="report-row"
          >
            <div class="rr-icon" :style="{ background: r.colorBg, color: r.color }">
              <component :is="r.icon" :size="18" />
            </div>
            <div class="rr-info">
              <div class="rr-name">{{ r.name }}</div>
              <div class="rr-desc">{{ r.desc }}</div>
            </div>
            <div class="rr-exports">
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
  FileDown, FileSpreadsheet, Download,
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
  { key: 'links',   label: 'Enllaços UTM',  count: socialLinks.length },
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
    { key: 'clicks',    label: 'Clics',      value: list.reduce((s, l) => s + l.clicks, 0) },
    { key: 'sessions',  label: 'Sessions',   value: list.reduce((s, l) => s + l.sessions, 0) },
    { key: 'carts',     label: 'Cistelles',  value: list.reduce((s, l) => s + l.carts, 0) },
    { key: 'purchases', label: 'Compres',    value: list.reduce((s, l) => s + l.purchases, 0) },
  ]
})

const funnelColors = ['#667eea', '#764ba2', '#F59E0B', '#10B981']
function barWidth(val) {
  const max = aggregatedFunnel.value[0].value || 1
  return (val / max) * 100
}

// ── Reports state ─────────────────────────────────────────────
const reportTypes = [
  { id: 'monthly',    name: 'Informe mensual',   desc: 'Resum complet d\'activitat',     icon: LayoutDashboard, color: '#667eea', colorBg: '#eef2ff' },
  { id: 'campaign',   name: 'Per campanya',      desc: 'Rendiment d\'una campanya',      icon: Megaphone,       color: '#10B981', colorBg: '#ecfdf5' },
  { id: 'influencer', name: 'Per influencer',    desc: 'Comparativa de col·laboradors',  icon: Users,           color: '#F59E0B', colorBg: '#fffbeb' },
  { id: 'conversion', name: 'De conversió',      desc: 'Embut i ROI per canal',          icon: TrendingUp,      color: '#EC4899', colorBg: '#fdf2f8' },
  { id: 'executive',  name: 'Executiu',          desc: 'KPIs clau en una pàgina',        icon: FileText,        color: '#6366F1', colorBg: '#eef2ff' },
]

const sectionsByType = {
  monthly:    ['Evolució de seguidors per xarxa', 'Publicacions i engagement', 'Top 5 posts del període', 'Resum de campanyes actives', 'Despesa i ingressos atribuïts'],
  campaign:   ['Fitxa de la campanya', 'KPIs de rendiment', 'Posts associats', 'Col·laboracions', 'Embut de conversió'],
  influencer: ['Taula comparativa d\'influencers', 'Rànquing per vendes', 'Cost per conversió', 'ROAS per col·laborador'],
  conversion: ['Embut agregat (clic → compra)', 'Revenue per canal', 'Anàlisi UTM', 'Comparativa campanyes'],
  executive:  ['KPIs globals', 'Tendència setmanal', 'Top influencer', 'Alerta destacada', 'Pròxims esdeveniments'],
}

const selectedReport = ref('monthly')
const today = new Date().toLocaleDateString('ca-ES', { day: '2-digit', month: 'long', year: 'numeric' })
const currentReport = computed(() => reportTypes.find(r => r.id === selectedReport.value))
const periodLabel = computed(() => ({
  '7d': 'Últims 7 dies', '30d': 'Últims 30 dies',
  '90d': 'Últims 3 mesos', 'ytd': 'Any 2026',
}[periodFilter.value]))

const previewKPIs = computed(() => {
  const totalReach = socialPosts.reduce((s, p) => s + p.reach, 0)
  const totalEng = socialPosts.reduce((s, p) => s + p.engagement, 0) / socialPosts.length
  const totalSales = socialCollaborations.reduce((s, c) => s + c.sales, 0)
  const totalCost = socialCollaborations.reduce((s, c) => s + c.cost, 0)
  return [
    { label: 'Abast total',          value: formatNumber(totalReach) },
    { label: 'Engagement mitjà',     value: totalEng.toFixed(1) + '%' },
    { label: 'Ingressos atribuïts',  value: formatCurrency(totalSales) },
    { label: 'Despesa',              value: formatCurrency(totalCost) },
    { label: 'ROAS',                 value: totalCost ? (totalSales / totalCost).toFixed(2) + 'x' : '—' },
    { label: 'Posts analitzats',     value: socialPosts.length },
  ]
})

const previewSections = computed(() => sectionsByType[selectedReport.value] || [])

function exportReport(format) {
  alert(`Exportant ${currentReport.value.name} en format ${format.toUpperCase()} (simulat)`)
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
const primaryActionLabel = computed(() => activeTab.value === 'links' ? 'Crear enllaç' : 'Generar informe')
const primaryActionIcon = computed(() => activeTab.value === 'links' ? Plus : FileDown)
function onPrimaryAction() {
  if (activeTab.value === 'reports') exportReport('pdf')
  else alert('Obrir formulari de creació d\'enllaç')
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

/* ── Reports tab (lista simple) ─────────────────────── */
.report-list { display: flex; flex-direction: column; }
.report-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.12s ease;
}
.report-row:last-child { border-bottom: none; }
.report-row:hover { background: var(--bg-secondary); }
.rr-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.rr-info { min-width: 0; }
.rr-name { font-size: 0.9rem; font-weight: 700; color: var(--text-primary); }
.rr-desc { font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px; }
.rr-exports { display: flex; gap: 0.375rem; flex-shrink: 0; }
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
