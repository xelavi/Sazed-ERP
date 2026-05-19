<template>
  <div v-if="account" class="panel">
    <!-- Hero -->
    <div class="panel-hero">
      <div class="hero-head">
        <span class="platform-pill" :style="platformStyle(account.platform)">
          {{ getPlatform(account.platform).label }}
        </span>
        <span class="acc-status" :class="account.status === 'connected' ? 'st-on' : 'st-off'">
          <span class="status-dot"></span>
          {{ account.status === 'connected' ? 'Conectada' : 'Desconectada' }}
        </span>
      </div>
      <h2 class="hero-name">{{ account.name }}</h2>
      <div class="hero-handle">{{ account.username }}</div>
    </div>

    <!-- Stats -->
    <div class="quick-stats">
      <div class="qs-cell">
        <div class="qs-key">Seguidores</div>
        <div class="qs-val">{{ formatNumber(account.followers) }}</div>
      </div>
      <div class="qs-cell">
        <div class="qs-key">Publicaciones</div>
        <div class="qs-val">{{ account.posts }}</div>
      </div>
    </div>

    <!-- Activity in this account -->
    <section class="panel-section">
      <h3 class="section-title">Actividad reciente</h3>
      <div v-if="recentPosts.length" class="recent-posts">
        <div v-for="post in recentPosts" :key="post.id" class="recent-row">
          <div class="recent-thumb" :style="thumbStyle(post)">
            <component :is="typeIcon(post.type)" :size="11" />
          </div>
          <div class="recent-info">
            <div class="recent-title">{{ post.title }}</div>
            <div class="recent-meta">{{ formatDate(post.date) }} · {{ post.type }}</div>
          </div>
          <div class="recent-eng" :class="engClass(post.engagement)">{{ post.engagement }}%</div>
        </div>
      </div>
      <div v-else class="empty-mini">
        Sin publicaciones recientes en esta cuenta.
      </div>
    </section>

    <!-- Account meta -->
    <section class="panel-section">
      <h3 class="section-title">Detalles de la cuenta</h3>
      <dl class="info-list">
        <div class="info-row">
          <dt>Responsable</dt>
          <dd>{{ account.responsible || '—' }}</dd>
        </div>
        <div class="info-row">
          <dt>Última sincronización</dt>
          <dd>{{ formatDateTime(account.lastSync) }}</dd>
        </div>
        <div class="info-row">
          <dt>Estado del token</dt>
          <dd>
            <span class="token-state" :class="account.status === 'connected' ? 'tok-ok' : 'tok-bad'">
              <span class="status-dot"></span>
              {{ account.status === 'connected' ? 'Válido' : 'Necesita renovación' }}
            </span>
          </dd>
        </div>
      </dl>
    </section>

    <!-- Observaciones -->
    <section v-if="account.observations" class="panel-section">
      <h3 class="section-title">Notas internas</h3>
      <p class="notes-text">{{ account.observations }}</p>
    </section>

    <!-- Disconnected warning -->
    <div v-if="account.status !== 'connected'" class="warning-card">
      <AlertTriangle :size="14" />
      <div>
        <strong>Token expirado.</strong>
        <p>Renueva la conexión para reanudar la sincronización automática de métricas.</p>
      </div>
    </div>

    <!-- Footer -->
    <div class="panel-footer">
      <button class="panel-btn panel-btn-ghost" @click="$emit('close')">Cerrar</button>
      <button v-if="account.status === 'connected'" class="panel-btn panel-btn-ghost">
        <RefreshCw :size="13" />
        Sincronizar
      </button>
      <button class="panel-btn panel-btn-primary">
        <Pencil :size="13" />
        Editar
      </button>
    </div>
  </div>

  <div v-else class="panel-empty">
    <AlertCircle :size="20" />
    <span>Cuenta no encontrada.</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  AlertCircle, AlertTriangle, RefreshCw, Pencil,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText,
} from 'lucide-vue-next'
import {
  socialAccounts, socialPosts,
  getPlatform, formatNumber, formatDate,
} from '@/services/socialCrmData'

const props = defineProps({
  accountId: { type: Number, required: true },
})

defineEmits(['close'])

const account = computed(() => socialAccounts.find(a => a.id === props.accountId))

const recentPosts = computed(() => {
  if (!account.value) return []
  return socialPosts
    .filter(p => p.accountId === account.value.id)
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
})

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function thumbStyle(post) {
  const p = getPlatform(post.platform)
  return { background: `linear-gradient(135deg, ${p.color}cc, ${p.color}66)` }
}
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function typeIcon(type) {
  const map = {
    'Imagen': ImageIcon, 'Vídeo': Film, 'Reel': Film, 'Story': Layers,
    'Carrusel': Layers, 'Tweet': MessageSquare, 'Hilo': MessageSquare, 'Short': Film,
  }
  return map[type] || FileText
}
function formatDateTime(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('es-ES', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
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

.hero-head { display: flex; align-items: center; justify-content: space-between; }
.platform-pill { font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.acc-status { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; font-weight: 600; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.st-on  { color: #10B981; }
.st-on  .status-dot { background: #10B981; box-shadow: 0 0 0 3px rgba(16,185,129,0.18); }
.st-off { color: #EF4444; }
.st-off .status-dot { background: #EF4444; }

.hero-name {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--text-primary);
  margin: 0.25rem 0 0;
  line-height: 1.2;
}
.hero-handle { font-size: 0.875rem; color: var(--text-secondary); font-feature-settings: "tnum"; }

/* Quick stats */
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

/* Recent posts */
.recent-posts { display: flex; flex-direction: column; gap: 0.4rem; }
.recent-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 0.625rem;
  align-items: center;
  padding: 0.5rem 0.625rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}
.recent-thumb {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.recent-info { min-width: 0; }
.recent-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.recent-meta { font-size: 0.7rem; color: var(--text-secondary); margin-top: 1px; }

.recent-eng { font-size: 0.78rem; font-weight: 700; }
.eng-high { color: #10B981; }
.eng-mid  { color: #F59E0B; }
.eng-low  { color: #EF4444; }

.empty-mini {
  padding: 1rem;
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.825rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}

/* Info list */
.info-list { margin: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.info-row { display: flex; justify-content: space-between; font-size: 0.85rem; align-items: baseline; gap: 1rem; }
.info-row dt { color: var(--text-secondary); margin: 0; }
.info-row dd { color: var(--text-primary); margin: 0; text-align: right; }

.token-state {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
  font-weight: 600;
}
.tok-ok  { color: #10B981; }
.tok-ok  .status-dot { background: #10B981; }
.tok-bad { color: #EF4444; }
.tok-bad .status-dot { background: #EF4444; }

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

/* Warning */
.warning-card {
  display: flex;
  gap: 0.625rem;
  padding: 0.75rem 0.875rem;
  border-radius: 10px;
  background: rgba(239,68,68,0.06);
  border: 1px solid rgba(239,68,68,0.2);
  color: #B91C1C;
  font-size: 0.825rem;
  line-height: 1.4;
}
.warning-card svg { flex-shrink: 0; margin-top: 1px; color: #EF4444; }
.warning-card strong { display: block; color: #991B1B; }
.warning-card p { margin: 2px 0 0; }

/* Footer */
.panel-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  flex-wrap: wrap;
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
