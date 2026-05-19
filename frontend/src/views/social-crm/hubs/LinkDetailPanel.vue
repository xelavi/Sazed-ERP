<template>
  <div v-if="lnk" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-meta">
        <span class="platform-pill" :style="platformStyle(lnk.origin)">
          {{ getPlatform(lnk.origin).label }}
        </span>
        <span class="origin-tag">{{ lnk.influencerName || 'Orgánico' }}</span>
      </div>
      <h2 class="hero-title">{{ lnk.name }}</h2>

      <!-- URL row with copy -->
      <div class="url-row">
        <code class="url-text">{{ shortUrl }}</code>
        <button class="url-copy" @click="copyUrl" :class="{ copied }">
          <component :is="copied ? Check : Copy" :size="12" />
          <span>{{ copied ? 'Copiado' : 'Copiar' }}</span>
        </button>
      </div>
    </div>

    <!-- KPIs -->
    <div class="quick-stats">
      <div class="qs-cell qs-revenue">
        <div class="qs-key">Ingresos</div>
        <div class="qs-val">{{ formatCurrency(lnk.revenue) }}</div>
      </div>
      <div class="qs-cell">
        <div class="qs-key">Conversión</div>
        <div class="qs-val">
          <span class="conv-pill" :class="convClass(lnk.conversion)">
            {{ lnk.conversion.toFixed(2) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- Funnel visualization -->
    <section class="panel-section">
      <h3 class="section-title">Embudo de conversión</h3>
      <div class="funnel">
        <div
          v-for="(step, i) in funnelSteps"
          :key="step.label"
          class="funnel-row"
        >
          <div class="funnel-meta">
            <span class="funnel-label">
              <span class="funnel-dot" :style="{ background: funnelColors[i] }"></span>
              {{ step.label }}
            </span>
            <span class="funnel-val">{{ formatNumber(step.value) }}</span>
          </div>
          <div class="funnel-bar-wrap">
            <div
              class="funnel-bar"
              :style="{
                width: ((step.value / (funnelSteps[0].value || 1)) * 100) + '%',
                background: funnelColors[i],
              }"
            ></div>
          </div>
          <div v-if="i > 0" class="funnel-pct">
            <ArrowDown :size="10" />
            {{ ((step.value / funnelSteps[i-1].value) * 100).toFixed(1) }}%
            <span class="muted">paso a paso</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Daily evolution chart -->
    <section class="panel-section">
      <h3 class="section-title">Evolución (30 días)</h3>
      <div class="evo-chart">
        <div
          v-for="(d, i) in evoData"
          :key="i"
          class="evo-bar-group"
          :title="`${d.label}: ${formatNumber(d.clicks)} clics`"
        >
          <div class="evo-bar-wrap">
            <div
              class="evo-bar"
              :style="{ height: (d.clicks / maxEvo * 90) + '%' }"
            ></div>
          </div>
          <span class="evo-label">{{ d.label }}</span>
        </div>
      </div>
      <div class="evo-legend">
        <span class="legend-item">
          <span class="legend-dot"></span>
          Clics diarios
        </span>
        <span class="legend-stat">Total: {{ formatNumber(lnk.clicks) }}</span>
      </div>
    </section>

    <!-- UTM details -->
    <section class="panel-section">
      <h3 class="section-title">Parámetros UTM</h3>
      <div class="utm-list">
        <div v-for="utm in utmRows" :key="utm.key" class="utm-row">
          <span class="utm-key">{{ utm.key }}</span>
          <code class="utm-val">{{ utm.value || '—' }}</code>
        </div>
      </div>
    </section>

    <!-- Linked entities -->
    <section class="panel-section">
      <h3 class="section-title">Vinculaciones</h3>
      <dl class="info-list">
        <div class="info-row">
          <dt>Campaña</dt>
          <dd>{{ lnk.campaignName || '—' }}</dd>
        </div>
        <div class="info-row">
          <dt>Influencer</dt>
          <dd>{{ lnk.influencerName || 'Orgánico' }}</dd>
        </div>
        <div class="info-row">
          <dt>URL destino</dt>
          <dd>
            <a :href="lnk.url" target="_blank" class="dest-link">
              {{ lnk.url }}
              <ExternalLink :size="11" />
            </a>
          </dd>
        </div>
      </dl>
    </section>

    <!-- Footer -->
    <div class="panel-footer">
      <button class="panel-btn panel-btn-ghost" @click="$emit('close')">Cerrar</button>
      <button class="panel-btn panel-btn-primary" @click="copyUrl">
        <Copy :size="13" />
        Copiar URL completa
      </button>
    </div>
  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Enlace no encontrado.</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Copy, Check, ArrowDown, ExternalLink, AlertCircle,
} from 'lucide-vue-next'
import {
  socialLinks, getPlatform, formatNumber, formatCurrency,
} from '@/services/socialCrmData'

const props = defineProps({
  linkId: { type: Number, required: true },
})

defineEmits(['close'])

const lnk = computed(() => socialLinks.find(l => l.id === props.linkId))
const copied = ref(false)

const shortUrl = computed(() => {
  if (!lnk.value) return ''
  const u = lnk.value.url
  return u.length > 38 ? u.slice(0, 35) + '…' : u
})

const fullUrl = computed(() => {
  if (!lnk.value) return ''
  const params = new URLSearchParams({
    utm_source:   lnk.value.utmSource,
    utm_medium:   lnk.value.utmMedium,
    utm_campaign: lnk.value.utmCampaign,
    ...(lnk.value.utmContent ? { utm_content: lnk.value.utmContent } : {}),
  })
  return `${lnk.value.url}?${params.toString()}`
})

const funnelSteps = computed(() => lnk.value ? [
  { label: 'Clics',    value: lnk.value.clicks },
  { label: 'Sesiones', value: lnk.value.sessions },
  { label: 'Carritos', value: lnk.value.carts },
  { label: 'Compras',  value: lnk.value.purchases },
] : [])

const funnelColors = ['#667eea', '#764ba2', '#F59E0B', '#10B981']

const utmRows = computed(() => lnk.value ? [
  { key: 'utm_source',   value: lnk.value.utmSource },
  { key: 'utm_medium',   value: lnk.value.utmMedium },
  { key: 'utm_campaign', value: lnk.value.utmCampaign },
  { key: 'utm_content',  value: lnk.value.utmContent },
] : [])

// Simulated daily evolution
const evoData = computed(() => {
  if (!lnk.value) return []
  const total = lnk.value.clicks
  const days = 14
  // weighted random pattern based on a sine wave + jitter
  return Array.from({ length: days }, (_, i) => {
    const wave = (Math.sin((i / days) * Math.PI * 2) + 1) / 2
    const jitter = 0.5 + Math.random() * 0.5
    const weight = wave * jitter
    return {
      label: `${i + 1}`,
      clicks: Math.round((total / days) * weight * 1.6),
    }
  })
})
const maxEvo = computed(() => Math.max(...evoData.value.map(d => d.clicks), 1))

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function convClass(v) { return v >= 5 ? 'conv-high' : v >= 2 ? 'conv-mid' : 'conv-low' }

function copyUrl() {
  if (!fullUrl.value) return
  navigator.clipboard.writeText(fullUrl.value).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 1500)
  })
}
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 1.25rem; }

/* Hero */
.panel-hero {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.hero-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.platform-pill { font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.origin-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 5px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 500;
}
.hero-title {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
}

.url-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.5rem 0.4rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}
.url-text {
  flex: 1;
  font-size: 0.78rem;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.url-copy {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.625rem;
  font-size: 0.7rem;
  font-weight: 600;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 5px;
  cursor: pointer;
  color: var(--text-primary);
  font-family: inherit;
  transition: all 0.15s ease;
}
.url-copy.copied { background: #10B981; color: white; border-color: #10B981; }

/* Quick stats */
.quick-stats {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 0.5rem;
}
.qs-cell {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.75rem 0.875rem;
}
.qs-revenue { background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.06)); }
.qs-key {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}
.qs-val {
  font-size: 1.15rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-feature-settings: "tnum";
}

.conv-pill {
  display: inline-block;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 999px;
}
.conv-high { background: rgba(16,185,129,0.14); color: #10B981; }
.conv-mid  { background: rgba(245,158,11,0.14); color: #F59E0B; }
.conv-low  { background: rgba(239,68,68,0.10);  color: #EF4444; }

/* Sections */
.panel-section { display: flex; flex-direction: column; gap: 0.625rem; }
.section-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--primary-color);
  margin: 0;
}

/* Funnel */
.funnel { display: flex; flex-direction: column; gap: 0.875rem; }
.funnel-row { display: flex; flex-direction: column; gap: 0.3rem; }
.funnel-meta { display: flex; align-items: baseline; justify-content: space-between; }
.funnel-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: var(--text-primary);
  font-weight: 600;
}
.funnel-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.funnel-val { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.funnel-bar-wrap { height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden; }
.funnel-bar { height: 100%; border-radius: 4px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
.funnel-pct {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
}
.funnel-pct svg { color: #94A3B8; }
.funnel-pct .muted { font-weight: 400; opacity: 0.65; }

/* Evolution chart */
.evo-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 100px;
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.875rem 0.875rem 0.5rem;
}
.evo-bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  cursor: default;
}
.evo-bar-wrap {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
}
.evo-bar {
  width: 100%;
  min-height: 3px;
  border-radius: 2px 2px 0 0;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s ease;
}
.evo-bar-group:hover .evo-bar { opacity: 0.7; }
.evo-label {
  font-size: 0.62rem;
  color: var(--text-secondary);
  font-feature-settings: "tnum";
}

.evo-legend {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.72rem;
  color: var(--text-secondary);
}
.legend-item { display: inline-flex; align-items: center; gap: 0.4rem; }
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}
.legend-stat { font-weight: 600; color: var(--text-primary); font-feature-settings: "tnum"; }

/* UTMs */
.utm-list { display: flex; flex-direction: column; gap: 0.4rem; }
.utm-row {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 0.625rem;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 7px;
}
.utm-key { font-size: 0.72rem; font-weight: 700; color: var(--text-secondary); font-family: 'SF Mono', monospace; }
.utm-val {
  font-size: 0.78rem;
  font-family: 'SF Mono', monospace;
  background: var(--bg-primary);
  padding: 2px 7px;
  border-radius: 4px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Info list */
.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.info-row { display: flex; justify-content: space-between; font-size: 0.85rem; align-items: baseline; gap: 1rem; }
.info-row dt { color: var(--text-secondary); margin: 0; }
.info-row dd { color: var(--text-primary); margin: 0; text-align: right; min-width: 0; }

.dest-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.78rem;
  font-family: 'SF Mono', monospace;
  word-break: break-all;
}
.dest-link:hover { text-decoration: underline; }

/* Footer */
.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}
.panel-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  border-radius: 7px;
  font-size: 0.825rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
}
.panel-btn-primary {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(102,126,234,0.30);
}
.panel-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
.panel-btn-ghost:hover { background: var(--bg-secondary); }

.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 4rem 1rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>
