<template>
  <SocialHubLayout
    title="Contingut"
    subtitle="Publicacions, comptes connectats i anàlisi del rendiment del contingut."
    :tabs="tabs"
    v-model="activeTab"
    :panel-open="!!panel.kind"
    @close-panel="closePanel"
  >
    <template #actions>
      <button v-if="activeTab !== 'posts'" class="hub-btn hub-btn-primary" @click="onPrimaryAction">
        <Plus :size="16" />
        <span>{{ primaryActionLabel }}</span>
      </button>
    </template>

    <!-- ── KPI strip ──────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Publicacions</div>
        <div class="kpi-val">{{ kpis.totalPosts }}</div>
        <div class="kpi-sub">{{ kpis.activeAccounts }} comptes actius</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Abast total</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalReach) }}</div>
        <div class="kpi-sub">{{ formatNumber(kpis.totalImpressions) }} impressions</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Engagement mitjà</div>
        <div class="kpi-val">
          <span :class="engClass(kpis.avgEngagement)">{{ kpis.avgEngagement.toFixed(1) }}%</span>
        </div>
        <div class="kpi-sub">{{ kpis.bestFormat }} top format</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Clics generats</div>
        <div class="kpi-val">{{ formatNumber(kpis.totalClicks) }}</div>
        <div class="kpi-sub">{{ kpis.disconnectedAccounts > 0 ? `⚠ ${kpis.disconnectedAccounts} compte(s) desconnectat(s)` : 'Tots els comptes connectats' }}</div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         TAB 1 · PUBLICACIONES
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'posts'" class="tab-section">
      <div class="filters-row">
        <div class="search-input-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="postSearch"
            class="filter-input search-input"
            placeholder="Cerca per títol, compte o campanya..."
          />
        </div>
        <select v-model="platformFilter" class="filter-input">
          <option value="all">Totes les xarxes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select v-model="postType" class="filter-input">
          <option value="all">Tots els tipus</option>
          <option v-for="t in CONTENT_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
        <select v-model="postCampaign" class="filter-input">
          <option value="all">Totes les campanyes</option>
          <option value="none">Sense campanya</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
        </select>
        <select v-model="postSort" class="filter-input">
          <option value="date">Més recents</option>
          <option value="reach">Major abast</option>
          <option value="engagement">Millor engagement</option>
          <option value="clicks">Més clics</option>
        </select>
        <div class="result-count">{{ filteredPosts.length }} publicacions</div>
        <button class="hub-btn hub-btn-ghost" :disabled="syncingPosts" @click="syncPosts">
          <Loader2 v-if="syncingPosts" :size="14" class="spin" />
          <RefreshCw v-else :size="14" />
          <span>Sincronitzar</span>
        </button>
      </div>

      <div class="data-card">
        <div class="data-head head-posts">
          <div class="th">Publicació</div>
          <div class="th">Xarxa</div>
          <div class="th">Tipus</div>
          <div class="th">Campanya</div>
          <div class="th th-num">Abast</div>
          <div class="th th-num">Likes</div>
          <div class="th th-num">Clics</div>
          <div class="th th-num">Eng.</div>
        </div>
        <!-- Loading state -->
        <div v-if="postsLoading" class="empty-row">
          <Loader2 :size="20" class="spin" />
          <span>Carregant publicacions…</span>
        </div>

        <div v-else class="data-rows">
          <button
            v-for="post in filteredPosts"
            :key="post.id"
            class="data-row row-posts"
            :class="{ active: panel.kind === 'post' && panel.id === post.id }"
            @click="openPost(post.id)"
          >
            <div class="cell cell-post">
              <div class="post-thumb" :style="thumbStyle(post)">
                <img v-if="post.thumbnail" :src="post.thumbnail" class="thumb-img" />
                <component v-else :is="typeIcon(post.type)" :size="13" />
              </div>
              <div class="post-block">
                <div class="row-name">{{ post.title }}</div>
                <div class="row-alias">{{ post.accountName }} · {{ formatDate(post.date) }}</div>
              </div>
            </div>
            <div class="cell">
              <span class="platform-pill" :style="platformStyle(post.platform)">
                {{ getPlatform(post.platform).label }}
              </span>
            </div>
            <div class="cell">
              <span class="type-tag">{{ post.type }}</span>
            </div>
            <div class="cell muted">
              {{ post.campaignName || '—' }}
            </div>
            <div class="cell cell-num font-mono">{{ formatNumber(post.reach) }}</div>
            <div class="cell cell-num font-mono">{{ formatNumber(post.likes) }}</div>
            <div class="cell cell-num font-mono">{{ formatNumber(post.clicks) }}</div>
            <div class="cell cell-num">
              <span class="eng-pill" :class="engClass(post.engagement)">{{ post.engagement }}%</span>
            </div>
          </button>
          <div v-if="!postsLoading && !filteredPosts.length" class="empty-row">
            <Frown :size="20" />
            <span>{{ posts.length ? 'No hi ha publicacions amb aquests filtres.' : 'Prem Sincronitzar per importar les publicacions de les teves xarxes.' }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 2 · CUENTAS
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'accounts'" class="tab-section">
      <div class="filters-row">
        <select v-model="platformFilter" class="filter-input">
          <option value="all">Totes les xarxes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <div class="result-count">{{ filteredAccounts.length }} comptes</div>
        <button class="hub-btn hub-btn-ghost" style="margin-left:auto" :disabled="syncingPosts" @click="syncPosts">
          <Loader2 v-if="syncingPosts" :size="14" class="spin" />
          <RefreshCw v-else :size="14" />
          <span>Sincronitzar</span>
        </button>
      </div>
      <div class="accounts-grid">
        <article
          v-for="acc in filteredAccounts"
          :key="acc.id"
          class="account-card"
          :class="{ active: panel.kind === 'account' && panel.id === acc.id, disconnected: acc.status !== 'connected' }"
          @click="openAccount(acc.id)"
        >
          <div class="acc-head">
            <span class="platform-pill" :style="platformStyle(acc.platform)">
              {{ getPlatform(acc.platform).label }}
            </span>
            <span class="acc-status" :class="acc.status === 'connected' ? 'st-on' : 'st-off'">
              <span class="status-dot"></span>
              {{ acc.status === 'connected' ? 'Connectat' : 'Desconnectat' }}
            </span>
          </div>
          <div class="acc-name">{{ acc.name }}</div>
          <div class="acc-handle">{{ acc.username }}</div>
          <div class="acc-stats">
            <div class="acc-stat">
              <div class="as-val">{{ formatNumber(acc.followers) }}</div>
              <div class="as-key">Seguidors</div>
            </div>
            <div class="acc-stat">
              <div class="as-val">{{ acc.posts }}</div>
              <div class="as-key">Posts</div>
            </div>
          </div>
          <div class="acc-foot">
            <span>Última sync.</span>
            <span class="muted">{{ formatRelativeDate(acc.lastSync) }}</span>

          </div>
          <div class="acc-arrow">
            <ArrowUpRight :size="14" />
          </div>
        </article>

        <div v-if="!filteredAccounts.length" class="empty-row">
          <Frown :size="20" />
          <span>No hi ha comptes amb aquests filtres.</span>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 3 · ANÀLISI
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'analytics'" class="tab-section analytics-tab">
      <!-- Performance by format -->
      <div class="analytics-card">
        <header class="ac-header">
          <div>
            <h3 class="ac-title">Rendiment per format</h3>
            <p class="ac-sub">Engagement mitjà per tipus de contingut publicat</p>
          </div>
          <span class="ac-counter">{{ contentByFormat.length }} formats</span>
        </header>
        <div class="format-grid">
          <article
            v-for="fmt in contentByFormat"
            :key="fmt.type"
            class="format-card"
          >
            <div class="fmt-head">
              <component :is="typeIcon(fmt.type)" :size="14" class="fmt-icon" />
              <span class="fmt-label">{{ fmt.type }}</span>
              <span class="fmt-count">{{ fmt.count }}</span>
            </div>
            <div class="fmt-eng" :class="engClass(fmt.engagement)">
              {{ fmt.engagement.toFixed(1) }}%
            </div>
            <div class="fmt-bar-wrap">
              <div
                class="fmt-bar"
                :style="{
                  width: Math.min(fmt.engagement * 12, 100) + '%',
                  background: engBarColor(fmt.engagement),
                }"
              ></div>
            </div>
            <div class="fmt-stats">
              <span>{{ formatNumber(fmt.avgReach) }} d'abast</span>
              <span>·</span>
              <span>{{ formatNumber(fmt.avgClicks) }} clics</span>
            </div>
          </article>
        </div>
      </div>

      <!-- Two-column: Platform + Time slot -->
      <div class="analytics-cols">
        <div class="analytics-card">
          <header class="ac-header">
            <div>
              <h3 class="ac-title">Per xarxa social</h3>
              <p class="ac-sub">Volum i rendiment agregat</p>
            </div>
          </header>
          <div class="platform-rows">
            <div
              v-for="plt in contentByPlatform"
              :key="plt.platform"
              class="platform-row"
            >
              <span class="platform-pill" :style="platformStyle(plt.platform)">
                {{ getPlatform(plt.platform).label }}
              </span>
              <div class="plt-stats">
                <div class="plt-cell">
                  <div class="plt-val">{{ plt.posts }}</div>
                  <div class="plt-key">posts</div>
                </div>
                <div class="plt-cell">
                  <div class="plt-val" :class="engClass(plt.engagement)">{{ plt.engagement.toFixed(1) }}%</div>
                  <div class="plt-key">eng.</div>
                </div>
                <div class="plt-cell">
                  <div class="plt-val font-mono">{{ formatNumber(plt.totalReach) }}</div>
                  <div class="plt-key">abast</div>
                </div>
                <div class="plt-cell">
                  <div class="plt-val font-mono">{{ formatNumber(plt.totalClicks) }}</div>
                  <div class="plt-key">clics</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="analytics-card">
          <header class="ac-header">
            <div>
              <h3 class="ac-title">Millor franja horària</h3>
              <p class="ac-sub">Engagement mitjà per hora de publicació</p>
            </div>
          </header>
          <div class="hours-list">
            <div v-for="slot in timeSlots" :key="slot.label" class="hour-row">
              <span class="hour-label">{{ slot.label }}</span>
              <div class="hour-bar-wrap">
                <div
                  class="hour-bar"
                  :class="{ 'hour-bar-best': slot.engagement === maxSlotEng }"
                  :style="{ width: (slot.engagement / maxSlotEng * 100) + '%' }"
                ></div>
              </div>
              <span class="hour-val" :class="{ 'hour-val-best': slot.engagement === maxSlotEng }">
                {{ slot.engagement.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </div>

    </section>

    <!-- ── Side panel ─────────────────────────────────────────── -->
    <template #panel>
      <PostDetailPanel
        v-if="panel.kind === 'post'"
        :post-id="panel.id"
        :posts="posts"
        @close="closePanel"
      />
      <AccountDetailPanel
        v-else-if="panel.kind === 'account'"
        :account-id="panel.id"
        @close="closePanel"
      />
    </template>
  </SocialHubLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Search, Plus, Frown, RefreshCw, ArrowUpRight,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText, Loader2,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'
import PostDetailPanel from './PostDetailPanel.vue'
import AccountDetailPanel from './AccountDetailPanel.vue'
import { get, post as apiPost } from '@/services/api'
import { useToast } from '@/composables/useToast'
import {
  socialAccounts, socialCampaigns,
  PLATFORMS, CONTENT_TYPES, getPlatform,
  formatNumber, formatDate,
} from '@/services/socialCrmData'

const toast = useToast()

// ── Posts state (real API) ─────────────────────────────────────
const posts         = ref([])
const postsLoading  = ref(true)
const syncingPosts  = ref(false)

async function loadPosts() {
  postsLoading.value = true
  try {
    const data = await get('/integrations/social/posts/')
    posts.value = (data.posts || []).map(normalizePost)
  } catch {
    toast.error('No s\'han pogut carregar les publicacions.')
  } finally {
    postsLoading.value = false
  }
}

async function syncPosts() {
  syncingPosts.value = true
  try {
    await apiPost('/integrations/social/posts/sync/')
    await loadPosts()
    toast.success('Publicacions sincronitzades.')
  } catch {
    toast.error('Error en sincronitzar les publicacions.')
  } finally {
    syncingPosts.value = false
  }
}

/** Map API fields to the shape expected by the template */
function normalizePost(p) {
  const typeMap = { video: 'Vídeo', post: 'Tweet', reel: 'Reel' }
  return {
    id:          p.id,
    platform:    p.provider,          // 'youtube' | 'twitter' | 'tiktok'
    type:        typeMap[p.post_type] || 'Vídeo',
    title:       p.title || p.description?.slice(0, 80) || '(sense títol)',
    accountName: p.account_name || '',
    date:        p.published_at || p.synced_at,
    reach:       p.views || 0,
    likes:       p.likes || 0,
    comments:    p.comments || 0,
    shares:      p.shares || 0,
    clicks:      p.shares || 0,       // best proxy available
    impressions: p.views || 0,
    engagement:  p.engagement || 0,
    thumbnail:   p.thumbnail_url || '',
    post_url:    p.post_url || '',
    campaignId:  null,
    campaignName: null,
  }
}

onMounted(loadPosts)

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('posts')

const tabs = computed(() => [
  { key: 'posts',     label: 'Publicacions', count: postsLoading.value ? null : posts.value.length },
  { key: 'accounts',  label: 'Comptes',      count: socialAccounts.length },
  { key: 'analytics', label: 'Anàlisi' },
])

// ── Global filters ────────────────────────────────────────────
const platformFilter = ref('all')

// ── Posts state ───────────────────────────────────────────────
const postSearch   = ref('')
const postType     = ref('all')
const postCampaign = ref('all')
const postSort     = ref('date')

const filteredPosts = computed(() => {
  let list = [...posts.value]
  if (platformFilter.value !== 'all') list = list.filter(p => p.platform === platformFilter.value)
  if (postType.value !== 'all') list = list.filter(p => p.type === postType.value)
  if (postSearch.value) {
    const q = postSearch.value.toLowerCase()
    list = list.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.accountName.toLowerCase().includes(q)
    )
  }
  return list.sort((a, b) => {
    if (postSort.value === 'date')       return new Date(b.date) - new Date(a.date)
    if (postSort.value === 'reach')      return b.reach - a.reach
    if (postSort.value === 'engagement') return b.engagement - a.engagement
    if (postSort.value === 'clicks')     return b.clicks - a.clicks
    return 0
  })
})

// ── Accounts state ────────────────────────────────────────────
const filteredAccounts = computed(() => {
  let list = [...socialAccounts]
  if (platformFilter.value !== 'all') list = list.filter(a => a.platform === platformFilter.value)
  return list
})

function syncAccounts() { syncPosts() }

// ── Analytics derivations ─────────────────────────────────────
const contentByFormat = computed(() => {
  const map = {}
  posts.value.forEach(p => {
    if (!map[p.type]) map[p.type] = { type: p.type, count: 0, totalEng: 0, totalReach: 0, totalClicks: 0 }
    map[p.type].count++
    map[p.type].totalEng += p.engagement
    map[p.type].totalReach += p.reach
    map[p.type].totalClicks += p.clicks
  })
  return Object.values(map).map(m => ({
    ...m,
    engagement: m.totalEng / m.count,
    avgReach:   Math.round(m.totalReach / m.count),
    avgClicks:  Math.round(m.totalClicks / m.count),
  })).sort((a, b) => b.engagement - a.engagement)
})

const contentByPlatform = computed(() => {
  const map = {}
  posts.value.forEach(p => {
    if (!map[p.platform]) map[p.platform] = { platform: p.platform, posts: 0, totalEng: 0, totalReach: 0, totalClicks: 0 }
    map[p.platform].posts++
    map[p.platform].totalEng += p.engagement
    map[p.platform].totalReach += p.reach
    map[p.platform].totalClicks += p.clicks
  })
  return Object.values(map).map(m => ({
    ...m,
    engagement: m.totalEng / m.posts,
  })).sort((a, b) => b.totalReach - a.totalReach)
})

const timeSlots = [
  { label: '00–06h', engagement: 2.1 }, { label: '06–09h', engagement: 3.4 },
  { label: '09–12h', engagement: 5.8 }, { label: '12–15h', engagement: 6.4 },
  { label: '15–18h', engagement: 5.1 }, { label: '18–21h', engagement: 7.2 },
  { label: '21–00h', engagement: 4.8 },
]
const maxSlotEng = computed(() => Math.max(...timeSlots.map(s => s.engagement)))

const topPosts = computed(() =>
  [...posts.value].sort((a, b) => b.engagement - a.engagement).slice(0, 5)
)

// ── KPIs ──────────────────────────────────────────────────────
const kpis = computed(() => {
  const list = posts.value
  const totalPosts        = list.length
  const totalReach        = list.reduce((s, p) => s + p.reach, 0)
  const totalImpressions  = list.reduce((s, p) => s + p.impressions, 0)
  const totalClicks       = list.reduce((s, p) => s + p.clicks, 0)
  const avgEngagement     = list.length ? list.reduce((s, p) => s + p.engagement, 0) / list.length : 0
  const bestFormat        = contentByFormat.value[0]?.type || '—'
  const activeAccounts    = socialAccounts.filter(a => a.status === 'connected').length
  const disconnectedAccounts = socialAccounts.filter(a => a.status !== 'connected').length
  return { totalPosts, totalReach, totalImpressions, totalClicks, avgEngagement, bestFormat, activeAccounts, disconnectedAccounts }
})

// ── Side panel ────────────────────────────────────────────────
const panel = reactive({ kind: null, id: null })
function openPost(id) { panel.kind = 'post'; panel.id = id }
function openAccount(id) { panel.kind = 'account'; panel.id = id }
function closePanel() { panel.kind = null; panel.id = null }

// ── Primary action (changes per tab) ──────────────────────────
const primaryActionLabel = computed(() => {
  if (activeTab.value === 'accounts') return 'Connectar un compte'
  return 'Exportar l\'anàlisi'
})
function onPrimaryAction() {
  alert(`Acció: ${primaryActionLabel.value}`)
}

// ── Helpers ───────────────────────────────────────────────────
function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
function engBarColor(v) { return v >= 6 ? '#10B981' : v >= 3 ? '#F59E0B' : '#EF4444' }

function typeIcon(type) {
  const map = {
    'Imatge':   ImageIcon,
    'Vídeo':    Film,
    'Reel':     Film,
    'Story':    Layers,
    'Carrusel': Layers,
    'Tweet':    MessageSquare,
    'Fil':      MessageSquare,
    'Short':    Film,
  }
  return map[type] || FileText
}

function thumbStyle(post) {
  if (post.thumbnail) return {}   // real image shown via <img>
  const platform = getPlatform(post.platform)
  return { background: `linear-gradient(135deg, ${platform.color}cc, ${platform.color}44)` }
}

function formatRelativeDate(iso) {
  if (!iso) return '—'
  const date = new Date(iso)
  const diffMs = Date.now() - date.getTime()
  const diffH  = Math.floor(diffMs / 3600000)
  if (diffH < 1)  return 'fa uns minuts'
  if (diffH < 24) return `fa ${diffH}h`
  const diffD = Math.floor(diffH / 24)
  if (diffD < 7) return `fa ${diffD}d`
  return formatDate(iso.split('T')[0])
}
</script>

<style scoped>
/* ── Header micro-controls ──────────────────────────── */
.hub-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  background: var(--bg-primary);
  color: var(--text-primary);
}
.hub-btn-primary {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(102,126,234,0.30);
}
.hub-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
.hub-btn-ghost { background: transparent; }
.hub-btn-ghost:hover { background: var(--bg-secondary); }

/* ── KPI strip (consistent w/ InfluencersHub) ─────────── */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
  margin-bottom: 1.5rem;
}
.kpi-tile {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.875rem 1rem;
  position: relative;
  overflow: hidden;
}
.kpi-tile::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 3px; height: 100%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  opacity: 0.55;
}
.kpi-key {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
}
.kpi-val {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  line-height: 1.05;
  font-feature-settings: "tnum";
}
.kpi-sub {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* ── Filters row ────────────────────────────────────── */
.tab-section { display: flex; flex-direction: column; gap: 1rem; }

.filters-row { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }

.filter-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.15s ease;
  min-width: 0;
}
.filter-input:hover { border-color: var(--primary-color); }
.filter-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }

.search-input-wrap { position: relative; flex: 1 1 280px; max-width: 360px; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { width: 100%; padding-left: 2rem; cursor: text; }

.result-count {
  margin-left: auto;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* ── Posts table ────────────────────────────────────── */
.data-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}
.data-head {
  display: grid;
  padding: 0.625rem 1.25rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
.head-posts { grid-template-columns: 2.5fr 0.9fr 0.8fr 1.3fr 0.9fr 0.8fr 0.8fr 0.7fr; }
.th-num { text-align: right; }

.data-rows { display: flex; flex-direction: column; }
.data-row {
  display: grid;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  border-left: none;
  border-right: none;
  border-top: none;
  cursor: pointer;
  text-align: left;
  font-family: inherit;
  font-size: 0.85rem;
  transition: background 0.12s ease;
  align-items: center;
}
.row-posts { grid-template-columns: 2.5fr 0.9fr 0.8fr 1.3fr 0.9fr 0.8fr 0.8fr 0.7fr; }
.data-row:last-child { border-bottom: none; }
.data-row:hover { background: var(--bg-secondary); }
.data-row.active {
  background: rgba(102,126,234,0.06);
  position: relative;
}
.data-row.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}

.cell { display: flex; align-items: center; min-width: 0; }
.cell-post { gap: 0.625rem; }
.cell-num { justify-content: flex-end; text-align: right; }
.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }
.muted { color: var(--text-secondary); }

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 7px;
  display: block;
}

.spin { animation: spin-anim 0.8s linear infinite; }
@keyframes spin-anim { to { transform: rotate(360deg); } }

.post-thumb {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  position: relative;
  box-shadow: 0 2px 4px rgba(15,23,42,0.08);
}

.post-block { min-width: 0; flex: 1; }
.row-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 320px;
}
.row-alias {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 1px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.platform-pill {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.type-tag {
  font-size: 0.72rem;
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 500;
}

.eng-pill {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}
.eng-high { background: rgba(16,185,129,0.12); color: #10B981; }
.eng-mid  { background: rgba(245,158,11,0.12); color: #F59E0B; }
.eng-low  { background: rgba(239,68,68,0.10); color: #EF4444; }

.empty-row {
  padding: 2.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ── Accounts grid ─────────────────────────────────── */
.accounts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.875rem;
}

.account-card {
  position: relative;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1rem 1.125rem;
  cursor: pointer;
  transition: all 0.18s ease;
  overflow: hidden;
}
.account-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 6px 18px rgba(102,126,234,0.10);
  transform: translateY(-2px);
}
.account-card.active {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.04);
}
.account-card.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}
.account-card.disconnected { opacity: 0.92; border-color: rgba(239,68,68,0.25); }
.account-card.disconnected:hover { border-color: #EF4444; box-shadow: 0 4px 12px rgba(239,68,68,0.15); }

.acc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.625rem; }
.acc-status { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.7rem; font-weight: 600; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.st-on  { color: #10B981; }
.st-on  .status-dot { background: #10B981; box-shadow: 0 0 0 3px rgba(16,185,129,0.18); }
.st-off { color: #EF4444; }
.st-off .status-dot { background: #EF4444; }

.acc-name { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; }
.acc-handle { font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 0.875rem; }

.acc-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}
.acc-stat { text-align: center; }
.as-val { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.as-key { font-size: 0.68rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }

.acc-foot {
  display: flex;
  justify-content: space-between;
  margin-top: 0.625rem;
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.acc-arrow {
  position: absolute;
  top: 1rem;
  right: 1rem;
  opacity: 0;
  transform: translate(-4px, 4px);
  transition: all 0.18s ease;
  color: var(--primary-color);
}
.account-card:hover .acc-arrow { opacity: 1; transform: translate(0, 0); }

/* ── Analytics tab ─────────────────────────────────── */
.analytics-tab { gap: 1.25rem; }

.analytics-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.ac-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(180deg, rgba(102,126,234,0.04), transparent);
}
.ac-title { font-size: 0.95rem; font-weight: 700; margin: 0; color: var(--text-primary); letter-spacing: -0.01em; }
.ac-sub { font-size: 0.78rem; color: var(--text-secondary); margin: 0.125rem 0 0; }
.ac-counter { font-size: 0.7rem; padding: 3px 9px; border-radius: 999px; background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600; }

.format-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
  padding: 1rem 1.25rem;
}

.format-card {
  background: var(--bg-secondary);
  border-radius: 10px;
  padding: 0.875rem 0.875rem 0.75rem;
}

.fmt-head { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.625rem; }
.fmt-icon { color: var(--text-secondary); }
.fmt-label { font-size: 0.78rem; font-weight: 600; color: var(--text-primary); flex: 1; }
.fmt-count { font-size: 0.7rem; color: var(--text-secondary); padding: 1px 7px; border-radius: 999px; background: var(--bg-primary); }

.fmt-eng { font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1; margin-bottom: 0.5rem; }
.fmt-bar-wrap { height: 5px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; margin-bottom: 0.5rem; }
.fmt-bar { height: 100%; border-radius: 3px; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.fmt-stats { font-size: 0.72rem; color: var(--text-secondary); display: flex; gap: 0.4rem; }

.analytics-cols {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1.25rem;
}

.platform-rows { padding: 0.875rem 1.25rem; display: flex; flex-direction: column; gap: 0.625rem; }
.platform-row {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 1rem;
  align-items: center;
  padding: 0.625rem;
  background: var(--bg-secondary);
  border-radius: 9px;
}

.plt-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.625rem; }
.plt-cell { text-align: right; }
.plt-val { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.plt-key { font-size: 0.66rem; text-transform: uppercase; color: var(--text-secondary); letter-spacing: 0.05em; }

.hours-list { padding: 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.4rem; }
.hour-row { display: grid; grid-template-columns: 60px 1fr 50px; gap: 0.625rem; align-items: center; }
.hour-label { font-size: 0.78rem; color: var(--text-secondary); font-feature-settings: "tnum"; }
.hour-bar-wrap { height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden; }
.hour-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.55;
}
.hour-bar-best { opacity: 1; box-shadow: 0 0 8px rgba(118,75,162,0.4); }
.hour-val { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); text-align: right; font-feature-settings: "tnum"; }
.hour-val-best { color: var(--primary-color); font-weight: 800; }

/* ── Responsive ────────────────────────────────────── */
@media (max-width: 1280px) {
  .head-posts, .row-posts {
    grid-template-columns: 2.2fr 0.9fr 0.7fr 1.1fr 0.8fr 0.7fr 0.7fr 0.7fr;
  }
}

@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .analytics-cols { grid-template-columns: 1fr; }
}

@media (max-width: 900px) {
  .data-head { display: none; }
  .data-row {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 0.75rem;
    padding: 0.875rem 1rem;
  }
  .cell-post { grid-column: 1 / -1; }
  .cell:not(.cell-post) { font-size: 0.78rem; }
  .platform-row { grid-template-columns: 1fr; gap: 0.5rem; }
  .plt-stats { grid-template-columns: repeat(2, 1fr); }
  .top-post-row { grid-template-columns: auto 1fr; }
  .post-thumb { display: none; }
  .tp-stats { grid-column: 1 / -1; justify-content: flex-start; flex-wrap: wrap; }
}

@media (max-width: 600px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
  .kpi-tile { padding: 0.625rem 0.75rem; }
  .kpi-val { font-size: 1.25rem; }
  .accounts-grid { grid-template-columns: 1fr; }
}
</style>
