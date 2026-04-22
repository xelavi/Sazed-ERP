<template>
  <div class="links-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Enlaces y trazabilidad</h1>
          <span class="count-badge">{{ filtered.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary"><Download :size="18" /><span>Exportar</span></button>
          <button class="btn btn-primary" @click="openForm"><Plus :size="18" /><span>Crear enlace</span></button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <select class="select" v-model="campaignFilter">
          <option value="all">Todas las campañas</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select class="select" v-model="originFilter">
          <option value="all">Todas las redes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select class="select" v-model="influencerFilter">
          <option value="all">Todos los influencers</option>
          <option value="organic">Solo orgánico</option>
          <option v-for="i in socialInfluencers" :key="i.id" :value="i.id">{{ i.alias }}</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Nombre del enlace</th>
                <th>Campaña</th>
                <th>Origen</th>
                <th>UTM Source</th>
                <th>UTM Campaign</th>
                <th class="text-right">Clics</th>
                <th class="text-right">Sesiones</th>
                <th class="text-right">Carritos</th>
                <th class="text-right">Compras</th>
                <th class="text-right">Ingresos</th>
                <th class="text-right">Conv. %</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="lnk in filtered" :key="lnk.id"
                class="clickable-row"
                @click="$router.push('/social-crm/links/' + lnk.id)">
                <td>
                  <div class="link-cell">
                    <LinkIcon :size="14" class="link-icon" />
                    <span class="link-name">{{ lnk.name }}</span>
                  </div>
                </td>
                <td class="text-sm text-secondary">{{ lnk.campaignName }}</td>
                <td><span class="platform-pill" :style="platformStyle(lnk.origin)">{{ getPlatform(lnk.origin).label }}</span></td>
                <td class="text-sm code-text">{{ lnk.utmSource }}</td>
                <td class="text-sm code-text">{{ lnk.utmCampaign }}</td>
                <td class="text-right font-medium">{{ formatNumber(lnk.clicks) }}</td>
                <td class="text-right">{{ formatNumber(lnk.sessions) }}</td>
                <td class="text-right">{{ formatNumber(lnk.carts) }}</td>
                <td class="text-right">{{ formatNumber(lnk.purchases) }}</td>
                <td class="text-right font-medium">{{ formatCurrency(lnk.revenue) }}</td>
                <td class="text-right"><span :class="convClass(lnk.conversion)">{{ lnk.conversion.toFixed(2) }}%</span></td>
                <td @click.stop>
                  <div class="row-actions">
                    <button class="icon-btn" @click="$router.push('/social-crm/links/' + lnk.id)" title="Ver detalle"><Eye :size="15" /></button>
                    <button class="icon-btn" title="Copiar enlace" @click.stop="copyLink(lnk)"><Copy :size="15" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create link modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Crear enlace trackeable</h2>
          <button class="icon-btn" @click="showForm = false"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field full-width"><label class="field-label">Nombre del enlace *</label><input class="input full" v-model="form.name" placeholder="Bio Link Primavera - Ana" /></div>
            <div class="field full-width"><label class="field-label">URL destino *</label><input class="input full" v-model="form.url" placeholder="https://mystore.es/coleccion" /></div>
            <div class="field"><label class="field-label">Campaña</label>
              <select class="select full" v-model.number="form.campaignId">
                <option :value="null">Sin campaña</option>
                <option v-for="c in socialCampaigns" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="field"><label class="field-label">Red / Origen</label>
              <select class="select full" v-model="form.origin">
                <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
              </select>
            </div>
            <div class="field"><label class="field-label">UTM Source</label><input class="input full" v-model="form.utmSource" placeholder="instagram" /></div>
            <div class="field"><label class="field-label">UTM Medium</label><input class="input full" v-model="form.utmMedium" placeholder="influencer" /></div>
            <div class="field"><label class="field-label">UTM Campaign</label><input class="input full" v-model="form.utmCampaign" /></div>
            <div class="field"><label class="field-label">UTM Content</label><input class="input full" v-model="form.utmContent" /></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showForm = false">Cancelar</button>
          <button class="btn btn-primary" @click="saveLink">Crear enlace</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Plus, Download, Eye, Copy, X, Link as LinkIcon } from 'lucide-vue-next'
import { socialLinks, socialCampaigns, socialInfluencers, PLATFORMS, getPlatform, formatNumber, formatCurrency } from '@/services/socialCrmData'

const links           = ref([...socialLinks])
const campaignFilter  = ref('all')
const originFilter    = ref('all')
const influencerFilter= ref('all')
const showForm        = ref(false)
const form = reactive({ name: '', url: '', campaignId: null, origin: 'instagram', utmSource: '', utmMedium: 'social', utmCampaign: '', utmContent: '' })

const filtered = computed(() => {
  let list = [...links.value]
  if (campaignFilter.value !== 'all')   list = list.filter(l => l.campaignId === campaignFilter.value)
  if (originFilter.value !== 'all')     list = list.filter(l => l.origin === originFilter.value)
  if (influencerFilter.value === 'organic') list = list.filter(l => !l.influencerId)
  else if (influencerFilter.value !== 'all') list = list.filter(l => l.influencerId === influencerFilter.value)
  return list
})

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function convClass(v) { return v >= 5 ? 'conv-high' : v >= 2 ? 'conv-mid' : 'conv-low' }

function copyLink(lnk) {
  const url = `${lnk.url}?utm_source=${lnk.utmSource}&utm_medium=${lnk.utmMedium}&utm_campaign=${lnk.utmCampaign}&utm_content=${lnk.utmContent}`
  navigator.clipboard.writeText(url).then(() => alert('Enlace copiado al portapapeles'))
}

function openForm() { Object.assign(form, { name: '', url: '', campaignId: null, origin: 'instagram', utmSource: '', utmMedium: 'social', utmCampaign: '', utmContent: '' }); showForm.value = true }
function saveLink() {
  if (!form.name || !form.url) return
  const camp = socialCampaigns.find(c => c.id === form.campaignId)
  links.value.push({ id: Date.now(), ...form, campaignName: camp?.name || null, influencerId: null, influencerName: null, clicks: 0, sessions: 0, carts: 0, purchases: 0, revenue: 0, conversion: 0 })
  showForm.value = false
}
</script>

<style scoped>
.links-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.filters-bar { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.clickable-row { cursor: pointer; transition: background 0.12s; }
.clickable-row:hover { background: var(--bg-secondary); }
.link-cell { display: flex; align-items: center; gap: 6px; }
.link-icon { color: var(--primary-color); flex-shrink: 0; }
.link-name { font-weight: 500; color: var(--text-primary); font-size: 0.88rem; }
.platform-pill { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; }
.code-text { font-family: monospace; font-size: 0.82rem; color: var(--text-secondary); }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.text-secondary { color: var(--text-secondary); }
.text-right { text-align: right; }
.conv-high { color: #10B981; font-weight: 700; }
.conv-mid  { color: #F59E0B; font-weight: 700; }
.conv-low  { color: #EF4444; font-weight: 700; }
.row-actions { display: flex; gap: 4px; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: none; background: none; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: background 0.15s; }
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: var(--spacing-md); }
.modal { background: var(--bg-primary); border-radius: var(--border-radius); width: 100%; max-width: 560px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); display: flex; flex-direction: column; max-height: 90vh; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.modal-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.modal-body { flex: 1; overflow-y: auto; padding: var(--spacing-lg); }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--spacing-sm); padding: var(--spacing-lg); border-top: 1px solid var(--border-color); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.field { display: flex; flex-direction: column; gap: 6px; }
.field.full-width { grid-column: 1 / 3; }
.field-label { font-size: 0.8rem; font-weight: 600; color: var(--text-primary); }
.input.full, .select.full { width: 100%; box-sizing: border-box; }
</style>
