<template>
  <div class="accounts-view">

    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Comptes connectats</h1>
        <span v-if="!loading" class="count-chip">{{ accounts.length }}</span>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" :disabled="syncing || loading" @click="syncAll">
          <RefreshCw :size="15" :class="{ spin: syncing }" />
          {{ syncing ? 'Sincronitzant…' : 'Sincronitzar tot' }}
        </button>
        <router-link to="/settings/company" class="btn btn-primary">
          <Plus :size="15" />
          Connectar compte
        </router-link>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="accounts-grid">
      <div v-for="n in 3" :key="n" class="account-card skeleton">
        <div class="skel skel-avatar" />
        <div style="flex:1">
          <div class="skel skel-line" style="width:55%;margin-bottom:6px" />
          <div class="skel skel-line" style="width:35%" />
        </div>
        <div class="skel skel-line" style="width:100%;margin-top:1rem;height:1px" />
        <div style="display:flex;gap:2rem;margin-top:0.75rem">
          <div v-for="m in 3" :key="m" style="flex:1">
            <div class="skel skel-line" style="width:50%;margin-bottom:5px" />
            <div class="skel skel-line" style="width:75%;height:10px" />
          </div>
        </div>
      </div>
    </div>

    <!-- Accounts -->
    <div v-else-if="accounts.length" class="accounts-grid">
      <div
        v-for="acc in accounts"
        :key="acc.id"
        class="account-card"
        :style="{ '--accent': isExpired(acc) ? '#ea580c' : platformAccent(acc.provider) }"
      >
        <!-- Card head -->
        <div class="card-head">
          <div class="avatar-wrap">
            <img v-if="acc.avatar" :src="acc.avatar" :alt="acc.name" class="avatar-img" />
            <div v-else class="avatar-fallback" :style="{ background: platformBg(acc.provider) }">
              <component :is="platformIcon(acc.provider)" :size="20"
                         :style="{ color: platformAccent(acc.provider) }" />
            </div>
            <!-- Platform badge -->
            <div class="platform-badge" :style="{ background: platformAccent(acc.provider) }">
              <component :is="platformIcon(acc.provider)" :size="10" style="color:#fff" />
            </div>
          </div>

          <div class="card-head-info">
            <p class="acc-name">{{ acc.name || acc.provider_user_id }}</p>
            <p class="acc-sub">
              <span v-if="acc.username">{{ acc.username }}</span>
              <span v-else>{{ platformLabel(acc.provider) }}</span>
            </p>
          </div>

          <button class="sync-btn" :disabled="syncingProvider[acc.provider]"
                  :title="'Sincronitzar ' + platformLabel(acc.provider)"
                  @click="syncOne(acc.provider)">
            <RefreshCw :size="13" :class="{ spin: syncingProvider[acc.provider] }" />
          </button>
        </div>

        <!-- Divider -->
        <div class="card-divider" />

        <!-- Stats -->
        <div v-if="getStats(acc).length" class="stats-grid">
          <div v-for="stat in getStats(acc)" :key="stat.label" class="stat-item">
            <div class="stat-top">
              <component :is="stat.icon" :size="13" class="stat-icon"
                         :style="{ color: platformAccent(acc.provider) }" />
              <span class="stat-num">{{ formatNum(stat.value) }}</span>
            </div>
            <span class="stat-lbl">{{ stat.label }}</span>
          </div>
        </div>
        <p v-else class="no-stats-hint">Fes clic a sincronitzar per carregar les dades</p>

        <!-- Footer -->
        <div class="card-footer" :class="{ 'footer-warn': isExpired(acc) }">
          <template v-if="isExpired(acc)">
            <AlertTriangle :size="11" />
            <span>Token expirat —</span>
            <router-link to="/" class="reconnect-link">Reconnectar →</router-link>
          </template>
          <template v-else>
            <Clock :size="11" />
            <span v-if="acc.stats_synced_at">Actualitzat {{ timeAgo(acc.stats_synced_at) }}</span>
            <span v-else class="muted">Mai sincronitzat</span>
          </template>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-state">
      <div class="empty-icon"><Link2 :size="36" /></div>
      <h3>No hi ha comptes connectats</h3>
      <p>Connecta les teves xarxes socials per veure les seves estadístiques aquí.</p>
      <router-link to="/settings/company" class="btn btn-primary">
        <Plus :size="15" /> Connectar compte
      </router-link>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  RefreshCw, Plus, Clock, Link2, AlertTriangle,
  Facebook, Youtube, Twitter, Music2,
  Users, Eye, Video, MessageSquare, UserPlus, Heart, ThumbsUp,
} from 'lucide-vue-next'
import { post, get } from '@/services/api'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const accounts        = ref([])
const loading         = ref(true)
const syncing         = ref(false)
const syncingProvider = reactive({})

// ── Platform config ───────────────────────────────────────────────────────────

const PLATFORMS = {
  facebook: { label: 'Facebook', icon: Facebook, accent: '#1877f2', bg: '#e7f0ff' },
  youtube:  { label: 'YouTube',  icon: Youtube,  accent: '#ff0000', bg: '#fff0f0' },
  twitter:  { label: 'X',        icon: Twitter,  accent: '#000000', bg: '#f0f4f8' },
  tiktok:   { label: 'TikTok',   icon: Music2,   accent: '#ee1d52', bg: '#fff0f4' },
}

const platformLabel  = p => PLATFORMS[p]?.label  ?? p
const platformIcon   = p => PLATFORMS[p]?.icon   ?? Link2
const platformAccent = p => PLATFORMS[p]?.accent ?? '#667eea'
const platformBg     = p => PLATFORMS[p]?.bg     ?? '#f5f5f5'

// ── Stats definitions per platform (with icon) ────────────────────────────────

const STAT_DEFS = {
  youtube:  [
    { key: 'subscribers', label: 'Subscriptors', icon: Users },
    { key: 'views',       label: 'Visualitzacions', icon: Eye },
    { key: 'videos',      label: 'Vídeos',       icon: Video },
  ],
  twitter:  [
    { key: 'followers',   label: 'Seguidors',    icon: Users },
    { key: 'following',   label: 'Seguint',      icon: UserPlus },
    { key: 'tweets',      label: 'Tweets',       icon: MessageSquare },
  ],
  tiktok:   [
    { key: 'followers',   label: 'Seguidors',    icon: Users },
    { key: 'likes',       label: 'Likes',        icon: Heart },
    { key: 'videos',      label: 'Vídeos',       icon: Video },
  ],
  facebook: [
    { key: 'fans',        label: 'Fans',         icon: ThumbsUp },
  ],
}

function getStats(acc) {
  return (STAT_DEFS[acc.provider] || [])
    .map(d => ({ ...d, value: acc.stats?.[d.key] }))
    .filter(s => s.value != null)
}

function isExpired(acc) {
  const exp = acc?.token_expires_at
  return !!exp && new Date(exp) < new Date()
}

// ── Formatting ────────────────────────────────────────────────────────────────

function formatNum(n) {
  if (n == null) return '—'
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K'
  return n.toLocaleString('ca-ES')
}

function timeAgo(iso) {
  if (!iso) return ''
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000)
  if (diff < 60)    return 'fa un moment'
  if (diff < 3600)  return `fa ${Math.floor(diff / 60)} min`
  if (diff < 86400) return `fa ${Math.floor(diff / 3600)} h`
  return `fa ${Math.floor(diff / 86400)} dies`
}

// ── API ───────────────────────────────────────────────────────────────────────

async function loadAccounts() {
  loading.value = true
  try {
    const data = await get('/integrations/social/accounts/')
    accounts.value = data.accounts || []
  } catch {
    toast.error('No s\'han pogut carregar els comptes.')
  } finally {
    loading.value = false
  }
}

async function syncAll() {
  syncing.value = true
  try {
    const data = await post('/integrations/social/sync/')
    accounts.value = data.accounts || accounts.value
    const ok    = (data.results || []).filter(r => r.ok).length
    const total = (data.results || []).length
    if (ok === total) toast.success(`${ok} compte${ok !== 1 ? 's' : ''} sincronitzat${ok !== 1 ? 's' : ''}.`)
    else toast.warning(`${ok}/${total} comptes sincronitzats.`)
  } catch {
    toast.error('Error en sincronitzar.')
  } finally {
    syncing.value = false
  }
}

async function syncOne(provider) {
  syncingProvider[provider] = true
  try {
    const data = await post(`/integrations/social/sync/?provider=${provider}`)
    const updated = (data.accounts || []).find(a => a.provider === provider)
    if (updated) {
      const idx = accounts.value.findIndex(a => a.provider === provider)
      if (idx >= 0) accounts.value[idx] = updated
    }
    const ok = (data.results || []).find(r => r.provider === provider)?.ok
    if (ok) toast.success(`${platformLabel(provider)} sincronitzat.`)
    else    toast.warning(`No s'ha pogut sincronitzar ${platformLabel(provider)}.`)
  } catch {
    toast.error(`Error en sincronitzar ${platformLabel(provider)}.`)
  } finally {
    syncingProvider[provider] = false
  }
}

onMounted(loadAccounts)
</script>

<style scoped>
.accounts-view {
  padding: var(--spacing-xl);
  max-width: 1000px;
}

/* ── Header ───────────────────────────────────── */
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--spacing-md); margin-bottom: var(--spacing-lg);
}
.header-left  { display: flex; align-items: center; gap: 0.625rem; }
.header-actions { display: flex; gap: var(--spacing-sm); }

.page-title {
  font-size: 1.5rem; font-weight: 700;
  color: var(--text-primary); margin: 0;
}
.count-chip {
  background: var(--bg-secondary); color: var(--text-secondary);
  font-size: 0.8rem; font-weight: 600;
  padding: 2px 9px; border-radius: 10px;
}

/* ── Grid ─────────────────────────────────────── */
.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

/* ── Card ─────────────────────────────────────── */
.account-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent, var(--border-color));
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: box-shadow 0.15s, transform 0.15s;
}
.account-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

/* ── Card head ────────────────────────────────── */
.card-head {
  display: flex; align-items: center; gap: 0.875rem;
}

.avatar-wrap { position: relative; flex-shrink: 0; }
.avatar-img {
  width: 44px; height: 44px; border-radius: 50%;
  object-fit: cover; border: 2px solid var(--border-color);
  display: block;
}
.avatar-fallback {
  width: 44px; height: 44px; border-radius: 50%;
  display: grid; place-items: center;
}
.platform-badge {
  position: absolute; bottom: -2px; right: -2px;
  width: 17px; height: 17px; border-radius: 50%;
  display: grid; place-items: center;
  border: 2px solid var(--bg-primary);
}

.card-head-info { flex: 1; min-width: 0; }
.acc-name {
  font-weight: 600; font-size: 0.95rem;
  color: var(--text-primary); margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.acc-sub {
  font-size: var(--font-size-xs); color: var(--text-secondary);
  margin: 0.15rem 0 0;
}

.sync-btn {
  flex-shrink: 0;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 30px; height: 30px;
  display: grid; place-items: center;
  cursor: pointer; color: var(--text-tertiary);
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.sync-btn:hover:not(:disabled) {
  background: var(--bg-secondary);
  color: var(--accent, var(--primary-color));
  border-color: var(--accent, var(--border-color));
}
.sync-btn:disabled { opacity: 0.45; cursor: default; }

/* ── Divider ──────────────────────────────────── */
.card-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0 -0.25rem;
}

/* ── Stats grid ───────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.stat-item {
  background: var(--bg-secondary);
  border-radius: calc(var(--border-radius) - 2px);
  padding: 0.625rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-top {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.stat-icon { flex-shrink: 0; opacity: 0.9; }

.stat-num {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  letter-spacing: -0.02em;
}

.stat-lbl {
  font-size: 0.67rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.no-stats-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0;
}

/* ── Footer ───────────────────────────────────── */
.card-footer {
  display: flex; align-items: center; gap: 0.3rem;
  font-size: 0.7rem; color: var(--text-tertiary);
  border-top: 1px solid var(--border-color);
  padding-top: 0.625rem;
  margin-top: auto;
}
.card-footer .muted { opacity: 0.6; }

/* ── Empty ────────────────────────────────────── */
.empty-state {
  display: flex; flex-direction: column;
  align-items: center; gap: var(--spacing-md);
  padding: calc(var(--spacing-xl) * 2) var(--spacing-xl);
  text-align: center;
}
.empty-icon {
  width: 72px; height: 72px; border-radius: 50%;
  background: var(--bg-secondary);
  display: grid; place-items: center;
  color: var(--text-tertiary);
}
.empty-state h3 { font-size: 1.15rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.empty-state p { font-size: var(--font-size-sm); color: var(--text-secondary); margin: 0; max-width: 320px; }

/* ── Skeleton ─────────────────────────────────── */
.skeleton { pointer-events: none; }
.skel {
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--border-color) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease-in-out infinite;
  border-radius: 6px;
}
.skel-avatar { width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0; }
.skel-line   { height: 14px; }

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ── Animations ───────────────────────────────── */
.spin { animation: rotate 0.9s linear infinite; }
@keyframes rotate { to { transform: rotate(360deg); } }

/* ── Token expired ────────────────────────────── */
.footer-warn { color: #ea580c; }
.reconnect-link { color: #ea580c; font-weight: 600; text-decoration: none; }
.reconnect-link:hover { text-decoration: underline; }

@media (max-width: 640px) {
  .accounts-view { padding: var(--spacing-md); }
  .page-header   { flex-direction: column; align-items: flex-start; }
  .accounts-grid { grid-template-columns: 1fr; }
  .stat-lbl       { display: none; }
}
</style>
