<template>
  <div v-if="campaign" class="panel">

    <!-- ── Hero ───────────────────────────────────────────────── -->
    <div class="hero">
      <div class="hero-badges">
        <span class="badge" :class="CAMPAIGN_STATUSES[campaign.status].cls">
          {{ CAMPAIGN_STATUSES[campaign.status].label }}
        </span>
        <span class="obj-tag">{{ campaign.objective }}</span>
      </div>
      <h2 class="hero-name">{{ campaign.name }}</h2>
      <div class="hero-row">
        <Calendar :size="13" class="icon-muted" />
        <span>{{ formatDate(campaign.startDate) }} → {{ formatDate(campaign.endDate) }}</span>
        <span class="hero-days">· {{ campaignDays }} dies</span>
      </div>
      <div v-if="campaign.responsible" class="hero-row">
        <User :size="13" class="icon-muted" />
        <span>{{ campaign.responsible }}</span>
      </div>
      <p v-if="campaign.description" class="hero-desc">{{ campaign.description }}</p>
    </div>

    <!-- ── KPIs principales ───────────────────────────────────── -->
    <div class="kpi-row">
      <div class="kpi-block kpi-primary">
        <div class="kb-label">Vendes atribuïdes</div>
        <div class="kb-value">{{ formatCurrency(campaign.sales) }}</div>
        <div class="kb-sub">{{ campaign.conversions }} conversions</div>
      </div>
      <div class="kpi-block">
        <div class="kb-label">ROAS consolidat</div>
        <div class="kb-value" :class="roasClass(campaign.roas)">{{ campaign.roas.toFixed(2) }}x</div>
        <div class="kb-sub">retorn sobre la inversió</div>
      </div>
      <div class="kpi-block">
        <div class="kb-label">Despesa total</div>
        <div class="kb-value">{{ formatCurrency(campaign.cost) }}</div>
        <div class="kb-sub">de {{ formatCurrency(campaign.budget) }}</div>
      </div>
    </div>

    <!-- ── Presupuesto ────────────────────────────────────────── -->
    <div class="budget-strip">
      <div class="bs-head">
        <span class="bs-label">Pressupost utilitzat</span>
        <span class="bs-pct" :class="budgetClass">{{ budgetPct.toFixed(0) }}%</span>
      </div>
      <div class="bs-bar-wrap">
        <div class="bs-bar" :class="budgetClass" :style="{ width: Math.min(budgetPct, 100) + '%' }"></div>
      </div>
    </div>

    <!-- ── Canales: resumen ───────────────────────────────────── -->
    <div class="channels-summary">
      <button
        v-for="ch in shownChannels"
        :key="ch.key"
        class="ch-card"
        :class="{ active: activeChannel === ch.key }"
        :style="{ '--ch-c': ch.color }"
        @click="activeChannel = ch.key"
      >
        <div class="ch-head">
          <span class="ch-icon" :style="{ background: ch.color + '18', color: ch.color }">
            <component :is="channelIcon(ch.icon)" :size="14" />
          </span>
          <span class="ch-name">{{ ch.label }}</span>
          <span class="ch-count">{{ ch.items }}</span>
        </div>
        <div class="ch-sales">{{ formatCurrency(ch.sales) }}</div>
        <div class="ch-roas" :class="roasClass(ch.roas)">
          ROAS {{ ch.roas > 0 ? ch.roas.toFixed(1) + 'x' : '—' }}
        </div>
        <div class="ch-bar-wrap">
          <div
            class="ch-bar"
            :style="{ width: pct(ch.sales, channelSalesTotal) + '%', background: ch.color }"
          ></div>
        </div>
        <div class="ch-contrib">{{ pct(ch.sales, channelSalesTotal).toFixed(0) }}% de vendes</div>
      </button>
    </div>

    <!-- ── Detalle por canal ──────────────────────────────────── -->
    <div class="channel-detail">
      <div class="cd-tabs">
        <button
          v-for="ch in shownChannels"
          :key="ch.key"
          class="cd-tab"
          :class="{ active: activeChannel === ch.key }"
          @click="activeChannel = ch.key"
        >
          {{ ch.label }}
          <span class="cd-tab-count">{{ ch.items }}</span>
        </button>
      </div>

      <!-- Contenido propio -->
      <div v-if="activeChannel === 'owned'" class="tab-body">
        <div v-if="linkedPosts.length" class="items-list">
          <div v-for="p in linkedPosts" :key="p.id" class="item-row">
            <div class="item-thumb" :style="thumbStyle(p)">
              <component :is="typeIcon(p.type)" :size="11" />
            </div>
            <div class="item-main">
              <div class="item-title">{{ p.title }}</div>
              <div class="item-meta">
                <span class="plat-pill" :style="platformStyle(p.platform)">
                  {{ getPlatform(p.platform).label }}
                </span>
                <span class="meta-txt">{{ formatDateShort(p.date) }}</span>
              </div>
            </div>
            <div class="item-right">
              <span class="eng-pill" :class="engClass(p.engagement)">{{ p.engagement }}%</span>
              <div class="item-sub">{{ formatNumber(p.reach) }} abast</div>
            </div>
          </div>
        </div>
        <div v-else class="tab-empty">Sense publicacions vinculades a aquesta campanya.</div>
      </div>

      <!-- Influencers -->
      <div v-if="activeChannel === 'influencers'" class="tab-body">
        <div v-if="linkedCollabs.length" class="items-list">
          <div v-for="c in linkedCollabs" :key="c.id" class="item-row">
            <div class="item-avatar" :style="avatarStyle(c.influencerName)">
              {{ c.influencerName[0] }}
            </div>
            <div class="item-main">
              <div class="item-title">{{ c.influencerName }}</div>
              <div class="item-meta">
                <span class="meta-txt">{{ c.format }}</span>
                <span class="meta-sep">·</span>
                <span class="meta-txt">{{ formatDateShort(c.publishDate) }}</span>
              </div>
            </div>
            <div class="item-right">
              <div class="item-sales">{{ formatCurrency(c.sales) }}</div>
              <span class="badge badge-sm" :class="COLLAB_STATUSES[c.status].cls">
                {{ COLLAB_STATUSES[c.status].label }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="tab-empty">Sense col·laboracions d'influencer en aquesta campanya.</div>
      </div>

      <!-- Anuncios de pago -->
      <div v-if="activeChannel === 'paid'" class="tab-body">
        <div v-if="adsByPlatform.length" class="ads-section">
          <div v-for="group in adsByPlatform" :key="group.platform" class="ad-platform">
            <div class="ap-header">
              <span class="plat-pill" :style="adPlatformStyle(group.platform)">
                {{ getAdPlatform(group.platform).label }}
              </span>
              <span class="ap-sync">
                <RefreshCw :size="10" />
                Dades sincronitzades
              </span>
            </div>
            <div class="ad-metrics">
              <div class="am-cell">
                <div class="am-val">{{ formatCurrency(group.spend) }}</div>
                <div class="am-key">Despesa</div>
              </div>
              <div class="am-cell">
                <div class="am-val">{{ formatNumber(group.impressions) }}</div>
                <div class="am-key">Impressions</div>
              </div>
              <div class="am-cell">
                <div class="am-val">{{ formatNumber(group.clicks) }}</div>
                <div class="am-key">Clics</div>
              </div>
              <div class="am-cell">
                <div class="am-val">{{ group.conversions }}</div>
                <div class="am-key">Conversions</div>
              </div>
              <div class="am-cell">
                <div class="am-val" :class="roasClass(group.roas)">
                  {{ group.roas > 0 ? group.roas.toFixed(2) + 'x' : '—' }}
                </div>
                <div class="am-key">ROAS</div>
              </div>
            </div>
          </div>
          <div class="ads-note">
            <Info :size="12" />
            La gestió dels anuncis es realitza directament a cada plataforma. L'ERP només rep i mostra les dades de rendiment.
          </div>
        </div>
        <div v-else class="tab-empty">
          Sense anuncis de pagament vinculats. Configura els conjunts d'anuncis en editar la campanya i introdueix l'ID de campanya de cada plataforma.
        </div>
      </div>
    </div>

    <!-- ── Objetivos vs real ──────────────────────────────────── -->
    <div v-if="targetRows.length" class="targets-section">
      <div class="targets-label">Objectius vs real</div>
      <div class="targets-grid">
        <div v-for="t in targetRows" :key="t.label" class="tc">
          <div class="tc-head">
            <span class="tc-name">{{ t.label }}</span>
            <span class="tc-pct" :class="pctClass(pct(t.actual, t.target))">
              {{ pct(t.actual, t.target).toFixed(0) }}%
            </span>
          </div>
          <div class="tc-bar-wrap">
            <div
              class="tc-bar"
              :class="pctClass(pct(t.actual, t.target))"
              :style="{ width: Math.min(pct(t.actual, t.target), 100) + '%' }"
            ></div>
          </div>
          <div class="tc-vals">
            <span class="tc-actual">{{ t.fmt(t.actual) }}</span>
            <span class="tc-of">de {{ t.fmt(t.target) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Productes ────────────────────────────────────────────── -->
    <div v-if="campaignProductsWithMetrics.length" class="products-section">
      <div class="prods-header">
        <Package :size="14" class="prods-header-icon" />
        <span class="prods-title">Productes</span>
        <span class="prods-count">{{ campaignProductsWithMetrics.length }}</span>
      </div>
      <div class="prods-list">
        <div v-for="p in campaignProductsWithMetrics" :key="p.id" class="prod-item">
          <div class="pi-icon-wrap">
            <Package :size="16" />
          </div>
          <div class="pi-info">
            <div class="pi-name">{{ p.name }}</div>
            <div class="pi-meta">
              <span class="pi-sku">{{ p.sku }}</span>
              <span class="pi-sep">·</span>
              <span class="pi-price">{{ formatCurrency(p.price) }}</span>
            </div>
          </div>
          <div class="pi-stats">
            <div v-if="p.reach" class="pi-stat">
              <div class="pis-val">{{ formatNumber(p.reach) }}</div>
              <div class="pis-key">Abast</div>
            </div>
            <div v-if="p.clicks" class="pi-stat">
              <div class="pis-val">{{ formatNumber(p.clicks) }}</div>
              <div class="pis-key">Clics</div>
            </div>
            <div v-if="p.sales" class="pi-stat">
              <div class="pis-val">{{ formatCurrency(p.sales) }}</div>
              <div class="pis-key">Vendes</div>
            </div>
          </div>
          <div class="pi-coverage">
            <span v-if="p.postCount" class="cov-pill cov-owned" title="Publicacions">
              <Megaphone :size="9" /> {{ p.postCount }}
            </span>
            <span v-if="p.infCount" class="cov-pill cov-inf" title="Influencers">
              <Users :size="9" /> {{ p.infCount }}
            </span>
            <span v-if="p.adCount" class="cov-pill cov-ad" title="Anuncis">
              <Target :size="9" /> {{ p.adCount }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Footer ─────────────────────────────────────────────── -->
    <div class="panel-footer">
      <button class="panel-btn" @click="$emit('close')">Tancar</button>
    </div>

  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Campanya no trobada.</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Calendar, User, AlertCircle, RefreshCw, Info,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText,
  Megaphone, Users, Target, Package,
} from 'lucide-vue-next'
import {
  socialCampaigns, socialPosts, socialCollaborations, erpProducts,
  CAMPAIGN_STATUSES, COLLAB_STATUSES, CAMPAIGN_CHANNELS,
  getPlatform, getAdPlatform, formatNumber, formatCurrency, formatDate,
  getCampaignAds, getCampaignChannelBreakdown, adMetrics,
} from '@/services/socialCrmData'

const props = defineProps({ campaignId: { type: Number, required: true } })
defineEmits(['close'])

const activeChannel = ref('owned')

const campaign     = computed(() => socialCampaigns.find(c => c.id === props.campaignId))
const linkedPosts  = computed(() => socialPosts.filter(p => p.campaignId === props.campaignId))
const linkedCollabs = computed(() => socialCollaborations.filter(c => c.campaignId === props.campaignId))
const linkedAds    = computed(() => getCampaignAds(props.campaignId))
const breakdown    = computed(() => getCampaignChannelBreakdown(props.campaignId))

const shownChannels = computed(() => {
  const selected = campaign.value?.channels || []
  return breakdown.value.channels.filter(ch => selected.includes(ch.key) || ch.items > 0)
})

const channelSalesTotal = computed(() =>
  breakdown.value.channels.reduce((s, ch) => s + ch.sales, 0)
)

// ── Ads agrupados por plataforma ──────────────────────────────
const adsByPlatform = computed(() => {
  const map = {}
  linkedAds.value.forEach(ad => {
    const m = adMetrics(ad)
    if (!map[ad.platform]) {
      map[ad.platform] = {
        platform:    ad.platform,
        spend:       0,
        impressions: 0,
        clicks:      0,
        conversions: 0,
        sales:       0,
      }
    }
    map[ad.platform].spend       += ad.spend  || 0
    map[ad.platform].impressions += m.impressions || 0
    map[ad.platform].clicks      += m.clicks      || 0
    map[ad.platform].conversions += m.conversions || 0
    map[ad.platform].sales       += ad.sales || 0
  })
  return Object.values(map).map(g => ({
    ...g,
    roas: g.spend > 0 ? g.sales / g.spend : 0,
  }))
})

// ── Duración y presupuesto ────────────────────────────────────
const campaignDays = computed(() => {
  if (!campaign.value) return 0
  return Math.round((new Date(campaign.value.endDate) - new Date(campaign.value.startDate)) / 86400000)
})
const budgetPct = computed(() =>
  campaign.value?.budget ? (campaign.value.cost / campaign.value.budget) * 100 : 0
)
const budgetClass = computed(() => {
  if (budgetPct.value > 100) return 'bd-over'
  if (budgetPct.value > 90)  return 'bd-warn'
  return 'bd-ok'
})

// ── Objetivos vs real ─────────────────────────────────────────
const targetRows = computed(() => {
  const c = campaign.value
  if (!c?.targets) return []
  return [
    { label: 'Vendes',       actual: c.sales,       target: c.targets.sales,       fmt: formatCurrency },
    { label: 'Conversions', actual: c.conversions, target: c.targets.conversions, fmt: formatNumber   },
    { label: 'Clics',       actual: c.clicks,      target: c.targets.clicks,      fmt: formatNumber   },
    { label: 'Abast',       actual: c.reach,       target: c.targets.reach,       fmt: formatNumber   },
  ].filter(t => t.target > 0)
})

// ── Products with aggregated metrics ─────────────────────────
const campaignProductsWithMetrics = computed(() => {
  const c = campaign.value
  if (!c?.productAssignments) return []

  const pa = c.productAssignments
  const productMap = new Map()

  function ensureProduct(p) {
    if (!productMap.has(p.id)) {
      productMap.set(p.id, {
        ...p,
        postCount: 0, infCount: 0, adCount: 0,
        reach: 0, clicks: 0, conversions: 0, sales: 0,
      })
    }
    return productMap.get(p.id)
  }

  // From posts
  for (const [postIdStr, products] of Object.entries(pa.posts || {})) {
    const post = linkedPosts.value.find(p => p.id === parseInt(postIdStr))
    for (const p of products) {
      const entry = ensureProduct(p)
      entry.postCount++
      if (post) {
        entry.reach  += post.reach  || 0
        entry.clicks += post.clicks || 0
      }
    }
  }

  // From influencers
  for (const [infIdStr, products] of Object.entries(pa.influencers || {})) {
    const collab = linkedCollabs.value.find(c => c.influencerId === parseInt(infIdStr))
    for (const p of products) {
      const entry = ensureProduct(p)
      entry.infCount++
      if (collab) {
        entry.sales       += collab.sales       || 0
        entry.conversions += collab.conversions || 0
      }
    }
  }

  // From ads
  for (const [, products] of Object.entries(pa.ads || {})) {
    for (const p of products) {
      const entry = ensureProduct(p)
      entry.adCount++
    }
  }

  return [...productMap.values()]
})

// ── Helpers ───────────────────────────────────────────────────
const CHANNEL_ICONS = { Megaphone, Users, Target }
function channelIcon(name) { return CHANNEL_ICONS[name] || Megaphone }
function pct(part, whole) { return whole > 0 ? (part / whole) * 100 : 0 }
function pctClass(v) { return v >= 100 ? 'pct-ok' : v >= 70 ? 'pct-mid' : 'pct-low' }
function roasClass(v) { return v >= 3 ? 'roas-good' : v >= 1 ? 'roas-ok' : 'roas-bad' }
function engClass(v)  { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function platformStyle(key)   { const p = getPlatform(key);   return { background: p.bg,  color: p.color } }
function adPlatformStyle(key) { const p = getAdPlatform(key); return { background: p.bg,  color: p.color } }
function thumbStyle(p) {
  const pl = getPlatform(p.platform)
  return { background: `linear-gradient(135deg, ${pl.color}cc, ${pl.color}66)` }
}
function avatarStyle(name) {
  const palette = [
    'linear-gradient(135deg,#667eea,#764ba2)',
    'linear-gradient(135deg,#f093fb,#f5576c)',
    'linear-gradient(135deg,#4facfe,#00f2fe)',
    'linear-gradient(135deg,#43e97b,#38f9d7)',
    'linear-gradient(135deg,#fa709a,#fee140)',
    'linear-gradient(135deg,#30cfd0,#330867)',
  ]
  return { background: palette[name.charCodeAt(0) % 6] }
}
function typeIcon(type) {
  return { 'Imatge': ImageIcon, 'Vídeo': Film, 'Reel': Film, 'Story': Layers,
           'Carrusel': Layers, 'Tweet': MessageSquare, 'Fil': MessageSquare, 'Short': Film }[type] || FileText
}
function formatDateShort(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('ca-ES', { day: '2-digit', month: 'short' })
}
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 1.375rem; }

/* ── Hero ───────────────────────────────────────── */
.hero {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.hero-badges { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
}
.badge-sm { font-size: 0.65rem; padding: 2px 7px; }
.obj-tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 5px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.hero-name {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0.25rem 0 0;
  line-height: 1.2;
}
.hero-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: var(--text-secondary);
}
.hero-days { font-weight: 600; color: var(--text-primary); }
.icon-muted { color: var(--text-secondary); flex-shrink: 0; }
.hero-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0.25rem 0 0;
}

/* ── KPIs ───────────────────────────────────────── */
.kpi-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr;
  gap: 0.5rem;
}
.kpi-block {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.75rem 0.875rem;
}
.kpi-primary {
  background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.05));
  border: 1px solid rgba(102,126,234,0.15);
}
.kb-label {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.3rem;
}
.kb-value {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.1;
}
.kb-sub {
  font-size: 0.68rem;
  color: var(--text-secondary);
  margin-top: 3px;
}
.roas-good { color: #10B981; }
.roas-ok   { color: #F59E0B; }
.roas-bad  { color: #EF4444; }

/* ── Presupuesto ────────────────────────────────── */
.budget-strip {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.bs-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bs-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}
.bs-pct {
  font-size: 0.82rem;
  font-weight: 700;
  font-feature-settings: "tnum";
}
.bs-pct.bd-ok   { color: #10B981; }
.bs-pct.bd-warn { color: #F59E0B; }
.bs-pct.bd-over { color: #EF4444; }
.bs-bar-wrap {
  height: 6px;
  background: var(--bg-secondary);
  border-radius: 3px;
  overflow: hidden;
}
.bs-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.bs-bar.bd-ok   { background: linear-gradient(90deg, #667eea, #764ba2); }
.bs-bar.bd-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.bs-bar.bd-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }

/* ── Canales resumen ────────────────────────────── */
.channels-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 0.5rem;
}
.ch-card {
  background: var(--bg-secondary);
  border: 2px solid transparent;
  border-radius: 10px;
  padding: 0.75rem 0.875rem;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  transition: all 0.18s ease;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.ch-card:hover {
  border-color: var(--ch-c);
  background: var(--bg-primary);
}
.ch-card.active {
  border-color: var(--ch-c);
  background: var(--bg-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ch-c) 12%, transparent);
}
.ch-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.ch-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ch-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-primary);
  flex: 1;
}
.ch-count {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border-radius: 999px;
  padding: 1px 7px;
}
.ch-sales {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  letter-spacing: -0.01em;
}
.ch-roas {
  font-size: 0.72rem;
  font-weight: 700;
}
.ch-bar-wrap {
  height: 3px;
  background: var(--border-color);
  border-radius: 2px;
  overflow: hidden;
}
.ch-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease;
}
.ch-contrib {
  font-size: 0.68rem;
  color: var(--text-secondary);
}

/* ── Detalle por canal ──────────────────────────── */
.channel-detail {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.cd-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.cd-tab {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.625rem 0.75rem;
  border: none;
  background: transparent;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.15s, border-color 0.15s;
  font-family: inherit;
}
.cd-tab:hover { color: var(--text-primary); }
.cd-tab.active {
  color: var(--primary-color);
  font-weight: 700;
  border-bottom-color: var(--primary-color);
  background: var(--bg-primary);
}
.cd-tab-count {
  font-size: 0.65rem;
  font-weight: 700;
  background: var(--bg-primary);
  color: var(--text-secondary);
  padding: 1px 6px;
  border-radius: 999px;
}
.cd-tab.active .cd-tab-count {
  background: rgba(102,126,234,0.1);
  color: var(--primary-color);
}

.tab-body { display: flex; flex-direction: column; }
.tab-empty {
  padding: 2rem 1.25rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Items list (posts + collabs) */
.items-list { display: flex; flex-direction: column; }
.item-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.625rem;
  align-items: center;
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.1s;
}
.item-row:last-child { border-bottom: none; }
.item-row:hover { background: var(--bg-secondary); }
.item-thumb {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.item-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.72rem;
  flex-shrink: 0;
}
.item-main { min-width: 0; }
.item-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.item-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 2px;
  font-size: 0.72rem;
  color: var(--text-secondary);
}
.plat-pill {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
}
.meta-txt { color: var(--text-secondary); }
.meta-sep { color: var(--text-secondary); }
.item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 3px;
}
.eng-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
}
.eng-high { background: rgba(16,185,129,0.12); color: #10B981; }
.eng-mid  { background: rgba(245,158,11,0.12); color: #F59E0B; }
.eng-low  { background: rgba(239,68,68,0.10); color: #EF4444; }
.item-sub {
  font-size: 0.68rem;
  color: var(--text-secondary);
  font-feature-settings: "tnum";
}
.item-sales {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text-primary);
  font-feature-settings: "tnum";
}

/* Anuncios de pago */
.ads-section { display: flex; flex-direction: column; }
.ad-platform {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--border-color);
}
.ad-platform:last-of-type { border-bottom: none; }
.ap-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.ap-sync {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.68rem;
  font-weight: 600;
  color: #10B981;
}
.ad-metrics {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.5rem;
}
.am-cell {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 0.5rem 0.625rem;
  text-align: center;
}
.am-val {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.1;
}
.am-key {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-top: 3px;
}
.ads-note {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  line-height: 1.45;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
}
.ads-note svg { flex-shrink: 0; margin-top: 1px; color: var(--text-secondary); }

/* ── Objetivos ──────────────────────────────────── */
.targets-section {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.targets-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
}
.targets-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.tc { display: flex; flex-direction: column; gap: 0.3rem; }
.tc-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.tc-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-primary);
}
.tc-pct {
  font-size: 0.72rem;
  font-weight: 700;
  font-feature-settings: "tnum";
}
.tc-bar-wrap { height: 5px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; }
.tc-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.pct-ok  .tc-bar, .tc-bar.pct-ok  { background: linear-gradient(90deg, #10B981, #059669); }
.pct-mid .tc-bar, .tc-bar.pct-mid { background: linear-gradient(90deg, #F59E0B, #D97706); }
.pct-low .tc-bar, .tc-bar.pct-low { background: linear-gradient(90deg, #EF4444, #B91C1C); }
.pct-ok  { color: #10B981; }
.pct-mid { color: #F59E0B; }
.pct-low { color: #EF4444; }
.tc-vals {
  display: flex;
  gap: 0.3rem;
  font-size: 0.7rem;
  font-feature-settings: "tnum";
}
.tc-actual { font-weight: 600; color: var(--text-primary); }
.tc-of { color: var(--text-secondary); }

/* ── Productes ──────────────────────────────────── */
.products-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.prods-header {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.625rem 1rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}
.prods-header-icon { color: var(--primary-color); opacity: 0.8; flex-shrink: 0; }
.prods-title {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
  flex: 1;
}
.prods-count {
  font-size: 0.68rem;
  font-weight: 700;
  background: rgba(102,126,234,0.1);
  color: var(--primary-color);
  padding: 1px 7px;
  border-radius: 999px;
}
.prods-list { display: flex; flex-direction: column; }
.prod-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 0.625rem;
  align-items: center;
  padding: 0.625rem 1rem;
  border-bottom: 1px solid var(--border-color);
  transition: background 0.1s;
}
.prod-item:last-child { border-bottom: none; }
.prod-item:hover { background: var(--bg-secondary); }

.pi-icon-wrap {
  width: 30px; height: 30px; border-radius: 8px;
  background: rgba(102,126,234,0.1); color: var(--primary-color);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.pi-info { min-width: 0; }
.pi-name {
  font-size: 0.82rem; font-weight: 600; color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.pi-meta {
  display: flex; align-items: center; gap: 0.3rem;
  margin-top: 2px; font-size: 0.7rem; color: var(--text-secondary);
}
.pi-sku {
  background: var(--bg-secondary); padding: 0 5px; border-radius: 4px;
  font-size: 0.65rem; font-weight: 600;
}
.pi-sep { opacity: 0.4; }
.pi-price { font-weight: 600; color: var(--text-primary); font-feature-settings: "tnum"; }

.pi-stats {
  display: flex; gap: 0.5rem;
}
.pi-stat { text-align: center; min-width: 40px; }
.pis-val {
  font-size: 0.75rem; font-weight: 700; color: var(--text-primary);
  font-feature-settings: "tnum"; line-height: 1.1;
}
.pis-key {
  font-size: 0.6rem; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.04em;
}

.pi-coverage {
  display: flex; gap: 0.25rem; flex-shrink: 0;
}
.cov-pill {
  display: inline-flex; align-items: center; gap: 0.2rem;
  font-size: 0.68rem; font-weight: 700; padding: 2px 6px; border-radius: 999px;
}
.cov-owned { background: rgba(102,126,234,0.12); color: #667eea; }
.cov-inf   { background: rgba(236,72,153,0.12);  color: #EC4899; }
.cov-ad    { background: rgba(245,158,11,0.12);  color: #F59E0B; }

/* ── Footer ─────────────────────────────────────── */
.panel-footer {
  display: flex;
  justify-content: flex-end;
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
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: inherit;
  transition: background 0.15s;
}
.panel-btn:hover { background: var(--bg-secondary); }

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
