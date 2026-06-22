<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  LayoutDashboard, Plus, Pencil, Check, X, GripVertical,
  MoreVertical, Trash2, RotateCcw, Maximize2, Layers, AlertTriangle,
} from 'lucide-vue-next'
import {
  KPIS, CHART_FORMATS, getKpiDef, defaultGroupBy, isDistribution,
} from '@/config/dashboardKpis'
import { useDashboardData } from '@/composables/useDashboardData'
import ChartRenderer from '@/components/charts/ChartRenderer.vue'

const STORAGE_KEY = 'dashboards.widgets.v2'

const SIZES = [
  { id: 'sm', label: 'Petit' },
  { id: 'md', label: 'Mitjà' },
  { id: 'lg', label: 'Ample' },
]

const { analytics, loading, error, load } = useDashboardData()

function uuid() {
  return (crypto?.randomUUID?.() || 'w-' + Math.random().toString(36).slice(2) + Date.now())
}

function defaultWidgets() {
  return [
    { id: uuid(), kpi: 'revenue', chart: 'stat', size: 'sm', groupBy: null },
    { id: uuid(), kpi: 'profit', chart: 'stat', size: 'sm', groupBy: null },
    { id: uuid(), kpi: 'new_customers', chart: 'stat', size: 'sm', groupBy: null },
    { id: uuid(), kpi: 'avg_ticket', chart: 'stat', size: 'sm', groupBy: null },
    { id: uuid(), kpi: 'revenue', chart: 'line', size: 'md', groupBy: null },
    { id: uuid(), kpi: 'revenue', chart: 'donut', size: 'md', groupBy: 'category' },
    { id: uuid(), kpi: 'expenses', chart: 'bar', size: 'md', groupBy: null },
    { id: uuid(), kpi: 'units_sold', chart: 'hbar', size: 'md', groupBy: 'product' },
  ]
}

const widgets = ref([])
const editMode = ref(false)
const menuFor = ref(null)

onMounted(() => {
  load().catch(() => {})
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : null
    widgets.value = Array.isArray(parsed) && parsed.length ? parsed : defaultWidgets()
  } catch {
    widgets.value = defaultWidgets()
  }
})

watch(widgets, (v) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(v))
}, { deep: true })

function groupByLabel(kpi, id) {
  return getKpiDef(kpi).groupBys.find((g) => g.id === id)?.label || ''
}
function widgetTitle(w) { return getKpiDef(w.kpi).label }
function widgetSubtitle(w) {
  const f = CHART_FORMATS.find((c) => c.id === w.chart)
  if (isDistribution(w.chart)) return `${f?.label} · per ${groupByLabel(w.kpi, w.groupBy).toLowerCase()}`
  return `${f?.label} · últims 12 mesos`
}
function widgetIcon(w) { return getKpiDef(w.kpi).icon }

function setSize(w, size) { w.size = size; menuFor.value = null }
function setWidgetGroupBy(w, id) { w.groupBy = id; menuFor.value = null }
function removeWidget(id) {
  widgets.value = widgets.value.filter((w) => w.id !== id)
  menuFor.value = null
}
function resetLayout() { widgets.value = defaultWidgets(); menuFor.value = null }

// ── Drag & drop reorder ─────────────────────────────
const dragId = ref(null)
function onDragStart(w) { dragId.value = w.id }
function onDragEnter(target) {
  if (!dragId.value || dragId.value === target.id) return
  const from = widgets.value.findIndex((w) => w.id === dragId.value)
  const to = widgets.value.findIndex((w) => w.id === target.id)
  if (from < 0 || to < 0) return
  const arr = [...widgets.value]
  const [moved] = arr.splice(from, 1)
  arr.splice(to, 0, moved)
  widgets.value = arr
}
function onDragEnd() { dragId.value = null }

// ── Add-widget modal ────────────────────────────────
const showAdd = ref(false)
const draft = ref({ kpi: 'revenue', chart: 'line', size: 'md', groupBy: null })

const draftDef = computed(() => getKpiDef(draft.value.kpi))
const draftHasGroups = computed(() => draftDef.value.groupBys.length > 0)
const temporalFormats = computed(() => CHART_FORMATS.filter((f) => f.kind === 'temporal'))
const distributionFormats = computed(() => CHART_FORMATS.filter((f) => f.kind === 'distribution'))

function openAdd() {
  draft.value = { kpi: 'revenue', chart: getKpiDef('revenue').defaultChart, size: 'md', groupBy: null }
  showAdd.value = true
}
function pickKpi(id) {
  const def = getKpiDef(id)
  draft.value.kpi = id
  // If current format is a distribution but the new KPI has no groups, fall back.
  if (isDistribution(draft.value.chart) && !def.groupBys.length) {
    draft.value.chart = def.defaultChart
  }
  draft.value.groupBy = isDistribution(draft.value.chart) ? defaultGroupBy(id) : null
}
function pickFormat(id) {
  draft.value.chart = id
  draft.value.groupBy = isDistribution(id) ? (draft.value.groupBy || defaultGroupBy(draft.value.kpi)) : null
}
function confirmAdd() {
  widgets.value = [...widgets.value, { id: uuid(), ...draft.value }]
  showAdd.value = false
}

const tsKpis = computed(() => KPIS)
</script>

<template>
  <div class="dash-view" @click="menuFor = null">
    <!-- Header -->
    <header class="view-header">
      <div class="header-left">
        <h1 class="view-title">
          <span class="title-icon"><LayoutDashboard :size="22" /></span>
          Dashboards
        </h1>
        <p class="view-subtitle">Els teus indicadors clau, amb dades reals de la teva empresa</p>
      </div>
      <div class="header-actions">
        <button v-if="editMode" class="btn btn-ghost" @click="resetLayout">
          <RotateCcw :size="16" /> <span class="btn-label">Restablir</span>
        </button>
        <button class="btn btn-secondary" @click="editMode = !editMode">
          <component :is="editMode ? Check : Pencil" :size="16" />
          <span class="btn-label">{{ editMode ? 'Fet' : 'Organitzar' }}</span>
        </button>
        <button class="btn btn-primary" @click="openAdd">
          <Plus :size="16" /> <span class="btn-label">Nou gràfic</span>
        </button>
      </div>
    </header>

    <div v-if="error" class="load-error">
      <AlertTriangle :size="16" /> No s'han pogut carregar les dades.
      <button class="link-btn" @click="load(true)">Reintentar</button>
    </div>

    <div v-if="editMode" class="edit-hint">
      <GripVertical :size="14" /> Arrossega les targetes per reordenar-les · fes servir el menú ⋮ per canviar la mida, l'agrupació o eliminar
    </div>

    <!-- Grid -->
    <div v-if="widgets.length" class="dash-grid" :class="{ editing: editMode }">
      <div
        v-for="w in widgets" :key="w.id"
        class="widget" :class="[`size-${w.size}`, { dragging: dragId === w.id }]"
        :draggable="editMode"
        @dragstart="onDragStart(w)"
        @dragenter.prevent="onDragEnter(w)"
        @dragover.prevent
        @dragend="onDragEnd"
      >
        <div class="widget-head">
          <span v-if="editMode" class="drag-handle"><GripVertical :size="16" /></span>
          <span class="widget-icon"><component :is="widgetIcon(w)" :size="16" /></span>
          <div class="widget-titles">
            <span class="widget-title">{{ widgetTitle(w) }}</span>
            <span class="widget-sub">{{ widgetSubtitle(w) }}</span>
          </div>
          <div class="widget-menu-wrap" @click.stop>
            <button class="icon-btn" @click="menuFor = menuFor === w.id ? null : w.id">
              <MoreVertical :size="16" />
            </button>
            <transition name="menu">
              <div v-if="menuFor === w.id" class="widget-menu">
                <div class="menu-section">Mida</div>
                <button
                  v-for="s in SIZES" :key="s.id"
                  class="menu-item" :class="{ active: w.size === s.id }"
                  @click="setSize(w, s.id)"
                >
                  <Maximize2 :size="14" /> {{ s.label }}
                </button>
                <template v-if="isDistribution(w.chart) && getKpiDef(w.kpi).groupBys.length">
                  <div class="menu-divider" />
                  <div class="menu-section">Agrupar per</div>
                  <button
                    v-for="g in getKpiDef(w.kpi).groupBys" :key="g.id"
                    class="menu-item" :class="{ active: w.groupBy === g.id }"
                    @click="setWidgetGroupBy(w, g.id)"
                  >
                    <Layers :size="14" /> {{ g.label }}
                  </button>
                </template>
                <div class="menu-divider" />
                <button class="menu-item danger" @click="removeWidget(w.id)">
                  <Trash2 :size="14" /> Eliminar
                </button>
              </div>
            </transition>
          </div>
        </div>
        <div class="widget-body" :class="{ short: w.chart === 'stat' }">
          <ChartRenderer :analytics="analytics" :kpi="w.kpi" :chart="w.chart" :group-by="w.groupBy" />
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="dash-empty">
      <div class="empty-icon"><LayoutDashboard :size="40" /></div>
      <h3>El teu dashboard està buit</h3>
      <p>Afegeix el teu primer gràfic per començar a visualitzar les teves dades.</p>
      <button class="btn btn-primary" @click="openAdd"><Plus :size="16" /> Nou gràfic</button>
    </div>

    <!-- Add modal -->
    <teleport to="body">
      <transition name="modal">
        <div v-if="showAdd" class="modal-overlay" @click.self="showAdd = false">
          <div class="modal">
            <div class="modal-head">
              <h2>Nou gràfic</h2>
              <button class="icon-btn" @click="showAdd = false"><X :size="18" /></button>
            </div>

            <div class="modal-body">
              <div class="builder">
                <!-- KPI picker -->
                <div class="builder-col">
                  <label class="builder-label">1 · Tria un KPI</label>
                  <div class="kpi-list">
                    <button
                      v-for="k in tsKpis" :key="k.id"
                      class="kpi-pick" :class="{ active: draft.kpi === k.id }"
                      @click="pickKpi(k.id)"
                    >
                      <span class="kpi-pick-icon" :style="{ color: k.color, background: k.color + '1a' }">
                        <component :is="k.icon" :size="16" />
                      </span>
                      {{ k.label }}
                    </button>
                  </div>
                </div>

                <!-- Format + group-by + preview -->
                <div class="builder-col">
                  <label class="builder-label">2 · Tria el format</label>

                  <div class="fmt-group-label">Evolució temporal</div>
                  <div class="fmt-list">
                    <button
                      v-for="f in temporalFormats" :key="f.id"
                      class="fmt-pick" :class="{ active: draft.chart === f.id }"
                      @click="pickFormat(f.id)"
                    >
                      <component :is="f.icon" :size="18" />
                      <span class="fmt-name">{{ f.label }}</span>
                      <span class="fmt-desc">{{ f.desc }}</span>
                    </button>
                  </div>

                  <div class="fmt-group-label">
                    Distribució
                    <span v-if="!draftHasGroups" class="fmt-note">— no disponible per a aquest KPI</span>
                  </div>
                  <div class="fmt-list">
                    <button
                      v-for="f in distributionFormats" :key="f.id"
                      class="fmt-pick" :class="{ active: draft.chart === f.id }"
                      :disabled="!draftHasGroups"
                      @click="pickFormat(f.id)"
                    >
                      <component :is="f.icon" :size="18" />
                      <span class="fmt-name">{{ f.label }}</span>
                      <span class="fmt-desc">{{ f.desc }}</span>
                    </button>
                  </div>

                  <template v-if="isDistribution(draft.chart) && draftHasGroups">
                    <label class="builder-label">Agrupar per</label>
                    <div class="size-row">
                      <button
                        v-for="g in draftDef.groupBys" :key="g.id"
                        class="size-pick" :class="{ active: draft.groupBy === g.id }"
                        @click="draft.groupBy = g.id"
                      >{{ g.label }}</button>
                    </div>
                  </template>

                  <label class="builder-label">Mida</label>
                  <div class="size-row">
                    <button
                      v-for="s in SIZES" :key="s.id"
                      class="size-pick" :class="{ active: draft.size === s.id }"
                      @click="draft.size = s.id"
                    >{{ s.label }}</button>
                  </div>

                  <label class="builder-label">Vista prèvia</label>
                  <div class="preview" :class="{ short: draft.chart === 'stat' }">
                    <ChartRenderer
                      :key="draft.kpi + draft.chart + draft.groupBy"
                      :analytics="analytics" :kpi="draft.kpi" :chart="draft.chart" :group-by="draft.groupBy"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div class="modal-foot">
              <button class="btn btn-secondary" @click="showAdd = false">Cancel·lar</button>
              <button class="btn btn-primary" @click="confirmAdd"><Plus :size="16" /> Afegir al dashboard</button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<style scoped>
.dash-view { width: 100%; max-width: 1500px; margin: 0 auto; }

/* Header */
.view-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: var(--spacing-lg); flex-wrap: wrap; gap: var(--spacing-md);
}
.view-title { display: flex; align-items: center; gap: 0.6rem; font-size: var(--font-size-2xl); font-weight: 700; }
.title-icon {
  width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center;
  background: var(--primary-light); color: var(--primary-color);
}
.view-subtitle { font-size: var(--font-size-sm); color: var(--text-secondary); margin-top: 4px; }
.header-actions { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.header-actions .btn { display: inline-flex; align-items: center; gap: 6px; }

.load-error {
  display: flex; align-items: center; gap: 8px;
  background: var(--error-light); color: var(--error-color);
  border-radius: var(--border-radius-sm); padding: 0.6rem 0.9rem;
  font-size: var(--font-size-sm); margin-bottom: var(--spacing-md);
}
.link-btn {
  background: none; border: none; color: var(--error-color); font-weight: 700;
  cursor: pointer; text-decoration: underline; font-family: var(--font-family);
}

.edit-hint {
  display: flex; align-items: center; gap: 6px;
  background: var(--primary-light); color: var(--primary-dark);
  border: 1px dashed var(--primary-color);
  border-radius: var(--border-radius-sm);
  padding: 0.6rem 0.9rem; font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

/* Grid */
.dash-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-md);
  align-items: stretch;
}
.size-sm { grid-column: span 3; }
.size-md { grid-column: span 6; }
.size-lg { grid-column: span 12; }

/* Widget card */
.widget {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  display: flex; flex-direction: column;
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base), transform var(--transition-base), border-color var(--transition-fast);
  min-height: 200px;
}
.widget:hover { box-shadow: var(--shadow-md); }
.size-sm { min-height: 168px; }
.dash-grid.editing .widget { cursor: grab; border-style: dashed; }
.dash-grid.editing .widget:hover { border-color: var(--primary-color); }
.widget.dragging { opacity: 0.5; transform: scale(0.98); box-shadow: var(--shadow-lg); }

.widget-head {
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: var(--spacing-md);
}
.drag-handle { color: var(--text-tertiary); display: flex; cursor: grab; }
.widget-icon {
  width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
  display: grid; place-items: center;
  background: var(--bg-secondary); color: var(--text-secondary);
}
.widget-titles { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.widget-title { font-size: var(--font-size-base); font-weight: 600; color: var(--text-primary); line-height: 1.2; }
.widget-sub {
  font-size: var(--font-size-xs); color: var(--text-tertiary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.icon-btn {
  background: none; border: none; cursor: pointer; color: var(--text-tertiary);
  padding: 5px; border-radius: 6px; display: grid; place-items: center;
  transition: all var(--transition-fast);
}
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.widget-menu-wrap { position: relative; }
.widget-menu {
  position: absolute; right: 0; top: calc(100% + 4px); z-index: 20;
  background: var(--bg-primary); border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm); box-shadow: var(--shadow-lg);
  padding: 0.35rem; min-width: 172px;
}
.menu-section {
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--text-tertiary); padding: 0.35rem 0.5rem 0.2rem; font-weight: 600;
}
.menu-item {
  display: flex; align-items: center; gap: 0.5rem; width: 100%;
  background: none; border: none; cursor: pointer; text-align: left;
  padding: 0.45rem 0.5rem; border-radius: 6px; font-size: var(--font-size-sm);
  color: var(--text-primary); font-family: var(--font-family);
  transition: background var(--transition-fast);
}
.menu-item:hover { background: var(--bg-secondary); }
.menu-item.active { color: var(--primary-color); font-weight: 600; }
.menu-item.danger { color: var(--error-color); }
.menu-item.danger:hover { background: var(--error-light); }
.menu-divider { height: 1px; background: var(--border-color); margin: 0.3rem 0; }

.widget-body { flex: 1; min-height: 280px; position: relative; }
.widget-body.short { min-height: 92px; }

/* Empty */
.dash-empty {
  display: flex; flex-direction: column; align-items: center; text-align: center;
  gap: 0.6rem; padding: 4rem 1rem; color: var(--text-secondary);
  border: 2px dashed var(--border-color); border-radius: var(--border-radius-lg);
}
.dash-empty .empty-icon {
  width: 78px; height: 78px; border-radius: 20px; display: grid; place-items: center;
  background: var(--primary-light); color: var(--primary-color); margin-bottom: 0.5rem;
}
.dash-empty h3 { font-size: var(--font-size-xl); color: var(--text-primary); }
.dash-empty .btn { margin-top: 0.75rem; display: inline-flex; align-items: center; gap: 6px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 2000;
  background: rgba(15, 23, 42, 0.5); backdrop-filter: blur(3px);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.modal {
  background: var(--bg-primary); border-radius: var(--border-radius-lg);
  width: 100%; max-width: 880px; max-height: 90vh;
  display: flex; flex-direction: column; box-shadow: var(--shadow-lg); overflow: hidden;
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color);
}
.modal-head h2 { font-size: var(--font-size-xl); font-weight: 700; }
.modal-body { padding: var(--spacing-lg); overflow-y: auto; }
.modal-foot {
  display: flex; justify-content: flex-end; gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg); border-top: 1px solid var(--border-color);
}
.modal-foot .btn { display: inline-flex; align-items: center; gap: 6px; }

.builder { display: grid; grid-template-columns: 1fr 1.1fr; gap: var(--spacing-lg); }
.builder-label {
  display: block; font-size: var(--font-size-sm); font-weight: 600;
  color: var(--text-primary); margin-bottom: 0.5rem;
}
.builder-col .builder-label ~ .builder-label { margin-top: var(--spacing-md); }
.kpi-list { display: flex; flex-direction: column; gap: 4px; }
.kpi-pick {
  display: flex; align-items: center; gap: 0.6rem; width: 100%;
  padding: 0.55rem 0.6rem; border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm); background: var(--bg-primary);
  cursor: pointer; font-size: var(--font-size-sm); color: var(--text-primary);
  font-family: var(--font-family); transition: all var(--transition-fast); text-align: left;
}
.kpi-pick:hover { border-color: var(--primary-color); background: var(--bg-secondary); }
.kpi-pick.active { border-color: var(--primary-color); background: var(--primary-light); font-weight: 600; }
.kpi-pick-icon { width: 28px; height: 28px; border-radius: 7px; display: grid; place-items: center; flex-shrink: 0; }

.fmt-group-label {
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.5px;
  color: var(--text-tertiary); font-weight: 600; margin: 0.35rem 0 0.35rem;
}
.fmt-note { text-transform: none; letter-spacing: 0; font-weight: 500; color: var(--text-tertiary); }
.fmt-list { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 0.25rem; }
.fmt-pick {
  display: grid; grid-template-columns: auto 1fr; grid-template-areas: 'ic name' 'ic desc';
  column-gap: 0.5rem; align-items: center;
  padding: 0.6rem; border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm); background: var(--bg-primary);
  cursor: pointer; text-align: left; transition: all var(--transition-fast);
  color: var(--text-secondary);
}
.fmt-pick > svg { grid-area: ic; }
.fmt-pick:hover:not(:disabled) { border-color: var(--primary-color); }
.fmt-pick:disabled { opacity: 0.45; cursor: not-allowed; }
.fmt-pick.active { border-color: var(--primary-color); background: var(--primary-light); color: var(--primary-color); }
.fmt-name { grid-area: name; font-size: var(--font-size-sm); font-weight: 600; color: var(--text-primary); }
.fmt-desc { grid-area: desc; font-size: 0.68rem; color: var(--text-tertiary); line-height: 1.3; }
.fmt-pick.active .fmt-name { color: var(--primary-color); }

.size-row { display: flex; gap: 6px; flex-wrap: wrap; }
.size-pick {
  flex: 1; min-width: 72px; padding: 0.45rem; border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm); background: var(--bg-primary);
  cursor: pointer; font-size: var(--font-size-sm); color: var(--text-secondary);
  font-family: var(--font-family); transition: all var(--transition-fast);
}
.size-pick.active { border-color: var(--primary-color); background: var(--primary-light); color: var(--primary-color); font-weight: 600; }

.preview {
  border: 1px solid var(--border-color); border-radius: var(--border-radius-sm);
  padding: var(--spacing-md); height: 240px; background: var(--bg-primary);
}
.preview.short { height: 130px; }

/* transitions */
.menu-enter-active, .menu-leave-active { transition: opacity 120ms ease, transform 120ms ease; }
.menu-enter-from, .menu-leave-to { opacity: 0; transform: translateY(-4px); }
.modal-enter-active, .modal-leave-active { transition: opacity 180ms ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .modal { transition: transform 220ms cubic-bezier(0.22,1,0.36,1); }
.modal-enter-from .modal { transform: translateY(14px) scale(0.98); }

/* Responsive */
@media (max-width: 1100px) {
  .size-sm { grid-column: span 6; }
  .size-md { grid-column: span 12; }
}
@media (max-width: 720px) {
  .dash-grid { grid-template-columns: 1fr; }
  .size-sm, .size-md, .size-lg { grid-column: span 1; }
  .builder { grid-template-columns: 1fr; }
  .fmt-list { grid-template-columns: 1fr; }
  .btn-label { display: inline; }
}
</style>
