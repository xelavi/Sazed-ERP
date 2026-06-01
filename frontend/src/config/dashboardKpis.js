/**
 * Dashboard KPI & chart-format registry.
 *
 * Each KPI maps to a backend analytics metric and can be shown either as a
 * temporal series (stat / line / bar) or as a distribution (donut / hbar).
 * Distribution charts use a "group by" dimension chosen in the options panel.
 */
import {
  Euro, TrendingUp, TrendingDown, Receipt, UserPlus, CreditCard, Package,
  BarChart3, LineChart, PieChart, Activity, AlignLeft,
} from 'lucide-vue-next'

// ── Formatting helpers ──────────────────────────────────────────────
export function formatValue(value, unit) {
  const n = Number(value ?? 0)
  if (unit === 'currency') {
    if (Math.abs(n) >= 1000) {
      return '€' + n.toLocaleString('es-ES', { maximumFractionDigits: 0 })
    }
    return '€' + n.toLocaleString('es-ES', { maximumFractionDigits: 2 })
  }
  if (unit === 'percent') return n.toFixed(1) + '%'
  return n.toLocaleString('es-ES', { maximumFractionDigits: 0 })
}

export function formatCompact(value, unit) {
  const n = Number(value ?? 0)
  const abs = Math.abs(n)
  let s
  if (abs >= 1_000_000) s = (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M'
  else if (abs >= 1_000) s = (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'k'
  else s = String(Math.round(n))
  if (unit === 'currency') return '€' + s
  if (unit === 'percent') return n.toFixed(1) + '%'
  return s
}

// ── Curated categorical palette (matches design-system accents) ─────
export const CATEGORY_PALETTE = [
  '#667eea', '#10b981', '#f59e0b', '#ec4899',
  '#3b82f6', '#8b5cf6', '#14b8a6', '#f97316',
  '#06b6d4', '#a855f7',
]

// ── Chart formats ───────────────────────────────────────────────────
export const TEMPORAL_FORMATS = ['stat', 'line', 'bar']
export const DISTRIBUTION_FORMATS = ['donut', 'hbar']

export const CHART_FORMATS = [
  { id: 'stat', label: 'Indicador', icon: Activity, kind: 'temporal', desc: 'Valor actual con tendencia' },
  { id: 'line', label: 'Área / Línea', icon: LineChart, kind: 'temporal', desc: 'Evolución mes a mes' },
  { id: 'bar', label: 'Barras', icon: BarChart3, kind: 'temporal', desc: 'Comparativa mensual' },
  { id: 'donut', label: 'Circular', icon: PieChart, kind: 'distribution', desc: 'Reparto porcentual' },
  { id: 'hbar', label: 'Barras horizontales', icon: AlignLeft, kind: 'distribution', desc: 'Ranking por grupo' },
]

export function isDistribution(chartId) {
  return DISTRIBUTION_FORMATS.includes(chartId)
}

// ── KPI registry (maps to backend analytics.metrics keys) ───────────
const KPI_DEFS = [
  {
    id: 'revenue', label: 'Ingresos', icon: Euro, color: '#10b981',
    defaultChart: 'line',
    groupBys: [
      { id: 'category', label: 'Categoría' },
      { id: 'product', label: 'Producto' },
      { id: 'region', label: 'Región' },
      { id: 'customer', label: 'Cliente' },
    ],
  },
  {
    id: 'expenses', label: 'Gastos', icon: TrendingDown, color: '#f97316',
    defaultChart: 'bar',
    groupBys: [{ id: 'provider', label: 'Proveedor' }],
  },
  {
    id: 'profit', label: 'Beneficio', icon: TrendingUp, color: '#667eea',
    defaultChart: 'line', groupBys: [],
  },
  {
    id: 'invoices', label: 'Facturas emitidas', icon: Receipt, color: '#3b82f6',
    defaultChart: 'bar',
    groupBys: [{ id: 'status', label: 'Estado' }],
  },
  {
    id: 'new_customers', label: 'Nuevos clientes', icon: UserPlus, color: '#ec4899',
    defaultChart: 'stat',
    groupBys: [
      { id: 'region', label: 'Región' },
      { id: 'type', label: 'Tipo' },
    ],
  },
  {
    id: 'avg_ticket', label: 'Ticket medio', icon: CreditCard, color: '#f59e0b',
    defaultChart: 'stat', groupBys: [],
  },
  {
    id: 'units_sold', label: 'Unidades vendidas', icon: Package, color: '#8b5cf6',
    defaultChart: 'hbar',
    groupBys: [
      { id: 'product', label: 'Producto' },
      { id: 'category', label: 'Categoría' },
    ],
  },
]

export const KPIS = KPI_DEFS

export function getKpiDef(kpiId) {
  return KPI_DEFS.find((k) => k.id === kpiId) || KPI_DEFS[0]
}

export function defaultGroupBy(kpiId) {
  const def = getKpiDef(kpiId)
  return def.groupBys[0]?.id || null
}

/**
 * Resolves the data a chart needs from the analytics payload.
 * Returns { series:[{label,value}], total, headline, delta, unit, color, empty }.
 */
export function getKpiView(analytics, kpiId, chartId, groupBy) {
  const def = getKpiDef(kpiId)
  const metric = analytics?.metrics?.[kpiId]
  const unit = metric?.unit || 'number'
  const base = { unit, color: def.color, total: 0, headline: 0, delta: 0 }

  if (!metric) return { ...base, series: [], empty: true }

  if (isDistribution(chartId)) {
    const dim = groupBy || defaultGroupBy(kpiId)
    const series = (metric.breakdowns && metric.breakdowns[dim]) || []
    const total = series.reduce((s, p) => s + p.value, 0)
    return { ...base, series, total, headline: total, empty: series.length === 0 }
  }

  // Temporal
  const labels = analytics.months || []
  const series = (metric.series || []).map((value, i) => ({
    label: labels[i] ?? '', value,
  }))
  const total = series.reduce((s, p) => s + p.value, 0)
  const last = series.at(-1)?.value ?? 0
  const prev = series.at(-2)?.value ?? 0
  const delta = prev ? ((last - prev) / Math.abs(prev)) * 100 : 0
  return {
    ...base,
    series,
    total,
    headline: last,
    delta: Math.round(delta * 10) / 10,
    empty: total === 0,
  }
}
