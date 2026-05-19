<template>
  <SocialHubLayout
    title="Campañas"
    subtitle="Planificación, rendimiento y cronología de las campañas en redes sociales."
    :tabs="tabs"
    v-model="activeTab"
    :panel-open="!!panel.kind"
    @close-panel="closePanel"
  >
    <template #actions>
      <select v-model="objectiveFilter" class="hub-mini-select">
        <option value="all">Todos los objetivos</option>
        <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
      </select>
      <button class="hub-btn hub-btn-primary" @click="openCreateModal">
        <Plus :size="15" />
        <span>Nueva campaña</span>
      </button>
    </template>

    <!-- ── KPI strip ─────────────────────────────────────────── -->
    <div class="kpi-strip">
      <div class="kpi-tile">
        <div class="kpi-key">Activas</div>
        <div class="kpi-val">{{ kpis.active }}<span class="kpi-suffix">/{{ kpis.total }}</span></div>
        <div class="kpi-sub">{{ kpis.draft }} en borrador · {{ kpis.completed }} cerradas</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Presupuesto activo</div>
        <div class="kpi-val">{{ formatCurrency(kpis.activeBudget) }}</div>
        <div class="kpi-sub">{{ formatCurrency(kpis.activeSpent) }} gastado</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">Ventas atribuidas</div>
        <div class="kpi-val">{{ formatCurrency(kpis.totalSales) }}</div>
        <div class="kpi-sub">en {{ kpis.totalConversions }} conversiones</div>
      </div>
      <div class="kpi-tile">
        <div class="kpi-key">ROAS medio</div>
        <div class="kpi-val">
          <span :class="roasClass(kpis.avgRoas)">{{ kpis.avgRoas.toFixed(2) }}x</span>
        </div>
        <div class="kpi-sub">{{ kpis.bestCampaign?.name || '—' }} top</div>
      </div>
    </div>

    <!-- ════════════════════════════════════════════════════════════
         TAB 1 · LISTA
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'list'" class="tab-section">
      <div class="filters-row">
        <div class="search-input-wrap">
          <Search :size="15" class="search-icon" />
          <input
            v-model="searchQ"
            class="filter-input search-input"
            placeholder="Buscar campaña..."
          />
        </div>
        <select v-model="statusFilter" class="filter-input">
          <option value="all">Todos los estados</option>
          <option v-for="(s, k) in CAMPAIGN_STATUSES" :key="k" :value="k">{{ s.label }}</option>
        </select>
        <select v-model="sortKey" class="filter-input">
          <option value="recent">Más recientes</option>
          <option value="sales">Mayor ventas</option>
          <option value="roas">Mejor ROAS</option>
          <option value="budget">Mayor presupuesto</option>
        </select>
        <div class="result-count">{{ filteredCampaigns.length }} campañas</div>
      </div>

      <div class="campaigns-grid">
        <article
          v-for="c in filteredCampaigns"
          :key="c.id"
          class="campaign-card"
          :class="{ active: panel.kind === 'campaign' && panel.id === c.id, ['st-' + c.status]: true }"
          @click="openCampaign(c.id)"
        >
          <header class="cc-head">
            <span class="badge" :class="CAMPAIGN_STATUSES[c.status].cls">
              {{ CAMPAIGN_STATUSES[c.status].label }}
            </span>
            <span class="objective-tag">{{ c.objective }}</span>
          </header>

          <h3 class="cc-name">{{ c.name }}</h3>

          <div class="cc-period">
            <Calendar :size="12" />
            <span>{{ formatDateShort(c.startDate) }} → {{ formatDateShort(c.endDate) }}</span>
          </div>

          <p v-if="c.description" class="cc-desc">{{ c.description }}</p>

          <!-- Mini KPIs -->
          <div class="cc-stats">
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ c.posts }}</div>
              <div class="cs-key">Posts</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ c.influencers }}</div>
              <div class="cs-key">Influencers</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val font-mono">{{ formatCurrency(c.sales) }}</div>
              <div class="cs-key">Ventas</div>
            </div>
            <div class="cc-stat">
              <div class="cs-val">
                <span class="roas-pill" :class="roasClass(c.roas)">{{ c.roas.toFixed(2) }}x</span>
              </div>
              <div class="cs-key">ROAS</div>
            </div>
          </div>

          <!-- Budget bar -->
          <div class="cc-budget">
            <div class="cb-row">
              <span class="cb-label">Presupuesto</span>
              <span class="cb-val font-mono">
                {{ formatCurrency(c.cost) }}
                <span class="cb-of">/ {{ formatCurrency(c.budget) }}</span>
              </span>
            </div>
            <div class="cb-bar-wrap">
              <div
                class="cb-bar"
                :style="{ width: budgetPct(c) + '%' }"
                :class="{
                  'cb-warn': budgetPct(c) > 90 && budgetPct(c) <= 100,
                  'cb-over': budgetPct(c) > 100,
                }"
              ></div>
            </div>
          </div>

          <div class="cc-arrow">
            <ArrowUpRight :size="14" />
          </div>
        </article>

        <div v-if="!filteredCampaigns.length" class="empty-grid">
          <Frown :size="20" />
          <span>No hay campañas con esos filtros.</span>
        </div>
      </div>
    </section>

    <!-- ════════════════════════════════════════════════════════════
         TAB 2 · CALENDARIO (Gantt)
       ════════════════════════════════════════════════════════════ -->
    <section v-if="activeTab === 'timeline'" class="tab-section timeline-tab">
      <div class="timeline-card">
        <header class="tl-header">
          <div>
            <h3 class="tl-title">Cronograma de campañas</h3>
            <p class="tl-sub">{{ timelineMonths.length }} meses · {{ filteredCampaigns.length }} campañas</p>
          </div>
          <div class="tl-legend">
            <span class="leg-item leg-active">
              <span class="leg-dot"></span> Activa
            </span>
            <span class="leg-item leg-completed">
              <span class="leg-dot"></span> Completada
            </span>
            <span class="leg-item leg-draft">
              <span class="leg-dot"></span> Borrador
            </span>
          </div>
        </header>

        <!-- Month grid -->
        <div class="gantt">
          <!-- Month headers -->
          <div class="gantt-months">
            <div
              v-for="m in timelineMonths"
              :key="m.key"
              class="gantt-month"
              :class="{ 'gantt-month-current': m.isCurrent }"
            >
              <span class="gm-name">{{ m.label }}</span>
            </div>
            <div
              v-if="todayPos !== null"
              class="gantt-today"
              :style="{ left: todayPos + '%' }"
              title="Hoy"
            >
              <span class="today-dot"></span>
              <span class="today-label">Hoy</span>
            </div>
          </div>

          <!-- Campaign rows -->
          <div class="gantt-rows">
            <button
              v-for="c in timelineCampaigns"
              :key="c.id"
              class="gantt-row"
              :class="{ active: panel.kind === 'campaign' && panel.id === c.id }"
              @click="openCampaign(c.id)"
            >
              <div class="gr-name-col">
                <span class="gr-name">{{ c.name }}</span>
                <span class="gr-meta">{{ c.objective }}</span>
              </div>
              <div class="gr-track">
                <!-- Background grid -->
                <div
                  v-for="m in timelineMonths"
                  :key="m.key"
                  class="track-cell"
                  :class="{ 'track-cell-current': m.isCurrent }"
                ></div>
                <!-- Campaign bar -->
                <div
                  class="gr-bar"
                  :class="['st-' + c.status]"
                  :style="{
                    left: c._barLeft + '%',
                    width: c._barWidth + '%',
                  }"
                  :title="`${c.name} · ${formatDate(c.startDate)} → ${formatDate(c.endDate)}`"
                >
                  <span class="bar-label">
                    <span class="bar-status-dot"></span>
                    {{ c.name }}
                  </span>
                </div>
              </div>
            </button>

            <div v-if="!timelineCampaigns.length" class="empty-grid">
              <Frown :size="20" />
              <span>No hay campañas en el rango visible.</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Side panel ─────────────────────────────────────────── -->
    <template #panel>
      <CampaignDetailPanel
        v-if="panel.kind === 'campaign'"
        :campaign-id="panel.id"
        @close="closePanel"
      />
    </template>

    <!-- ── Create modal ──────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
        <div class="modal">
          <header class="modal-header">
            <h2 class="modal-title">Nueva campaña</h2>
            <button class="modal-close" @click="showCreateModal = false">
              <X :size="18" />
            </button>
          </header>
          <div class="modal-body">
            <div class="form-grid">
              <div class="field field-full">
                <label class="field-label">Nombre</label>
                <input v-model="form.name" class="field-input" placeholder="Nombre de la campaña" />
              </div>
              <div class="field">
                <label class="field-label">Objetivo</label>
                <select v-model="form.objective" class="field-input">
                  <option v-for="o in CAMPAIGN_OBJECTIVES" :key="o" :value="o">{{ o }}</option>
                </select>
              </div>
              <div class="field">
                <label class="field-label">Presupuesto (€)</label>
                <input v-model.number="form.budget" type="number" class="field-input" placeholder="0.00" />
              </div>
              <div class="field">
                <label class="field-label">Inicio</label>
                <input v-model="form.startDate" type="date" class="field-input" />
              </div>
              <div class="field">
                <label class="field-label">Fin</label>
                <input v-model="form.endDate" type="date" class="field-input" />
              </div>
              <div class="field field-full">
                <label class="field-label">Responsable</label>
                <input v-model="form.responsible" class="field-input" placeholder="Nombre" />
              </div>
              <div class="field field-full">
                <label class="field-label">Descripción</label>
                <textarea v-model="form.description" class="field-input field-textarea" rows="3"></textarea>
              </div>
            </div>
          </div>
          <footer class="modal-footer">
            <button class="hub-btn hub-btn-ghost" @click="showCreateModal = false">Cancelar</button>
            <button class="hub-btn hub-btn-primary" @click="saveCampaign">Crear campaña</button>
          </footer>
        </div>
      </div>
    </Teleport>
  </SocialHubLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import {
  Search, Plus, Frown, ArrowUpRight, Calendar, X,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'
import CampaignDetailPanel from './CampaignDetailPanel.vue'
import {
  socialCampaigns, CAMPAIGN_STATUSES, CAMPAIGN_OBJECTIVES,
  formatNumber, formatCurrency, formatDate,
} from '@/services/socialCrmData'

// ── Tabs ──────────────────────────────────────────────────────
const activeTab = ref('list')

const tabs = computed(() => [
  { key: 'list',     label: 'Lista',      count: socialCampaigns.length },
  { key: 'timeline', label: 'Cronograma' },
])

// ── Filters ───────────────────────────────────────────────────
const searchQ          = ref('')
const statusFilter     = ref('all')
const objectiveFilter  = ref('all')
const sortKey          = ref('recent')

const filteredCampaigns = computed(() => {
  let list = [...socialCampaigns]
  if (statusFilter.value !== 'all')    list = list.filter(c => c.status === statusFilter.value)
  if (objectiveFilter.value !== 'all') list = list.filter(c => c.objective === objectiveFilter.value)
  if (searchQ.value) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(c => c.name.toLowerCase().includes(q))
  }
  return list.sort((a, b) => {
    if (sortKey.value === 'sales')  return b.sales - a.sales
    if (sortKey.value === 'roas')   return b.roas - a.roas
    if (sortKey.value === 'budget') return b.budget - a.budget
    return new Date(b.startDate) - new Date(a.startDate)
  })
})

// ── KPIs ──────────────────────────────────────────────────────
const kpis = computed(() => {
  const total = socialCampaigns.length
  const active = socialCampaigns.filter(c => c.status === 'active').length
  const draft = socialCampaigns.filter(c => c.status === 'draft').length
  const completed = socialCampaigns.filter(c => c.status === 'completed').length
  const activeCampaigns = socialCampaigns.filter(c => c.status === 'active')
  const activeBudget = activeCampaigns.reduce((s, c) => s + c.budget, 0)
  const activeSpent  = activeCampaigns.reduce((s, c) => s + c.cost, 0)
  const totalSales = socialCampaigns.reduce((s, c) => s + c.sales, 0)
  const totalConversions = socialCampaigns.reduce((s, c) => s + c.conversions, 0)
  const totalCost = socialCampaigns.reduce((s, c) => s + c.cost, 0)
  const avgRoas = totalCost ? totalSales / totalCost : 0
  const bestCampaign = [...socialCampaigns]
    .filter(c => c.cost > 0)
    .sort((a, b) => b.roas - a.roas)[0]
  return { total, active, draft, completed, activeBudget, activeSpent, totalSales, totalConversions, avgRoas, bestCampaign }
})

// ── Timeline (gantt) calculations ─────────────────────────────
const today = new Date()
today.setHours(0, 0, 0, 0)

const timelineMonths = computed(() => {
  // Span the union of all campaign date ranges, padded by 1 month
  if (!filteredCampaigns.value.length) return []
  const allStarts = filteredCampaigns.value.map(c => new Date(c.startDate).getTime())
  const allEnds = filteredCampaigns.value.map(c => new Date(c.endDate).getTime())
  const min = new Date(Math.min(...allStarts))
  const max = new Date(Math.max(...allEnds))
  min.setDate(1); min.setHours(0, 0, 0, 0)
  max.setMonth(max.getMonth() + 1, 1)

  const months = []
  const cur = new Date(min)
  while (cur < max) {
    const monthKey = `${cur.getFullYear()}-${cur.getMonth()}`
    const isCurrent = cur.getFullYear() === today.getFullYear() && cur.getMonth() === today.getMonth()
    months.push({
      key: monthKey,
      label: cur.toLocaleDateString('es-ES', { month: 'short', year: '2-digit' }),
      start: new Date(cur),
      end: new Date(cur.getFullYear(), cur.getMonth() + 1, 1),
      isCurrent,
    })
    cur.setMonth(cur.getMonth() + 1)
  }
  return months
})

const totalSpanMs = computed(() => {
  if (!timelineMonths.value.length) return 1
  const first = timelineMonths.value[0].start
  const last = timelineMonths.value[timelineMonths.value.length - 1].end
  return last.getTime() - first.getTime()
})

const todayPos = computed(() => {
  if (!timelineMonths.value.length) return null
  const first = timelineMonths.value[0].start.getTime()
  const last = timelineMonths.value[timelineMonths.value.length - 1].end.getTime()
  if (today.getTime() < first || today.getTime() > last) return null
  return ((today.getTime() - first) / (last - first)) * 100
})

const timelineCampaigns = computed(() => {
  if (!timelineMonths.value.length) return []
  const firstMs = timelineMonths.value[0].start.getTime()
  return filteredCampaigns.value
    .map(c => {
      const start = new Date(c.startDate).getTime()
      const end = new Date(c.endDate).getTime()
      const left = ((start - firstMs) / totalSpanMs.value) * 100
      const width = ((end - start) / totalSpanMs.value) * 100
      return {
        ...c,
        _barLeft: Math.max(0, left),
        _barWidth: Math.max(width, 2),
      }
    })
    .sort((a, b) => new Date(a.startDate) - new Date(b.startDate))
})

// ── Side panel ────────────────────────────────────────────────
const panel = reactive({ kind: null, id: null })
function openCampaign(id) { panel.kind = 'campaign'; panel.id = id }
function closePanel() { panel.kind = null; panel.id = null }

// ── Create modal ──────────────────────────────────────────────
const showCreateModal = ref(false)
const form = reactive({
  name: '', objective: 'Awareness', budget: 0, startDate: '', endDate: '',
  responsible: '', description: '',
})

function openCreateModal() {
  Object.assign(form, { name: '', objective: 'Awareness', budget: 0, startDate: '', endDate: '', responsible: '', description: '' })
  showCreateModal.value = true
}

function saveCampaign() {
  if (!form.name) return
  socialCampaigns.push({
    id: Date.now(),
    ...form,
    status: 'draft',
    posts: 0, influencers: 0, clicks: 0, conversions: 0, sales: 0,
    reach: 0, impressions: 0, engagement: 0, cost: 0, roas: 0,
    timeline: [],
  })
  showCreateModal.value = false
}

// ── Helpers ───────────────────────────────────────────────────
function formatDateShort(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}
function budgetPct(c) {
  if (!c.budget) return 0
  return (c.cost / c.budget) * 100
}
function roasClass(v) {
  if (v >= 3) return 'roas-good'
  if (v >= 1) return 'roas-ok'
  return 'roas-bad'
}
</script>

<style scoped>
/* ── Header micro-controls ──────────────────────────── */
.hub-mini-select {
  padding: 0.4rem 0.625rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.8rem;
  cursor: pointer;
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
  font-family: inherit;
}
.hub-btn-primary {
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 6px rgba(102,126,234,0.30);
}
.hub-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(102,126,234,0.4); }
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
.kpi-suffix { font-size: 0.85rem; color: var(--text-secondary); font-weight: 500; margin-left: 2px; }
.kpi-sub { font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

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
}
.filter-input:hover { border-color: var(--primary-color); }
.filter-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }

.search-input-wrap { position: relative; flex: 1 1 240px; max-width: 320px; }
.search-icon { position: absolute; left: 0.625rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); pointer-events: none; }
.search-input { width: 100%; padding-left: 2rem; cursor: text; }
.result-count { margin-left: auto; font-size: 0.78rem; color: var(--text-secondary); font-weight: 500; }

/* ── Campaign cards (list tab) ──────────────────────── */
.campaigns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 0.875rem;
}

.campaign-card {
  position: relative;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.125rem 1.25rem 1rem;
  cursor: pointer;
  transition: all 0.18s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}
.campaign-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  opacity: 0;
  transition: opacity 0.2s ease;
}
.campaign-card.st-active::before  { background: linear-gradient(90deg, #10B981, #059669); opacity: 0.85; }
.campaign-card.st-draft::before   { background: linear-gradient(90deg, #94A3B8, #64748B); opacity: 0.5; }
.campaign-card.st-completed::before { background: linear-gradient(90deg, #667eea, #764ba2); opacity: 0.6; }
.campaign-card.st-paused::before  { background: linear-gradient(90deg, #F59E0B, #D97706); opacity: 0.85; }

.campaign-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 8px 22px rgba(102,126,234,0.10);
  transform: translateY(-2px);
}
.campaign-card.active {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.04);
  box-shadow: 0 0 0 3px rgba(102,126,234,0.08);
}

.cc-head { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.badge { font-size: 0.7rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.objective-tag {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.cc-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
  line-height: 1.25;
}

.cc-period {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
  font-feature-settings: "tnum";
}

.cc-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.45;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cc-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  padding: 0.625rem 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}
.cc-stat { text-align: center; }
.cs-val { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); font-feature-settings: "tnum"; line-height: 1.1; }
.cs-key { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

.font-mono { font-feature-settings: "tnum"; font-variant-numeric: tabular-nums; }

.roas-pill {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 999px;
}
.roas-good { background: rgba(16,185,129,0.14); color: #10B981; }
.roas-ok   { background: rgba(245,158,11,0.14); color: #F59E0B; }
.roas-bad  { background: rgba(239,68,68,0.10); color: #EF4444; }

/* Budget bar */
.cc-budget { display: flex; flex-direction: column; gap: 0.3rem; }
.cb-row { display: flex; justify-content: space-between; align-items: baseline; }
.cb-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
.cb-val { font-size: 0.78rem; color: var(--text-primary); font-weight: 600; }
.cb-of { color: var(--text-secondary); font-weight: 400; }

.cb-bar-wrap { height: 5px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.cb-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.cb-bar.cb-warn { background: linear-gradient(90deg, #F59E0B, #D97706); }
.cb-bar.cb-over { background: linear-gradient(90deg, #EF4444, #B91C1C); }

.cc-arrow {
  position: absolute;
  top: 1rem;
  right: 1rem;
  opacity: 0;
  transform: translate(-4px, 4px);
  transition: all 0.18s ease;
  color: var(--primary-color);
}
.campaign-card:hover .cc-arrow { opacity: 1; transform: translate(0, 0); }

.empty-grid {
  grid-column: 1 / -1;
  padding: 3rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

/* ── Timeline (gantt) ───────────────────────────────── */
.timeline-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.tl-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.tl-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.01em; }
.tl-sub { font-size: 0.72rem; color: var(--text-secondary); margin: 2px 0 0; }

.tl-legend { display: flex; gap: 0.875rem; flex-wrap: wrap; }
.leg-item { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; color: var(--text-secondary); }
.leg-dot { width: 8px; height: 8px; border-radius: 2px; }
.leg-active    .leg-dot { background: linear-gradient(135deg, #10B981, #059669); }
.leg-completed .leg-dot { background: linear-gradient(135deg, #667eea, #764ba2); }
.leg-draft     .leg-dot { background: linear-gradient(135deg, #94A3B8, #64748B); }

/* Gantt grid */
.gantt {
  display: grid;
  grid-template-columns: 220px 1fr;
  overflow-x: auto;
}

/* Months header — first col empty placeholder, second col = months */
.gantt-months {
  grid-column: 2;
  display: flex;
  position: relative;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}
.gantt-month {
  flex: 1;
  padding: 0.5rem 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  text-align: center;
  border-right: 1px solid var(--border-color);
  min-width: 75px;
}
.gantt-month:last-child { border-right: none; }
.gantt-month-current {
  background: rgba(102,126,234,0.08);
  color: var(--primary-color);
  font-weight: 700;
}

.gantt-today {
  position: absolute;
  top: 0; bottom: 0;
  z-index: 4;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.today-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #EC4899;
  margin-top: -4px;
  box-shadow: 0 0 0 3px rgba(236,72,153,0.2);
}
.today-label {
  font-size: 0.62rem;
  font-weight: 700;
  color: #EC4899;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--bg-primary);
  padding: 1px 5px;
  border-radius: 4px;
  margin-top: 2px;
}

/* Today vertical line stretches across rows */
.gantt-rows { grid-column: 1 / -1; display: contents; }

.gantt-row {
  display: grid;
  grid-template-columns: 220px 1fr;
  align-items: center;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  transition: background 0.12s ease;
  position: relative;
}
.gantt-row:last-child { border-bottom: none; }
.gantt-row:hover { background: var(--bg-secondary); }
.gantt-row.active { background: rgba(102,126,234,0.05); }
.gantt-row.active::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0; width: 3px;
  background: linear-gradient(180deg, #667eea, #764ba2);
  z-index: 3;
}

.gr-name-col {
  padding: 0.75rem 1rem;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.gr-name {
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gr-meta { font-size: 0.68rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }

.gr-track {
  position: relative;
  height: 48px;
  display: flex;
}

.track-cell {
  flex: 1;
  border-right: 1px dashed var(--border-color);
  min-width: 75px;
}
.track-cell:last-child { border-right: none; }
.track-cell-current { background: rgba(102,126,234,0.04); }

.gr-bar {
  position: absolute;
  top: 50%;
  height: 24px;
  margin-top: -12px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 0.625rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: white;
  overflow: hidden;
  z-index: 2;
  transition: filter 0.15s ease, transform 0.15s ease;
  cursor: pointer;
}
.gr-bar:hover { filter: brightness(1.1); transform: scaleY(1.1); }

.gr-bar.st-active    { background: linear-gradient(135deg, #10B981, #059669); box-shadow: 0 2px 6px rgba(16,185,129,0.3); }
.gr-bar.st-completed { background: linear-gradient(135deg, #667eea, #764ba2); box-shadow: 0 2px 6px rgba(102,126,234,0.3); }
.gr-bar.st-draft     {
  background: repeating-linear-gradient(45deg, #94A3B8, #94A3B8 6px, #64748B 6px, #64748B 12px);
  box-shadow: 0 2px 4px rgba(100,116,139,0.2);
}
.gr-bar.st-paused    { background: linear-gradient(135deg, #F59E0B, #D97706); box-shadow: 0 2px 6px rgba(245,158,11,0.3); }

.bar-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(255,255,255,0.8);
  flex-shrink: 0;
}

/* ── Modal ─────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,0.55);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  backdrop-filter: blur(4px);
}
.modal {
  background: var(--bg-primary);
  border-radius: 14px;
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(15,23,42,0.25);
  overflow: hidden;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-color);
}
.modal-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin: 0; letter-spacing: -0.01em; }
.modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}
.modal-close:hover { background: var(--bg-secondary); color: var(--text-primary); }
.modal-body { padding: 1.25rem; overflow-y: auto; }
.modal-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  background: var(--bg-secondary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
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
  width: 100%;
  box-sizing: border-box;
  transition: all 0.15s ease;
}
.field-input:focus { outline: none; border-color: var(--primary-color); box-shadow: 0 0 0 3px rgba(102,126,234,0.15); }
.field-textarea { resize: vertical; }

/* ── Responsive ────────────────────────────────────── */
@media (max-width: 1100px) {
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
  .gantt { grid-template-columns: 160px 1fr; }
  .gantt-row { grid-template-columns: 160px 1fr; }
  .gr-name-col { padding: 0.625rem 0.75rem; }
}

@media (max-width: 600px) {
  .kpi-strip { grid-template-columns: 1fr 1fr; gap: 0.5rem; }
  .campaigns-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
  .cc-stats { grid-template-columns: repeat(2, 1fr); gap: 0.625rem; }
}
</style>
