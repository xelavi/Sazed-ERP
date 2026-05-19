<template>
  <div v-if="inf" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-avatar" :style="avatarStyle">{{ inf.name[0] }}</div>
      <div class="hero-info">
        <h2 class="hero-name">{{ inf.name }}</h2>
        <div class="hero-alias">{{ inf.alias }}</div>
        <div class="hero-platforms">
          <span
            v-for="plt in inf.platforms"
            :key="plt"
            class="platform-pill"
            :style="platformStyle(plt)"
          >
            {{ getPlatform(plt).label }}
          </span>
          <span class="status-chip" :class="'st-' + inf.status">
            <span class="status-dot"></span>
            {{ statusLabel(inf.status) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Quick stats -->
    <div class="quick-stats">
      <div class="qs-cell">
        <div class="qs-key">Seguidores</div>
        <div class="qs-val">{{ formatNumber(inf.followers) }}</div>
      </div>
      <div class="qs-cell">
        <div class="qs-key">Engagement</div>
        <div class="qs-val">
          <span :class="engClass(inf.engagementMid)">{{ inf.engagementMid }}%</span>
        </div>
      </div>
      <div class="qs-cell">
        <div class="qs-key">Ventas atrib.</div>
        <div class="qs-val">{{ formatCurrency(inf.salesGenerated) }}</div>
      </div>
      <div class="qs-cell">
        <div class="qs-key">Rating</div>
        <div class="qs-val rating-cell">
          <Star :size="14" class="star-filled" />
          <span>{{ inf.rating > 0 ? inf.rating.toFixed(1) : '—' }}</span>
        </div>
      </div>
    </div>

    <!-- Profile details -->
    <section class="panel-section">
      <h3 class="section-title">Perfil</h3>
      <dl class="info-list">
        <div class="info-row"><dt>Nicho</dt><dd>{{ inf.niche }}</dd></div>
        <div class="info-row"><dt>Contacto</dt><dd>{{ inf.contact }}</dd></div>
        <div class="info-row"><dt>Agencia</dt><dd>{{ inf.agency || '—' }}</dd></div>
        <div class="info-row"><dt>País</dt><dd>{{ inf.country }}</dd></div>
        <div class="info-row"><dt>Idioma</dt><dd>{{ inf.language }}</dd></div>
      </dl>
    </section>

    <!-- Internal rating -->
    <section v-if="inf.collaborations > 0" class="panel-section">
      <h3 class="section-title">Valoración interna</h3>
      <div class="rating-list">
        <div class="rating-row" v-for="r in ratingDimensions" :key="r.key">
          <div class="rating-name">{{ r.label }}</div>
          <div class="rating-bar-wrap">
            <div
              class="rating-bar"
              :style="{ width: (inf[r.key] / 5 * 100) + '%', background: ratingColor(inf[r.key]) }"
            ></div>
          </div>
          <div class="rating-score">{{ inf[r.key].toFixed(1) }}</div>
        </div>
      </div>
    </section>

    <!-- Notes -->
    <section v-if="inf.notes" class="panel-section">
      <h3 class="section-title">Notas internas</h3>
      <p class="notes-text">{{ inf.notes }}</p>
    </section>

    <!-- Collab history -->
    <section class="panel-section">
      <div class="section-head">
        <h3 class="section-title">Historial de colaboraciones</h3>
        <span class="section-count">{{ collabs.length }}</span>
      </div>
      <ul class="collab-list">
        <li
          v-for="c in collabs"
          :key="c.id"
          class="collab-item"
          @click="$emit('open-collab', c.id)"
        >
          <div class="collab-main">
            <div class="collab-name">{{ c.campaignName }}</div>
            <div class="collab-meta">{{ c.format }} · {{ formatDate(c.publishDate) }}</div>
          </div>
          <div class="collab-stats">
            <div class="collab-sales">{{ formatCurrency(c.sales) }}</div>
            <span class="badge" :class="COLLAB_STATUSES[c.status].cls">
              {{ COLLAB_STATUSES[c.status].label }}
            </span>
          </div>
        </li>
        <li v-if="!collabs.length" class="collab-empty">Sin colaboraciones registradas.</li>
      </ul>
    </section>

    <!-- Actions -->
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
    <span>Influencer no encontrado.</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Star, Pencil, AlertCircle } from 'lucide-vue-next'
import {
  socialInfluencers, socialCollaborations, COLLAB_STATUSES,
  getPlatform, formatNumber, formatCurrency, formatDate,
} from '@/services/socialCrmData'

const props = defineProps({
  influencerId: { type: Number, required: true },
})

defineEmits(['close', 'open-collab'])

const inf = computed(() => socialInfluencers.find(i => i.id === props.influencerId))
const collabs = computed(() =>
  socialCollaborations.filter(c => c.influencerId === props.influencerId)
)

const ratingDimensions = [
  { key: 'contentQuality', label: 'Calidad del contenido' },
  { key: 'reliability',    label: 'Cumplimiento' },
  { key: 'brandAffinity',  label: 'Afinidad con la marca' },
  { key: 'reputationRisk', label: 'Riesgo reputacional (inv.)' },
]

const avatarStyle = computed(() => {
  if (!inf.value) return {}
  const seed = (inf.value.name.charCodeAt(0) + inf.value.id) % 6
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

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function statusLabel(s) { return s === 'active' ? 'Activo' : s === 'prospect' ? 'Prospecto' : 'Archivado' }
function ratingColor(v) { return v >= 4 ? '#10B981' : v >= 2.5 ? '#F59E0B' : '#EF4444' }
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
</script>

<style scoped>
.panel { display: flex; flex-direction: column; gap: 1.25rem; }

/* Hero */
.panel-hero {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border-color);
}

.hero-avatar {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 1.4rem;
  flex-shrink: 0;
  box-shadow: 0 6px 14px rgba(15,23,42,0.10);
}

.hero-info { min-width: 0; flex: 1; }
.hero-name {
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  margin: 0 0 2px;
  line-height: 1.2;
}
.hero-alias { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
.hero-platforms { display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center; }

.platform-pill {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.st-active   .status-dot { background: #10B981; }
.st-prospect .status-dot { background: #F59E0B; }
.st-archived .status-dot { background: #94A3B8; }

/* Quick stats grid */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}
.qs-cell {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.625rem 0.75rem;
}
.qs-key {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
}
.qs-val {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  font-feature-settings: "tnum";
}
.rating-cell { display: flex; align-items: center; gap: 0.3rem; }
.star-filled { color: #F59E0B; fill: #F59E0B; }

.eng-high { color: #10B981; }
.eng-mid  { color: #F59E0B; }
.eng-low  { color: #EF4444; }

/* Sections */
.panel-section {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
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

/* Info list */
.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  align-items: baseline;
  gap: 1rem;
}
.info-row dt { color: var(--text-secondary); margin: 0; flex-shrink: 0; }
.info-row dd { color: var(--text-primary); margin: 0; text-align: right; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Rating bars */
.rating-list { display: flex; flex-direction: column; gap: 0.5rem; }
.rating-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr auto;
  gap: 0.625rem;
  align-items: center;
}
.rating-name { font-size: 0.78rem; color: var(--text-primary); }
.rating-bar-wrap { height: 5px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.rating-bar { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.rating-score { font-size: 0.78rem; font-weight: 700; color: var(--text-primary); min-width: 24px; text-align: right; font-feature-settings: "tnum"; }

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

/* Collab list */
.collab-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.collab-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.collab-item:hover {
  background: var(--bg-primary);
  box-shadow: 0 2px 6px rgba(15,23,42,0.06);
  transform: translateX(2px);
}
.collab-main { flex: 1; min-width: 0; }
.collab-name { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); }
.collab-meta { font-size: 0.72rem; color: var(--text-secondary); margin-top: 1px; }
.collab-stats { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.collab-sales { font-size: 0.85rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.collab-empty { padding: 1rem; text-align: center; color: var(--text-secondary); font-size: 0.825rem; background: var(--bg-secondary); border-radius: 8px; }

.badge { font-size: 0.68rem; font-weight: 600; padding: 2px 7px; border-radius: 999px; }

/* Footer */
.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  position: sticky;
  bottom: -1rem;
  background: linear-gradient(180deg, transparent, var(--bg-primary) 30%);
  padding-bottom: 0.5rem;
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

/* Empty */
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
