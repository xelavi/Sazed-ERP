<template>
  <div class="social-dashboard-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Social CRM</h1>
          <span class="subtitle">Dashboard general</span>
        </div>
        <div class="header-actions">
          <select class="select filter-select" v-model="periodFilter">
            <option value="7d">Últimos 7 días</option>
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 3 meses</option>
            <option value="ytd">Este año</option>
          </select>
          <select class="select filter-select" v-model="platformFilter">
            <option value="all">Todas las redes</option>
            <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
          </select>
          <select class="select filter-select" v-model="campaignFilter">
            <option value="all">Todas las campañas</option>
            <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <button class="btn btn-secondary">
            <Download :size="18" />
            <span>Exportar</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="card kpi-card" v-for="(kpi, key) in dashboardKPIs" :key="key">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">
            <span v-if="key === 'attributedSales'">{{ formatCurrency(kpi.value) }}</span>
            <span v-else-if="key === 'avgEngagement'">{{ kpi.value }}%</span>
            <span v-else>{{ formatNumber(kpi.value) }}</span>
          </div>
          <div class="kpi-change" :class="kpi.change >= 0 ? 'positive' : 'negative'">
            <TrendingUp v-if="kpi.change >= 0" :size="14" />
            <TrendingDown v-else :size="14" />
            {{ kpi.change >= 0 ? '+' : '' }}{{ kpi.change }}%
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <!-- Evolution Chart (CSS-based) -->
        <div class="card chart-card">
          <div class="card-header">
            <h3 class="card-title">Evolución</h3>
            <div class="chart-legend">
              <span v-for="m in chartMetrics" :key="m.key"
                class="legend-item"
                :class="{ active: activeMetric === m.key }"
                @click="activeMetric = m.key">
                <span class="legend-dot" :style="{ background: m.color }"></span>
                {{ m.label }}
              </span>
            </div>
          </div>
          <div class="chart-area">
            <div class="bar-chart">
              <div
                v-for="(val, i) in currentChartData"
                :key="i"
                class="bar-group">
                <div class="bar-wrap">
                  <div
                    class="bar"
                    :style="{
                      height: barHeight(val) + '%',
                      background: activeChartMetric.color
                    }">
                  </div>
                </div>
                <span class="bar-label">{{ evolutionData.labels[i] }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Alerts panel -->
        <div class="card alerts-card">
          <div class="card-header">
            <h3 class="card-title">Alertas activas</h3>
            <router-link to="/social-crm/alerts" class="card-link">Ver todas</router-link>
          </div>
          <div class="alerts-list">
            <div
              v-for="alert in pendingAlerts"
              :key="alert.id"
              class="alert-item"
              :class="'severity-' + alert.severity">
              <div class="alert-severity-dot"></div>
              <div class="alert-info">
                <div class="alert-desc">{{ alert.description }}</div>
                <div class="alert-entity">{{ alert.entity }}</div>
              </div>
              <span class="badge" :class="severityClass(alert.severity)">{{ alert.severity }}</span>
            </div>
            <div v-if="!pendingAlerts.length" class="empty-state-sm">Sin alertas activas</div>
          </div>
        </div>

        <!-- Top content ranking -->
        <div class="card ranking-card">
          <div class="card-header">
            <h3 class="card-title">Top 5 publicaciones</h3>
            <router-link to="/social-crm/posts" class="card-link">Ver todas</router-link>
          </div>
          <div class="ranking-list">
            <div
              v-for="(post, i) in topPostsData"
              :key="post.id"
              class="ranking-item"
              @click="$router.push('/social-crm/posts/' + post.id)">
              <span class="rank-num">{{ i + 1 }}</span>
              <div class="rank-info">
                <div class="rank-title">{{ post.title }}</div>
                <div class="rank-meta">
                  <span class="platform-badge" :style="platformStyle(post.platform)">{{ getPlatform(post.platform).label }}</span>
                  <span class="meta-stat"><Heart :size="12" /> {{ formatNumber(post.likes) }}</span>
                  <span class="meta-stat"><Eye :size="12" /> {{ formatNumber(post.reach) }}</span>
                </div>
              </div>
              <span class="eng-badge">{{ post.engagement }}%</span>
            </div>
          </div>
        </div>

        <!-- Influencers summary -->
        <div class="card influencers-card">
          <div class="card-header">
            <h3 class="card-title">Colaboraciones</h3>
            <router-link to="/social-crm/collaborations" class="card-link">Ver todas</router-link>
          </div>
          <div class="collab-summary">
            <div class="collab-stat">
              <span class="stat-num">{{ activeCollabs }}</span>
              <span class="stat-label">Activas</span>
            </div>
            <div class="collab-stat">
              <span class="stat-num">{{ pendingMetrics }}</span>
              <span class="stat-label">Sin métricas</span>
            </div>
            <div class="collab-stat">
              <span class="stat-num">{{ completedCollabs }}</span>
              <span class="stat-label">Completadas</span>
            </div>
          </div>
          <div class="best-influencer">
            <span class="best-label">Mejor colaboración del periodo:</span>
            <div class="best-item">
              <div class="influencer-avatar">{{ bestCollab?.influencerName[0] }}</div>
              <div>
                <div class="best-name">{{ bestCollab?.influencerName }}</div>
                <div class="best-stats">{{ formatCurrency(bestCollab?.sales ?? 0) }} en ventas · {{ bestCollab?.conversions }} conversiones</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { TrendingUp, TrendingDown, Download, Heart, Eye } from 'lucide-vue-next'
import {
  dashboardKPIs, evolutionData, socialCampaigns, socialCollaborations, socialAlerts,
  socialPosts, topPosts, PLATFORMS, formatNumber, formatCurrency, getPlatform
} from '@/services/socialCrmData'

const periodFilter   = ref('30d')
const platformFilter = ref('all')
const campaignFilter = ref('all')
const activeMetric   = ref('followers')

const chartMetrics = [
  { key: 'followers',    label: 'Seguidores',   color: '#667eea' },
  { key: 'reach',        label: 'Alcance',      color: '#10B981' },
  { key: 'engagement',   label: 'Engagement',   color: '#F59E0B' },
  { key: 'conversions',  label: 'Conversiones', color: '#EC4899' },
]

const activeChartMetric = computed(() => chartMetrics.find(m => m.key === activeMetric.value))
const currentChartData  = computed(() => evolutionData[activeMetric.value])

function barHeight(val) {
  const arr = currentChartData.value
  const max = Math.max(...arr)
  return max ? (val / max) * 90 : 0
}

const pendingAlerts = computed(() => socialAlerts.filter(a => a.status === 'pending').slice(0, 4))

function severityClass(s) {
  return s === 'high' ? 'badge-error' : s === 'medium' ? 'badge-warning' : 'badge-info'
}

const topPostsData = computed(() =>
  topPosts.map(id => socialPosts.find(p => p.id === id)).filter(Boolean)
)

function platformStyle(key) {
  const p = getPlatform(key)
  return { background: p.bg, color: p.color, border: `1px solid ${p.color}30` }
}

const activeCollabs    = computed(() => socialCollaborations.filter(c => c.status === 'active').length)
const completedCollabs = computed(() => socialCollaborations.filter(c => c.status === 'completed').length)
const pendingMetrics   = computed(() => socialCollaborations.filter(c => c.status === 'active' && c.reach === 0).length)
const bestCollab       = computed(() => [...socialCollaborations].sort((a, b) => b.sales - a.sales)[0])
</script>

<style scoped>
.social-dashboard-view { display: flex; flex-direction: column; height: 100%; }

.view-header {
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}
.header-content { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--spacing-md); }
.title-section { display: flex; align-items: baseline; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.subtitle { font-size: 0.875rem; color: var(--text-secondary); }
.header-actions { display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap; }

.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-lg); }

/* KPI Grid */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: var(--spacing-md); }
.kpi-card { padding: var(--spacing-md) var(--spacing-lg); }
.kpi-label { font-size: 0.75rem; color: var(--text-secondary); margin-bottom: var(--spacing-xs); text-transform: uppercase; letter-spacing: 0.04em; }
.kpi-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.kpi-change { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; font-weight: 600; }
.kpi-change.positive { color: #10B981; }
.kpi-change.negative { color: #EF4444; }

/* Dashboard grid */
.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg); }
@media (max-width: 900px) { .dashboard-grid { grid-template-columns: 1fr; } }

.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.card-link { font-size: 0.8rem; color: var(--primary-color); text-decoration: none; }
.card-link:hover { text-decoration: underline; }

/* Chart */
.chart-card { grid-column: 1 / 3; }
@media (max-width: 900px) { .chart-card { grid-column: 1; } }

.chart-legend { display: flex; gap: var(--spacing-md); flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; padding: 4px 8px; border-radius: 6px; transition: background 0.15s; }
.legend-item.active { background: var(--bg-secondary); color: var(--text-primary); font-weight: 600; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

.chart-area { padding: var(--spacing-lg); }
.bar-chart { display: flex; align-items: flex-end; gap: var(--spacing-lg); height: 160px; }
.bar-group { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.bar-wrap { flex: 1; display: flex; align-items: flex-end; width: 100%; }
.bar { width: 100%; min-height: 4px; border-radius: 4px 4px 0 0; transition: height 0.4s ease; }
.bar-label { font-size: 0.75rem; color: var(--text-secondary); }

/* Alerts */
.alerts-list { padding: var(--spacing-sm); display: flex; flex-direction: column; gap: 6px; }
.alert-item { display: flex; align-items: flex-start; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border-radius: 8px; background: var(--bg-secondary); cursor: default; }
.alert-severity-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.severity-high .alert-severity-dot { background: #EF4444; }
.severity-medium .alert-severity-dot { background: #F59E0B; }
.severity-low .alert-severity-dot { background: #3B82F6; }
.alert-info { flex: 1; min-width: 0; }
.alert-desc { font-size: 0.8rem; color: var(--text-primary); line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.alert-entity { font-size: 0.75rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty-state-sm { padding: var(--spacing-md); text-align: center; color: var(--text-secondary); font-size: 0.85rem; }

/* Ranking */
.ranking-list { padding: var(--spacing-sm); display: flex; flex-direction: column; gap: 6px; }
.ranking-item { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border-radius: 8px; cursor: pointer; transition: background 0.15s; }
.ranking-item:hover { background: var(--bg-secondary); }
.rank-num { width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: 50%; font-size: 0.75rem; font-weight: 700; color: var(--text-secondary); flex-shrink: 0; }
.rank-info { flex: 1; min-width: 0; }
.rank-title { font-size: 0.82rem; color: var(--text-primary); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-meta { display: flex; align-items: center; gap: var(--spacing-sm); margin-top: 3px; flex-wrap: wrap; }
.platform-badge { font-size: 0.7rem; padding: 2px 6px; border-radius: 10px; font-weight: 600; }
.meta-stat { display: flex; align-items: center; gap: 3px; font-size: 0.75rem; color: var(--text-secondary); }
.eng-badge { font-size: 0.8rem; font-weight: 700; color: var(--primary-color); flex-shrink: 0; }

/* Collaborations summary */
.collab-summary { display: flex; gap: var(--spacing-lg); padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.collab-stat { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-num { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 0.75rem; color: var(--text-secondary); text-align: center; }
.best-influencer { padding: var(--spacing-md) var(--spacing-lg); }
.best-label { font-size: 0.75rem; color: var(--text-secondary); display: block; margin-bottom: var(--spacing-sm); }
.best-item { display: flex; align-items: center; gap: var(--spacing-md); }
.influencer-avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
.best-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.best-stats { font-size: 0.8rem; color: var(--text-secondary); }

.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
</style>
