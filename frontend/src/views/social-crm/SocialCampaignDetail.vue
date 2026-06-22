<template>
  <div class="campaign-page">

    <!-- ── Capçalera sticky ────────────────────────────────────── -->
    <div class="page-header">
      <div class="header-top">
        <router-link to="/social-crm/campaigns" class="back-link">
          <ChevronLeft :size="16" />
          Campanyes
        </router-link>
        <div v-if="campaign" class="header-right">
          <span class="badge" :class="CAMPAIGN_STATUSES[campaign.status].cls">
            {{ CAMPAIGN_STATUSES[campaign.status].label }}
          </span>
          <span class="obj-pill">{{ campaign.objective }}</span>
        </div>
      </div>
      <h1 v-if="campaign" class="page-title">{{ campaign.name }}</h1>

      <!-- Nav de seccions -->
      <nav v-if="campaign" class="section-nav">
        <button
          v-for="s in sections"
          :key="s.key"
          class="snav-btn"
          :class="{ active: activeSection === s.key }"
          @click="scrollTo(s.key)"
        >
          {{ s.label }}
        </button>
      </nav>
    </div>

    <!-- ── Contingut ──────────────────────────────────────────── -->
    <div v-if="campaign" class="page-body">

      <!-- ══ SECCIÓ: GENERAL ════════════════════════════════════ -->
      <section :ref="el => sectionRefs['general'] = el" class="page-section">
        <div class="section-head">
          <h2 class="section-title">General</h2>
          <div class="campaign-meta">
            <span class="meta-item">
              <Calendar :size="13" />
              {{ formatDate(campaign.startDate) }} → {{ formatDate(campaign.endDate) }}
              <strong>· {{ campaignDays }} dies</strong>
            </span>
            <span v-if="campaign.responsible" class="meta-item">
              <User :size="13" />
              {{ campaign.responsible }}
            </span>
          </div>
        </div>
        <p v-if="campaign.description" class="campaign-desc">{{ campaign.description }}</p>

        <!-- KPIs socials -->
        <div class="social-kpis">
          <div class="sk-tile">
            <div class="sk-label">Abast total</div>
            <div class="sk-value">{{ formatNumber(overview.reach) }}</div>
            <div class="sk-sub">persones assolides</div>
          </div>
          <div class="sk-tile">
            <div class="sk-label">Impressions</div>
            <div class="sk-value">{{ formatNumber(overview.impressions) }}</div>
            <div class="sk-sub">visualitzacions totals</div>
          </div>
          <div class="sk-tile">
            <div class="sk-label">Interaccions</div>
            <div class="sk-value">{{ formatNumber(overview.interactions) }}</div>
            <div class="sk-sub">likes · comentaris · compartits</div>
          </div>
          <div class="sk-tile sk-tile-highlight" :class="perceptionClass">
            <div class="sk-label">Engagement mitjà</div>
            <div class="sk-value">{{ overview.avgEngagement.toFixed(1) }}%</div>
            <div class="sk-sub perception-label">{{ perceptionLabel }}</div>
          </div>
        </div>

        <!-- Pressupost i atribució (secundaris) -->
        <div class="secondary-row">
          <div class="budget-block">
            <div class="budget-head">
              <span class="budget-label">Pressupost</span>
              <span class="budget-nums">
                <strong>{{ formatCurrency(campaign.cost) }}</strong>
                <span class="budget-of">de {{ formatCurrency(campaign.budget) }}</span>
                <span class="budget-pct" :class="budgetClass">{{ budgetPct.toFixed(0) }}%</span>
              </span>
            </div>
            <div class="budget-bar-wrap">
              <div class="budget-bar" :class="budgetClass" :style="{ width: Math.min(budgetPct, 100) + '%' }"></div>
            </div>
          </div>
          <div v-if="campaign.sales > 0" class="attribution-block">
            <span class="attr-label">Vendes atribuïdes</span>
            <span class="attr-value">{{ formatCurrency(campaign.sales) }}</span>
            <span class="attr-sub">· {{ campaign.conversions }} conversions · ROAS {{ campaign.roas.toFixed(2) }}x</span>
          </div>
        </div>
      </section>

      <!-- ══ SECCIÓ: CONTINGUT PROPI ══════════════════════════ -->
      <section :ref="el => sectionRefs['content'] = el" class="page-section">
        <div class="section-head">
          <h2 class="section-title">Contingut propi</h2>
          <span class="section-count">{{ linkedPosts.length }} publicacions</span>
        </div>

        <!-- Mini KPIs de contingut -->
        <div class="content-kpis">
          <div class="ck-item">
            <div class="ck-val">{{ formatNumber(contentStats.reach) }}</div>
            <div class="ck-key">Abast</div>
          </div>
          <div class="ck-item">
            <div class="ck-val">{{ formatNumber(contentStats.likes) }}</div>
            <div class="ck-key">Likes</div>
          </div>
          <div class="ck-item">
            <div class="ck-val">{{ formatNumber(contentStats.comments) }}</div>
            <div class="ck-key">Comentaris</div>
          </div>
          <div class="ck-item">
            <div class="ck-val">{{ formatNumber(contentStats.shares) }}</div>
            <div class="ck-key">Compartits</div>
          </div>
          <div class="ck-item">
            <div class="ck-val" :class="engClass(contentStats.avgEngagement)">
              {{ contentStats.avgEngagement.toFixed(1) }}%
            </div>
            <div class="ck-key">Eng. mitjà</div>
          </div>
        </div>

        <!-- Filtre per plataforma -->
        <div class="platform-filter">
          <button
            class="pf-chip"
            :class="{ active: contentPlatform === 'all' }"
            @click="contentPlatform = 'all'"
          >Totes</button>
          <button
            v-for="(p, key) in availablePostPlatforms"
            :key="key"
            class="pf-chip"
            :class="{ active: contentPlatform === key }"
            :style="contentPlatform === key ? { background: p.color, borderColor: p.color, color: 'white' } : {}"
            @click="contentPlatform = key"
          >{{ p.label }}</button>
        </div>

        <!-- Llista de publicacions -->
        <div class="card posts-card">
          <div class="posts-head">
            <div class="ph-col ph-main">Publicació</div>
            <div class="ph-col">Xarxa</div>
            <div class="ph-col ph-num">Abast</div>
            <div class="ph-col ph-num">Likes</div>
            <div class="ph-col ph-num">Comentaris</div>
            <div class="ph-col ph-num">Engagement</div>
          </div>
          <div
            v-for="p in filteredPosts"
            :key="p.id"
            class="post-row"
            @click="$router.push('/social-crm/content')"
          >
            <div class="pr-main">
              <div class="post-thumb" :style="thumbStyle(p)">
                <component :is="typeIcon(p.type)" :size="11" />
              </div>
              <div class="post-info">
                <div class="post-title">{{ p.title }}</div>
                <div class="post-date">{{ formatDateShort(p.date) }} · {{ p.type }}</div>
              </div>
            </div>
            <div class="pr-cell">
              <span class="plat-pill" :style="platformStyle(p.platform)">
                {{ getPlatform(p.platform).label }}
              </span>
            </div>
            <div class="pr-cell pr-num">{{ formatNumber(p.reach) }}</div>
            <div class="pr-cell pr-num">{{ formatNumber(p.likes) }}</div>
            <div class="pr-cell pr-num">{{ formatNumber(p.comments) }}</div>
            <div class="pr-cell pr-num">
              <span class="eng-pill" :class="engClass(p.engagement)">{{ p.engagement }}%</span>
            </div>
          </div>
          <div v-if="!filteredPosts.length" class="empty-state">
            Sense publicacions {{ contentPlatform !== 'all' ? 'en aquesta plataforma' : 'vinculades a aquesta campanya' }}.
          </div>
        </div>
      </section>

      <!-- ══ SECCIÓ: INFLUENCERS ════════════════════════════════ -->
      <section :ref="el => sectionRefs['influencers'] = el" class="page-section">
        <div class="section-head">
          <h2 class="section-title">Influencers</h2>
          <span class="section-count">{{ linkedCollabs.length }} col·laboracions</span>
        </div>

        <!-- Cercador -->
        <div class="search-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="influencerSearch"
            class="search-input"
            placeholder="Cercar per nom o àlies..."
          />
        </div>

        <!-- Llista d'influencers -->
        <div class="card influencers-card">
          <div
            v-for="collab in filteredCollabs"
            :key="collab.id"
            class="influencer-row"
            @click="goToInfluencer(collab.influencerId)"
          >
            <div class="inf-avatar" :style="avatarStyle(collab.influencerName)">
              {{ collab.influencerName[0] }}
            </div>
            <div class="inf-main">
              <div class="inf-name">{{ collab.influencerName }}</div>
              <div class="inf-alias">{{ collab.influencerAlias }}</div>
            </div>
            <div class="inf-collab">
              <div class="ic-format">{{ collab.format }}</div>
              <div class="ic-date">{{ formatDateShort(collab.publishDate) }}</div>
            </div>
            <div class="inf-reach">
              <div class="ir-val">{{ collab.reach > 0 ? formatNumber(collab.reach) : '—' }}</div>
              <div class="ir-key">abast</div>
            </div>
            <div class="inf-status">
              <span class="badge badge-sm" :class="COLLAB_STATUSES[collab.status].cls">
                {{ COLLAB_STATUSES[collab.status].label }}
              </span>
            </div>
            <ChevronRight :size="16" class="inf-arrow" />
          </div>
          <div v-if="!filteredCollabs.length" class="empty-state">
            {{ linkedCollabs.length ? 'Sense resultats per a aquesta cerca.' : 'Sense col·laboracions d\'influencer en aquesta campanya.' }}
          </div>
        </div>
      </section>

      <!-- ══ SECCIÓ: ANUNCIS DE PAGAMENT ══════════════════════ -->
      <section :ref="el => sectionRefs['ads'] = el" class="page-section">
        <div class="section-head">
          <h2 class="section-title">Anuncis de pagament</h2>
          <span v-if="adsByPlatform.length" class="section-count">{{ adsByPlatform.length }} plataforma{{ adsByPlatform.length !== 1 ? 'es' : '' }}</span>
        </div>

        <div v-if="adsByPlatform.length" class="ads-grid">
          <div v-for="group in adsByPlatform" :key="group.platform" class="ad-platform-card">
            <div class="apc-header">
              <span class="plat-pill" :style="adPlatformStyle(group.platform)">
                {{ getAdPlatform(group.platform).label }}
              </span>
              <span class="sync-tag">
                <RefreshCw :size="10" /> Sincronitzat
              </span>
            </div>
            <div class="apc-metrics">
              <div class="apm-cell">
                <div class="apm-val">{{ formatCurrency(group.spend) }}</div>
                <div class="apm-key">Despesa</div>
              </div>
              <div class="apm-cell">
                <div class="apm-val">{{ formatNumber(group.impressions) }}</div>
                <div class="apm-key">Impressions</div>
              </div>
              <div class="apm-cell">
                <div class="apm-val">{{ formatNumber(group.clicks) }}</div>
                <div class="apm-key">Clics</div>
              </div>
              <div class="apm-cell">
                <div class="apm-val">{{ group.conversions }}</div>
                <div class="apm-key">Conversions</div>
              </div>
              <div class="apm-cell">
                <div class="apm-val" :class="roasClass(group.roas)">
                  {{ group.roas > 0 ? group.roas.toFixed(2) + 'x' : '—' }}
                </div>
                <div class="apm-key">ROAS</div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-card">
          Sense anuncis de pagament vinculats. En editar la campanya podeu afegir els conjunts d'anuncis de cada plataforma i el seu ID de campanya extern per activar la sincronització.
        </div>

        <div v-if="adsByPlatform.length" class="ads-note">
          <Info :size="13" />
          Els anuncis es gestionen directament a Meta Ads Manager, Google Ads, etc. L'ERP rep i mostra les dades de rendiment.
        </div>
      </section>

      <!-- ══ SECCIÓ: ATRIBUCIÓ ═════════════════════════════════ -->
      <section :ref="el => sectionRefs['attribution'] = el" class="page-section">
        <div class="section-head">
          <h2 class="section-title">Atribució</h2>
          <span class="section-count">{{ linkedLinks.length }} enllaços UTM</span>
        </div>

        <div v-if="linkedLinks.length" class="card">
          <div class="links-head">
            <div class="lh-col lh-main">Enllaç</div>
            <div class="lh-col">Origen</div>
            <div class="lh-col lh-num">Clics</div>
            <div class="lh-col lh-num">Compres</div>
            <div class="lh-col lh-num">Ingressos</div>
            <div class="lh-col lh-num">Conversió</div>
          </div>
          <div v-for="l in linkedLinks" :key="l.id" class="link-row">
            <div class="lr-main">
              <div class="link-name">{{ l.name }}</div>
              <code class="utm-chip">{{ l.utmCampaign }}</code>
            </div>
            <div class="lr-cell">
              <span class="plat-pill" :style="platformStyle(l.origin)">
                {{ getPlatform(l.origin).label }}
              </span>
            </div>
            <div class="lr-cell lr-num">{{ formatNumber(l.clicks) }}</div>
            <div class="lr-cell lr-num">{{ formatNumber(l.purchases) }}</div>
            <div class="lr-cell lr-num font-medium">{{ formatCurrency(l.revenue) }}</div>
            <div class="lr-cell lr-num">
              <span class="conv-pill" :class="convClass(l.conversion)">
                {{ l.conversion.toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>

        <div v-else class="empty-card">
          Sense enllaços UTM generats per a aquesta campanya. Els enllaços d'atribució permeten mesurar conversions per canal i font de trànsit.
        </div>
      </section>

    </div>

    <!-- Not found -->
    <div v-else-if="!loading" class="not-found">
      <AlertCircle :size="40" />
      <p>Campanya no trobada.</p>
      <router-link to="/social-crm/campaigns" class="btn btn-secondary">Tornar a campanyes</router-link>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronLeft, ChevronRight, Calendar, User, Search,
  AlertCircle, RefreshCw, Info,
  Image as ImageIcon, Film, Layers, MessageSquare, FileText,
} from 'lucide-vue-next'
import {
  CAMPAIGN_STATUSES, COLLAB_STATUSES,
  getPlatform, getAdPlatform, formatNumber, formatCurrency, formatDate,
  PLATFORMS,
} from '@/services/socialCrmData'
import socialCrmApi, { enrichWithBreakdown } from '@/services/socialCrm'
import { useToast } from '@/composables/useToast'

const route  = useRoute()
const router = useRouter()
const toast  = useToast()

// ── Dades carregades del backend (social_crm) ─────────────────
const campaign      = ref(null)
const linkedPosts   = ref([])
const linkedCollabs = ref([])
const linkedAds     = ref([])
const linkedLinks   = ref([])
const loading       = ref(true)

async function loadCampaign() {
  const id = Number(route.params.id)
  loading.value = true
  try {
    const [camp, bd, posts, collabs, ads, links] = await Promise.all([
      socialCrmApi.getCampaign(id),
      socialCrmApi.channelBreakdown(id),
      socialCrmApi.listPosts({ campaign: id }),
      socialCrmApi.listCollaborations({ campaign: id }),
      socialCrmApi.listAdSets({ campaign: id }),
      socialCrmApi.listLinks({ campaign: id }),
    ])
    enrichWithBreakdown(camp, bd)
    campaign.value      = camp
    linkedPosts.value   = posts
    linkedCollabs.value = collabs
    linkedAds.value     = ads
    linkedLinks.value   = links
  } catch (e) {
    campaign.value = null
    toast.error(e.message || 'No s\'ha pogut carregar la campanya.')
  } finally {
    loading.value = false
  }
}

onMounted(loadCampaign)
watch(() => route.params.id, loadCampaign)

// ── Seccions ─────────────────────────────────────────────────
const sections = [
  { key: 'general',     label: 'General' },
  { key: 'content',     label: 'Contingut' },
  { key: 'influencers', label: 'Influencers' },
  { key: 'ads',         label: 'Anuncis' },
  { key: 'attribution', label: 'Atribució' },
]
const activeSection = ref('general')
const sectionRefs = ref({})

function scrollTo(key) {
  activeSection.value = key
  const el = sectionRefs.value[key]
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// ── Mètriques overview (suma de tots els canals) ─────────────
const overview = computed(() => {
  const posts   = linkedPosts.value
  const collabs = linkedCollabs.value
  const ads     = linkedAds.value

  const reach       = posts.reduce((s, p) => s + (p.reach || 0), 0)
                    + collabs.reduce((s, c) => s + (c.reach || 0), 0)
  const impressions = posts.reduce((s, p) => s + (p.impressions || 0), 0)
                    + ads.reduce((s, a) => s + (a.impressions || 0), 0)
  const interactions = posts.reduce((s, p) => s + (p.likes || 0) + (p.comments || 0) + (p.shares || 0), 0)
  const avgEngagement = posts.length
    ? posts.reduce((s, p) => s + (p.engagement || 0), 0) / posts.length
    : 0

  return { reach, impressions, interactions, avgEngagement }
})

const perceptionClass = computed(() => {
  const e = overview.value.avgEngagement
  return e >= 5 ? 'perception-good' : e >= 2 ? 'perception-mid' : 'perception-low'
})
const perceptionLabel = computed(() => {
  const e = overview.value.avgEngagement
  return e >= 5 ? 'Bona resposta' : e >= 2 ? 'Resposta normal' : 'Interacció baixa'
})

// ── Pressupost ────────────────────────────────────────────────
const budgetPct = computed(() =>
  campaign.value?.budget ? (campaign.value.cost / campaign.value.budget) * 100 : 0
)
const budgetClass = computed(() => {
  const p = budgetPct.value
  return p > 100 ? 'bd-over' : p > 90 ? 'bd-warn' : 'bd-ok'
})
const campaignDays = computed(() => {
  if (!campaign.value) return 0
  return Math.round((new Date(campaign.value.endDate) - new Date(campaign.value.startDate)) / 86400000)
})

// ── Contingut propi ───────────────────────────────────────────
const contentPlatform = ref('all')

const contentStats = computed(() => {
  const posts = linkedPosts.value
  return {
    reach:          posts.reduce((s, p) => s + (p.reach    || 0), 0),
    likes:          posts.reduce((s, p) => s + (p.likes    || 0), 0),
    comments:       posts.reduce((s, p) => s + (p.comments || 0), 0),
    shares:         posts.reduce((s, p) => s + (p.shares   || 0), 0),
    avgEngagement:  posts.length ? posts.reduce((s, p) => s + (p.engagement || 0), 0) / posts.length : 0,
  }
})

const availablePostPlatforms = computed(() => {
  const keys = [...new Set(linkedPosts.value.map(p => p.platform))]
  return Object.fromEntries(keys.map(k => [k, getPlatform(k)]))
})

const filteredPosts = computed(() => {
  if (contentPlatform.value === 'all') return linkedPosts.value
  return linkedPosts.value.filter(p => p.platform === contentPlatform.value)
})

// ── Influencers ────────────────────────────────────────────────
const influencerSearch = ref('')

const filteredCollabs = computed(() => {
  const q = influencerSearch.value.toLowerCase()
  if (!q) return linkedCollabs.value
  return linkedCollabs.value.filter(c =>
    c.influencerName.toLowerCase().includes(q) ||
    (c.influencerAlias || '').toLowerCase().includes(q)
  )
})

function goToInfluencer(influencerId) {
  if (influencerId) {
    router.push(`/social-crm/influencers?open=${influencerId}`)
  }
}

// ── Anuncis agrupats per plataforma ─────────────────────────
const adsByPlatform = computed(() => {
  const map = {}
  linkedAds.value.forEach(ad => {
    if (!map[ad.platform]) {
      map[ad.platform] = { platform: ad.platform, spend: 0, impressions: 0, clicks: 0, conversions: 0, sales: 0 }
    }
    map[ad.platform].spend       += ad.spend  || 0
    map[ad.platform].impressions += ad.impressions || 0
    map[ad.platform].clicks      += ad.clicks      || 0
    map[ad.platform].conversions += ad.conversions || 0
    map[ad.platform].sales       += ad.sales || 0
  })
  return Object.values(map).map(g => ({
    ...g,
    roas: g.spend > 0 ? g.sales / g.spend : 0,
  }))
})

// ── Helpers ────────────────────────────────────────────────────
function platformStyle(key)   { const p = getPlatform(key);   return { background: p.bg, color: p.color } }
function adPlatformStyle(key) { const p = getAdPlatform(key); return { background: p.bg, color: p.color } }

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

function engClass(v)  { return v >= 5 ? 'eng-high' : v >= 2 ? 'eng-mid' : 'eng-low' }
function roasClass(v) { return v >= 3 ? 'roas-good' : v >= 1 ? 'roas-ok' : 'roas-bad' }
function convClass(v) { return v >= 5 ? 'eng-high' : v >= 2 ? 'eng-mid' : 'eng-low' }

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
.campaign-page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* ── Capçalera ────────────────────────────────────────── */
.page-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-md) var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}
.back-link:hover { color: var(--primary-color); }
.header-right { display: flex; align-items: center; gap: var(--spacing-sm); }

.badge { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.badge-sm { font-size: 0.65rem; padding: 2px 7px; }
.obj-pill {
  font-size: 0.72rem;
  padding: 3px 9px;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.page-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

/* Nav de seccions */
.section-nav {
  display: flex;
  gap: 0;
  border-top: 1px solid var(--border-color);
  margin: 0 calc(-1 * var(--spacing-xl));
  padding: 0 var(--spacing-xl);
}
.snav-btn {
  padding: 0.625rem 1rem;
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.15s, border-color 0.15s;
  font-family: var(--font-family);
  white-space: nowrap;
}
.snav-btn:hover { color: var(--text-primary); }
.snav-btn.active {
  color: var(--primary-color);
  font-weight: 700;
  border-bottom-color: var(--primary-color);
}

/* ── Body ────────────────────────────────────────────── */
.page-body {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* ── Seccions ───────────────────────────────────────── */
.page-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  scroll-margin-top: 140px;
}
.section-head {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  border-bottom: 2px solid var(--border-color);
}
.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}
.section-count {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 2px 9px;
  border-radius: 999px;
}

/* Meta de campanya */
.campaign-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}
.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
.meta-item strong { color: var(--text-primary); }
.campaign-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.55;
  margin: 0;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-sm);
  border-left: 3px solid var(--primary-color);
}

/* KPIs socials */
.social-kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}
.sk-tile {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
.sk-tile-highlight { border-width: 2px; }
.sk-tile-highlight.perception-good { border-color: #10B981; background: rgba(16,185,129,0.04); }
.sk-tile-highlight.perception-mid  { border-color: #F59E0B; background: rgba(245,158,11,0.04); }
.sk-tile-highlight.perception-low  { border-color: #EF4444; background: rgba(239,68,68,0.04); }
.sk-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  margin-bottom: 0.4rem;
}
.sk-value {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  font-feature-settings: "tnum";
  line-height: 1.1;
}
.sk-sub { font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 4px; }
.perception-label { font-weight: 700; }
.sk-tile-highlight.perception-good .perception-label { color: #10B981; }
.sk-tile-highlight.perception-mid  .perception-label { color: #F59E0B; }
.sk-tile-highlight.perception-low  .perception-label { color: #EF4444; }

/* Fila secundària */
.secondary-row {
  display: flex;
  gap: var(--spacing-xl);
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  flex-wrap: wrap;
}
.budget-block { flex: 1; min-width: 280px; display: flex; flex-direction: column; gap: 6px; }
.budget-head { display: flex; align-items: center; gap: var(--spacing-sm); }
.budget-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  flex: 1;
}
.budget-nums { display: flex; align-items: baseline; gap: 5px; font-size: var(--font-size-sm); font-feature-settings: "tnum"; }
.budget-of { color: var(--text-secondary); }
.budget-pct { font-weight: 700; }
.budget-pct.bd-ok   { color: #10B981; }
.budget-pct.bd-warn { color: #F59E0B; }
.budget-pct.bd-over { color: #EF4444; }
.budget-bar-wrap { height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden; }
.budget-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}
.budget-bar.bd-ok   { background: linear-gradient(90deg, #667eea, #764ba2); }
.budget-bar.bd-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.budget-bar.bd-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }

.attribution-block {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
}
.attr-label { color: var(--text-secondary); }
.attr-value { font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.attr-sub { color: var(--text-secondary); font-size: var(--font-size-xs); }

/* ── Contingut ───────────────────────────────────────── */
.content-kpis {
  display: flex;
  gap: 0;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.ck-item {
  flex: 1;
  padding: var(--spacing-md) var(--spacing-lg);
  text-align: center;
  border-right: 1px solid var(--border-color);
}
.ck-item:last-child { border-right: none; }
.ck-val { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.ck-key { font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 3px; }

/* Platform filter */
.platform-filter { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.pf-chip {
  padding: 0.375rem 0.875rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  font-weight: 600;
  cursor: pointer;
  font-family: var(--font-family);
  transition: all 0.15s;
}
.pf-chip:hover { border-color: var(--primary-color); color: var(--primary-color); }
.pf-chip.active { background: var(--primary-color); border-color: var(--primary-color); color: white; }

/* Posts card */
.card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.posts-head, .links-head {
  display: grid;
  padding: 0.5rem var(--spacing-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}
.posts-head { grid-template-columns: 2.5fr 0.9fr 1fr 0.8fr 1.1fr 0.9fr; }
.links-head { grid-template-columns: 2fr 0.9fr 0.8fr 0.8fr 1fr 0.9fr; }
.ph-num, .lh-num { text-align: right; }

.post-row {
  display: grid;
  grid-template-columns: 2.5fr 0.9fr 1fr 0.8fr 1.1fr 0.9fr;
  padding: 0.625rem var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  align-items: center;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.post-row:last-child { border-bottom: none; }
.post-row:hover { background: var(--bg-secondary); }

.pr-main { display: flex; align-items: center; gap: var(--spacing-sm); }
.post-thumb {
  width: 30px; height: 30px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: white; flex-shrink: 0;
}
.post-info { min-width: 0; }
.post-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.post-date { font-size: var(--font-size-xs); color: var(--text-tertiary); margin-top: 1px; }

.pr-cell { display: flex; align-items: center; }
.pr-num { justify-content: flex-end; font-size: var(--font-size-sm); color: var(--text-primary); font-feature-settings: "tnum"; }

.plat-pill { font-size: 0.65rem; font-weight: 600; padding: 2px 7px; border-radius: 999px; }

.eng-pill { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; }
.eng-high { background: rgba(16,185,129,0.1); color: #10B981; }
.eng-mid  { background: rgba(245,158,11,0.1); color: #F59E0B; }
.eng-low  { background: rgba(239,68,68,0.08); color: #EF4444; }

/* ── Influencers ─────────────────────────────────────── */
.search-wrap {
  position: relative;
  max-width: 380px;
}
.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(102,126,234,0.12);
}

.influencer-row {
  display: grid;
  grid-template-columns: auto 1fr 1fr 100px auto auto;
  gap: var(--spacing-md);
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background var(--transition-fast);
}
.influencer-row:last-child { border-bottom: none; }
.influencer-row:hover { background: var(--bg-secondary); }

.inf-avatar {
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}
.inf-main { min-width: 0; }
.inf-name { font-size: var(--font-size-sm); font-weight: 700; color: var(--text-primary); }
.inf-alias { font-size: var(--font-size-xs); color: var(--text-secondary); margin-top: 1px; }
.inf-collab { display: flex; flex-direction: column; gap: 1px; }
.ic-format { font-size: var(--font-size-sm); font-weight: 500; color: var(--text-primary); }
.ic-date { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.inf-reach { text-align: right; }
.ir-val { font-size: var(--font-size-sm); font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; }
.ir-key { font-size: var(--font-size-xs); color: var(--text-secondary); }
.inf-status { display: flex; justify-content: flex-end; }
.inf-arrow { color: var(--text-secondary); flex-shrink: 0; }
.influencer-row:hover .inf-arrow { color: var(--primary-color); }

/* ── Anuncis ────────────────────────────────────────── */
.ads-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-md);
}
.ad-platform-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.apc-header { display: flex; align-items: center; justify-content: space-between; }
.sync-tag {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.68rem; font-weight: 600; color: #10B981;
}
.apc-metrics {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-sm);
}
.apm-cell { text-align: center; }
.apm-val { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; line-height: 1.1; }
.apm-key { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-top: 3px; }
.roas-good { color: #10B981; }
.roas-ok   { color: #F59E0B; }
.roas-bad  { color: #EF4444; }

.ads-note {
  display: flex; align-items: flex-start; gap: var(--spacing-sm);
  padding: var(--spacing-md); font-size: var(--font-size-xs);
  color: var(--text-secondary); line-height: 1.5;
  background: var(--bg-secondary); border-radius: var(--border-radius-sm);
}
.ads-note svg { flex-shrink: 0; margin-top: 1px; }

/* ── Atribució ──────────────────────────────────────── */
.link-row {
  display: grid;
  grid-template-columns: 2fr 0.9fr 0.8fr 0.8fr 1fr 0.9fr;
  padding: 0.625rem var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  align-items: center;
  transition: background var(--transition-fast);
}
.link-row:last-child { border-bottom: none; }
.link-row:hover { background: var(--bg-secondary); }
.lr-main { display: flex; flex-direction: column; gap: 2px; }
.link-name { font-size: var(--font-size-sm); font-weight: 600; color: var(--text-primary); }
.utm-chip {
  font-size: 0.68rem; font-family: monospace;
  background: rgba(102,126,234,0.1); color: var(--primary-color);
  padding: 1px 6px; border-radius: 4px;
  align-self: flex-start;
}
.lr-cell { display: flex; align-items: center; }
.lr-num { justify-content: flex-end; font-size: var(--font-size-sm); font-feature-settings: "tnum"; color: var(--text-primary); }
.font-medium { font-weight: 600; }
.conv-pill { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; }

/* ── Empty states ────────────────────────────────────── */
.empty-state {
  padding: var(--spacing-xl) var(--spacing-lg);
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
.empty-card {
  padding: var(--spacing-xl) var(--spacing-lg);
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  line-height: 1.6;
  box-shadow: var(--shadow-sm);
}

/* ── Not found ───────────────────────────────────────── */
.not-found {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: var(--spacing-md);
  padding: 6rem var(--spacing-xl);
  color: var(--text-secondary); text-align: center;
}
.not-found p { font-size: var(--font-size-lg); color: var(--text-primary); }
.not-found .btn { display: inline-flex; align-items: center; gap: 6px; }

/* ── Responsive ──────────────────────────────────────── */
@media (max-width: 1100px) {
  .social-kpis { grid-template-columns: repeat(2, 1fr); }
  .post-row, .posts-head { grid-template-columns: 1.8fr 0.9fr 1fr 0.8fr 0; }
  .post-row > *:nth-child(5), .posts-head > *:nth-child(5) { display: none; }
}
@media (max-width: 800px) {
  .page-body { padding: var(--spacing-lg); }
  .apc-metrics { grid-template-columns: repeat(3, 1fr); }
  .influencer-row { grid-template-columns: auto 1fr auto auto; }
  .inf-collab, .inf-reach { display: none; }
  .secondary-row { flex-direction: column; align-items: flex-start; }
  .social-kpis { grid-template-columns: 1fr 1fr; }
  .content-kpis { flex-wrap: wrap; }
  .ck-item { min-width: 80px; }
}
@media (max-width: 600px) {
  .posts-head { display: none; }
  .post-row {
    grid-template-columns: auto 1fr auto;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
  }
  .pr-main { grid-column: 1 / 2; }
  .post-row > *:nth-child(2),
  .post-row > *:nth-child(3),
  .post-row > *:nth-child(4),
  .post-row > *:nth-child(5) { display: none; }
}
</style>
