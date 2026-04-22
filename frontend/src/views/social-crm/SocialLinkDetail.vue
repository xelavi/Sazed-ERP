<template>
  <div class="link-detail-view">
    <div class="view-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/social-crm/links" class="breadcrumb-link">Enlaces</router-link>
          <ChevronRight :size="16" class="breadcrumb-sep" />
          <span class="breadcrumb-current">{{ lnk?.name }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="copyLink"><Copy :size="18" /><span>Copiar URL</span></button>
        </div>
      </div>
    </div>

    <div v-if="lnk" class="content-wrapper">
      <!-- Base data -->
      <div class="card data-card">
        <div class="data-grid">
          <div class="data-item"><span class="data-key">Nombre</span><span class="font-medium">{{ lnk.name }}</span></div>
          <div class="data-item"><span class="data-key">URL destino</span><a :href="lnk.url" target="_blank" class="link-url">{{ lnk.url }}</a></div>
          <div class="data-item"><span class="data-key">Campaña</span><span>{{ lnk.campaignName || '—' }}</span></div>
          <div class="data-item"><span class="data-key">Origen</span><span class="platform-pill" :style="platformStyle(lnk.origin)">{{ getPlatform(lnk.origin).label }}</span></div>
          <div class="data-item"><span class="data-key">Influencer</span><span>{{ lnk.influencerName || 'Orgánico' }}</span></div>
          <div class="data-item"><span class="data-key">UTMs</span>
            <span class="utm-codes">
              <code>utm_source={{ lnk.utmSource }}</code>
              <code>utm_medium={{ lnk.utmMedium }}</code>
              <code>utm_campaign={{ lnk.utmCampaign }}</code>
              <code v-if="lnk.utmContent">utm_content={{ lnk.utmContent }}</code>
            </span>
          </div>
        </div>
      </div>

      <div class="kpi-row">
        <div class="card kpi-card" v-for="kpi in linkKPIs" :key="kpi.label">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">{{ kpi.format(lnk[kpi.field]) }}</div>
        </div>
      </div>

      <div class="two-col">
        <!-- Conversion funnel -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Embudo de conversión</h3></div>
          <div class="funnel">
            <div
              v-for="(step, i) in funnelSteps"
              :key="step.label"
              class="funnel-step">
              <div class="funnel-bar-wrap">
                <div
                  class="funnel-bar"
                  :style="{ width: funnelWidth(step.value) + '%', background: funnelColor(i) }">
                </div>
              </div>
              <div class="funnel-info">
                <span class="funnel-label">{{ step.label }}</span>
                <span class="funnel-val">{{ formatNumber(step.value) }}</span>
                <span class="funnel-pct" v-if="i > 0">{{ funnelPct(step.value, funnelSteps[0].value).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Temporal evolution (simulated) -->
        <div class="card">
          <div class="card-header"><h3 class="card-title">Evolución temporal (últimos 30 días)</h3></div>
          <div class="chart-area">
            <div class="bar-chart">
              <div v-for="(d, i) in evoData" :key="i" class="bar-group">
                <div class="bar-wrap">
                  <div class="bar" :style="{ height: (d.clicks / maxEvo * 85) + '%', background: '#667eea' }"></div>
                </div>
                <span class="bar-label">{{ d.label }}</span>
              </div>
            </div>
            <div class="evo-legend"><span style="color:#667eea">■</span> Clics diarios</div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <AlertCircle :size="40" />
      <p>Enlace no encontrado.</p>
      <router-link to="/social-crm/links" class="btn btn-secondary">Volver</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Copy, AlertCircle } from 'lucide-vue-next'
import { socialLinks, getPlatform, formatNumber, formatCurrency } from '@/services/socialCrmData'

const route = useRoute()
const lnk   = computed(() => socialLinks.find(l => l.id === Number(route.params.id)))

const linkKPIs = [
  { label: 'Clics',       field: 'clicks',     format: formatNumber },
  { label: 'Sesiones',    field: 'sessions',   format: formatNumber },
  { label: 'Carritos',    field: 'carts',      format: formatNumber },
  { label: 'Compras',     field: 'purchases',  format: formatNumber },
  { label: 'Ingresos',    field: 'revenue',    format: formatCurrency },
  { label: 'Conversión',  field: 'conversion', format: v => v.toFixed(2) + '%' },
]

const funnelSteps = computed(() => lnk.value ? [
  { label: 'Clics',    value: lnk.value.clicks },
  { label: 'Sesiones', value: lnk.value.sessions },
  { label: 'Carritos', value: lnk.value.carts },
  { label: 'Compras',  value: lnk.value.purchases },
] : [])

function funnelWidth(val) { const max = funnelSteps.value[0]?.value || 1; return (val / max) * 100 }
function funnelPct(val, base) { return base ? (val / base) * 100 : 0 }
function funnelColor(i) { return ['#667eea','#10B981','#F59E0B','#EC4899'][i] }

// Simulated daily evolution (random-ish based on total clicks)
const evoData = computed(() => {
  if (!lnk.value) return []
  const total = lnk.value.clicks
  const labels = ['1/4','5/4','10/4','15/4','17/4']
  const weights = [0.15, 0.25, 0.30, 0.20, 0.10]
  return labels.map((label, i) => ({ label, clicks: Math.round(total * weights[i]) }))
})
const maxEvo = computed(() => Math.max(...evoData.value.map(d => d.clicks), 1))

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function copyLink() {
  if (!lnk.value) return
  const url = `${lnk.value.url}?utm_source=${lnk.value.utmSource}&utm_medium=${lnk.value.utmMedium}&utm_campaign=${lnk.value.utmCampaign}`
  navigator.clipboard.writeText(url).then(() => alert('URL copiada al portapapeles'))
}
</script>

<style scoped>
.link-detail-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-md) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.breadcrumb { display: flex; align-items: center; gap: 6px; }
.breadcrumb-link { font-size: 0.875rem; color: var(--primary-color); text-decoration: none; }
.breadcrumb-sep { color: var(--text-secondary); }
.breadcrumb-current { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.data-card { padding: var(--spacing-lg); }
.data-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--spacing-md); }
.data-item { display: flex; flex-direction: column; gap: 4px; }
.data-key { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); }
.font-medium { font-weight: 600; color: var(--text-primary); }
.link-url { color: var(--primary-color); font-size: 0.85rem; word-break: break-all; }
.platform-pill { display: inline-block; font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; }
.utm-codes { display: flex; flex-wrap: wrap; gap: 4px; }
.utm-codes code { background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px; font-size: 0.78rem; font-family: monospace; color: var(--text-primary); }
.kpi-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: var(--spacing-md); }
.kpi-card { padding: var(--spacing-md) var(--spacing-lg); }
.kpi-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 4px; }
.kpi-value { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.funnel { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.funnel-step { display: flex; flex-direction: column; gap: 6px; }
.funnel-bar-wrap { height: 10px; background: var(--bg-secondary); border-radius: 5px; overflow: hidden; }
.funnel-bar { height: 100%; border-radius: 5px; transition: width 0.5s ease; }
.funnel-info { display: flex; align-items: center; gap: var(--spacing-md); }
.funnel-label { font-size: 0.85rem; color: var(--text-primary); font-weight: 500; min-width: 70px; }
.funnel-val { font-size: 0.88rem; font-weight: 700; color: var(--text-primary); min-width: 60px; }
.funnel-pct { font-size: 0.78rem; color: var(--text-secondary); }
.chart-area { padding: var(--spacing-lg); }
.bar-chart { display: flex; align-items: flex-end; gap: var(--spacing-md); height: 140px; }
.bar-group { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1; }
.bar-wrap { flex: 1; display: flex; align-items: flex-end; width: 100%; }
.bar { width: 100%; min-height: 4px; border-radius: 4px 4px 0 0; }
.bar-label { font-size: 0.72rem; color: var(--text-secondary); }
.evo-legend { font-size: 0.78rem; color: var(--text-secondary); margin-top: var(--spacing-sm); }
.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); height: 100%; color: var(--text-secondary); }
</style>
