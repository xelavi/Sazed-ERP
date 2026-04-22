<template>
  <div class="campaign-detail-view">
    <div class="view-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/social-crm/campaigns" class="breadcrumb-link">Campañas</router-link>
          <ChevronRight :size="16" class="breadcrumb-sep" />
          <span class="breadcrumb-current">{{ campaign?.name }}</span>
        </div>
        <div class="header-actions">
          <span class="badge" v-if="campaign" :class="CAMPAIGN_STATUSES[campaign.status].cls">{{ CAMPAIGN_STATUSES[campaign.status].label }}</span>
          <button class="btn btn-secondary"><Pencil :size="18" /><span>Editar</span></button>
        </div>
      </div>
    </div>

    <div v-if="campaign" class="content-wrapper">
      <!-- General data -->
      <div class="info-strip card">
        <div class="info-item"><span class="info-key">Objetivo</span><span class="badge badge-info">{{ campaign.objective }}</span></div>
        <div class="info-item"><span class="info-key">Periodo</span><span>{{ formatDate(campaign.startDate) }} – {{ formatDate(campaign.endDate) }}</span></div>
        <div class="info-item"><span class="info-key">Presupuesto</span><span class="font-medium">{{ formatCurrency(campaign.budget) }}</span></div>
        <div class="info-item"><span class="info-key">Responsable</span><span>{{ campaign.responsible }}</span></div>
        <div class="info-item full"><span class="info-key">Descripción</span><span class="text-secondary">{{ campaign.description }}</span></div>
      </div>

      <!-- KPI row -->
      <div class="kpi-row">
        <div class="card kpi-card" v-for="kpi in campaignKPIs" :key="kpi.label">
          <div class="kpi-label">{{ kpi.label }}</div>
          <div class="kpi-value">{{ kpi.format(campaign[kpi.field]) }}</div>
        </div>
      </div>

      <div class="detail-grid">
        <!-- Posts linked -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Publicaciones vinculadas</h3>
            <span class="count-badge">{{ linkedPosts.length }}</span>
          </div>
          <div class="mini-table-wrap">
            <table class="table">
              <thead><tr><th>Fecha</th><th>Red</th><th>Tipo</th><th class="text-right">Alcance</th><th class="text-right">Eng.</th></tr></thead>
              <tbody>
                <tr v-for="p in linkedPosts" :key="p.id" class="clickable-row" @click="$router.push('/social-crm/posts/' + p.id)">
                  <td class="text-sm text-secondary">{{ formatDate(p.date) }}</td>
                  <td><span class="platform-pill" :style="platformStyle(p.platform)">{{ getPlatform(p.platform).label }}</span></td>
                  <td><span class="badge badge-info">{{ p.type }}</span></td>
                  <td class="text-right">{{ formatNumber(p.reach) }}</td>
                  <td class="text-right"><span :class="engClass(p.engagement)">{{ p.engagement }}%</span></td>
                </tr>
                <tr v-if="!linkedPosts.length"><td colspan="5" class="empty-cell">Sin publicaciones vinculadas</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Collabs linked -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Influencers / Colaboraciones</h3>
            <span class="count-badge">{{ linkedCollabs.length }}</span>
          </div>
          <div class="mini-table-wrap">
            <table class="table">
              <thead><tr><th>Influencer</th><th>Formato</th><th>Estado</th><th class="text-right">Ventas</th></tr></thead>
              <tbody>
                <tr v-for="c in linkedCollabs" :key="c.id" class="clickable-row" @click="$router.push('/social-crm/collaborations/' + c.id)">
                  <td class="font-medium">{{ c.influencerAlias }}</td>
                  <td class="text-sm text-secondary">{{ c.format }}</td>
                  <td><span class="badge" :class="COLLAB_STATUSES[c.status].cls">{{ COLLAB_STATUSES[c.status].label }}</span></td>
                  <td class="text-right font-medium">{{ formatCurrency(c.sales) }}</td>
                </tr>
                <tr v-if="!linkedCollabs.length"><td colspan="4" class="empty-cell">Sin colaboraciones</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Timeline -->
        <div class="card full-col">
          <div class="card-header"><h3 class="card-title">Cronología</h3></div>
          <div class="timeline" v-if="campaign.timeline.length">
            <div v-for="(ev, i) in campaign.timeline" :key="i" class="timeline-item">
              <div class="timeline-dot" :class="'type-' + ev.type"></div>
              <div class="timeline-content">
                <span class="timeline-date">{{ formatDate(ev.date) }}</span>
                <span class="timeline-event">{{ ev.event }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-cell">Sin hitos registrados</div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <AlertCircle :size="40" />
      <p>Campaña no encontrada.</p>
      <router-link to="/social-crm/campaigns" class="btn btn-secondary">Volver a campañas</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Pencil, AlertCircle } from 'lucide-vue-next'
import { socialCampaigns, socialPosts, socialCollaborations, CAMPAIGN_STATUSES, COLLAB_STATUSES, getPlatform, formatNumber, formatCurrency, formatDate } from '@/services/socialCrmData'

const route    = useRoute()
const campaign = computed(() => socialCampaigns.find(c => c.id === Number(route.params.id)))

const linkedPosts  = computed(() => socialPosts.filter(p => p.campaignId === campaign.value?.id))
const linkedCollabs = computed(() => socialCollaborations.filter(c => c.campaignId === campaign.value?.id))

const campaignKPIs = [
  { label: 'Alcance',       field: 'reach',       format: formatNumber },
  { label: 'Impresiones',   field: 'impressions', format: formatNumber },
  { label: 'Engagement',    field: 'engagement',  format: v => v + '%' },
  { label: 'Clics',         field: 'clicks',      format: formatNumber },
  { label: 'Conversiones',  field: 'conversions', format: formatNumber },
  { label: 'Ventas',        field: 'sales',       format: formatCurrency },
  { label: 'Coste',         field: 'cost',        format: formatCurrency },
  { label: 'ROAS',          field: 'roas',        format: v => v.toFixed(2) + 'x' },
]

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function engClass(v) { return v >= 6 ? 'eng-high' : v >= 3 ? 'eng-mid' : 'eng-low' }
</script>

<style scoped>
.campaign-detail-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-md) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.breadcrumb { display: flex; align-items: center; gap: 6px; }
.breadcrumb-link { font-size: 0.875rem; color: var(--primary-color); text-decoration: none; }
.breadcrumb-sep { color: var(--text-secondary); }
.breadcrumb-current { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; }
.header-actions { display: flex; align-items: center; gap: var(--spacing-sm); }

.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }

.info-strip { display: flex; flex-wrap: wrap; gap: var(--spacing-lg); padding: var(--spacing-lg); }
.info-item { display: flex; align-items: center; gap: var(--spacing-sm); }
.info-item.full { width: 100%; }
.info-key { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }

.kpi-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: var(--spacing-md); }
.kpi-card { padding: var(--spacing-md) var(--spacing-lg); }
.kpi-label { font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 4px; text-transform: uppercase; }
.kpi-value { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.full-col { grid-column: 1 / 3; }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.mini-table-wrap { overflow-x: auto; }
.clickable-row { cursor: pointer; transition: background 0.12s; }
.clickable-row:hover { background: var(--bg-secondary); }
.text-right { text-align: right; }
.text-sm { font-size: 0.85rem; }
.platform-pill { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; }
.empty-cell { text-align: center; color: var(--text-secondary); font-size: 0.85rem; padding: var(--spacing-lg); }
.eng-high { color: #10B981; font-weight: 700; }
.eng-mid  { color: #F59E0B; font-weight: 700; }
.eng-low  { color: #EF4444; font-weight: 700; }

.timeline { padding: var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.timeline-item { display: flex; align-items: flex-start; gap: var(--spacing-md); }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.type-milestone { background: var(--primary-color); }
.type-post { background: #10B981; }
.type-review { background: #F59E0B; }
.timeline-content { display: flex; gap: var(--spacing-md); align-items: center; }
.timeline-date { font-size: 0.82rem; color: var(--text-secondary); min-width: 100px; }
.timeline-event { font-size: 0.88rem; color: var(--text-primary); }

.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); height: 100%; color: var(--text-secondary); }
</style>
