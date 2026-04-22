<template>
  <div class="analytics-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Analítica</h1>
        </div>
        <div class="header-actions">
          <div class="tab-toggle">
            <button :class="['tab-btn', { active: tab === 'content' }]" @click="tab = 'content'">Contenido</button>
            <button :class="['tab-btn', { active: tab === 'influencers' }]" @click="tab = 'influencers'">Influencers</button>
          </div>
          <select class="select" v-model="periodFilter">
            <option value="30d">Últimos 30 días</option>
            <option value="90d">Últimos 3 meses</option>
            <option value="ytd">Este año</option>
          </select>
          <select class="select" v-model="campaignFilter">
            <option value="all">Todas las campañas</option>
            <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- CONTENT ANALYTICS -->
      <template v-if="tab === 'content'">
        <div class="section-title">Rendimiento por formato de contenido</div>
        <div class="bar-compare-grid">
          <div class="card compare-card" v-for="fmt in contentByFormat" :key="fmt.type">
            <div class="fmt-header">
              <span class="badge badge-info">{{ fmt.type }}</span>
              <span class="fmt-count">{{ fmt.count }} posts</span>
            </div>
            <div class="fmt-stats">
              <div class="fmt-stat"><span class="stat-val">{{ fmt.engagement.toFixed(1) }}%</span><span class="stat-key">Eng.</span></div>
              <div class="fmt-stat"><span class="stat-val">{{ formatNumber(fmt.avgReach) }}</span><span class="stat-key">Alcance</span></div>
              <div class="fmt-stat"><span class="stat-val">{{ formatNumber(fmt.avgClicks) }}</span><span class="stat-key">Clics</span></div>
            </div>
            <div class="eng-bar-wrap">
              <div class="eng-bar" :style="{ width: Math.min(fmt.engagement * 10, 100) + '%', background: engColor(fmt.engagement) }"></div>
            </div>
          </div>
        </div>

        <div class="two-col">
          <div class="card">
            <div class="card-header"><h3 class="card-title">Rendimiento por red social</h3></div>
            <div class="platform-table">
              <div class="pt-row pt-header">
                <span>Red</span>
                <span class="text-right">Posts</span>
                <span class="text-right">Eng. medio</span>
                <span class="text-right">Alcance total</span>
                <span class="text-right">Clics</span>
              </div>
              <div class="pt-row" v-for="plt in contentByPlatform" :key="plt.platform">
                <span><span class="platform-pill" :style="platformStyle(plt.platform)">{{ getPlatform(plt.platform).label }}</span></span>
                <span class="text-right text-sm">{{ plt.posts }}</span>
                <span class="text-right" :class="engClass(plt.engagement)">{{ plt.engagement.toFixed(1) }}%</span>
                <span class="text-right font-medium">{{ formatNumber(plt.totalReach) }}</span>
                <span class="text-right text-sm">{{ formatNumber(plt.totalClicks) }}</span>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header"><h3 class="card-title">Rendimiento por franja horaria (publicación)</h3></div>
            <div class="hour-chart">
              <div v-for="slot in timeSlots" :key="slot.label" class="hour-row">
                <span class="hour-label">{{ slot.label }}</span>
                <div class="hour-bar-wrap">
                  <div class="hour-bar" :style="{ width: (slot.engagement / maxSlotEng * 100) + '%' }"></div>
                </div>
                <span class="hour-val">{{ slot.engagement.toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- INFLUENCER ANALYTICS -->
      <template v-if="tab === 'influencers'">
        <div class="section-title">Comparativa de influencers</div>
        <div class="card table-card">
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Influencer</th>
                  <th class="text-right">Alcance</th>
                  <th class="text-right">Engagement</th>
                  <th class="text-right">Clics</th>
                  <th class="text-right">Conversiones</th>
                  <th class="text-right">Ventas</th>
                  <th class="text-right">Coste</th>
                  <th class="text-right">CPA</th>
                  <th class="text-right">ROAS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inf in influencerStats" :key="inf.id">
                  <td>
                    <div class="inf-cell">
                      <div class="small-avatar">{{ inf.name[0] }}</div>
                      <div>
                        <div class="inf-name">{{ inf.name }}</div>
                        <div class="inf-alias">{{ inf.alias }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="text-right">{{ formatNumber(inf.totalReach) }}</td>
                  <td class="text-right"><span :class="engClass(inf.avgEngagement)">{{ inf.avgEngagement.toFixed(1) }}%</span></td>
                  <td class="text-right">{{ formatNumber(inf.totalClicks) }}</td>
                  <td class="text-right">{{ inf.totalConversions }}</td>
                  <td class="text-right font-medium">{{ formatCurrency(inf.totalSales) }}</td>
                  <td class="text-right">{{ formatCurrency(inf.totalCost) }}</td>
                  <td class="text-right">{{ inf.totalConversions ? formatCurrency(inf.totalCost / inf.totalConversions) : '—' }}</td>
                  <td class="text-right"><span :class="inf.roas >= 3 ? 'roas-good' : inf.roas >= 1 ? 'roas-ok' : 'roas-bad'">{{ inf.roas.toFixed(2) }}x</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="two-col">
          <div class="card">
            <div class="card-header"><h3 class="card-title">Ranking por ventas generadas</h3></div>
            <div class="ranking-list">
              <div v-for="(inf, i) in influencersByRanking" :key="inf.id" class="rank-row">
                <span class="rank-num">{{ i + 1 }}</span>
                <div class="rank-info">
                  <div class="rank-name">{{ inf.name }}</div>
                  <div class="rank-bar-wrap">
                    <div class="rank-bar" :style="{ width: (inf.totalSales / maxSales * 100) + '%' }"></div>
                  </div>
                </div>
                <span class="rank-val">{{ formatCurrency(inf.totalSales) }}</span>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="card-header"><h3 class="card-title">Dispersión coste vs. ventas</h3></div>
            <div class="scatter-note">
              <BarChart2 :size="32" class="scatter-icon" />
              <span>Visualización disponible próximamente con integración de gráficos</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { BarChart2 } from 'lucide-vue-next'
import { socialPosts, socialCampaigns, socialInfluencers, socialCollaborations, getPlatform, formatNumber, formatCurrency } from '@/services/socialCrmData'

const tab            = ref('content')
const periodFilter   = ref('30d')
const campaignFilter = ref('all')

// Content by format
const contentByFormat = computed(() => {
  const map = {}
  socialPosts.forEach(p => {
    if (!map[p.type]) map[p.type] = { type: p.type, count: 0, totalEng: 0, totalReach: 0, totalClicks: 0 }
    map[p.type].count++
    map[p.type].totalEng   += p.engagement
    map[p.type].totalReach += p.reach
    map[p.type].totalClicks += p.clicks
  })
  return Object.values(map).map(m => ({
    ...m,
    engagement: m.totalEng / m.count,
    avgReach:   Math.round(m.totalReach / m.count),
    avgClicks:  Math.round(m.totalClicks / m.count),
  })).sort((a, b) => b.engagement - a.engagement)
})

// Content by platform
const contentByPlatform = computed(() => {
  const map = {}
  socialPosts.forEach(p => {
    if (!map[p.platform]) map[p.platform] = { platform: p.platform, posts: 0, totalEng: 0, totalReach: 0, totalClicks: 0 }
    map[p.platform].posts++
    map[p.platform].totalEng   += p.engagement
    map[p.platform].totalReach += p.reach
    map[p.platform].totalClicks += p.clicks
  })
  return Object.values(map).map(m => ({
    ...m, engagement: m.totalEng / m.posts,
  })).sort((a, b) => b.totalReach - a.totalReach)
})

// Simulated time slots
const timeSlots = [
  { label: '00–06h', engagement: 2.1 }, { label: '06–09h', engagement: 3.4 },
  { label: '09–12h', engagement: 5.8 }, { label: '12–15h', engagement: 6.4 },
  { label: '15–18h', engagement: 5.1 }, { label: '18–21h', engagement: 7.2 },
  { label: '21–00h', engagement: 4.8 },
]
const maxSlotEng = computed(() => Math.max(...timeSlots.map(s => s.engagement)))

// Influencer stats from collaborations
const influencerStats = computed(() => {
  return socialInfluencers.map(inf => {
    const collabs = socialCollaborations.filter(c => c.influencerId === inf.id)
    const totalReach       = collabs.reduce((s, c) => s + c.reach, 0)
    const totalClicks      = collabs.reduce((s, c) => s + c.clicks, 0)
    const totalConversions = collabs.reduce((s, c) => s + c.conversions, 0)
    const totalSales       = collabs.reduce((s, c) => s + c.sales, 0)
    const totalCost        = collabs.reduce((s, c) => s + c.cost, 0)
    return {
      ...inf,
      totalReach, totalClicks, totalConversions, totalSales, totalCost,
      avgEngagement: inf.engagementMid,
      roas: totalCost ? totalSales / totalCost : 0,
    }
  }).filter(i => i.totalCost > 0)
})

const influencersByRanking = computed(() => [...influencerStats.value].sort((a, b) => b.totalSales - a.totalSales))
const maxSales = computed(() => Math.max(...influencersByRanking.value.map(i => i.totalSales), 1))

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function engColor(v) { return v >= 6 ? '#10B981' : v >= 3 ? '#F59E0B' : '#EF4444' }
</script>

<style scoped>
.analytics-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); flex-wrap: wrap; }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.header-actions { display: flex; align-items: center; gap: var(--spacing-sm); flex-wrap: wrap; }
.tab-toggle { display: flex; background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: 3px; }
.tab-btn { padding: 6px 16px; border: none; background: none; border-radius: 6px; cursor: pointer; font-size: 0.875rem; color: var(--text-secondary); transition: all 0.15s; }
.tab-btn.active { background: var(--bg-primary); color: var(--text-primary); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-lg); }
.section-title { font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.05em; }
.bar-compare-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--spacing-md); }
.compare-card { padding: var(--spacing-md); }
.fmt-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--spacing-sm); }
.fmt-count { font-size: 0.75rem; color: var(--text-secondary); }
.fmt-stats { display: flex; justify-content: space-between; margin-bottom: var(--spacing-sm); }
.fmt-stat { display: flex; flex-direction: column; align-items: center; }
.stat-val { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); }
.stat-key { font-size: 0.72rem; color: var(--text-secondary); }
.eng-bar-wrap { height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.eng-bar { height: 100%; border-radius: 3px; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.platform-table { padding: var(--spacing-sm); }
.pt-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr 1fr; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border-bottom: 1px solid var(--border-color); font-size: 0.85rem; align-items: center; }
.pt-header { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; }
.platform-pill { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; }
.hour-chart { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: 8px; }
.hour-row { display: flex; align-items: center; gap: var(--spacing-sm); }
.hour-label { font-size: 0.8rem; color: var(--text-secondary); min-width: 60px; }
.hour-bar-wrap { flex: 1; height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden; }
.hour-bar { height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 4px; }
.hour-val { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); min-width: 36px; text-align: right; }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.inf-cell { display: flex; align-items: center; gap: var(--spacing-sm); }
.small-avatar { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.78rem; flex-shrink: 0; }
.inf-name { font-weight: 600; font-size: 0.85rem; color: var(--text-primary); }
.inf-alias { font-size: 0.75rem; color: var(--text-secondary); }
.text-right { text-align: right; }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.eng-high { color: #10B981; font-weight: 700; }
.eng-mid  { color: #F59E0B; font-weight: 700; }
.eng-low  { color: #EF4444; font-weight: 700; }
.roas-good { color: #10B981; font-weight: 700; }
.roas-ok   { color: #F59E0B; font-weight: 700; }
.roas-bad  { color: #EF4444; font-weight: 700; }
.ranking-list { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: 10px; }
.rank-row { display: flex; align-items: center; gap: var(--spacing-sm); }
.rank-num { width: 22px; height: 22px; display: flex; align-items: center; justify-content: center; background: var(--bg-secondary); border-radius: 50%; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }
.rank-info { flex: 1; }
.rank-name { font-size: 0.85rem; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
.rank-bar-wrap { height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.rank-bar { height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 3px; }
.rank-val { font-size: 0.85rem; font-weight: 700; color: var(--text-primary); min-width: 80px; text-align: right; }
.scatter-note { padding: var(--spacing-xl); display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm); color: var(--text-secondary); text-align: center; font-size: 0.85rem; }
.scatter-icon { color: var(--text-secondary); }
</style>
