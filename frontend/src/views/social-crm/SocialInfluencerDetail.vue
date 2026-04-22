<template>
  <div class="influencer-detail-view">
    <div class="view-header">
      <div class="header-content">
        <div class="breadcrumb">
          <router-link to="/social-crm/influencers" class="breadcrumb-link">Influencers</router-link>
          <ChevronRight :size="16" class="breadcrumb-sep" />
          <span class="breadcrumb-current">{{ inf?.name }}</span>
        </div>
        <div class="header-actions">
          <span class="badge" v-if="inf" :class="statusClass(inf.status)">{{ statusLabel(inf.status) }}</span>
          <button class="btn btn-secondary"><Pencil :size="18" /><span>Editar</span></button>
          <button class="btn btn-primary" @click="$router.push('/social-crm/collaborations')"><Plus :size="18" /><span>Crear colaboración</span></button>
        </div>
      </div>
    </div>

    <div v-if="inf" class="content-wrapper">
      <div class="detail-grid">
        <!-- Profile card -->
        <div class="card profile-card">
          <div class="profile-hero">
            <div class="big-avatar">{{ inf.name[0] }}</div>
            <div class="profile-info">
              <h2 class="profile-name">{{ inf.name }}</h2>
              <div class="profile-alias">{{ inf.alias }}</div>
              <div class="profile-platforms">
                <span v-for="plt in inf.platforms" :key="plt" class="platform-pill" :style="platformStyle(plt)">{{ getPlatform(plt).label }}</span>
              </div>
            </div>
          </div>
          <div class="profile-details">
            <div class="detail-row"><span class="det-key">Nicho</span><span>{{ inf.niche }}</span></div>
            <div class="detail-row"><span class="det-key">Contacto</span><span>{{ inf.contact }}</span></div>
            <div class="detail-row"><span class="det-key">Agencia</span><span>{{ inf.agency || '—' }}</span></div>
            <div class="detail-row"><span class="det-key">País</span><span>{{ inf.country }}</span></div>
            <div class="detail-row"><span class="det-key">Idioma</span><span>{{ inf.language }}</span></div>
          </div>
          <div class="notes-section">
            <div class="notes-label">Notas internas</div>
            <div class="notes-text">{{ inf.notes || '—' }}</div>
          </div>
        </div>

        <!-- Metrics -->
        <div class="metrics-col">
          <div class="card">
            <div class="card-header"><h3 class="card-title">Métricas generales (media)</h3></div>
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-val">{{ formatNumber(inf.followers) }}</div>
                <div class="metric-label">Seguidores</div>
              </div>
              <div class="metric-item">
                <div class="metric-val">{{ inf.engagementMid }}%</div>
                <div class="metric-label">Engagement</div>
              </div>
              <div class="metric-item">
                <div class="metric-val">{{ formatNumber(inf.reachMid) }}</div>
                <div class="metric-label">Alcance medio</div>
              </div>
              <div class="metric-item">
                <div class="metric-val">{{ formatNumber(inf.clicksMid) }}</div>
                <div class="metric-label">Clics medios</div>
              </div>
              <div class="metric-item">
                <div class="metric-val">{{ inf.conversionsMid }}</div>
                <div class="metric-label">Conv. medias</div>
              </div>
              <div class="metric-item">
                <div class="metric-val">{{ formatCurrency(inf.salesGenerated) }}</div>
                <div class="metric-label">Ventas totales</div>
              </div>
            </div>
          </div>

          <!-- Internal rating -->
          <div class="card">
            <div class="card-header"><h3 class="card-title">Valoración interna</h3></div>
            <div class="rating-grid" v-if="inf.collaborations > 0">
              <div class="rating-item" v-for="r in ratingDimensions" :key="r.key">
                <div class="rating-name">{{ r.label }}</div>
                <div class="rating-bar-wrap">
                  <div class="rating-bar" :style="{ width: (inf[r.key] / 5 * 100) + '%', background: ratingColor(inf[r.key]) }"></div>
                </div>
                <div class="rating-score">{{ inf[r.key].toFixed(1) }}</div>
              </div>
            </div>
            <div v-else class="empty-cell">Sin colaboraciones — valoración pendiente</div>
          </div>
        </div>

        <!-- Collaborations history -->
        <div class="card full-col">
          <div class="card-header">
            <h3 class="card-title">Historial de colaboraciones</h3>
            <span class="count-badge">{{ infCollabs.length }}</span>
          </div>
          <div class="table-wrapper">
            <table class="table">
              <thead>
                <tr>
                  <th>Campaña</th>
                  <th>Formato</th>
                  <th>Fecha</th>
                  <th class="text-right">Coste</th>
                  <th class="text-right">Alcance</th>
                  <th class="text-right">Conversiones</th>
                  <th class="text-right">Ventas</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in infCollabs" :key="c.id" class="clickable-row" @click="$router.push('/social-crm/collaborations/' + c.id)">
                  <td class="font-medium">{{ c.campaignName }}</td>
                  <td class="text-sm text-secondary">{{ c.format }}</td>
                  <td class="text-sm text-secondary">{{ formatDate(c.publishDate) }}</td>
                  <td class="text-right">{{ formatCurrency(c.cost) }}</td>
                  <td class="text-right">{{ formatNumber(c.reach) }}</td>
                  <td class="text-right">{{ c.conversions }}</td>
                  <td class="text-right font-medium">{{ formatCurrency(c.sales) }}</td>
                  <td><span class="badge" :class="COLLAB_STATUSES[c.status].cls">{{ COLLAB_STATUSES[c.status].label }}</span></td>
                </tr>
                <tr v-if="!infCollabs.length"><td colspan="8" class="empty-cell">Sin colaboraciones registradas</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <AlertCircle :size="40" />
      <p>Influencer no encontrado.</p>
      <router-link to="/social-crm/influencers" class="btn btn-secondary">Volver</router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ChevronRight, Pencil, Plus, AlertCircle } from 'lucide-vue-next'
import { socialInfluencers, socialCollaborations, COLLAB_STATUSES, getPlatform, formatNumber, formatCurrency, formatDate } from '@/services/socialCrmData'

const route = useRoute()
const inf   = computed(() => socialInfluencers.find(i => i.id === Number(route.params.id)))
const infCollabs = computed(() => socialCollaborations.filter(c => c.influencerId === inf.value?.id))

const ratingDimensions = [
  { key: 'contentQuality', label: 'Calidad del contenido' },
  { key: 'reliability',    label: 'Cumplimiento' },
  { key: 'brandAffinity',  label: 'Afinidad con la marca' },
  { key: 'reputationRisk', label: 'Riesgo reputacional (invertido)' },
]

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function statusClass(s) { return s === 'active' ? 'badge-active' : s === 'prospect' ? 'badge-warning' : 'badge-inactive' }
function statusLabel(s) { return s === 'active' ? 'Activo' : s === 'prospect' ? 'Prospecto' : 'Archivado' }
function ratingColor(v) { return v >= 4 ? '#10B981' : v >= 2.5 ? '#F59E0B' : '#EF4444' }
</script>

<style scoped>
.influencer-detail-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-md) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.breadcrumb { display: flex; align-items: center; gap: 6px; }
.breadcrumb-link { font-size: 0.875rem; color: var(--primary-color); text-decoration: none; }
.breadcrumb-sep { color: var(--text-secondary); }
.breadcrumb-current { font-size: 0.875rem; color: var(--text-primary); font-weight: 600; }
.header-actions { display: flex; align-items: center; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.detail-grid { display: grid; grid-template-columns: 300px 1fr; gap: var(--spacing-md); }
.metrics-col { display: flex; flex-direction: column; gap: var(--spacing-md); }
.full-col { grid-column: 1 / 3; }

.profile-hero { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.big-avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.3rem; flex-shrink: 0; }
.profile-name { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0 0 2px; }
.profile-alias { font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 6px; }
.profile-platforms { display: flex; gap: 4px; flex-wrap: wrap; }
.platform-pill { font-size: 0.72rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.profile-details { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: 8px; border-bottom: 1px solid var(--border-color); }
.detail-row { display: flex; justify-content: space-between; font-size: 0.85rem; }
.det-key { color: var(--text-secondary); }
.notes-section { padding: var(--spacing-md) var(--spacing-lg); }
.notes-label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 6px; }
.notes-text { font-size: 0.85rem; color: var(--text-primary); line-height: 1.5; }

.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }

.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--spacing-sm); padding: var(--spacing-md); }
.metric-item { background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: var(--spacing-sm) var(--spacing-md); text-align: center; }
.metric-val { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.metric-label { font-size: 0.72rem; color: var(--text-secondary); }

.rating-grid { padding: var(--spacing-md) var(--spacing-lg); display: flex; flex-direction: column; gap: var(--spacing-sm); }
.rating-item { display: flex; align-items: center; gap: var(--spacing-sm); }
.rating-name { font-size: 0.82rem; color: var(--text-primary); min-width: 180px; }
.rating-bar-wrap { flex: 1; height: 6px; background: var(--bg-secondary); border-radius: 3px; overflow: hidden; }
.rating-bar { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.rating-score { font-size: 0.82rem; font-weight: 700; color: var(--text-primary); min-width: 28px; text-align: right; }

.table-wrapper { overflow-x: auto; }
.clickable-row { cursor: pointer; transition: background 0.12s; }
.clickable-row:hover { background: var(--bg-secondary); }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.text-secondary { color: var(--text-secondary); }
.text-right { text-align: right; }
.empty-cell { text-align: center; padding: var(--spacing-lg); color: var(--text-secondary); font-size: 0.85rem; }
.not-found { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--spacing-md); height: 100%; color: var(--text-secondary); }
</style>
