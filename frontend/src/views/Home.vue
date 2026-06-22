<template>
  <div class="home-view">
    <!-- ── No company: welcome / get started ───────── -->
    <div v-if="!hasCompany" class="welcome-empty">
      <div class="welcome-hero">
        <div class="welcome-icon"><Building2 :size="34" /></div>
        <h1 class="welcome-title">
          Et donem la benvinguda{{ firstName !== 'there' ? `, ${firstName}` : '' }}
        </h1>
        <p class="welcome-sub">
          El teu compte encara no està vinculat a cap empresa. Per començar a utilitzar
          Seshat ERP, crea una empresa o uneix-te a una de ja existent.
        </p>
      </div>

      <div class="welcome-cards">
        <div class="welcome-card">
          <div class="welcome-card-icon tone-primary"><Plus :size="22" /></div>
          <h2 class="welcome-card-title">Crear una empresa</h2>
          <p class="welcome-card-text">
            Configura el teu negoci i comença a gestionar productes, factures, clients i molt més.
          </p>
          <router-link to="/onboarding" class="btn btn-primary welcome-cta">
            Crear empresa
            <ArrowRight :size="16" />
          </router-link>
        </div>

        <div class="welcome-card">
          <div class="welcome-card-icon tone-info"><Mail :size="22" /></div>
          <h2 class="welcome-card-title">Unir-te a una empresa</h2>
          <p class="welcome-card-text">
            Vas a treballar en una empresa ja registrada? Demana a un administrador que t'enviï una
            invitació. La rebràs a la teva bústia i, en acceptar-la, hi tindràs accés.
          </p>
          <router-link to="/inbox" class="btn btn-secondary welcome-cta">
            Anar a la bústia
            <ArrowRight :size="16" />
          </router-link>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════ -->
    <!-- ── Dashboard (requires an active company) ──── -->
    <!-- ══════════════════════════════════════════════ -->
    <template v-else>

    <!-- ① Greeting ─────────────────────────────────── -->
    <header class="home-greeting">
      <h1 class="greeting-text">{{ greetingPrefix }}{{ firstName }}</h1>
    </header>

    <!-- ② Metrics ──────────────────────────────────── -->
    <section class="card metrics-card">
      <div class="metrics-header">
        <h2 class="metrics-title">Les teves mètriques</h2>
        <router-link to="/dashboards" class="metrics-link">
          Anar a Dashboards
          <ArrowRight :size="13" />
        </router-link>
      </div>
      <div class="metrics-cols">
        <router-link to="/invoices" class="metric-col">
          <span class="metric-label">VENDES</span>
          <span class="metric-period">Últims 12 mesos</span>
          <span class="metric-value">{{ fmt(totalRevenue) }}€</span>
        </router-link>
        <div class="metric-divider"></div>
        <router-link to="/purchase-invoices" class="metric-col">
          <span class="metric-label metric-label--expense">COMPRES</span>
          <span class="metric-period">Últims 12 mesos</span>
          <span class="metric-value">{{ fmt(totalExpenses) }}€</span>
        </router-link>
      </div>
    </section>

    <!-- ③ Integrations ─────────────────────────────── -->
    <section class="card integrations-card">
      <div class="integrations-intro">
        <h2 class="integrations-heading">Treu el màxim profit de Seshat</h2>
        <p class="integrations-sub">
          Connecta l'ERP amb la teva botiga en línia i les teves xarxes socials
          per gestionar-ho tot des d'un sol lloc.
        </p>
      </div>
      <IntegrationsSection />
    </section>

    <!-- ④ Activity ─────────────────────────────────── -->
    <section class="card activity-card">
      <div class="activity-header">
        <h2 class="section-title">Activitat recent</h2>
        <div class="filter-bar">
          <button
            class="ftab" :class="{ active: activityFilter === 'all' }"
            @click="activityFilter = 'all'"
          >Tot</button>
          <button
            class="ftab" :class="{ active: activityFilter === 'paid' }"
            @click="activityFilter = 'paid'"
          ><Euro :size="12" /> Pagaments</button>
          <button
            class="ftab" :class="{ active: activityFilter === 'stock' }"
            @click="activityFilter = 'stock'"
          ><Package :size="12" /> Estoc</button>
        </div>
      </div>

      <div v-if="filteredFeed.length" class="feed">
        <div v-for="ev in filteredFeed" :key="ev.id" class="feed-row">
          <span class="feed-icon" :class="`kind-${ev.kind}`">
            <component :is="ev.icon" :size="14" />
          </span>
          <div class="feed-body">
            <span class="feed-desc">{{ ev.desc }}</span>
            <span class="feed-time">{{ ev.time }}</span>
          </div>
          <span class="feed-amount" :class="ev.amountTone">{{ ev.amount }}</span>
        </div>
      </div>

      <div v-else class="empty-box">
        <Activity :size="22" class="empty-icon" />
        <p>No hi ha activitat recent per mostrar.</p>
      </div>
    </section>

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Wallet, AlertCircle, Users,
  ArrowRight, Activity, Send, PackageX, Euro, Package,
  Building2, Plus, Mail,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import IntegrationsSection from '@/components/IntegrationsSection.vue'
import dashboardApi from '@/services/dashboard'
import invoicesApi from '@/services/invoices'
import inventoryApi from '@/services/inventory'

const { user, hasCompany } = useAuth()

// ─── Greeting ─────────────────────────────────────
const now = new Date()
const hour = now.getHours()
const greetingPrefix = computed(() => {
  if (hour < 5) return 'Encara despert/a, '
  if (hour < 12) return 'Bon dia, '
  if (hour < 18) return 'Bona tarda, '
  return 'Bona nit, '
})
const firstName = computed(() => {
  const u = user.value
  if (!u) return 'there'
  return u.first_name || u.name?.split(' ')[0] || u.email?.split('@')[0] || 'there'
})

// ─── Formatting ───────────────────────────────────
function fmt(v) {
  const n = Number(v ?? 0)
  return n.toLocaleString('ca-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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

// Analytics (12-month totals)
const totalRevenue = ref(0)
const totalExpenses = ref(0)

const overdueAmount = computed(() => Number(summary.value.overdue_balance ?? 0))
const overdueCount = computed(() => overdueInvoices.value.length)

// ─── Activity filter ──────────────────────────────
const activityFilter = ref('all')

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
      desc: `${p.customer_name} · ${p.invoice_number}`,
      amount: `+€${fmt(p.amount)}`,
      amountTone: 'positive',
    })
  })

  recentMovements.value.forEach(m => {
    const sign = m.movement_type === 'In' ? '+' : m.movement_type === 'Out' ? '−' : '±'
    const tone = m.movement_type === 'In' ? 'positive' : m.movement_type === 'Out' ? 'negative' : ''
    const mvWord = { In: 'entrada', Out: 'sortida', Adjust: 'ajust', Return: 'devolució' }[m.movement_type] || m.movement_type.toLowerCase()
    items.push({
      id: `mv-${m.id}`,
      ts: new Date(m.created_at),
      time: shortTime(m.created_at),
      kind: 'stock',
      icon: Package,
      desc: `${m.product_name} · ${mvWord}`,
      amount: `${sign}${m.quantity} u.`,
      amountTone: tone,
    })
  })

  return items.sort((a, b) => b.ts - a.ts).slice(0, 6)
})

const filteredFeed = computed(() => {
  if (activityFilter.value === 'all') return pulseFeed.value
  return pulseFeed.value.filter(ev => ev.kind === activityFilter.value)
})

function shortTime(iso) {
  const d = new Date(iso)
  const today = new Date()
  const same = d.toDateString() === today.toDateString()
  if (same) {
    return 'Avui · ' + d.toLocaleTimeString('ca-ES', { hour: '2-digit', minute: '2-digit', hour12: false })
  }
  return d.toLocaleDateString('ca-ES', { month: 'short', day: 'numeric' })
}

// ─── Load ─────────────────────────────────────────
async function loadAll() {
  const results = await Promise.allSettled([
    dashboardApi.getSummary(),
    dashboardApi.getWallet(),
    dashboardApi.getAnalytics(),
    inventoryApi.getMovements(6),
  ])

  if (results[0].status === 'fulfilled') summary.value = results[0].value
  if (results[1].status === 'fulfilled') {
    recentPayments.value = results[1].value.recent_payments || []
  }
  if (results[2].status === 'fulfilled') {
    const analytics = results[2].value
    const revSeries = analytics?.metrics?.revenue?.series || []
    const expSeries = analytics?.metrics?.expenses?.series || []
    totalRevenue.value = revSeries.reduce((a, b) => a + b, 0)
    totalExpenses.value = expSeries.reduce((a, b) => a + b, 0)
  }
  if (results[3].status === 'fulfilled') {
    recentMovements.value = results[3].value || []
  }
}

onMounted(() => {
  if (hasCompany.value) loadAll()
})
</script>

<style scoped>
.home-view {
  width: 100%;
}

/* ═══════════════════════════════════════════════════
   NO-COMPANY WELCOME
   ═══════════════════════════════════════════════════ */
.welcome-empty {
  max-width: 860px;
  margin: 0 auto;
  padding: clamp(1.5rem, 5vh, 4rem) 0;
}
.welcome-hero {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}
.welcome-icon {
  width: 72px; height: 72px; border-radius: 18px;
  margin: 0 auto var(--spacing-md);
  display: grid; place-items: center;
  background: var(--primary-light); color: var(--primary-color);
}
.welcome-title {
  font-size: var(--font-size-2xl); font-weight: 700; color: var(--text-primary);
}
.welcome-sub {
  margin: 0.5rem auto 0; max-width: 540px;
  font-size: var(--font-size-base); color: var(--text-secondary); line-height: 1.6;
}
.welcome-cards {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-lg);
}
.welcome-card {
  border: 1px solid var(--border-color); border-radius: var(--border-radius);
  padding: var(--spacing-lg); background: var(--bg-primary);
  display: flex; flex-direction: column; align-items: flex-start; gap: 0.625rem;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}
.welcome-card:hover { box-shadow: var(--shadow-md); border-color: var(--primary-color); }
.welcome-card-icon {
  width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center;
}
.welcome-card-icon.tone-primary { background: var(--primary-light); color: var(--primary-color); }
.welcome-card-icon.tone-info { background: var(--info-light); color: var(--info-color); }
.welcome-card-title { font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); margin: 0; }
.welcome-card-text { font-size: var(--font-size-sm); color: var(--text-secondary); line-height: 1.55; margin: 0; flex: 1; }
.welcome-cta { display: inline-flex; align-items: center; gap: 6px; text-decoration: none; margin-top: 0.5rem; }
@media (max-width: 640px) { .welcome-cards { grid-template-columns: 1fr; } }


/* ═══════════════════════════════════════════════════
   ① GREETING
   ═══════════════════════════════════════════════════ */
.home-greeting {
  margin-bottom: var(--spacing-md);
}
.greeting-text {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}


/* ═══════════════════════════════════════════════════
   ② METRICS CARD
   ═══════════════════════════════════════════════════ */
.metrics-card {
  margin-bottom: var(--spacing-md);
}
.metrics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}
.metrics-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.metrics-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--primary-color);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}
.metrics-link:hover { opacity: 0.8; }

.metrics-cols {
  display: flex;
  align-items: stretch;
  gap: 0;
}
.metric-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-decoration: none;
  color: inherit;
  padding: 0.5rem 0;
  border-radius: 8px;
  transition: background var(--transition-fast);
}
.metric-col:hover { background: var(--bg-secondary); }

.metric-divider {
  width: 1px;
  align-self: stretch;
  background: var(--border-color);
  margin: 0 var(--spacing-lg);
  flex-shrink: 0;
}
.metric-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.metric-label--expense {
  color: var(--text-secondary);
}
.metric-period {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}
.metric-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 4px;
}


/* ═══════════════════════════════════════════════════
   ③ INTEGRATIONS CARD
   ═══════════════════════════════════════════════════ */
.integrations-card {
  margin-bottom: var(--spacing-md);
}
.integrations-intro {
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}
.integrations-heading {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.integrations-sub {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}


/* ═══════════════════════════════════════════════════
   ④ ACTIVITY CARD
   ═══════════════════════════════════════════════════ */
.activity-card {
  margin-bottom: var(--spacing-lg);
}
.activity-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}
.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

/* Filter bar */
.filter-bar {
  display: flex; align-items: center; gap: 2px;
  background: var(--bg-secondary); border: 1px solid var(--border-color);
  border-radius: 8px; padding: 3px;
}
.ftab {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 0.25rem 0.625rem; font-size: var(--font-size-xs); font-weight: 500;
  color: var(--text-secondary); background: transparent;
  border: none; border-radius: 5px; cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  white-space: nowrap; font-family: var(--font-family);
}
.ftab:hover { color: var(--text-primary); }
.ftab.active { background: white; color: var(--text-primary); box-shadow: var(--shadow-sm); }

/* Feed rows */
.feed {
  display: flex; flex-direction: column;
}
.feed-row {
  display: grid; grid-template-columns: auto 1fr auto;
  gap: var(--spacing-md); align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-color);
}
.feed-row:last-child { border-bottom: none; }

.feed-icon {
  width: 30px; height: 30px; border-radius: 8px;
  display: grid; place-items: center; flex-shrink: 0;
}
.feed-icon.kind-paid { background: var(--success-light); color: var(--success-color); }
.feed-icon.kind-stock { background: var(--info-light); color: var(--info-color); }

.feed-body { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.feed-desc {
  font-size: var(--font-size-sm); color: var(--text-primary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.feed-time { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.feed-amount {
  font-size: var(--font-size-sm); font-weight: 600;
  color: var(--text-primary); white-space: nowrap;
}
.feed-amount.positive { color: var(--success-color); }
.feed-amount.negative { color: var(--error-color); }

/* Empty state */
.empty-box {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; padding: 1.5rem 1rem; color: var(--text-tertiary); gap: 0.375rem;
}
.empty-icon { opacity: 0.5; }
.empty-box p { margin: 0; font-size: var(--font-size-sm); color: var(--text-secondary); }


/* ═══════════════════════════════════════════════════
   RESPONSIVE
   ═══════════════════════════════════════════════════ */
@media (max-width: 640px) {
  .metrics-cols { flex-direction: column; }
  .metric-divider {
    width: 100%; height: 1px;
    margin: var(--spacing-sm) 0;
  }
  .activity-header { flex-direction: column; align-items: flex-start; }
}
</style>
