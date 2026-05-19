<template>
  <div v-if="collab" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-meta">
        <span class="badge" :class="COLLAB_STATUSES[collab.status].cls">
          {{ COLLAB_STATUSES[collab.status].label }}
        </span>
        <code class="code-chip">{{ collab.code }}</code>
      </div>
      <h2 class="hero-title">{{ collab.campaignName }}</h2>
      <div class="hero-influencer" @click="$emit('open-influencer', collab.influencerId)">
        <div class="hero-avatar" :style="avatarStyle">{{ collab.influencerName[0] }}</div>
        <div>
          <div class="hi-name">{{ collab.influencerName }}</div>
          <div class="hi-alias">{{ collab.influencerAlias }}</div>
        </div>
        <ArrowUpRight :size="14" class="hi-arrow" />
      </div>
    </div>

    <!-- Performance vs Expected -->
    <section class="panel-section">
      <h3 class="section-title">Rendimiento vs. esperado</h3>
      <div class="perf-grid">
        <div class="perf-row" v-for="m in perfMetrics" :key="m.key">
          <div class="perf-name">{{ m.label }}</div>
          <div class="perf-bars">
            <div class="perf-bar-wrap">
              <div
                class="perf-bar perf-bar-actual"
                :style="{ width: barWidth(m.actual, m.expected) + '%' }"
              ></div>
            </div>
            <div class="perf-vals">
              <span class="perf-val">{{ formatVal(m.actual, m.format) }}</span>
              <span class="perf-expected">/ {{ formatVal(m.expected, m.format) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Engagement metrics -->
    <section class="panel-section">
      <h3 class="section-title">Métricas reportadas</h3>
      <div class="metrics-grid">
        <div class="metric-cell">
          <Heart :size="14" />
          <div class="m-val">{{ formatNumber(collab.likes) }}</div>
          <div class="m-key">Likes</div>
        </div>
        <div class="metric-cell">
          <MessageCircle :size="14" />
          <div class="m-val">{{ formatNumber(collab.comments) }}</div>
          <div class="m-key">Comentarios</div>
        </div>
        <div class="metric-cell">
          <Share2 :size="14" />
          <div class="m-val">{{ formatNumber(collab.shares) }}</div>
          <div class="m-key">Compartidos</div>
        </div>
        <div class="metric-cell">
          <Eye :size="14" />
          <div class="m-val">{{ formatNumber(collab.impressions) }}</div>
          <div class="m-key">Impresiones</div>
        </div>
      </div>
    </section>

    <!-- Acuerdo -->
    <section class="panel-section">
      <h3 class="section-title">Acuerdo</h3>
      <dl class="info-list">
        <div class="info-row"><dt>Formato</dt><dd>{{ collab.format }}</dd></div>
        <div class="info-row"><dt>Publicación</dt><dd>{{ formatDate(collab.publishDate) }}</dd></div>
        <div class="info-row"><dt>Coste</dt><dd class="font-mono">{{ formatCurrency(collab.cost) }}</dd></div>
        <div class="info-row" v-if="roas">
          <dt>ROAS</dt>
          <dd>
            <span class="roas-pill" :class="roasClass">{{ roas.toFixed(2) }}x</span>
          </dd>
        </div>
      </dl>
    </section>

    <!-- Deliverables -->
    <section v-if="collab.deliverables" class="panel-section">
      <h3 class="section-title">Entregables</h3>
      <p class="deliverables-text">{{ collab.deliverables }}</p>
    </section>

    <!-- Evidences -->
    <section v-if="collab.evidences?.length" class="panel-section">
      <h3 class="section-title">Evidencias</h3>
      <ul class="ev-list">
        <li v-for="ev in collab.evidences" :key="ev" class="ev-item">
          <Paperclip :size="13" />
          <span>{{ ev }}</span>
        </li>
      </ul>
    </section>

    <!-- Observations -->
    <section v-if="collab.observations || collab.recommendation" class="panel-section">
      <h3 class="section-title">Observaciones</h3>
      <p v-if="collab.observations" class="notes-text">{{ collab.observations }}</p>
      <p v-if="collab.recommendation" class="reco-text">
        <ThumbsUp :size="13" />
        <span>{{ collab.recommendation }}</span>
      </p>
    </section>

    <!-- Footer actions -->
    <div class="panel-footer">
      <button class="panel-btn panel-btn-ghost" @click="$emit('close')">Cerrar</button>
      <button class="panel-btn panel-btn-primary">
        <Pencil :size="14" />
        Editar
      </button>
    </div>
  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Colaboración no encontrada.</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  ArrowUpRight, Heart, MessageCircle, Share2, Eye,
  Paperclip, Pencil, ThumbsUp, AlertCircle,
} from 'lucide-vue-next'
import {
  socialCollaborations, COLLAB_STATUSES,
  formatNumber, formatCurrency, formatDate,
} from '@/services/socialCrmData'

const props = defineProps({
  collabId: { type: Number, required: true },
})

defineEmits(['close', 'open-influencer'])

const collab = computed(() => socialCollaborations.find(c => c.id === props.collabId))

const perfMetrics = computed(() => {
  if (!collab.value) return []
  return [
    { key: 'reach',       label: 'Alcance',     actual: collab.value.reach,       expected: collab.value.expectedReach,       format: 'number' },
    { key: 'clicks',      label: 'Clics',       actual: collab.value.clicks,      expected: collab.value.expectedClicks,      format: 'number' },
    { key: 'conversions', label: 'Conversiones',actual: collab.value.conversions, expected: collab.value.expectedConversions, format: 'number' },
  ].filter(m => m.expected > 0 || m.actual > 0)
})

const roas = computed(() => {
  if (!collab.value || !collab.value.cost) return null
  return collab.value.sales / collab.value.cost
})

const roasClass = computed(() => {
  if (!roas.value) return ''
  if (roas.value >= 3) return 'roas-good'
  if (roas.value >= 1) return 'roas-ok'
  return 'roas-bad'
})

const avatarStyle = computed(() => {
  if (!collab.value) return {}
  const seed = collab.value.influencerName.charCodeAt(0) % 6
  const palette = [
    'linear-gradient(135deg, #667eea, #764ba2)',
    'linear-gradient(135deg, #f093fb, #f5576c)',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    'linear-gradient(135deg, #43e97b, #38f9d7)',
    'linear-gradient(135deg, #fa709a, #fee140)',
    'linear-gradient(135deg, #30cfd0, #330867)',
  ]
  return { background: palette[seed] }
})

function barWidth(actual, expected) {
  if (!expected) return actual > 0 ? 100 : 0
  return Math.min((actual / expected) * 100, 130)
}

function formatVal(v, fmt) {
  if (fmt === 'number') return formatNumber(v)
  if (fmt === 'currency') return formatCurrency(v)
  return v
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

.hero-meta { display: flex; align-items: center; gap: 0.5rem; }
.badge { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.code-chip {
  background: var(--bg-secondary);
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 0.78rem;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  color: var(--text-primary);
  font-weight: 500;
}

.hero-title {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.25;
}

.hero-influencer {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.hero-influencer:hover {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.04);
}

.hero-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.hi-name { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); }
.hi-alias { font-size: 0.72rem; color: var(--text-secondary); }
.hi-arrow { color: var(--text-secondary); margin-left: auto; transition: transform 0.15s ease; }
.hero-influencer:hover .hi-arrow { color: var(--primary-color); transform: translate(2px, -2px); }

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

/* Performance bars */
.perf-grid { display: flex; flex-direction: column; gap: 0.625rem; }
.perf-row { display: flex; flex-direction: column; gap: 0.3rem; }
.perf-name { font-size: 0.78rem; color: var(--text-primary); font-weight: 500; }
.perf-bars { display: flex; align-items: center; gap: 0.625rem; }
.perf-bar-wrap {
  flex: 1;
  height: 7px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}
.perf-bar-wrap::before {
  content: '';
  position: absolute;
  left: calc(100% / 1.3);
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(0,0,0,0.18);
  z-index: 1;
}
.perf-bar { height: 100%; border-radius: 4px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.perf-bar-actual { background: linear-gradient(90deg, #667eea, #764ba2); }
.perf-vals { display: flex; align-items: baseline; gap: 0.25rem; min-width: 90px; justify-content: flex-end; }
.perf-val { font-size: 0.825rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.perf-expected { font-size: 0.72rem; color: var(--text-secondary); font-feature-settings: "tnum"; }

/* Engagement metrics grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}
.metric-cell {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.625rem 0.75rem;
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: 0 0.5rem;
  align-items: center;
}
.metric-cell svg { grid-row: 1 / 3; color: var(--text-secondary); }
.m-val { font-size: 1rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.m-key { font-size: 0.7rem; color: var(--text-secondary); }

/* Info list */
.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.info-row { display: flex; justify-content: space-between; font-size: 0.85rem; align-items: baseline; gap: 1rem; }
.info-row dt { color: var(--text-secondary); margin: 0; }
.info-row dd { color: var(--text-primary); margin: 0; text-align: right; }
.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; font-weight: 600; }

.roas-pill {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 999px;
}
.roas-good { background: rgba(16,185,129,0.14); color: #10B981; }
.roas-ok   { background: rgba(245,158,11,0.14); color: #F59E0B; }
.roas-bad  { background: rgba(239,68,68,0.10); color: #EF4444; }

/* Deliverables */
.deliverables-text {
  font-size: 0.85rem;
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0;
  background: var(--bg-secondary);
  padding: 0.75rem 0.875rem;
  border-radius: 8px;
}

/* Evidences */
.ev-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.3rem; }
.ev-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.625rem;
  background: var(--bg-secondary);
  border-radius: 7px;
  font-size: 0.8rem;
  color: var(--text-primary);
}
.ev-item svg { color: var(--text-secondary); flex-shrink: 0; }

/* Observations */
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

.reco-text {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  font-size: 0.825rem;
  color: var(--text-primary);
  line-height: 1.5;
  margin: 0.5rem 0 0;
  padding: 0.625rem 0.75rem;
  background: rgba(16,185,129,0.08);
  border-radius: 8px;
  border-left: 3px solid #10B981;
}
.reco-text svg { color: #10B981; flex-shrink: 0; margin-top: 2px; }

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
