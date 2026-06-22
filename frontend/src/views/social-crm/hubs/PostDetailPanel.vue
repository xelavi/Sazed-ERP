<template>
  <div v-if="post" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-meta">
        <span class="platform-pill" :style="platformStyle(post.platform)">
          {{ getPlatform(post.platform).label }}
        </span>
        <span class="type-tag">{{ post.type }}</span>
        <span class="date-text">{{ formatDate(post.date) }}</span>
      </div>
      <h2 class="hero-title">{{ post.title }}</h2>
      <div class="hero-meta-row">
        <span v-if="post.accountName" class="meta-bit">
          <AtSign :size="12" />
          {{ post.accountName }}
        </span>
        <span v-if="post.campaignName" class="meta-bit">
          <Target :size="12" />
          {{ post.campaignName }}
        </span>
      </div>
    </div>

    <!-- Engagement headline -->
    <div class="engagement-feature" :class="engClass(post.engagement)">
      <div class="ef-row">
        <div>
          <div class="ef-label">Engagement</div>
          <div class="ef-value">{{ post.engagement }}%</div>
        </div>
        <div class="ef-aside">
          <div class="ef-tag">{{ engLabel(post.engagement) }}</div>
          <div v-if="posts.length > 1" class="ef-sub">mitjana: {{ avgEngagement.toFixed(1) }}%</div>
        </div>
      </div>
      <div class="ef-bar-wrap">
        <div
          class="ef-bar"
          :style="{ width: Math.min(post.engagement * 10, 100) + '%' }"
        ></div>
      </div>
    </div>

    <!-- Preview -->
    <section v-if="hasPreview" class="panel-section">
      <h3 class="section-title">Vista prèvia</h3>

      <div v-if="youtubeId" class="preview-embed">
        <iframe
          :src="`https://www.youtube.com/embed/${youtubeId}`"
          title="Reproductor de YouTube"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowfullscreen
        ></iframe>
      </div>

      <a
        v-else-if="post.thumbnail"
        :href="post.post_url || undefined"
        target="_blank"
        rel="noopener"
        class="preview-thumb"
      >
        <img :src="post.thumbnail" :alt="post.title" />
      </a>

      <a
        v-if="post.post_url"
        :href="post.post_url"
        target="_blank"
        rel="noopener"
        class="preview-link"
      >
        Obrir publicació original a {{ getPlatform(post.platform).label }}
        <ExternalLink :size="11" />
      </a>
    </section>

    <!-- KPI grid (real metrics, mateixos valors que la fila) -->
    <section class="panel-section">
      <h3 class="section-title">Mètriques</h3>
      <div class="kpi-grid">
        <div class="kpi-cell" v-for="kpi in postKPIs" :key="kpi.label">
          <component :is="kpi.icon" :size="13" class="kpi-icon" />
          <div class="kpi-val">{{ formatNumber(kpi.value) }}</div>
          <div class="kpi-key">{{ kpi.label }}</div>
        </div>
      </div>
    </section>

    <!-- Comparativa -->
    <section v-if="posts.length > 1" class="panel-section">
      <h3 class="section-title">vs. mitjana del període</h3>
      <div class="compare-list">
        <div v-for="m in compareMetrics" :key="m.label" class="compare-row">
          <span class="cmp-label">{{ m.label }}</span>
          <div class="cmp-bars">
            <span class="cmp-this">{{ m.format(post[m.field]) }}</span>
            <span class="cmp-sep">/</span>
            <span class="cmp-avg">{{ m.format(m.avg) }}</span>
          </div>
          <div class="cmp-diff" :class="post[m.field] >= m.avg ? 'pos' : 'neg'">
            <component :is="post[m.field] >= m.avg ? TrendingUp : TrendingDown" :size="11" />
            {{ Math.abs(((post[m.field] - m.avg) / (m.avg || 1)) * 100).toFixed(0) }}%
          </div>
        </div>
      </div>
    </section>

    <!-- Detalls -->
    <section class="panel-section">
      <h3 class="section-title">Detalls</h3>
      <dl class="info-list">
        <div class="info-row">
          <dt>Tipus</dt>
          <dd>{{ post.type }}</dd>
        </div>
        <div class="info-row">
          <dt>Publicat</dt>
          <dd>{{ formatDate(post.date) }}</dd>
        </div>
        <div class="info-row">
          <dt>Campanya</dt>
          <dd>{{ post.campaignName || '—' }}</dd>
        </div>
        <div v-if="post.post_url" class="info-row">
          <dt>Enllaç</dt>
          <dd>
            <a :href="post.post_url" target="_blank" rel="noopener" class="link-inline">
              Veure original
              <ExternalLink :size="11" />
            </a>
          </dd>
        </div>
      </dl>
    </section>

    <!-- Footer -->
    <div class="panel-footer">
      <button class="panel-btn panel-btn-ghost" @click="$emit('close')">Tancar</button>
      <a
        v-if="post.post_url"
        class="panel-btn panel-btn-primary"
        :href="post.post_url"
        target="_blank"
        rel="noopener"
      >
        <ExternalLink :size="14" />
        Obrir publicació
      </a>
    </div>
  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Publicació no trobada.</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  AtSign, Target, ExternalLink, AlertCircle,
  Heart, MessageCircle, MousePointer, BarChart2,
  TrendingUp, TrendingDown,
} from 'lucide-vue-next'
import { getPlatform, formatNumber, formatDate } from '@/services/socialCrmData'

const props = defineProps({
  postId: { type: [Number, String], required: true },
  posts:  { type: Array, default: () => [] },
})

defineEmits(['close'])

// Read the real post from the list passed by the hub (DB-backed data),
// never from mock data — guarantees platform/metrics match the table row.
const post = computed(() => props.posts.find(p => p.id === props.postId) || null)

// Real metrics only, identical values to the table row.
const postKPIs = computed(() => {
  const p = post.value
  if (!p) return []
  return [
    { label: 'Abast',      value: p.reach,    icon: BarChart2 },
    { label: 'M\'agrada',  value: p.likes,    icon: Heart },
    { label: 'Comentaris', value: p.comments, icon: MessageCircle },
    { label: 'Clics',      value: p.clicks,   icon: MousePointer },
  ]
})

const avgEngagement = computed(() => {
  if (!props.posts.length) return 0
  return props.posts.reduce((s, p) => s + (p.engagement || 0), 0) / props.posts.length
})

const compareMetrics = computed(() => {
  const list = props.posts
  const avg = (field) => list.length ? list.reduce((s, p) => s + (p[field] || 0), 0) / list.length : 0
  return [
    { label: 'Abast',      field: 'reach',      avg: Math.round(avg('reach')),                  format: formatNumber },
    { label: 'Engagement', field: 'engagement', avg: parseFloat(avg('engagement').toFixed(1)),  format: v => v + '%' },
    { label: 'M\'agrada',  field: 'likes',      avg: Math.round(avg('likes')),                  format: formatNumber },
    { label: 'Comentaris', field: 'comments',   avg: Math.round(avg('comments')),               format: formatNumber },
  ]
})

// YouTube video id extracted from the stored post URL → enables the embed player.
const youtubeId = computed(() => {
  const p = post.value
  if (!p || p.platform !== 'youtube') return ''
  const m = (p.post_url || '').match(/[?&]v=([\w-]+)/)
  return m ? m[1] : ''
})

const hasPreview = computed(() => {
  const p = post.value
  return !!(p && (youtubeId.value || p.thumbnail || p.post_url))
})

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function engLabel(v) { return v >= 6 ? 'Molt alt' : v >= 4 ? 'Alt' : v >= 2 ? 'Mitjà' : 'Baix' }
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
.hero-meta { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.platform-pill { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; }
.type-tag {
  font-size: 0.7rem;
  padding: 2px 7px;
  border-radius: 5px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 500;
}
.date-text {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-left: auto;
}
.hero-title {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
}
.hero-meta-row { display: flex; flex-wrap: wrap; gap: 0.625rem; align-items: center; }
.meta-bit {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  color: var(--text-secondary);
}
.meta-bit svg { color: var(--text-secondary); opacity: 0.7; }

/* Engagement feature */
.engagement-feature {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 0.875rem 1rem;
  position: relative;
  overflow: hidden;
}
.engagement-feature::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at top right, currentColor, transparent 70%);
  opacity: 0.06;
  pointer-events: none;
}
.engagement-feature.eng-high { color: #10B981; }
.engagement-feature.eng-mid  { color: #F59E0B; }
.engagement-feature.eng-low  { color: #EF4444; }

.ef-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.625rem;
  position: relative;
}
.ef-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
.ef-value {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
  color: currentColor;
  font-feature-settings: "tnum";
}
.ef-aside { text-align: right; }
.ef-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 999px;
  background: currentColor;
  color: var(--bg-primary);
  margin-bottom: 0.25rem;
}
.engagement-feature.eng-high .ef-tag { background: rgba(16,185,129,0.18); color: #10B981; }
.engagement-feature.eng-mid  .ef-tag { background: rgba(245,158,11,0.18); color: #F59E0B; }
.engagement-feature.eng-low  .ef-tag { background: rgba(239,68,68,0.14); color: #EF4444; }

.ef-sub { font-size: 0.7rem; color: var(--text-secondary); }

.ef-bar-wrap {
  height: 5px;
  background: rgba(0,0,0,0.05);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}
.ef-bar {
  height: 100%;
  background: currentColor;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

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

/* Preview */
.preview-embed {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: #000;
}
.preview-embed iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
.preview-thumb {
  display: block;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  line-height: 0;
}
.preview-thumb img { width: 100%; height: auto; display: block; }
.preview-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
}
.preview-link:hover { text-decoration: underline; }

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

/* Compare */
.compare-list { display: flex; flex-direction: column; gap: 0.4rem; }
.compare-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.625rem;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}
.cmp-label { font-size: 0.78rem; color: var(--text-primary); font-weight: 500; }
.cmp-bars { display: inline-flex; align-items: baseline; gap: 0.3rem; font-feature-settings: "tnum"; }
.cmp-this { font-size: 0.85rem; font-weight: 700; color: var(--text-primary); }
.cmp-sep  { color: var(--text-secondary); opacity: 0.5; }
.cmp-avg  { font-size: 0.78rem; color: var(--text-secondary); }

.cmp-diff {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 5px;
}
.cmp-diff.pos { background: rgba(16,185,129,0.12); color: #10B981; }
.cmp-diff.neg { background: rgba(239,68,68,0.12);  color: #EF4444; }

/* Info list */
.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.info-row { display: flex; justify-content: space-between; font-size: 0.85rem; align-items: baseline; gap: 1rem; }
.info-row dt { color: var(--text-secondary); margin: 0; }
.info-row dd { color: var(--text-primary); margin: 0; text-align: right; }
.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; font-weight: 600; }

.link-inline {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
}
.link-inline:hover { text-decoration: underline; }

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
  text-decoration: none;
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
