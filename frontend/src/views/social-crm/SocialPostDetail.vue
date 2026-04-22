<template>
  <div class="post-detail-view">
    <div class="view-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/social-crm/posts" class="breadcrumb-link">Publicaciones</router-link>
          <ChevronRight :size="16" class="breadcrumb-sep" />
          <span class="breadcrumb-current">Detalle</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" /><span>Exportar fila</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="post" class="content-wrapper">
      <div class="detail-grid">
        <!-- Summary + Preview -->
        <div class="left-col">
          <div class="card summary-card">
            <div class="summary-header">
              <span class="platform-pill" :style="platformStyle(post.platform)">{{ getPlatform(post.platform).label }}</span>
              <span class="badge badge-info">{{ post.type }}</span>
              <span class="date-label">{{ formatDate(post.date) }}</span>
            </div>
            <h2 class="post-title">{{ post.title }}</h2>
            <div class="meta-row">
              <span class="meta-item"><span class="meta-key">Cuenta:</span> {{ post.accountName }}</span>
              <span class="meta-item"><span class="meta-key">Campaña:</span> {{ post.campaignName || '—' }}</span>
              <span class="meta-item"><span class="meta-key">Producto:</span> {{ post.productName || '—' }}</span>
            </div>
            <!-- Simulated preview placeholder -->
            <div class="post-preview">
              <div class="preview-placeholder">
                <ImageIcon :size="32" class="preview-icon" />
                <span>Vista previa del contenido</span>
                <a href="#" class="preview-link" @click.prevent>Ver post original <ExternalLink :size="12" /></a>
              </div>
            </div>
          </div>
        </div>

        <!-- KPIs -->
        <div class="right-col">
          <div class="card kpi-card">
            <div class="card-header"><h3 class="card-title">KPIs del post</h3></div>
            <div class="kpi-grid">
              <div class="kpi-item" v-for="kpi in postKPIs" :key="kpi.label">
                <div class="kpi-icon"><component :is="kpi.icon" :size="18" /></div>
                <div class="kpi-value">{{ kpi.format(post[kpi.field]) }}</div>
                <div class="kpi-label">{{ kpi.label }}</div>
              </div>
            </div>
          </div>

          <!-- Engagement bar -->
          <div class="card">
            <div class="card-header"><h3 class="card-title">Engagement</h3></div>
            <div class="engagement-section">
              <div class="eng-big" :class="engClass(post.engagement)">{{ post.engagement }}%</div>
              <div class="eng-bar-wrap">
                <div class="eng-bar" :style="{ width: Math.min(post.engagement * 10, 100) + '%', background: engColor(post.engagement) }"></div>
              </div>
              <div class="eng-desc">
                <span :class="engClass(post.engagement)">{{ engLabel(post.engagement) }}</span>
                — media de la cuenta: {{ avgEngagement.toFixed(1) }}%
              </div>
            </div>
          </div>

          <!-- Trazabilidad -->
          <div class="card">
            <div class="card-header"><h3 class="card-title">Trazabilidad</h3></div>
            <div class="trace-body">
              <div class="trace-row"><span class="trace-label">Clics generados</span><span class="trace-val">{{ formatNumber(post.clicks) }}</span></div>
              <div class="trace-row"><span class="trace-label">Conversiones</span><span class="trace-val">—</span></div>
              <div class="trace-row"><span class="trace-label">Ventas atribuidas</span><span class="trace-val">—</span></div>
              <div class="trace-row"><span class="trace-label">UTM Campaign</span><span class="trace-val text-secondary">{{ post.campaignName ? post.campaignName.toLowerCase().replace(/\s/g,'-') : '—' }}</span></div>
            </div>
          </div>
        </div>

        <!-- Comparativa -->
        <div class="full-col">
          <div class="card">
            <div class="card-header"><h3 class="card-title">Comparativa con otros posts</h3></div>
            <div class="compare-grid">
              <div class="compare-item" v-for="m in compareMetrics" :key="m.label">
                <div class="compare-label">{{ m.label }}</div>
                <div class="compare-vals">
                  <div>
                    <div class="compare-this">{{ m.format(post[m.field]) }}</div>
                    <div class="compare-sub">Este post</div>
                  </div>
                  <div class="compare-sep">/</div>
                  <div>
                    <div class="compare-avg">{{ m.format(m.avg) }}</div>
                    <div class="compare-sub">Media del periodo</div>
                  </div>
                </div>
                <div class="compare-diff" :class="post[m.field] >= m.avg ? 'pos' : 'neg'">
                  {{ post[m.field] >= m.avg ? '▲' : '▼' }}
                  {{ Math.abs(((post[m.field] - m.avg) / (m.avg || 1)) * 100).toFixed(0) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <AlertCircle :size="40" />
      <p>Publicación no encontrada.</p>
      <router-link to="/social-crm/posts" class="btn btn-secondary">Volver a publicaciones</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Download, Heart, MessageCircle, Share2, Bookmark, Eye, MousePointer, BarChart2, Image as ImageIcon, ExternalLink, AlertCircle } from 'lucide-vue-next'
import { socialPosts, getPlatform, formatNumber, formatDate } from '@/services/socialCrmData'

const route = useRoute()
const post  = computed(() => socialPosts.find(p => p.id === Number(route.params.id)))

function platformStyle(key) {
  const p = getPlatform(key)
  return { background: p.bg, color: p.color }
}

const postKPIs = [
  { label: 'Likes',          field: 'likes',       icon: Heart,         format: formatNumber },
  { label: 'Comentarios',    field: 'comments',    icon: MessageCircle, format: formatNumber },
  { label: 'Compartidos',    field: 'shares',      icon: Share2,        format: formatNumber },
  { label: 'Guardados',      field: 'saves',       icon: Bookmark,      format: formatNumber },
  { label: 'Visualizaciones',field: 'views',       icon: Eye,           format: formatNumber },
  { label: 'Alcance',        field: 'reach',       icon: BarChart2,     format: formatNumber },
  { label: 'Impresiones',    field: 'impressions', icon: BarChart2,     format: formatNumber },
  { label: 'Clics',          field: 'clicks',      icon: MousePointer,  format: formatNumber },
]

const avgEngagement = computed(() => {
  const list = socialPosts
  return list.reduce((s, p) => s + p.engagement, 0) / list.length
})

const compareMetrics = computed(() => {
  const avg = (field) => socialPosts.reduce((s, p) => s + p[field], 0) / socialPosts.length
  return [
    { label: 'Alcance',     field: 'reach',      avg: Math.round(avg('reach')),      format: formatNumber },
    { label: 'Engagement',  field: 'engagement', avg: parseFloat(avg('engagement').toFixed(1)), format: v => v + '%' },
    { label: 'Clics',       field: 'clicks',     avg: Math.round(avg('clicks')),     format: formatNumber },
    { label: 'Likes',       field: 'likes',      avg: Math.round(avg('likes')),      format: formatNumber },
  ]
})

function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function engColor(v) { return v >= 6 ? '#10B981' : v >= 3 ? '#F59E0B' : '#EF4444' }
function engLabel(v) { return v >= 6 ? 'Muy alto' : v >= 4 ? 'Alto' : v >= 2 ? 'Medio' : 'Bajo' }
</script>

<style scoped>
.post-detail-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-md) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; }
.breadcrumb { display: flex; align-items: center; gap: 6px; }
.breadcrumb-link { font-size: 0.875rem; color: var(--primary-color); text-decoration: none; }
.breadcrumb-sep { color: var(--text-secondary); }
.breadcrumb-current { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; }
.header-actions { display: flex; gap: var(--spacing-sm); }

.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg); }
.left-col, .right-col { display: flex; flex-direction: column; gap: var(--spacing-md); }
.full-col { grid-column: 1 / 3; }

.summary-header { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-md) var(--spacing-lg); flex-wrap: wrap; }
.platform-pill { font-size: 0.78rem; font-weight: 600; padding: 3px 10px; border-radius: 12px; }
.date-label { font-size: 0.82rem; color: var(--text-secondary); margin-left: auto; }
.post-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); padding: 0 var(--spacing-lg) var(--spacing-sm); margin: 0; }
.meta-row { display: flex; flex-wrap: wrap; gap: var(--spacing-md); padding: 0 var(--spacing-lg) var(--spacing-md); }
.meta-item { font-size: 0.82rem; color: var(--text-secondary); }
.meta-key { font-weight: 600; color: var(--text-primary); }
.post-preview { margin: 0 var(--spacing-lg) var(--spacing-lg); }
.preview-placeholder { border: 2px dashed var(--border-color); border-radius: var(--border-radius); padding: var(--spacing-xl); display: flex; flex-direction: column; align-items: center; gap: var(--spacing-sm); color: var(--text-secondary); }
.preview-icon { color: var(--text-secondary); }
.preview-link { display: flex; align-items: center; gap: 4px; font-size: 0.82rem; color: var(--primary-color); text-decoration: none; }

.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--spacing-sm); padding: var(--spacing-md); }
.kpi-item { display: flex; flex-direction: column; align-items: center; gap: 4px; padding: var(--spacing-sm); background: var(--bg-secondary); border-radius: var(--border-radius-sm); }
.kpi-icon { color: var(--primary-color); }
.kpi-value { font-size: 1rem; font-weight: 700; color: var(--text-primary); }
.kpi-label { font-size: 0.7rem; color: var(--text-secondary); text-align: center; }

.engagement-section { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.eng-big { font-size: 2rem; font-weight: 800; }
.eng-high { color: #10B981; }
.eng-mid  { color: #F59E0B; }
.eng-low  { color: #EF4444; }
.eng-bar-wrap { height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden; }
.eng-bar { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.eng-desc { font-size: 0.82rem; color: var(--text-secondary); }

.trace-body { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.trace-row { display: flex; justify-content: space-between; padding: var(--spacing-xs) 0; border-bottom: 1px solid var(--border-color); }
.trace-label { font-size: 0.85rem; color: var(--text-secondary); }
.trace-val { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }

.compare-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--spacing-md); padding: var(--spacing-lg); }
.compare-item { background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: var(--spacing-md); }
.compare-label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-bottom: var(--spacing-sm); }
.compare-vals { display: flex; align-items: center; gap: var(--spacing-sm); margin-bottom: 6px; }
.compare-this { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.compare-avg  { font-size: 1.1rem; font-weight: 700; color: var(--text-secondary); }
.compare-sep  { color: var(--border-color); font-size: 1.2rem; }
.compare-sub  { font-size: 0.7rem; color: var(--text-secondary); }
.compare-diff { font-size: 0.82rem; font-weight: 700; }
.compare-diff.pos { color: #10B981; }
.compare-diff.neg { color: #EF4444; }

.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); height: 100%; color: var(--text-secondary); }
</style>
