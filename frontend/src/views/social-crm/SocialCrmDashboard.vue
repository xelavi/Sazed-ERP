<template>
  <div class="summary-view">

    <!-- ── Capçalera ─────────────────────────────────────────────── -->
    <header class="view-header">
      <div class="header-left">
        <div class="title-icon"><BarChart2 :size="22" /></div>
        <div>
          <h1 class="view-title">Resum Social CRM</h1>
          <p class="view-subtitle">{{ today }}</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="period-tabs">
          <button v-for="opt in periodOptions" :key="opt.value"
            class="period-btn" :class="{ active: periodFilter === opt.value }"
            @click="periodFilter = opt.value">{{ opt.label }}</button>
        </div>
      </div>
    </header>

    <!-- ── KPI strip ──────────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div v-for="kpi in kpiTiles" :key="kpi.key" class="kpi-tile" :style="{ '--accent': kpi.color }">
        <div class="kpi-icon-wrap" :style="{ background: kpi.colorBg, color: kpi.color }">
          <component :is="kpi.icon" :size="22" />
        </div>
        <div class="kpi-body">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">{{ kpi.formatted }}</div>
          <div v-if="kpi.sub" class="kpi-sub">{{ kpi.sub }}</div>
        </div>
      </div>
    </div>

    <!-- ── Graella principal: campanyes + pendents ──────────────── -->
    <div class="main-grid">

      <!-- Campanyes actives -->
      <div class="card">
        <div class="card-head">
          <div class="card-head-left">
            <div class="section-icon" style="background:rgba(102,126,234,.12);color:#667eea">
              <Target :size="15" />
            </div>
            <h3 class="section-title">Campanyes actives</h3>
            <span v-if="activeCampaigns.length" class="count-pill primary">{{ activeCampaigns.length }}</span>
          </div>
          <router-link to="/social-crm/campaigns" class="card-action">
            Veure-les totes <ChevronRight :size="14" />
          </router-link>
        </div>
        <div class="campaign-list">
          <router-link v-for="c in activeCampaigns" :key="c.id"
            :to="`/social-crm/campaigns?open=${c.id}`" class="camp-row">
            <div class="camp-main">
              <div class="camp-name">{{ c.name }}</div>
              <div class="camp-tags">
                <span class="camp-obj-tag">{{ c.objective }}</span>
                <span class="camp-days-tag" :class="daysUrgencyClass(c.endDate)">
                  <Clock :size="11" /> {{ daysLeftLabel(c.endDate) }}
                </span>
              </div>
            </div>
            <div class="camp-budget-block">
              <div class="camp-budget-nums">
                <span class="camp-spent">{{ formatCurrency(c.cost) }}</span>
                <span class="camp-of">/ {{ formatCurrency(c.budget) }}</span>
                <span class="camp-pct" :class="budgetFillClass(c)">{{ budgetPct(c).toFixed(0) }}%</span>
              </div>
              <div class="budget-bar-wrap">
                <div class="budget-bar-fill"
                  :style="{ width: Math.min(budgetPct(c), 100) + '%' }"
                  :class="budgetFillClass(c)"></div>
              </div>
            </div>
            <div class="camp-roas-block">
              <span class="roas-badge" :class="roasClass(c.roas)">{{ c.roas.toFixed(1) }}x</span>
              <span class="camp-roas-label">ROAS</span>
            </div>
          </router-link>
          <div v-if="!activeCampaigns.length" class="empty-state-sm">
            <Target :size="32" /><p>No hi ha campanyes actives</p>
          </div>
        </div>
      </div>

      <!-- Accions pendents -->
      <div class="card">
        <div class="card-head">
          <div class="card-head-left">
            <div class="section-icon"
              :style="pendingActions.length
                ? 'background:rgba(239,68,68,.12);color:#EF4444'
                : 'background:rgba(16,185,129,.12);color:#10B981'">
              <AlertCircle v-if="pendingActions.length" :size="15" />
              <CheckCircle v-else :size="15" />
            </div>
            <h3 class="section-title">Accions pendents</h3>
            <span v-if="pendingActions.length" class="count-badge">{{ pendingActions.length }}</span>
          </div>
        </div>
        <div class="pending-list">
          <div v-for="action in pendingActions" :key="action.id"
            class="pending-row" :class="'pri-' + action.priority">
            <div class="pending-icon-wrap" :class="'pri-' + action.priority">
              <AlertTriangle v-if="action.priority === 'high'" :size="13" />
              <Clock v-else-if="action.priority === 'medium'" :size="13" />
              <Info v-else :size="13" />
            </div>
            <div class="pending-body">
              <div class="pending-title">{{ action.title }}</div>
              <div class="pending-sub">{{ action.sub }}</div>
            </div>
            <router-link :to="action.link" class="pending-link">Veure</router-link>
          </div>
          <div v-if="!pendingActions.length" class="pending-ok">
            <CheckCircle :size="17" /> Tot al dia
          </div>
        </div>
      </div>
    </div>

    <!-- ── Gràfic de creixement ───────────────────────────────────── -->
    <div class="card growth-card">
      <div class="card-head growth-head">
        <div class="card-head-left">
          <div class="section-icon" style="background:rgba(102,126,234,.12);color:#667eea">
            <TrendingUp :size="15" />
          </div>
          <h3 class="section-title">Creixement de seguidors</h3>
          <span class="period-badge">Últims 6 mesos</span>
        </div>
        <!-- Filtre de compte -->
        <div class="account-filter">
          <button class="acc-btn" :class="{ active: selectedAccountId === null }"
            @click="selectedAccountId = null">Totes</button>
          <button v-for="acc in socialAccounts" :key="acc.id"
            class="acc-btn"
            :class="{ active: selectedAccountId === acc.id }"
            :style="selectedAccountId === acc.id
              ? { background: getPlatform(acc.platform).bg, color: getPlatform(acc.platform).color, borderColor: getPlatform(acc.platform).color + '80' }
              : {}"
            @click="selectedAccountId = acc.id">
            {{ getPlatform(acc.platform).label }}
          </button>
        </div>
      </div>

      <!-- Stats del gràfic -->
      <div class="growth-stats">
        <div class="gs-item">
          <div class="gs-val" :style="{ color: chartColor }">{{ formatNumber(chartCurrentValue) }}</div>
          <div class="gs-label">{{ selectedAccountId ? 'Seguidors actuals' : 'Total seguidors' }}</div>
        </div>
        <div class="gs-divider"></div>
        <div class="gs-item">
          <div class="gs-val" :class="Number(chartGrowthPct) >= 0 ? 'val-green' : 'val-red'">
            {{ Number(chartGrowthPct) >= 0 ? '+' : '' }}{{ chartGrowthPct }}%
          </div>
          <div class="gs-label">Creixement en el període</div>
        </div>
        <div class="gs-divider"></div>
        <div class="gs-item">
          <div class="gs-val" :class="Number(chartDelta) >= 0 ? 'val-green' : 'val-red'">
            {{ Number(chartDelta) >= 0 ? '+' : '' }}{{ formatNumber(chartDelta) }}
          </div>
          <div class="gs-label">Seguidors nous</div>
        </div>
        <template v-if="!selectedAccountId">
          <div class="gs-divider"></div>
          <div class="gs-item">
            <div class="gs-val" style="color:#10B981">{{ connectedCount }}</div>
            <div class="gs-label">Comptes connectades</div>
          </div>
        </template>
      </div>

      <!-- Chart -->
      <div class="chart-body">
        <div class="chart-y-axis">
          <span>{{ formatNumber(chartYMax) }}</span>
          <span>{{ formatNumber(Math.round((chartYMax + chartYMin) / 2)) }}</span>
          <span>{{ formatNumber(chartYMin) }}</span>
        </div>
        <div class="chart-main">
          <div class="chart-svg-wrap">
            <svg class="growth-svg" viewBox="0 0 600 140" preserveAspectRatio="none">
              <!-- Grid lines -->
              <line x1="0" x2="600" y1="12"  y2="12"  class="grid-line" />
              <line x1="0" x2="600" y1="68"  y2="68"  class="grid-line" />
              <line x1="0" x2="600" y1="124" y2="124" class="grid-line" />
              <!-- Area fill -->
              <path :d="chartAreaPath" class="chart-area-path"
                :style="{ fill: chartColor }" />
              <!-- Line -->
              <path :d="chartLinePath" class="chart-line-path"
                :style="{ stroke: chartColor }" />
            </svg>
            <div v-for="(pt, i) in chartPoints" :key="i"
              class="chart-dot-html"
              :style="{
                left: (pt.x / 600 * 100) + '%',
                top:  (pt.y / 140 * 100) + '%',
                background: chartColor
              }">
            </div>
          </div>
          <div class="chart-x-labels">
            <span v-for="label in MONTH_LABELS" :key="label">{{ label }}</span>
          </div>
        </div>
      </div>

      <!-- Llegenda quan mostrem totes les comptes -->
      <div v-if="!selectedAccountId" class="chart-legend">
        <div v-for="acc in socialAccounts" :key="acc.id" class="legend-item">
          <span class="legend-dot" :style="{ background: getPlatform(acc.platform).color }"></span>
          <span class="legend-name">{{ getPlatform(acc.platform).label }}</span>
          <span class="legend-val">{{ formatNumber(acc.followers) }}</span>
          <span class="legend-growth" :class="Number(accountGrowth[acc.id]) >= 0 ? 'val-green' : 'val-red'">
            {{ Number(accountGrowth[acc.id]) >= 0 ? '+' : '' }}{{ accountGrowth[acc.id] }}%
          </span>
        </div>
      </div>
    </div>

    <!-- ── Fila inferior: publicacions + estat comptes ────────────── -->
    <div class="bottom-grid">

      <!-- Millors publicacions -->
      <div class="card">
        <div class="card-head">
          <div class="card-head-left">
            <div class="section-icon" style="background:rgba(245,158,11,.12);color:#F59E0B">
              <Star :size="15" />
            </div>
            <h3 class="section-title">Millors publicacions</h3>
          </div>
          <router-link to="/social-crm/content" class="card-action">
            Veure contingut <ChevronRight :size="14" />
          </router-link>
        </div>
        <div class="posts-list">
          <div v-for="(post, i) in topPostsData" :key="post.id" class="post-row">
            <div class="post-rank" :class="'rank-' + (i + 1)">{{ i + 1 }}</div>
            <div class="post-info">
              <div class="post-title">{{ post.title }}</div>
              <div class="post-meta">
                <span class="plat-pill" :style="platformStyle(post.platform)">{{ getPlatform(post.platform).label }}</span>
                <span class="post-stat">{{ formatNumber(post.reach) }} abast</span>
                <span class="post-stat">{{ formatNumber(post.likes) }} likes</span>
              </div>
            </div>
            <span class="eng-pill" :class="engClass(post.engagement)">{{ post.engagement }}%</span>
          </div>
          <div v-if="!topPostsData.length" class="empty-state-sm">
            <Star :size="32" /><p>Sense publicacions sincronitzades</p>
          </div>
        </div>
      </div>

      <!-- Estat de les comptes -->
      <div class="card">
        <div class="card-head">
          <div class="card-head-left">
            <div class="section-icon" style="background:rgba(16,185,129,.12);color:#10B981">
              <Share2 :size="15" />
            </div>
            <h3 class="section-title">Estat de les comptes</h3>
          </div>
          <router-link to="/social-crm/accounts" class="card-action">
            Gestionar <ChevronRight :size="14" />
          </router-link>
        </div>
        <div class="accounts-list">
          <div v-for="acc in socialAccounts" :key="acc.id" class="acc-row">
            <div class="acc-platform-icon"
              :style="{ background: getPlatform(acc.platform).bg, color: getPlatform(acc.platform).color }">
              {{ getPlatform(acc.platform).label[0] }}
            </div>
            <div class="acc-info">
              <div class="acc-name">{{ acc.name }}</div>
              <div class="acc-username">{{ acc.username }}</div>
            </div>
            <div class="acc-metrics">
              <template v-if="acc.status === 'connected'">
                <div class="acc-followers">{{ formatNumber(acc.followers) }}</div>
                <div class="acc-growth" :class="Number(accountGrowth[acc.id]) >= 0 ? 'val-green' : 'val-red'">
                  {{ Number(accountGrowth[acc.id]) >= 0 ? '+' : '' }}{{ accountGrowth[acc.id] }}%
                </div>
              </template>
              <div v-else class="acc-followers" style="color: var(--text-tertiary)">—</div>
            </div>
            <span class="acc-status-badge" :class="acc.status === 'connected' ? 'status-ok' : 'status-err'">
              {{ acc.status === 'connected' ? 'Connectada' : 'Desconnectada' }}
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  BarChart2, TrendingUp, Users, Eye, Zap, CheckCircle,
  Target, ChevronRight, AlertCircle, AlertTriangle, Clock, Info, Star, Share2,
} from 'lucide-vue-next'
import {
  socialCampaigns, socialCollaborations,
  socialInfluencers, socialPosts, topPosts, socialAccounts,
  formatNumber, formatCurrency, getPlatform,
} from '@/services/socialCrmData'

const periodFilter   = ref('30d')
const periodOptions  = [
  { value: '7d',  label: '7 dies'  },
  { value: '30d', label: '30 dies' },
  { value: '90d', label: '3 mesos' },
  { value: 'ytd', label: 'Enguany' },
]

const today = new Date().toLocaleDateString('ca-ES', { weekday: 'long', day: 'numeric', month: 'long' })

// ── KPI tiles ─────────────────────────────────────────────────
const kpiTiles = computed(() => {
  const totalSales    = socialCollaborations.reduce((s, c) => s + (c.sales || 0), 0)
  const totalCost     = socialCollaborations.reduce((s, c) => s + (c.cost  || 0), 0)
  const avgRoas       = totalCost ? totalSales / totalCost : 0
  const totalReach    = socialPosts.reduce((s, p) => s + (p.reach || 0), 0)
  const avgEngagement = socialPosts.length
    ? socialPosts.reduce((s, p) => s + (p.engagement || 0), 0) / socialPosts.length : 0

  return [
    {
      key: 'sales', label: 'Vendes atribuïdes',
      formatted: formatCurrency(totalSales),
      sub: `${socialCollaborations.reduce((s, c) => s + (c.conversions || 0), 0)} conversions`,
      icon: TrendingUp, color: '#10B981', colorBg: 'rgba(16,185,129,0.1)',
    },
    {
      key: 'roas', label: 'ROAS mitjà',
      formatted: avgRoas.toFixed(2) + 'x',
      sub: `${socialCampaigns.filter(c => c.status === 'active').length} campanyes actives`,
      icon: Zap, color: '#667eea', colorBg: 'rgba(102,126,234,0.1)',
    },
    {
      key: 'reach', label: 'Abast total',
      formatted: formatNumber(totalReach),
      sub: `${socialPosts.length} publicacions`,
      icon: Eye, color: '#F59E0B', colorBg: 'rgba(245,158,11,0.1)',
    },
    {
      key: 'engagement', label: 'Engagement mitjà',
      formatted: avgEngagement.toFixed(1) + '%',
      sub: `${socialInfluencers.filter(i => i.status === 'active').length} influencers actius`,
      icon: Users, color: '#EC4899', colorBg: 'rgba(236,72,153,0.1)',
    },
  ]
})

// ── Campanyes actives ──────────────────────────────────────────
const activeCampaigns = computed(() =>
  socialCampaigns
    .filter(c => c.status === 'active')
    .sort((a, b) => new Date(a.endDate) - new Date(b.endDate))
    .slice(0, 6)
)

function budgetPct(c) { return c.budget ? (c.cost / c.budget) * 100 : 0 }
function budgetFillClass(c) {
  const p = budgetPct(c)
  if (p > 100) return 'fill-over'
  if (p > 90)  return 'fill-warn'
  return ''
}
function roasClass(v) {
  return v >= 3 ? 'roas-good' : v >= 1 ? 'roas-ok' : 'roas-bad'
}
function daysLeftLabel(endDate) {
  if (!endDate) return '—'
  const days = Math.ceil((new Date(endDate) - new Date()) / 86400000)
  if (days < 0)   return 'Finalitzada'
  if (days === 0) return 'Finalitza avui'
  if (days === 1) return 'Finalitza demà'
  return `${days} dies restants`
}
function daysUrgencyClass(endDate) {
  if (!endDate) return ''
  const days = Math.ceil((new Date(endDate) - new Date()) / 86400000)
  if (days <= 2) return 'days-urgent'
  if (days <= 7) return 'days-warn'
  return ''
}

// ── Accions pendents (basades en dades reals) ──────────────────
const pendingActions = computed(() => {
  const actions = []

  // Comptes desconnectades
  const disconnected = socialAccounts.filter(a => a.status === 'disconnected')
  if (disconnected.length) {
    actions.push({
      id: 'disconnected',
      priority: 'high',
      title: `${disconnected.length} compte${disconnected.length !== 1 ? 's' : ''} desconnectada${disconnected.length !== 1 ? 's' : ''}`,
      sub: disconnected.map(a => a.name).join(', '),
      link: '/social-crm/accounts',
    })
  }

  // Col·laboracions sense mètriques
  const sinMetricas = socialCollaborations.filter(c => c.status === 'active' && (!c.reach || c.reach === 0))
  if (sinMetricas.length) {
    actions.push({
      id: 'metrics',
      priority: 'high',
      title: `${sinMetricas.length} col·laboraci${sinMetricas.length !== 1 ? 'ons' : 'ó'} sense mètriques`,
      sub: 'Pendent de càrrega manual',
      link: '/social-crm/influencers',
    })
  }

  // Campanyes que finalitzen en ≤7 dies
  const expiring = socialCampaigns.filter(c => {
    if (c.status !== 'active') return false
    const days = Math.ceil((new Date(c.endDate) - new Date()) / 86400000)
    return days >= 0 && days <= 7
  })
  expiring.forEach(c => {
    const days = Math.ceil((new Date(c.endDate) - new Date()) / 86400000)
    actions.push({
      id: `exp-${c.id}`,
      priority: days <= 2 ? 'high' : 'medium',
      title: `"${c.name}" finalitza ${days === 0 ? 'avui' : 'd\'aquí a ' + days + (days === 1 ? ' dia' : ' dies')}`,
      sub: 'Revisa el rendiment abans del tancament',
      link: `/social-crm/campaigns?open=${c.id}`,
    })
  })

  // Campanyes al >90% del pressupost
  const overBudget = socialCampaigns.filter(c => c.status === 'active' && budgetPct(c) > 90)
  overBudget.forEach(c => {
    if (expiring.find(e => e.id === c.id)) return
    actions.push({
      id: `budget-${c.id}`,
      priority: 'medium',
      title: `"${c.name}" al ${budgetPct(c).toFixed(0)}% del pressupost`,
      sub: `${formatCurrency(c.cost)} gastat de ${formatCurrency(c.budget)}`,
      link: `/social-crm/campaigns?open=${c.id}`,
    })
  })

  return actions.slice(0, 7)
})

// ── Gràfic de creixement ───────────────────────────────────────

// Historial de seguidors dels últims 6 mesos per compte (dades de demostració)
const FOLLOWER_HISTORY = {
  1: [41200, 43100, 44800, 46200, 47500, 48300],  // Instagram: creixement constant
  4: [16800, 16500, 16100, 15800, 15500, 15200],  // Facebook: lleugera davallada
  5: [3200,  3900,  5200,  6800,  6900,  6700],   // YouTube: pic viral, lleuger ajust
  2: [6200,  9800,  14300, 18200, 21000, 22100],  // TikTok: creixement explosiu
  3: [11400, 10900, 10500, 10200, 9950,  9800],   // X: davallada gradual
}

const MONTH_LABELS = (() => {
  const labels = []
  const now = new Date()
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    labels.push(d.toLocaleDateString('ca-ES', { month: 'short' }).replace('.', ''))
  }
  return labels
})()

const selectedAccountId = ref(null)

const connectedCount = computed(() => socialAccounts.filter(a => a.status === 'connected').length)

// Dades del gràfic: total de totes o una conta concreta
const chartHistory = computed(() => {
  if (selectedAccountId.value === null) {
    return MONTH_LABELS.map((_, i) =>
      socialAccounts.reduce((sum, acc) => sum + (FOLLOWER_HISTORY[acc.id]?.[i] || 0), 0)
    )
  }
  return FOLLOWER_HISTORY[selectedAccountId.value] || []
})

const chartColor = computed(() => {
  if (selectedAccountId.value === null) return '#667eea'
  const acc = socialAccounts.find(a => a.id === selectedAccountId.value)
  return acc ? getPlatform(acc.platform).color : '#667eea'
})

const chartCurrentValue = computed(() => {
  const h = chartHistory.value
  return h.length ? h[h.length - 1] : 0
})
const chartYMin = computed(() => Math.min(...(chartHistory.value.length ? chartHistory.value : [0])))
const chartYMax = computed(() => Math.max(...(chartHistory.value.length ? chartHistory.value : [0])))

const chartGrowthPct = computed(() => {
  const h = chartHistory.value
  if (!h.length || h[0] === 0) return '0.0'
  return ((h[h.length - 1] - h[0]) / h[0] * 100).toFixed(1)
})

const chartDelta = computed(() => {
  const h = chartHistory.value
  return h.length ? h[h.length - 1] - h[0] : 0
})

// Percentatge de creixement per compte (per la llegenda i la taula)
const accountGrowth = computed(() => {
  const result = {}
  for (const acc of socialAccounts) {
    const h = FOLLOWER_HISTORY[acc.id]
    result[acc.id] = h && h.length && h[0] !== 0
      ? ((h[h.length - 1] - h[0]) / h[0] * 100).toFixed(1)
      : '0.0'
  }
  return result
})

// Construcció dels punts i paths SVG
const SVG_W = 600
const SVG_H = 140
const PAD_T = 14
const PAD_B = 14

const chartPoints = computed(() => {
  const h = chartHistory.value
  if (h.length < 2) return []
  const min   = Math.min(...h)
  const max   = Math.max(...h)
  const range = max - min || 1
  const useH  = SVG_H - PAD_T - PAD_B
  return h.map((val, i) => ({
    x: (i / (h.length - 1)) * SVG_W,
    y: PAD_T + (1 - (val - min) / range) * useH,
  }))
})

function smoothPath(pts) {
  if (!pts.length) return ''
  if (pts.length === 1) return `M ${pts[0].x} ${pts[0].y}`
  let d = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const cp = (pts[i - 1].x + pts[i].x) / 2
    d += ` C ${cp} ${pts[i - 1].y} ${cp} ${pts[i].y} ${pts[i].x} ${pts[i].y}`
  }
  return d
}

const chartLinePath = computed(() => smoothPath(chartPoints.value))
const chartAreaPath = computed(() => {
  const pts = chartPoints.value
  if (!pts.length) return ''
  const bottom = SVG_H - PAD_B
  return `${smoothPath(pts)} L ${pts[pts.length - 1].x} ${bottom} L ${pts[0].x} ${bottom} Z`
})

// ── Top publicacions ──────────────────────────────────────────
const topPostsData = computed(() =>
  topPosts.map(id => socialPosts.find(p => p.id === id)).filter(Boolean).slice(0, 4)
)

function platformStyle(key) {
  const p = getPlatform(key)
  return { background: p.bg, color: p.color }
}
function engClass(v) {
  return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low'
}
</script>

<style scoped>
/* ── Base ────────────────────────────────────────────── */
.summary-view {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding-bottom: var(--spacing-xl);
}

/* ── Capçalera ──────────────────────────────────────── */
.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}
.header-left { display: flex; align-items: center; gap: 0.85rem; }
.title-icon {
  width: 46px; height: 46px;
  border-radius: 13px;
  display: grid; place-items: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(102,126,234,.35);
}
.view-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}
.view-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 3px 0 0;
  text-transform: capitalize;
}
.period-tabs {
  display: flex;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 3px;
  gap: 2px;
}
.period-btn {
  padding: 0.4rem 0.9rem;
  border: none;
  border-radius: calc(var(--border-radius-sm) - 2px);
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
  white-space: nowrap;
}
.period-btn:hover { color: var(--text-primary); }
.period-btn.active {
  background: var(--bg-primary);
  color: var(--primary-color);
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,.1);
}

/* ── KPI strip ──────────────────────────────────────── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}
.kpi-tile {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-top: 3px solid var(--accent, var(--primary-color));
  border-radius: var(--border-radius);
  padding: 1.1rem 1.25rem;
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}
.kpi-tile:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.08); }
.kpi-icon-wrap {
  width: 44px; height: 44px;
  border-radius: 11px;
  display: grid; place-items: center;
  flex-shrink: 0;
}
.kpi-body { min-width: 0; flex: 1; }
.kpi-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}
.kpi-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -.02em;
  line-height: 1.1;
  font-feature-settings: "tnum";
}
.kpi-sub { font-size: 0.8rem; color: var(--text-tertiary); margin-top: 5px; }

/* ── Graella principal ──────────────────────────────── */
.main-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: var(--spacing-lg);
  align-items: start;
}
.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}

/* ── Card base ──────────────────────────────────────── */
.card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}
.card-head-left { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
.section-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: grid; place-items: center;
  flex-shrink: 0;
}
.section-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.card-action {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.8rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  transition: opacity var(--transition-fast);
  flex-shrink: 0;
}
.card-action:hover { opacity: .75; }

/* Pills i badges */
.count-pill {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 22px; height: 22px; padding: 0 6px;
  border-radius: 999px; font-size: 0.72rem; font-weight: 700; line-height: 1;
}
.count-pill.primary { background: var(--primary-light); color: var(--primary-color); }
.count-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 22px; height: 22px; padding: 0 5px;
  border-radius: 999px; background: #EF4444; color: white;
  font-size: 0.72rem; font-weight: 700; line-height: 1;
}
.period-badge {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 2px 8px;
  border-radius: 999px;
}

/* ── Campanyes ──────────────────────────────────────── */
.campaign-list { display: flex; flex-direction: column; }
.camp-row {
  display: grid;
  grid-template-columns: 1fr 200px 80px;
  gap: 1rem;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  text-decoration: none;
  transition: background var(--transition-fast);
}
.camp-row:last-child { border-bottom: none; }
.camp-row:hover { background: var(--bg-secondary); }
.camp-name {
  font-size: 0.925rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.camp-tags { display: flex; align-items: center; gap: 6px; margin-top: 5px; flex-wrap: wrap; }
.camp-obj-tag {
  font-size: 0.72rem; font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  padding: 1px 7px; border-radius: 4px;
}
.camp-days-tag {
  display: flex; align-items: center; gap: 3px;
  font-size: 0.72rem; font-weight: 500; color: var(--text-tertiary);
}
.camp-days-tag.days-warn   { color: #F59E0B; }
.camp-days-tag.days-urgent { color: #EF4444; font-weight: 700; }

.camp-budget-block { display: flex; flex-direction: column; gap: 5px; }
.camp-budget-nums {
  display: flex; align-items: baseline; gap: 3px;
  font-size: 0.8rem; font-feature-settings: "tnum";
}
.camp-spent { font-weight: 600; color: var(--text-primary); }
.camp-of    { color: var(--text-tertiary); }
.camp-pct   { margin-left: auto; font-weight: 700; font-size: 0.72rem; color: var(--text-secondary); }
.camp-pct.fill-warn { color: #F59E0B; }
.camp-pct.fill-over { color: #EF4444; }
.budget-bar-wrap { height: 5px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.budget-bar-fill {
  height: 100%; background: var(--primary-color);
  border-radius: 3px; transition: width .4s ease;
}
.budget-bar-fill.fill-warn { background: #F59E0B; }
.budget-bar-fill.fill-over { background: #EF4444; }
.camp-roas-block { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.roas-badge {
  font-size: 0.85rem; font-weight: 700;
  padding: 3px 10px; border-radius: 7px;
  font-feature-settings: "tnum";
}
.roas-good { background: rgba(16,185,129,.12); color: #10B981; }
.roas-ok   { background: rgba(245,158,11,.12); color: #F59E0B; }
.roas-bad  { background: rgba(239,68,68,.1);   color: #EF4444; }
.camp-roas-label { font-size: 0.62rem; text-transform: uppercase; letter-spacing: .06em; color: var(--text-tertiary); }

/* ── Pendents ───────────────────────────────────────── */
.pending-list { display: flex; flex-direction: column; }
.pending-row {
  display: flex; align-items: flex-start;
  gap: 0.6rem; padding: 0.8rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  transition: background var(--transition-fast);
}
.pending-row:last-child { border-bottom: none; }
.pending-row:hover { background: var(--bg-secondary); }
.pending-icon-wrap {
  width: 26px; height: 26px; border-radius: 7px;
  display: grid; place-items: center; flex-shrink: 0; margin-top: 1px;
}
.pending-icon-wrap.pri-high   { background: rgba(239,68,68,.12); color: #EF4444; }
.pending-icon-wrap.pri-medium { background: rgba(245,158,11,.12); color: #F59E0B; }
.pending-icon-wrap.pri-low    { background: rgba(59,130,246,.12); color: #3B82F6; }
.pending-body { flex: 1; min-width: 0; }
.pending-title { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); line-height: 1.3; }
.pending-sub {
  font-size: 0.78rem; color: var(--text-tertiary); margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pending-link { font-size: 0.78rem; color: var(--primary-color); text-decoration: none; font-weight: 600; flex-shrink: 0; margin-top: 3px; }
.pending-ok {
  display: flex; align-items: center; gap: 8px;
  padding: 1rem 1.25rem;
  font-size: 0.875rem; color: #10B981; font-weight: 500;
}

/* ── Gràfic de creixement ───────────────────────────── */
.growth-card { overflow: visible; }
.growth-head { flex-wrap: wrap; gap: 0.75rem; }
.account-filter {
  display: flex; align-items: center;
  gap: 4px; flex-wrap: wrap;
}
.acc-btn {
  padding: 0.3rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
  white-space: nowrap;
}
.acc-btn:hover { color: var(--text-primary); border-color: var(--text-secondary); }
.acc-btn.active {
  font-weight: 600;
  box-shadow: 0 1px 4px rgba(0,0,0,.1);
  /* Per defecte botó "Totes"; els botons de comptes sobreescriuen amb inline style */
  background: var(--primary-light);
  color: var(--primary-color);
  border-color: rgba(102,126,234,.5);
}

.growth-stats {
  display: flex;
  align-items: center;
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  gap: 0;
}
.gs-item { padding: 0 1.5rem; text-align: center; }
.gs-item:first-child { padding-left: 0; text-align: left; }
.gs-val {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.15;
}
.gs-label { font-size: 0.78rem; color: var(--text-tertiary); margin-top: 2px; }
.gs-divider { width: 1px; background: var(--border-color); align-self: stretch; }

.val-green { color: #10B981; }
.val-red   { color: #EF4444; }

/* Chart */
.chart-body {
  display: flex;
  padding: 0.75rem 1.25rem 0;
  gap: 0.5rem;
  align-items: stretch;
}
.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 58px;
  flex-shrink: 0;
  padding-bottom: 24px;
  text-align: right;
}
.chart-y-axis span { font-size: 0.7rem; color: var(--text-tertiary); font-feature-settings: "tnum"; }
.chart-main { flex: 1; min-width: 0; }
.growth-svg {
  width: 100%;
  height: 140px;
  display: block;
}
.grid-line { stroke: var(--border-color); stroke-width: 1; }
.chart-area-path { opacity: .12; }
.chart-line-path { fill: none; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }
.chart-svg-wrap { position: relative; height: 140px; width: 100%; }
.chart-dot-html {
  position: absolute;
  width: 8px; height: 8px;
  border-radius: 50%;
  border: 2px solid white;
  transform: translate(-50%, -50%);
  pointer-events: none;
  box-shadow: 0 0 0 1px rgba(0,0,0,.08);
}
.chart-x-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 0 0.75rem;
  margin-top: 4px;
}
.chart-x-labels span { font-size: 0.72rem; color: var(--text-tertiary); text-transform: capitalize; }

/* Llegenda */
.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-name { font-size: 0.78rem; color: var(--text-secondary); }
.legend-val { font-size: 0.78rem; font-weight: 600; color: var(--text-primary); font-feature-settings: "tnum"; }
.legend-growth { font-size: 0.72rem; font-weight: 600; }

/* ── Millors publicacions ───────────────────────────── */
.posts-list { display: flex; flex-direction: column; }
.post-row {
  display: flex; align-items: center;
  gap: 0.75rem; padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  transition: background var(--transition-fast);
}
.post-row:last-child { border-bottom: none; }
.post-row:hover { background: var(--bg-secondary); }
.post-rank {
  width: 26px; height: 26px; border-radius: 7px;
  display: grid; place-items: center;
  font-size: 0.78rem; font-weight: 700;
  flex-shrink: 0;
  background: var(--bg-secondary); color: var(--text-secondary);
}
.rank-1 { background: rgba(251,191,36,.18); color: #B45309; }
.rank-2 { background: rgba(156,163,175,.2);  color: #6B7280; }
.rank-3 { background: rgba(180,125,74,.15);  color: #92400E; }
.post-info { flex: 1; min-width: 0; }
.post-title {
  font-size: 0.875rem; font-weight: 500; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.post-meta { display: flex; align-items: center; gap: 0.5rem; margin-top: 4px; flex-wrap: wrap; }
.plat-pill { font-size: 0.68rem; font-weight: 600; padding: 2px 7px; border-radius: 999px; }
.post-stat { font-size: 0.78rem; color: var(--text-tertiary); font-feature-settings: "tnum"; }
.eng-pill { font-size: 0.78rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; flex-shrink: 0; }
.eng-high { background: rgba(16,185,129,.1); color: #10B981; }
.eng-mid  { background: rgba(245,158,11,.1); color: #F59E0B; }
.eng-low  { background: rgba(239,68,68,.08); color: #EF4444; }

/* ── Estat de les comptes ───────────────────────────── */
.accounts-list { display: flex; flex-direction: column; }
.acc-row {
  display: flex; align-items: center;
  gap: 0.75rem; padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  transition: background var(--transition-fast);
}
.acc-row:last-child { border-bottom: none; }
.acc-row:hover { background: var(--bg-secondary); }
.acc-platform-icon {
  width: 34px; height: 34px; border-radius: 9px;
  display: grid; place-items: center;
  font-size: 0.8rem; font-weight: 700;
  flex-shrink: 0;
}
.acc-info { flex: 1; min-width: 0; }
.acc-name {
  font-size: 0.875rem; font-weight: 600; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.acc-username { font-size: 0.75rem; color: var(--text-tertiary); margin-top: 1px; }
.acc-metrics { text-align: right; flex-shrink: 0; }
.acc-followers { font-size: 0.925rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.acc-growth { font-size: 0.72rem; font-weight: 600; margin-top: 1px; }
.acc-status-badge {
  font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .04em;
  padding: 3px 8px; border-radius: 999px;
  flex-shrink: 0;
}
.status-ok  { background: rgba(16,185,129,.1); color: #10B981; }
.status-err { background: rgba(239,68,68,.1);  color: #EF4444; }

/* ── Estat buit ──────────────────────────────────────── */
.empty-state-sm {
  padding: 2rem 1.25rem;
  display: flex; flex-direction: column;
  align-items: center; gap: 8px;
  color: var(--text-tertiary);
}
.empty-state-sm svg { opacity: .3; }
.empty-state-sm p { font-size: 0.875rem; margin: 0; }

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 1200px) {
  .main-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 1024px) {
  .main-grid   { grid-template-columns: 1fr; }
  .bottom-grid { grid-template-columns: 1fr; }
  .kpi-strip   { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 720px) {
  .kpi-strip    { grid-template-columns: 1fr 1fr; }
  .camp-row     { grid-template-columns: 1fr; gap: 0.5rem; }
  .period-tabs  { flex-wrap: wrap; }
  .account-filter { justify-content: flex-start; }
}
</style>
