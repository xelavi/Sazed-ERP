<template>
  <SocialHubLayout
    title="Influencers"
    subtitle="Catálogo, colaboraciones activas y carga de métricas en una sola superficie."
    :tabs="tabs"
    v-model="activeTab"
    :panel-open="!!panel.kind"
    @close-panel="closePanel"
  >
    <!-- ── Header actions (right side of title) ──────────────── -->
    <template #actions>
      <div class="hub-filter-group">
        <select v-model="periodFilter" class="hub-mini-select" aria-label="Periodo">
          <option value="30d">Últimos 30 días</option>
          <option value="90d">Últimos 3 meses</option>
          <option value="ytd">Año actual</option>
        </select>
        <select v-model="platformFilter" class="hub-mini-select" aria-label="Plataforma">
          <option value="all">Todas las redes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
      </div>
      <button class="hub-btn hub-btn-primary" @click="onPrimaryAction">
        <Plus :size="16" />
        <span>{{ primaryActionLabel }}</span>
      </button>
    </template>

    <!-- ── KPI strip (always visible at top of hub body) ─────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Influencers activos</div>
        <div class="kpi-val">{{ kpis.activeInfluencers }}<span class="kpi-suffix">/{{ kpis.totalInfluencers }}</span></div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Colaboraciones activas</div>
        <div class="kpi-val">{{ kpis.activeCollabs }}</div>
        <div class="kpi-sub">{{ kpis.completedCollabs }} completadas · {{ kpis.draftCollabs }} en draft</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Ventas atribuidas</div>
        <div class="kpi-val">{{ formatCurrency(kpis.attributedSales) }}</div>
        <div class="kpi-sub">ROAS medio {{ kpis.avgRoas.toFixed(2) }}x</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Métricas pendientes</div>
        <div class="kpi-val" :class="{ 'kpi-warn': kpis.pendingMetrics > 0 }">{{ kpis.pendingMetrics }}</div>
        <div class="kpi-sub">colaboraciones sin reportar</div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         TAB 1 · CATÁLOGO
       ══════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'catalog'" class="tab-section">
      <div class="filters-row">
        <div class="search-input-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="searchQ"
            class="filter-input search-input"
            placeholder="Buscar por nombre o alias..."
          />
        </div>
        <select v-model="nicheFilter" class="filter-input">
          <option value="all">Todos los nichos</option>
          <option v-for="n in niches" :key="n" :value="n">{{ n }}</option>
        </select>
        <select v-model="statusFilter" class="filter-input">
          <option value="all">Todos los estados</option>
          <option value="active">Activos</option>
          <option value="prospect">Prospectos</option>
          <option value="archived">Archivados</option>
        </select>
        <select v-model="sizeFilter" class="filter-input">
          <option value="all">Cualquier tamaño</option>
          <option value="nano">Nano (&lt;10K)</option>
          <option value="micro">Micro (10K–100K)</option>
          <option value="macro">Macro (100K–1M)</option>
          <option value="mega">Mega (&gt;1M)</option>
        </select>
        <div class="result-count">{{ filteredInfluencers.length }} resultados</div>
      </div>

      <div class="data-card">
        <div class="data-head">
          <div class="th th-name">Influencer</div>
          <div class="th th-platform">Red</div>
          <div class="th th-num">Seguidores</div>
          <div class="th">Nicho</div>
          <div class="th th-num">Engagement</div>
          <div class="th th-num">Colabs</div>
          <div class="th th-num">Ventas</div>
          <div class="th th-rating">Rating</div>
          <div class="th"></div>
        </div>
        <div class="data-rows">
          <button
            v-for="inf in filteredInfluencers"
            :key="inf.id"
            class="data-row"
            :class="{ active: panel.kind === 'influencer' && panel.id === inf.id }"
            @click="openInfluencer(inf.id)"
          >
            <div class="cell cell-name">
              <div class="avatar" :style="avatarStyle(inf)">{{ inf.name[0] }}</div>
              <div class="name-block">
                <div class="row-name">{{ inf.name }}</div>
                <div class="row-alias">{{ inf.alias }}</div>
              </div>
            </div>
            <div class="cell">
              <span class="platform-pill" :style="platformStyle(inf.platform)">
                {{ getPlatform(inf.platform).label }}
              </span>
            </div>
            <div class="cell cell-num font-mono">{{ formatNumber(inf.followers) }}</div>
            <div class="cell">
              <span class="niche-tag">{{ inf.niche }}</span>
            </div>
            <div class="cell cell-num">
              <span class="eng-pill" :class="engClass(inf.engagementMid)">
                {{ inf.engagementMid }}%
              </span>
            </div>
            <div class="cell cell-num font-mono">{{ inf.collaborations }}</div>
            <div class="cell cell-num font-mono">{{ formatCurrency(inf.salesGenerated) }}</div>
            <div class="cell cell-rating">
              <template v-if="inf.rating > 0">
                <Star :size="12" class="star-filled" />
                <span class="rating-num">{{ inf.rating.toFixed(1) }}</span>
              </template>
              <span v-else class="muted">—</span>
            </div>
            <div class="cell cell-status">
              <span class="status-dot" :class="'st-' + inf.status"></span>
            </div>
          </button>
          <div v-if="!filteredInfluencers.length" class="empty-row">
            <Frown :size="20" />
            <span>No hay influencers que coincidan con los filtros.</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         TAB 2 · COLABORACIONES
       ══════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'collaborations'" class="tab-section">
      <div class="filters-row">
        <select v-model="collabStatus" class="filter-input">
          <option value="all">Todos los estados</option>
          <option v-for="(s, k) in COLLAB_STATUSES" :key="k" :value="k">{{ s.label }}</option>
        </select>
        <select v-model="collabCampaign" class="filter-input">
          <option value="all">Todas las campañas</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="collabInfluencer" class="filter-input">
          <option value="all">Todos los influencers</option>
          <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
        </select>
        <div class="result-count">{{ filteredCollabs.length }} colaboraciones</div>
      </div>

      <div class="data-card">
        <div class="data-head head-collabs">
          <div class="th">Influencer</div>
          <div class="th">Campaña</div>
          <div class="th">Formato</div>
          <div class="th">Fecha</div>
          <div class="th th-num">Coste</div>
          <div class="th">Código</div>
          <div class="th th-num">Conv.</div>
          <div class="th th-num">Ventas</div>
          <div class="th th-status">Estado</div>
        </div>
        <div class="data-rows">
          <button
            v-for="c in filteredCollabs"
            :key="c.id"
            class="data-row row-collab"
            :class="{ active: panel.kind === 'collaboration' && panel.id === c.id }"
            @click="openCollaboration(c.id)"
          >
            <div class="cell cell-name">
              <div class="avatar avatar-sm" :style="avatarStyleByName(c.influencerName)">
                {{ c.influencerName[0] }}
              </div>
              <div class="name-block">
                <div class="row-name">{{ c.influencerName }}</div>
                <div class="row-alias">{{ c.influencerAlias }}</div>
              </div>
            </div>
            <div class="cell"><span class="link-text">{{ c.campaignName }}</span></div>
            <div class="cell muted">{{ c.format }}</div>
            <div class="cell muted">{{ formatDate(c.publishDate) }}</div>
            <div class="cell cell-num font-mono">{{ formatCurrency(c.cost) }}</div>
            <div class="cell"><code class="code-chip">{{ c.code }}</code></div>
            <div class="cell cell-num font-mono">{{ c.conversions }}</div>
            <div class="cell cell-num font-mono">{{ formatCurrency(c.sales) }}</div>
            <div class="cell">
              <span class="badge" :class="COLLAB_STATUSES[c.status].cls">
                {{ COLLAB_STATUSES[c.status].label }}
              </span>
            </div>
          </button>
          <div v-if="!filteredCollabs.length" class="empty-row">
            <Frown :size="20" />
            <span>No hay colaboraciones registradas con esos filtros.</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         TAB 3 · CARGA DE MÉTRICAS
       ══════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'metrics'" class="tab-section metrics-tab">
      <div class="metrics-grid">
        <!-- Form -->
        <div class="form-card">
          <div class="form-card-head">
            <div>
              <h3 class="form-card-title">Reportar métricas de una colaboración</h3>
              <p class="form-card-sub">Carga manual de datos cuando la API no está disponible.</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="field field-full">
              <label class="field-label">Influencer</label>
              <select v-model.number="form.influencerId" class="field-input" @change="onInfluencerChange">
                <option :value="null">— Seleccionar —</option>
                <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">
                  {{ i.name }} ({{ i.alias }})
                </option>
              </select>
            </div>
            <div class="field field-full">
              <label class="field-label">Colaboración</label>
              <select v-model.number="form.collaborationId" class="field-input" :disabled="!form.influencerId">
                <option :value="null">{{ form.influencerId ? '— Seleccionar —' : 'Selecciona influencer primero' }}</option>
                <option v-for="c in availableCollabs" :key="c.id" :value="c.id">
                  {{ c.campaignName }} — {{ formatDate(c.publishDate) }}
                </option>
              </select>
            </div>
            <div class="field">
              <label class="field-label">Descripción de la publicación</label>
              <input v-model="form.publicationDesc" class="field-input" placeholder="Ej: TikTok #1 — Primavera" />
            </div>
            <div class="field">
              <label class="field-label">Fecha real</label>
              <input v-model="form.date" type="date" class="field-input" />
            </div>

            <div class="field-section">
              <span class="field-section-label">Alcance</span>
            </div>
            <div class="field"><label class="field-label">Alcance</label>
              <input v-model.number="form.reach" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Impresiones</label>
              <input v-model.number="form.impressions" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Visualizaciones</label>
              <input v-model.number="form.views" type="number" class="field-input" placeholder="0" /></div>

            <div class="field-section">
              <span class="field-section-label">Interacción</span>
            </div>
            <div class="field"><label class="field-label">Likes</label>
              <input v-model.number="form.likes" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Comentarios</label>
              <input v-model.number="form.comments" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Compartidos</label>
              <input v-model.number="form.shares" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Clics</label>
              <input v-model.number="form.clicks" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Conversiones</label>
              <input v-model.number="form.conversions" type="number" class="field-input" placeholder="0" /></div>
            <div class="field"><label class="field-label">Ventas (€)</label>
              <input v-model.number="form.sales" type="number" class="field-input" placeholder="0" /></div>

            <div class="field-section">
              <span class="field-section-label">Trazabilidad</span>
            </div>
            <div class="field"><label class="field-label">Fuente del dato</label>
              <select v-model="form.source" class="field-input">
                <option value="screenshot">Captura de pantalla</option>
                <option value="api">API / Plataforma</option>
                <option value="email">Email del influencer</option>
                <option value="report">Informe PDF</option>
                <option value="other">Otro</option>
              </select>
            </div>
            <div class="field"><label class="field-label">Estado</label>
              <select v-model="form.status" class="field-input">
                <option value="pending">Pendiente de validar</option>
                <option value="validated">Validado</option>
              </select>
            </div>

            <div class="field field-full">
              <div class="upload-zone">
                <Upload :size="18" />
                <span class="upload-text">Arrastra capturas, PDFs o evidencias</span>
                <button class="upload-btn">Seleccionar archivos</button>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button class="hub-btn hub-btn-ghost" @click="resetForm">Limpiar</button>
            <button class="hub-btn hub-btn-primary" @click="submitMetrics">
              <Save :size="15" />
              Guardar métricas
            </button>
          </div>
        </div>

        <!-- History sidebar -->
        <aside class="history-card">
          <div class="history-head">
            <h3 class="history-title">Historial reciente</h3>
            <span class="history-count">{{ history.length }}</span>
          </div>
          <ul class="history-list">
            <li v-for="h in history" :key="h.id" class="history-item">
              <div class="hist-status" :class="h.status === 'validated' ? 'st-validated' : 'st-pending'">
                <CheckCircle v-if="h.status === 'validated'" :size="11" />
                <Clock v-else :size="11" />
              </div>
              <div class="hist-body">
                <div class="hist-name">{{ h.influencerName }}</div>
                <div class="hist-meta">{{ h.publicationDesc }}</div>
                <div class="hist-foot">{{ formatDate(h.date) }} · {{ h.uploadedBy }}</div>
              </div>
            </li>
            <li v-if="!history.length" class="hist-empty">Sin cargas todavía.</li>
          </ul>
        </aside>
      </div>
    </section>

    <!-- ══════════════════════════════════════════════════════════
         SIDE PANEL · contenido dinámico según panel.kind
       ══════════════════════════════════════════════════════════ -->
    <template #panel>
      <InfluencerDetailPanel
        v-if="panel.kind === 'influencer'"
        :influencer-id="panel.id"
        @close="closePanel"
        @open-collab="openCollaboration"
      />
      <CollaborationDetailPanel
        v-else-if="panel.kind === 'collaboration'"
        :collab-id="panel.id"
        @close="closePanel"
        @open-influencer="openInfluencer"
      />
    </template>
  </SocialHubLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import {
  Search, Plus, Star, Frown, Upload, Save, CheckCircle, Clock,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'
import InfluencerDetailPanel from './InfluencerDetailPanel.vue'
import CollaborationDetailPanel from './CollaborationDetailPanel.vue'
import {
  socialInfluencers, socialCollaborations, socialCampaigns, metricsHistory,
  PLATFORMS, COLLAB_STATUSES, getPlatform,
  formatNumber, formatCurrency, formatDate,
} from '@/services/socialCrmData'

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('catalog')

const tabs = computed(() => [
  { key: 'catalog',        label: 'Catálogo',         count: socialInfluencers.length },
  { key: 'collaborations', label: 'Colaboraciones',   count: socialCollaborations.length },
  { key: 'metrics',        label: 'Carga de métricas' },
])

// ── Global header filters ─────────────────────────────────────
const periodFilter   = ref('30d')
const platformFilter = ref('all')

// ── Catalog state ─────────────────────────────────────────────
const searchQ      = ref('')
const nicheFilter  = ref('all')
const statusFilter = ref('all')
const sizeFilter   = ref('all')

const niches = computed(() => [...new Set(socialInfluencers.map(i => i.niche))])

const filteredInfluencers = computed(() => {
  let list = [...socialInfluencers]
  if (platformFilter.value !== 'all') {
    list = list.filter(i => i.platforms?.includes(platformFilter.value) || i.platform === platformFilter.value)
  }
  if (searchQ.value) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(i => i.name.toLowerCase().includes(q) || i.alias.toLowerCase().includes(q))
  }
  if (nicheFilter.value !== 'all')  list = list.filter(i => i.niche === nicheFilter.value)
  if (statusFilter.value !== 'all') list = list.filter(i => i.status === statusFilter.value)
  if (sizeFilter.value !== 'all') {
    list = list.filter(i => {
      if (sizeFilter.value === 'nano')  return i.followers < 10000
      if (sizeFilter.value === 'micro') return i.followers >= 10000 && i.followers < 100000
      if (sizeFilter.value === 'macro') return i.followers >= 100000 && i.followers < 1000000
      if (sizeFilter.value === 'mega')  return i.followers >= 1000000
      return true
    })
  }
  return list
})

// ── Collaborations state ──────────────────────────────────────
const collabStatus     = ref('all')
const collabCampaign   = ref('all')
const collabInfluencer = ref('all')

const filteredCollabs = computed(() => {
  let list = [...socialCollaborations]
  if (collabStatus.value !== 'all')     list = list.filter(c => c.status === collabStatus.value)
  if (collabCampaign.value !== 'all')   list = list.filter(c => c.campaignId === collabCampaign.value)
  if (collabInfluencer.value !== 'all') list = list.filter(c => c.influencerId === collabInfluencer.value)
  return list.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate))
})

// ── Metrics form ──────────────────────────────────────────────
const history = ref([...metricsHistory])
const form = reactive({
  influencerId: null, collaborationId: null, publicationDesc: '', date: '',
  reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0,
  clicks: 0, conversions: 0, sales: 0,
  source: 'screenshot', status: 'pending',
})

const availableCollabs = computed(() =>
  form.influencerId
    ? socialCollaborations.filter(c => c.influencerId === form.influencerId)
    : []
)

function onInfluencerChange() { form.collaborationId = null }
function resetForm() {
  Object.assign(form, {
    influencerId: null, collaborationId: null, publicationDesc: '', date: '',
    reach: 0, impressions: 0, views: 0, likes: 0, comments: 0, shares: 0,
    clicks: 0, conversions: 0, sales: 0, source: 'screenshot', status: 'pending',
  })
}
function submitMetrics() {
  if (!form.influencerId || !form.collaborationId) {
    alert('Selecciona influencer y colaboración'); return
  }
  const inf = socialInfluencers.find(i => i.id === form.influencerId)
  history.value.unshift({
    id: Date.now(),
    date: form.date || new Date().toISOString().split('T')[0],
    influencerName: inf?.name,
    collaborationId: form.collaborationId,
    publicationDesc: form.publicationDesc || 'Sin descripción',
    uploadedBy: 'Usuario actual',
    status: form.status,
    reach: form.reach, impressions: form.impressions, views: form.views,
    likes: form.likes, comments: form.comments, shares: form.shares,
  })
  resetForm()
}

// ── KPIs (always visible across tabs) ─────────────────────────
const kpis = computed(() => {
  const totalInfluencers = socialInfluencers.length
  const activeInfluencers = socialInfluencers.filter(i => i.status === 'active').length
  const activeCollabs    = socialCollaborations.filter(c => c.status === 'active').length
  const completedCollabs = socialCollaborations.filter(c => c.status === 'completed').length
  const draftCollabs     = socialCollaborations.filter(c => c.status === 'draft').length
  const pendingMetrics   = socialCollaborations.filter(c => c.status === 'active' && c.reach === 0).length
  const attributedSales  = socialCollaborations.reduce((s, c) => s + (c.sales || 0), 0)
  const totalCost        = socialCollaborations.reduce((s, c) => s + (c.cost || 0), 0)
  const avgRoas          = totalCost ? attributedSales / totalCost : 0
  return { totalInfluencers, activeInfluencers, activeCollabs, completedCollabs, draftCollabs,
           pendingMetrics, attributedSales, avgRoas }
})

// ── Side panel ────────────────────────────────────────────────
const panel = reactive({ kind: null, id: null })

function openInfluencer(id) { panel.kind = 'influencer';   panel.id = id }
function openCollaboration(id) { panel.kind = 'collaboration'; panel.id = id }
function closePanel() { panel.kind = null; panel.id = null }

// ── Primary action (changes per tab) ──────────────────────────
const primaryActionLabel = computed(() => {
  if (activeTab.value === 'catalog')        return 'Nuevo influencer'
  if (activeTab.value === 'collaborations') return 'Nueva colaboración'
  return 'Cargar métricas'
})
function onPrimaryAction() {
  if (activeTab.value === 'metrics') {
    return // already on the form
  }
  alert(`Abrir formulario para: ${primaryActionLabel.value}`)
}

// ── Helpers ───────────────────────────────────────────────────
function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }

function avatarStyle(inf) {
  // Generate consistent gradient per-influencer
  const seed = (inf.name.charCodeAt(0) + inf.id) % 6
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

function avatarStyleByName(name) {
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

function engClass(v) {
  if (v >= 6) return 'eng-high'
  if (v >= 3) return 'eng-mid'
  return 'eng-low'
}
</script>

<style scoped>
/* ── Header micro-controls ──────────────────────────── */
.hub-filter-group {
  display: flex;
  gap: 0.375rem;
}

.hub-mini-select {
  padding: 0.4rem 0.625rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: border-color 0.15s ease;
}
.hub-mini-select:hover { border-color: var(--primary-color); }

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
.hub-btn-ghost { background: transparent; border-color: var(--border-color); }
.hub-btn-ghost:hover { background: var(--bg-secondary); }

/* ── KPI strip ──────────────────────────────────────── */
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

.kpi-suffix {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
  margin-left: 2px;
}

.kpi-warn { color: #F59E0B; }

.kpi-sub {
  font-size: 0.72rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

/* ── Filters row ────────────────────────────────────── */
.tab-section { display: flex; flex-direction: column; gap: 1rem; }

.filters-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

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

.search-input-wrap { position: relative; flex: 1 1 240px; max-width: 320px; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { width: 100%; padding-left: 2rem; cursor: text; }

.result-count {
  margin-left: auto;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-weight: 500;
}

/* ── Data card (table-style) ────────────────────────── */
.data-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.data-head {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr 0.7fr 1.2fr 1fr 0.4fr;
  padding: 0.625rem 1.25rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-secondary);
}

.head-collabs {
  grid-template-columns: 1.5fr 1.5fr 1.2fr 1fr 1fr 1fr 0.8fr 1fr 1fr;
}

.th-name { padding-left: 0; }
.th-num { text-align: right; }
.th-rating { text-align: right; }
.th-status { text-align: center; }

.data-rows { display: flex; flex-direction: column; }

.data-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.2fr 1fr 0.7fr 1.2fr 1fr 0.4fr;
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

.row-collab {
  grid-template-columns: 1.5fr 1.5fr 1.2fr 1fr 1fr 1fr 0.8fr 1fr 1fr;
}

.data-row:last-child { border-bottom: none; }
.data-row:hover { background: var(--bg-secondary); }
.data-row.active {
  background: rgba(102,126,234,0.06);
  position: relative;
}
.data-row.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
}

.cell {
  display: flex;
  align-items: center;
  min-width: 0;
}
.cell-name { gap: 0.625rem; }
.cell-num { justify-content: flex-end; text-align: right; }
.cell-rating { justify-content: flex-end; gap: 0.25rem; }
.cell-status { justify-content: center; }

.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.avatar-sm { width: 28px; height: 28px; font-size: 0.78rem; }

.name-block { min-width: 0; overflow: hidden; }
.row-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.row-alias {
  font-size: 0.75rem;
  color: var(--text-secondary);
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

.niche-tag {
  font-size: 0.72rem;
  padding: 3px 8px;
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

.star-filled { color: #F59E0B; fill: #F59E0B; }
.rating-num { font-size: 0.78rem; font-weight: 600; color: var(--text-primary); }

.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.st-active   { background: #10B981; box-shadow: 0 0 0 3px rgba(16,185,129,0.15); }
.st-prospect { background: #F59E0B; box-shadow: 0 0 0 3px rgba(245,158,11,0.15); }
.st-archived { background: #94A3B8; }

.muted { color: var(--text-secondary); }

.code-chip {
  background: var(--bg-secondary);
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 0.78rem;
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
  color: var(--text-primary);
  font-weight: 500;
}

.link-text {
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.85rem;
}

.empty-row {
  padding: 2.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ── Metrics tab ────────────────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 1.25rem;
  align-items: start;
}

.form-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.form-card-head {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(102,126,234,0.04), transparent);
}
.form-card-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0 0 0.25rem; letter-spacing: -0.01em; }
.form-card-sub { font-size: 0.825rem; color: var(--text-secondary); margin: 0; }

.form-grid {
  padding: 1.25rem 1.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.875rem;
}

.field { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; }
.field-full { grid-column: 1 / -1; }
.field-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
}
.field-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: inherit;
  transition: all 0.15s ease;
  width: 100%;
  box-sizing: border-box;
}
.field-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }
.field-input:disabled { background: var(--bg-secondary); cursor: not-allowed; opacity: 0.6; }

.field-section {
  grid-column: 1 / -1;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed var(--border-color);
}
.field-section-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--primary-color);
}

.upload-zone {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.upload-text { flex: 1; }
.upload-btn {
  padding: 0.4rem 0.75rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.78rem;
  cursor: pointer;
  font-family: inherit;
  color: var(--text-primary);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

/* History sidebar */
.history-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  position: sticky;
  top: 0;
}
.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.history-title { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.history-count { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 999px; background: var(--bg-secondary); color: var(--text-secondary); }

.history-list {
  list-style: none;
  padding: 0.5rem;
  margin: 0;
  max-height: 480px;
  overflow-y: auto;
}
.history-item {
  display: flex;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  border-radius: 7px;
  transition: background 0.12s ease;
  align-items: flex-start;
}
.history-item:hover { background: var(--bg-secondary); }

.hist-status {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.st-validated { background: rgba(16,185,129,0.14); color: #10B981; }
.st-pending   { background: rgba(245,158,11,0.14); color: #F59E0B; }

.hist-body { min-width: 0; flex: 1; }
.hist-name { font-size: 0.825rem; font-weight: 600; color: var(--text-primary); }
.hist-meta { font-size: 0.75rem; color: var(--text-secondary); margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hist-foot { font-size: 0.7rem; color: var(--text-secondary); margin-top: 4px; opacity: 0.75; }
.hist-empty { padding: 2rem 1rem; text-align: center; color: var(--text-secondary); font-size: 0.85rem; }

/* Badge styles (reuse global variables but ensure visible) */
.badge { font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; white-space: nowrap; }

/* ── Responsive ─────────────────────────────────────── */
@media (max-width: 1280px) {
  .data-head, .data-row {
    grid-template-columns: 2fr 1fr 1fr 1fr 0.8fr 0.6fr 1fr 0.9fr 0.4fr;
  }
  .head-collabs, .row-collab {
    grid-template-columns: 1.4fr 1.4fr 1fr 0.9fr 0.9fr 0.9fr 0.7fr 1fr 1fr;
  }
}

@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .metrics-grid { grid-template-columns: 1fr; }
  .history-card { position: static; }
}

@media (max-width: 900px) {
  .data-head { display: none; }
  .data-row, .row-collab {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.5rem 0.75rem;
    padding: 0.875rem 1rem;
  }
  .cell-name { grid-column: 1 / -1; }
  .cell:not(.cell-name) { font-size: 0.78rem; }
  .form-grid { grid-template-columns: 1fr 1fr; }
  .filters-row { gap: 0.4rem; }
  .filter-input { font-size: 0.78rem; padding: 0.4rem 0.5rem; }
  .result-count { width: 100%; text-align: right; }
}

@media (max-width: 600px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
  .kpi-tile { padding: 0.625rem 0.75rem; }
  .kpi-val { font-size: 1.25rem; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
