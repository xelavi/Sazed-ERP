<template>
  <div v-if="campaign" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-meta">
        <span class="badge" :class="CAMPAIGN_STATUSES[campaign.status].cls">
          {{ CAMPAIGN_STATUSES[campaign.status].label }}
        </span>
        <span class="objective-tag">{{ campaign.objective }}</span>
      </div>
      <h2 class="hero-name">{{ campaign.name }}</h2>
      <div class="hero-period">
        <Calendar :size="13" />
        <span>{{ formatDate(campaign.startDate) }} → {{ formatDate(campaign.endDate) }}</span>
        <span class="period-days">· {{ campaignDays }} días</span>
      </div>
    </div>

    <!-- Performance hero stats -->
    <div class="perf-row">
      <div class="perf-tile perf-tile-primary">
        <div class="pt-key">Ventas</div>
        <div class="pt-val">{{ formatCurrency(campaign.sales) }}</div>
      </div>
      <div class="perf-tile">
        <div class="pt-key">ROAS</div>
        <div class="pt-val">
          <span :class="roasClass(campaign.roas)">{{ campaign.roas.toFixed(2) }}x</span>
        </div>
      </div>
    </div>

    <!-- Budget progress -->
    <section class="panel-section">
      <h3 class="section-title">Presupuesto</h3>
      <div class="budget-card">
        <div class="bd-row">
          <div>
            <div class="bd-spent">{{ formatCurrency(campaign.cost) }}</div>
            <div class="bd-key">gastado</div>
          </div>
          <div class="bd-aside">
            <div class="bd-budget">de {{ formatCurrency(campaign.budget) }}</div>
            <div class="bd-pct" :class="budgetClass">{{ budgetPct.toFixed(0) }}%</div>
          </div>
        </div>
        <div class="bd-bar-wrap">
          <div
            class="bd-bar"
            :class="budgetClass"
            :style="{ width: Math.min(budgetPct, 100) + '%' }"
          ></div>
        </div>
      </div>
    </section>

    <!-- KPI grid -->
    <section class="panel-section">
      <h3 class="section-title">Métricas</h3>
      <div class="kpi-grid">
        <div class="kpi-cell" v-for="kpi in campaignKPIs" :key="kpi.label">
          <component :is="kpi.icon" :size="13" class="kpi-icon" />
          <div class="kpi-val">{{ kpi.format(campaign[kpi.field]) }}</div>
          <div class="kpi-key">{{ kpi.label }}</div>
        </div>
      </div>
    </section>

    <!-- Description -->
    <section v-if="campaign.description" class="panel-section">
      <h3 class="section-title">Descripción</h3>
      <p class="notes-text">{{ campaign.description }}</p>
    </section>

    <!-- Linked posts -->
    <section class="panel-section">
      <div class="section-head">
        <h3 class="section-title">Publicaciones</h3>
        <span class="section-count">{{ linkedPosts.length }}</span>
      </div>
      <ul class="entity-list">
        <li
          v-for="p in linkedPosts.slice(0, 5)"
          :key="p.id"
          class="entity-item"
        >
          <div class="entity-thumb" :style="thumbStyle(p)">
            <component :is="typeIcon(p.type)" :size="11" />
          </div>
          <div class="entity-main">
            <div class="entity-title">{{ p.title }}</div>
            <div class="entity-meta">
              <span class="platform-pill" :style="platformStyle(p.platform)">
                {{ getPlatform(p.platform).label }}
              </span>
              <span class="muted">·</span>
              <span class="muted">{{ formatDateShort(p.date) }}</span>
            </div>
          </div>
          <span class="entity-eng" :class="engClass(p.engagement)">{{ p.engagement }}%</span>
        </li>
        <li v-if="!linkedPosts.length" class="entity-empty">Sin publicaciones vinculadas.</li>
      </ul>
      <div v-if="linkedPosts.length > 5" class="more-link">
        + {{ linkedPosts.length - 5 }} más
      </div>
    </section>

    <!-- Linked collaborations -->
    <section class="panel-section">
      <div class="section-head">
        <h3 class="section-title">Colaboraciones</h3>
        <span class="section-count">{{ linkedCollabs.length }}</span>
      </div>
      <ul class="entity-list">
        <li
          v-for="c in linkedCollabs"
          :key="c.id"
          class="entity-item entity-collab"
        >
          <div class="collab-avatar" :style="avatarStyle(c.influencerName)">
            {{ c.influencerName[0] }}
          </div>
          <div class="entity-main">
            <div class="entity-title">{{ c.influencerName }}</div>
            <div class="entity-meta">{{ c.format }}</div>
          </div>
          <div class="collab-stats">
            <div class="cs-sales">{{ formatCurrency(c.sales) }}</div>
            <span class="badge badge-sm" :class="COLLAB_STATUSES[c.status].cls">
              {{ COLLAB_STATUSES[c.status].label }}
            </span>
          </div>
        </li>
        <li v-if="!linkedCollabs.length" class="entity-empty">Sin colaboraciones.</li>
      </ul>
    </section>

    <!-- Timeline / milestones -->
    <section v-if="campaign.timeline?.length" class="panel-section">
      <h3 class="section-title">Cronología</h3>
      <ol class="timeline">
        <li
          v-for="(ev, i) in campaign.timeline"
          :key="i"
          class="tl-event"
          :class="'tl-' + ev.type"
        >
          <div class="tl-marker">
            <component :is="eventIcon(ev.type)" :size="11" />
          </div>
          <div class="tl-body">
            <div class="tl-date">{{ formatDate(ev.date) }}</div>
            <div class="tl-event-text">{{ ev.event }}</div>
          </div>
        </li>
      </ol>
    </section>

    <!-- Footer -->
    <div class="panel-footer">
      <button class="panel-btn panel-btn-ghost" @click="$emit('close')">Cerrar</button>
      <button class="panel-btn panel-btn-primary">
        <Pencil :size="13" />
        Editar
      </button>
    </div>
  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Campaña no encontrada.</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Calendar, Pencil, AlertCircle,
  Eye, MousePointer, Heart, Target, TrendingUp, ShoppingCart, DollarSign,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText,
  Flag, MessageCircle, CheckCircle,
} from 'lucide-vue-next'
import {
  socialCampaigns, socialPosts, socialCollaborations,
  CAMPAIGN_STATUSES, COLLAB_STATUSES,
  getPlatform, formatNumber, formatCurrency, formatDate,
} from '@/services/socialCrmData'

const props = defineProps({
  campaignId: { type: Number, required: true },
})

defineEmits(['close'])

const campaign = computed(() => socialCampaigns.find(c => c.id === props.campaignId))

const linkedPosts   = computed(() => socialPosts.filter(p => p.campaignId === props.campaignId))
const linkedCollabs = computed(() => socialCollaborations.filter(c => c.campaignId === props.campaignId))

const campaignDays = computed(() => {
  if (!campaign.value) return 0
  const start = new Date(campaign.value.startDate)
  const end = new Date(campaign.value.endDate)
  return Math.round((end - start) / 86400000)
})

const budgetPct = computed(() => {
  if (!campaign.value || !campaign.value.budget) return 0
  return (campaign.value.cost / campaign.value.budget) * 100
})

const budgetClass = computed(() => {
  if (budgetPct.value > 100) return 'bd-over'
  if (budgetPct.value > 90) return 'bd-warn'
  return 'bd-ok'
})

const campaignKPIs = [
  { label: 'Alcance',      field: 'reach',       icon: Eye,         format: formatNumber },
  { label: 'Impresiones',  field: 'impressions', icon: Eye,         format: formatNumber },
  { label: 'Engagement',   field: 'engagement',  icon: Heart,       format: v => v + '%' },
  { label: 'Clics',        field: 'clicks',      icon: MousePointer,format: formatNumber },
  { label: 'Conversiones', field: 'conversions', icon: ShoppingCart,format: formatNumber },
  { label: 'Coste',        field: 'cost',        icon: DollarSign,  format: formatCurrency },
]

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function thumbStyle(p) { const pl = getPlatform(p.platform); return { background: `linear-gradient(135deg, ${pl.color}cc, ${pl.color}66)` } }
function avatarStyle(name) {
  const seed = name.charCodeAt(0) % 6
  const palette = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)',
    'linear-gradient(135deg, #30cfd0, #330867)',
  ]
  return { background: palette[seed] }
}
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function roasClass(v) {
  if (v >= 3) return 'roas-good'
  if (v >= 1) return 'roas-ok'
  return 'roas-bad'
}
function typeIcon(type) {
  const map = { 'Imagen': ImageIcon, 'Vídeo': Film, 'Reel': Film, 'Story': Layers, 'Carrusel': Layers, 'Tweet': MessageSquare, 'Hilo': MessageSquare, 'Short': Film }
  return map[type] || FileText
}
function eventIcon(type) {
  const map = { milestone: Flag, post: FileText, review: CheckCircle }
  return map[type] || MessageCircle
}
function formatDateShort(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 1.25rem; }

/* Hero */
.panel-hero {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.hero-meta { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.badge { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.badge-sm { font-size: 0.65rem; padding: 2px 7px; }
.objective-tag {
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
.hero-period {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-feature-settings: "tnum";
}
.period-days { font-weight: 600; color: var(--text-primary); }

/* Performance row */
.perf-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 0.5rem;
}
.perf-tile {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.75rem 0.875rem;
}
.perf-tile-primary {
  background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.06));
}
.pt-key {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}
.pt-val {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.1;
}

.roas-good { color: #10B981; }
.roas-ok   { color: #F59E0B; }
.roas-bad  { color: #EF4444; }

/* Sections */
.panel-section { display: flex; flex-direction: column; gap: 0.625rem; }
.section-head { display: flex; align-items: center; justify-content: space-between; }
.section-title {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--primary-color);
  margin: 0;
}
.section-count {
  font-size: 0.7rem;
  font-weight: 600;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 999px;
}

/* Budget */
.budget-card {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.75rem 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.bd-row { display: flex; align-items: flex-end; justify-content: space-between; }
.bd-spent { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; line-height: 1.05; }
.bd-key { font-size: 0.68rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 1px; }
.bd-aside { text-align: right; }
.bd-budget { font-size: 0.72rem; color: var(--text-secondary); }
.bd-pct { font-size: 0.95rem; font-weight: 800; font-feature-settings: "tnum"; line-height: 1; }
.bd-pct.bd-ok   { color: #10B981; }
.bd-pct.bd-warn { color: #F59E0B; }
.bd-pct.bd-over { color: #EF4444; }

.bd-bar-wrap { height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; }
.bd-bar { height: 100%; border-radius: 3px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.bd-bar.bd-ok   { background: linear-gradient(90deg, #667eea, #764ba2); }
.bd-bar.bd-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.bd-bar.bd-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }

/* KPI grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}
.kpi-cell {
  background: var(--bg-secondary);
  border-radius: 9px;
  padding: 0.625rem 0.75rem;
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: 0 0.5rem;
  align-items: center;
}
.kpi-icon { grid-row: 1 / 3; color: var(--text-secondary); }
.kpi-val { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.kpi-key { font-size: 0.7rem; color: var(--text-secondary); }

/* Notes */
.notes-text {
  font-size: 0.85rem;
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
  background: var(--bg-secondary);
  padding: 0.75rem 0.875rem;
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

/* Entity lists (posts / collabs) */
.entity-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.entity-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.625rem;
  align-items: center;
  padding: 0.5rem 0.625rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}
.entity-thumb {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.entity-main { min-width: 0; }
.entity-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.entity-meta {
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-top: 1px;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}
.platform-pill { font-size: 0.65rem; font-weight: 600; padding: 1px 6px; border-radius: 999px; }
.muted { color: var(--text-secondary); }

.entity-eng { font-size: 0.78rem; font-weight: 700; }
.eng-high { color: #10B981; }
.eng-mid  { color: #F59E0B; }
.eng-low  { color: #EF4444; }

.entity-empty { padding: 0.875rem; text-align: center; color: var(--text-secondary); font-size: 0.825rem; background: var(--bg-secondary); border-radius: 8px; }

.collab-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.72rem;
}

.collab-stats { display: flex; flex-direction: column; align-items: flex-end; gap: 3px; }
.cs-sales { font-size: 0.78rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }

.more-link {
  text-align: center;
  font-size: 0.78rem;
  color: var(--primary-color);
  padding: 0.4rem;
  font-weight: 600;
  cursor: pointer;
}
.more-link:hover { text-decoration: underline; }

/* Timeline */
.timeline {
  list-style: none;
  padding: 0 0 0 0.5rem;
  margin: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 12px;
  top: 5px;
  bottom: 5px;
  width: 2px;
  background: var(--border-color);
  border-radius: 1px;
}

.tl-event {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.625rem;
  align-items: flex-start;
  position: relative;
}

.tl-marker {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  border: 2px solid var(--border-color);
  color: var(--text-secondary);
  flex-shrink: 0;
  z-index: 2;
}
.tl-event.tl-milestone .tl-marker { border-color: #667eea; color: #667eea; background: rgba(102,126,234,0.08); }
.tl-event.tl-post      .tl-marker { border-color: #10B981; color: #10B981; background: rgba(16,185,129,0.08); }
.tl-event.tl-review    .tl-marker { border-color: #F59E0B; color: #F59E0B; background: rgba(245,158,11,0.08); }

.tl-body { padding-top: 1px; }
.tl-date {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}
.tl-event-text { font-size: 0.825rem; color: var(--text-primary); margin-top: 1px; }

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
