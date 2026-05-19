<template>
  <div class="home-view">
    <!-- ── Header ──────────────────────────────────── -->
    <header class="view-header">
      <div class="header-left">
        <h1 class="view-title">{{ greetingPrefix }}{{ firstName }}</h1>
        <p class="view-subtitle">{{ longDate }}</p>
      </div>
      <div class="header-actions">
        <router-link to="/invoices" class="btn btn-secondary">
          <FileText :size="16" />
          <span class="btn-label">New invoice</span>
        </router-link>
        <router-link to="/customers" class="btn btn-primary">
          <UserPlus :size="16" />
          <span class="btn-label">New customer</span>
        </router-link>
      </div>
    </header>

    <!-- ── KPI Row ─────────────────────────────────── -->
    <section class="kpi-row">
      <router-link to="/invoices" class="kpi-card clickable">
        <div class="kpi-icon kpi-blue"><Wallet :size="22" /></div>
        <div class="kpi-info">
          <span class="kpi-value">€{{ fmt(summary.pending_balance) }}</span>
          <span class="kpi-label">Outstanding</span>
        </div>
      </router-link>

      <router-link to="/invoices" class="kpi-card clickable">
        <div class="kpi-icon kpi-red"><AlertCircle :size="22" /></div>
        <div class="kpi-info">
          <span class="kpi-value" :class="{ 'text-danger': overdueAmount > 0 }">
            €{{ fmt(overdueAmount) }}
          </span>
          <span class="kpi-label">Overdue · {{ overdueCount }}</span>
        </div>
      </router-link>

      <div class="kpi-card">
        <div class="kpi-icon kpi-green"><TrendingUp :size="22" /></div>
        <div class="kpi-info">
          <span class="kpi-value">€{{ fmt(summary.total_invoiced) }}</span>
          <span class="kpi-label">Invoiced — {{ shortMonth }}</span>
        </div>
      </div>

      <router-link to="/customers" class="kpi-card clickable">
        <div class="kpi-icon kpi-purple"><Users :size="22" /></div>
        <div class="kpi-info">
          <span class="kpi-value">{{ summary.active_customers ?? 0 }}</span>
          <span class="kpi-label">Active customers</span>
        </div>
      </router-link>
    </section>

    <!-- ── Sparkline: payments last 14 days ───────── -->
    <section class="card chart-card">
      <div class="card-header-row">
        <div>
          <h2 class="card-title">Payments received</h2>
          <p class="card-subtitle">Last 14 days</p>
        </div>
        <div class="chart-total">
          <span class="chart-total-label">Total</span>
          <span class="chart-total-value">€{{ fmt(sparkTotal) }}</span>
        </div>
      </div>
      <div class="chart-wrapper">
        <svg
          v-if="paymentSpark.length"
          class="sparkline"
          :viewBox="`0 0 ${sparkW} ${sparkH}`"
          preserveAspectRatio="none"
        >
          <g v-for="(v, i) in paymentSpark" :key="i">
            <rect
              :x="i * (sparkW / paymentSpark.length) + 2"
              :y="sparkH - barH(v)"
              :width="(sparkW / paymentSpark.length) - 4"
              :height="barH(v)"
              rx="2"
              class="spark-bar"
              :class="{ today: i === paymentSpark.length - 1, empty: v === 0 }"
            />
          </g>
        </svg>
        <div v-else class="chart-empty">No payments recorded yet.</div>
        <div class="chart-axis">
          <span>14 days ago</span>
          <span>Today</span>
        </div>
      </div>
    </section>

    <!-- ── Two-column: Attention + Recent activity ── -->
    <section class="dual-grid">
      <!-- Attention -->
      <div class="card">
        <div class="card-header-row">
          <div>
            <h2 class="card-title">Needs attention</h2>
            <p class="card-subtitle">Items that require action</p>
          </div>
          <span class="count-pill" v-if="attentionItems.length">
            {{ attentionItems.length }}
          </span>
        </div>

        <ul v-if="attentionItems.length" class="attention-list">
          <li v-for="item in attentionItems" :key="item.key" class="attention-row">
            <div class="attention-icon" :class="`tone-${item.tone}`">
              <component :is="item.icon" :size="18" />
            </div>
            <div class="attention-body">
              <div class="attention-title">
                <span class="attention-count">{{ item.count }}</span>
                <span class="attention-label">{{ item.label }}</span>
              </div>
              <span class="attention-note" v-if="item.note">{{ item.note }}</span>
            </div>
            <router-link :to="item.to" class="btn btn-sm btn-secondary attention-cta">
              {{ item.cta }}
              <ArrowRight :size="14" />
            </router-link>
          </li>
        </ul>

        <div v-else class="empty-state">
          <CheckCircle2 :size="32" class="empty-icon" />
          <p>All caught up — nothing requires attention right now.</p>
        </div>
      </div>

      <!-- Recent activity -->
      <div class="card">
        <div class="card-header-row">
          <div>
            <h2 class="card-title">Recent activity</h2>
            <p class="card-subtitle">Latest payments &amp; stock movements</p>
          </div>
        </div>

        <ol v-if="pulseFeed.length" class="pulse-list">
          <li v-for="ev in pulseFeed" :key="ev.id" class="pulse-row">
            <span class="pulse-kind" :class="`kind-${ev.kind}`">
              <component :is="ev.icon" :size="14" />
            </span>
            <div class="pulse-body">
              <span class="pulse-desc">{{ ev.desc }}</span>
              <span class="pulse-time">{{ ev.time }}</span>
            </div>
            <span class="pulse-amount" :class="ev.amountTone">{{ ev.amount }}</span>
          </li>
        </ol>

        <div v-else class="empty-state">
          <Activity :size="32" class="empty-icon" />
          <p>No recent activity to show.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  FileText, UserPlus, Wallet, AlertCircle, TrendingUp, Users,
  ArrowRight, CheckCircle2, Activity, Send, PackageX, Euro, Package,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import dashboardApi from '@/services/dashboard'
import invoicesApi from '@/services/invoices'
import inventoryApi from '@/services/inventory'

const { user } = useAuth()

// ─── Greeting & date ──────────────────────────────
const now = new Date()
const hour = now.getHours()
const greetingPrefix = computed(() => {
  if (hour < 5) return 'Still up, '
  if (hour < 12) return 'Good morning, '
  if (hour < 18) return 'Good afternoon, '
  return 'Good evening, '
})
const firstName = computed(() => {
  const u = user.value
  if (!u) return 'there'
  return u.first_name || u.name?.split(' ')[0] || u.email?.split('@')[0] || 'there'
})
const longDate = now.toLocaleDateString('en-US', {
  weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
})
const shortMonth = now.toLocaleDateString('en-US', { month: 'short' })

// ─── Formatting ───────────────────────────────────
function fmt(v) {
  const n = Number(v ?? 0)
  return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// ─── State ────────────────────────────────────────
const summary = ref({
  total_invoiced: 0,
  pending_balance: 0,
  overdue_balance: 0,
  invoice_count: 0,
  active_customers: 0,
})
const overdueInvoices = ref([])
const draftInvoices = ref([])
const lowStockProducts = ref([])
const recentPayments = ref([])
const recentMovements = ref([])

const overdueAmount = computed(() => Number(summary.value.overdue_balance ?? 0))
const overdueCount = computed(() => overdueInvoices.value.length)

// ─── Attention items ──────────────────────────────
const attentionItems = computed(() => {
  const items = []
  if (overdueCount.value > 0) {
    items.push({
      key: 'overdue',
      tone: 'red',
      icon: AlertCircle,
      count: overdueCount.value,
      label: overdueCount.value === 1 ? 'invoice overdue' : 'invoices overdue',
      note: `€${fmt(overdueAmount.value)} past due`,
      cta: 'Chase',
      to: '/invoices',
    })
  }
  if (draftInvoices.value.length > 0) {
    items.push({
      key: 'drafts',
      tone: 'blue',
      icon: Send,
      count: draftInvoices.value.length,
      label: draftInvoices.value.length === 1 ? 'draft awaiting send' : 'drafts awaiting send',
      note: null,
      cta: 'Review',
      to: '/invoices',
    })
  }
  if (lowStockProducts.value.length > 0) {
    items.push({
      key: 'lowstock',
      tone: 'amber',
      icon: PackageX,
      count: lowStockProducts.value.length,
      label: lowStockProducts.value.length === 1 ? 'product below min stock' : 'products below min stock',
      note: lowStockProducts.value.slice(0, 2).map(p => p.name).join(' · '),
      cta: 'Restock',
      to: '/inventory',
    })
  }
  return items
})

// ─── Pulse feed ───────────────────────────────────
const pulseFeed = computed(() => {
  const items = []

  recentPayments.value.forEach(p => {
    items.push({
      id: `pay-${p.id}`,
      ts: new Date(p.date),
      time: shortTime(p.date),
      kind: 'paid',
      icon: Euro,
      desc: `Payment · ${p.customer_name} (${p.invoice_number})`,
      amount: `+€${fmt(p.amount)}`,
      amountTone: 'positive',
    })
  })

  recentMovements.value.forEach(m => {
    const sign = m.movement_type === 'In' ? '+' : m.movement_type === 'Out' ? '−' : '±'
    const tone = m.movement_type === 'In' ? 'positive' : m.movement_type === 'Out' ? 'negative' : ''
    items.push({
      id: `mv-${m.id}`,
      ts: new Date(m.created_at),
      time: shortTime(m.created_at),
      kind: 'stock',
      icon: Package,
      desc: `Stock ${m.movement_type.toLowerCase()} · ${m.product_name}`,
      amount: `${sign}${m.quantity} u.`,
      amountTone: tone,
    })
  })

  return items.sort((a, b) => b.ts - a.ts).slice(0, 8)
})

function shortTime(iso) {
  const d = new Date(iso)
  const today = new Date()
  const same = d.toDateString() === today.toDateString()
  if (same) {
    return 'Today · ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  }
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// ─── Sparkline ────────────────────────────────────
const sparkW = 600
const sparkH = 80

const paymentSpark = computed(() => {
  const days = 14
  const buckets = Array(days).fill(0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  recentPayments.value.forEach(p => {
    const d = new Date(p.date)
    d.setHours(0, 0, 0, 0)
    const diff = Math.round((today - d) / (1000 * 60 * 60 * 24))
    if (diff >= 0 && diff < days) {
      buckets[days - 1 - diff] += Number(p.amount || 0)
    }
  })
  return buckets
})

const sparkTotal = computed(() => paymentSpark.value.reduce((a, b) => a + b, 0))

function barH(v) {
  const max = Math.max(...paymentSpark.value, 1)
  const minH = v > 0 ? 4 : 2
  return Math.max(minH, (v / max) * (sparkH - 6))
}

// ─── Load ─────────────────────────────────────────
async function loadAll() {
  const results = await Promise.allSettled([
    dashboardApi.getSummary(),
    dashboardApi.getWallet(),
    invoicesApi.getAll({ status: 'Draft', page_size: 5 }),
    invoicesApi.getAll({ overdue: true, page_size: 5 }),
    inventoryApi.getAllStock({ stock_status: 'low' }),
    inventoryApi.getMovements(8),
  ])

  if (results[0].status === 'fulfilled') summary.value = results[0].value
  if (results[1].status === 'fulfilled') {
    recentPayments.value = results[1].value.recent_payments || []
  }
  if (results[2].status === 'fulfilled') {
    const v = results[2].value
    draftInvoices.value = Array.isArray(v) ? v : (v.results || [])
  }
  if (results[3].status === 'fulfilled') {
    const v = results[3].value
    overdueInvoices.value = Array.isArray(v) ? v : (v.results || [])
  }
  if (results[4].status === 'fulfilled') {
    const v = results[4].value
    lowStockProducts.value = (Array.isArray(v) ? v : []).slice(0, 8)
  }
  if (results[5].status === 'fulfilled') {
    recentMovements.value = results[5].value || []
  }
}

onMounted(loadAll)
</script>

<style scoped>
.home-view {
  width: 100%;
}

/* ── Header ───────────────────────────────────── */
.view-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
  gap: var(--spacing-md);
}
.view-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
}
.view-subtitle {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: 2px;
}
.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}
.header-actions .btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
}

/* ── KPI Row ──────────────────────────────────── */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}
.kpi-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
  text-decoration: none;
  color: inherit;
}
.kpi-card:hover { box-shadow: var(--shadow-md); }
.kpi-card.clickable { cursor: pointer; }
.kpi-card.clickable:hover { border-color: var(--primary-color); }
.kpi-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.kpi-blue { background: var(--info-light); color: var(--info-color); }
.kpi-green { background: var(--success-light); color: var(--success-color); }
.kpi-amber { background: var(--warning-light); color: var(--warning-color); }
.kpi-red { background: var(--error-light); color: var(--error-color); }
.kpi-purple { background: #ede9fe; color: var(--accent-purple); }
.kpi-info { display: flex; flex-direction: column; min-width: 0; }
.kpi-value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}
.kpi-value.text-danger { color: var(--error-color); }
.kpi-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 2px;
}

/* ── Chart card ───────────────────────────────── */
.card-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.card-subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 2px 0 0;
}
.chart-card {
  margin-bottom: var(--spacing-lg);
}
.chart-total {
  text-align: right;
  display: flex;
  flex-direction: column;
}
.chart-total-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.chart-total-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
}
.chart-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.sparkline {
  width: 100%;
  height: 80px;
  display: block;
}
.spark-bar {
  fill: var(--primary-color);
  opacity: 0.75;
  transition: opacity 200ms ease;
}
.spark-bar.empty {
  fill: var(--border-color);
  opacity: 1;
}
.spark-bar.today {
  fill: var(--primary-dark);
  opacity: 1;
}
.sparkline:hover .spark-bar:not(.empty) { opacity: 0.45; }
.sparkline:hover .spark-bar:not(.empty):hover { opacity: 1; }
.chart-axis {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}
.chart-empty {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
  font-style: italic;
}

/* ── Dual grid ────────────────────────────────── */
.dual-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.count-pill {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  font-weight: 600;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
}

/* ── Attention list ───────────────────────────── */
.attention-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}
.attention-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--spacing-md);
  align-items: center;
  padding: 0.875rem 0;
  border-bottom: 1px solid var(--border-color);
}
.attention-row:last-child { border-bottom: none; }
.attention-row:first-child { padding-top: 0.25rem; }

.attention-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.attention-icon.tone-red { background: var(--error-light); color: var(--error-color); }
.attention-icon.tone-amber { background: var(--warning-light); color: var(--warning-color); }
.attention-icon.tone-blue { background: var(--info-light); color: var(--info-color); }

.attention-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.attention-title {
  display: flex;
  align-items: baseline;
  gap: 0.375rem;
  flex-wrap: wrap;
}
.attention-count {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
}
.attention-label {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}
.attention-note {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.attention-cta {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  white-space: nowrap;
}

/* ── Pulse list ───────────────────────────────── */
.pulse-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}
.pulse-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: var(--spacing-md);
  align-items: center;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--border-color);
}
.pulse-row:last-child { border-bottom: none; }
.pulse-row:first-child { padding-top: 0.25rem; }

.pulse-kind {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.pulse-kind.kind-paid { background: var(--success-light); color: var(--success-color); }
.pulse-kind.kind-stock { background: var(--info-light); color: var(--info-color); }

.pulse-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.pulse-desc {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.pulse-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}
.pulse-amount {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}
.pulse-amount.positive { color: var(--success-color); }
.pulse-amount.negative { color: var(--error-color); }

/* ── Empty state ──────────────────────────────── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem 1rem;
  color: var(--text-tertiary);
  gap: 0.5rem;
}
.empty-icon {
  color: var(--text-tertiary);
  opacity: 0.6;
}
.empty-state p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* ── Responsive ───────────────────────────────── */
@media (max-width: 1024px) {
  .kpi-row { grid-template-columns: repeat(2, 1fr); }
  .dual-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .kpi-row { grid-template-columns: 1fr; }
  .header-actions .btn-label { display: inline; }
  .attention-row {
    grid-template-columns: auto 1fr;
    grid-template-areas:
      "icon body"
      "cta cta";
  }
  .attention-icon { grid-area: icon; }
  .attention-body { grid-area: body; }
  .attention-cta {
    grid-area: cta;
    justify-self: start;
    margin-top: 0.25rem;
  }
}
</style>
