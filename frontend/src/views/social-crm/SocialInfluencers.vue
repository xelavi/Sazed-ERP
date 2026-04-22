<template>
  <div class="influencers-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Influencers</h1>
          <span class="count-badge">{{ filtered.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openForm">
            <Plus :size="18" /><span>Nuevo influencer</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <div class="search-box">
          <Search :size="16" class="search-icon" />
          <input class="input search-input" v-model="searchQ" placeholder="Buscar por nombre o alias..." />
        </div>
        <select class="select" v-model="platformFilter">
          <option value="all">Todas las redes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select class="select" v-model="nicheFilter">
          <option value="all">Todos los nichos</option>
          <option v-for="n in niches" :key="n" :value="n">{{ n }}</option>
        </select>
        <select class="select" v-model="statusFilter">
          <option value="all">Todos los estados</option>
          <option value="active">Activo</option>
          <option value="prospect">Prospecto</option>
          <option value="archived">Archivado</option>
        </select>
        <select class="select" v-model="followersFilter">
          <option value="all">Cualquier tamaño</option>
          <option value="nano">Nano (&lt;10K)</option>
          <option value="micro">Micro (10K–100K)</option>
          <option value="macro">Macro (100K–1M)</option>
          <option value="mega">Mega (&gt;1M)</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Influencer</th>
                <th>Red principal</th>
                <th class="text-right">Seguidores</th>
                <th>Nicho</th>
                <th>Contacto</th>
                <th>Estado</th>
                <th class="text-right">Colaboraciones</th>
                <th class="text-right">Ventas generadas</th>
                <th class="text-right">Valoración</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inf in filtered" :key="inf.id">
                <td>
                  <div class="influencer-cell">
                    <div class="avatar">{{ inf.name[0] }}</div>
                    <div>
                      <div class="inf-name">{{ inf.name }}</div>
                      <div class="inf-alias">{{ inf.alias }}</div>
                    </div>
                  </div>
                </td>
                <td><span class="platform-pill" :style="platformStyle(inf.platform)">{{ getPlatform(inf.platform).label }}</span></td>
                <td class="text-right font-medium">{{ formatNumber(inf.followers) }}</td>
                <td><span class="badge badge-info">{{ inf.niche }}</span></td>
                <td class="text-sm text-secondary">{{ inf.contact }}</td>
                <td>
                  <span class="badge" :class="statusClass(inf.status)">{{ statusLabel(inf.status) }}</span>
                </td>
                <td class="text-right">{{ inf.collaborations }}</td>
                <td class="text-right font-medium">{{ formatCurrency(inf.salesGenerated) }}</td>
                <td class="text-right">
                  <div class="star-rating" v-if="inf.rating > 0">
                    <Star :size="13" v-for="i in 5" :key="i" :class="i <= Math.round(inf.rating) ? 'star-filled' : 'star-empty'" />
                    <span class="rating-num">{{ inf.rating }}</span>
                  </div>
                  <span v-else class="text-secondary">—</span>
                </td>
                <td>
                  <div class="row-actions">
                    <button class="icon-btn" @click="$router.push('/social-crm/influencers/' + inf.id)" title="Ver ficha"><Eye :size="15" /></button>
                    <button class="icon-btn" title="Editar"><Pencil :size="15" /></button>
                    <button class="icon-btn" title="Crear colaboración" @click="$router.push('/social-crm/collaborations')"><Handshake :size="15" /></button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add influencer modal (simplified) -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal">
        <div class="modal-header">
          <h2 class="modal-title">Nuevo influencer</h2>
          <button class="icon-btn" @click="showForm = false"><X :size="20" /></button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field"><label class="field-label">Nombre *</label><input class="input full" v-model="form.name" /></div>
            <div class="field"><label class="field-label">Alias / Handle *</label><input class="input full" v-model="form.alias" placeholder="@alias" /></div>
            <div class="field"><label class="field-label">Red principal</label>
              <select class="select full" v-model="form.platform">
                <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
              </select>
            </div>
            <div class="field"><label class="field-label">Nicho</label><input class="input full" v-model="form.niche" placeholder="Lifestyle, Moda..." /></div>
            <div class="field"><label class="field-label">Seguidores</label><input class="input full" type="number" v-model.number="form.followers" /></div>
            <div class="field"><label class="field-label">Contacto</label><input class="input full" v-model="form.contact" placeholder="email o agencia" /></div>
            <div class="field"><label class="field-label">Agencia</label><input class="input full" v-model="form.agency" /></div>
            <div class="field"><label class="field-label">País</label><input class="input full" v-model="form.country" value="España" /></div>
            <div class="field full-width"><label class="field-label">Notas internas</label><textarea class="input full textarea" v-model="form.notes" rows="3"></textarea></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showForm = false">Cancelar</button>
          <button class="btn btn-primary" @click="saveInfluencer">Añadir influencer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { Plus, Search, Eye, Pencil, Star, X } from 'lucide-vue-next'
import { Handshake } from 'lucide-vue-next'
import { socialInfluencers, PLATFORMS, getPlatform, formatNumber, formatCurrency } from '@/services/socialCrmData'

const influencers    = ref([...socialInfluencers])
const searchQ        = ref('')
const platformFilter = ref('all')
const nicheFilter    = ref('all')
const statusFilter   = ref('all')
const followersFilter= ref('all')
const showForm       = ref(false)
const form = reactive({ name: '', alias: '', platform: 'instagram', niche: '', followers: 0, contact: '', agency: '', country: 'España', notes: '' })

const niches = computed(() => [...new Set(influencers.value.map(i => i.niche))])

const filtered = computed(() => {
  let list = [...influencers.value]
  if (searchQ.value) {
    const q = searchQ.value.toLowerCase()
    list = list.filter(i => i.name.toLowerCase().includes(q) || i.alias.toLowerCase().includes(q))
  }
  if (platformFilter.value !== 'all') list = list.filter(i => i.platform === platformFilter.value)
  if (nicheFilter.value !== 'all')    list = list.filter(i => i.niche === nicheFilter.value)
  if (statusFilter.value !== 'all')   list = list.filter(i => i.status === statusFilter.value)
  if (followersFilter.value !== 'all') {
    list = list.filter(i => {
      if (followersFilter.value === 'nano')  return i.followers < 10000
      if (followersFilter.value === 'micro') return i.followers >= 10000 && i.followers < 100000
      if (followersFilter.value === 'macro') return i.followers >= 100000 && i.followers < 1000000
      if (followersFilter.value === 'mega')  return i.followers >= 1000000
      return true
    })
  }
  return list
})

function platformStyle(key) { const p = getPlatform(key); return { background: p.bg, color: p.color } }
function statusClass(s) { return s === 'active' ? 'badge-active' : s === 'prospect' ? 'badge-warning' : 'badge-inactive' }
function statusLabel(s) { return s === 'active' ? 'Activo' : s === 'prospect' ? 'Prospecto' : 'Archivado' }

function openForm() { Object.assign(form, { name: '', alias: '', platform: 'instagram', niche: '', followers: 0, contact: '', agency: '', country: 'España', notes: '' }); showForm.value = true }
function saveInfluencer() {
  if (!form.name) return
  influencers.value.push({ id: Date.now(), ...form, platforms: [form.platform], status: 'prospect', collaborations: 0, salesGenerated: 0, rating: 0, engagementMid: 0, reachMid: 0, clicksMid: 0, conversionsMid: 0, contentQuality: 0, reliability: 0, brandAffinity: 0, reputationRisk: 0 })
  showForm.value = false
}
</script>

<style scoped>
.influencers-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.count-badge { background: var(--bg-secondary); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 10px; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); display: flex; flex-direction: column; gap: var(--spacing-md); }
.filters-bar { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; align-items: center; }
.search-box { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 10px; color: var(--text-secondary); }
.search-input { padding-left: 34px; min-width: 220px; }
.select { padding: 0.5rem 0.75rem; border: 1px solid var(--border-color); border-radius: var(--border-radius-sm); background: var(--bg-primary); color: var(--text-primary); font-size: 0.875rem; cursor: pointer; }
.table-card { overflow: hidden; }
.table-wrapper { overflow-x: auto; }
.influencer-cell { display: flex; align-items: center; gap: var(--spacing-sm); }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.85rem; flex-shrink: 0; }
.inf-name { font-weight: 600; font-size: 0.88rem; color: var(--text-primary); }
.inf-alias { font-size: 0.78rem; color: var(--text-secondary); }
.platform-pill { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; }
.text-right { text-align: right; }
.font-medium { font-weight: 600; color: var(--text-primary); }
.text-sm { font-size: 0.85rem; }
.text-secondary { color: var(--text-secondary); }
.star-rating { display: flex; align-items: center; gap: 2px; justify-content: flex-end; }
.star-filled { color: #F59E0B; fill: #F59E0B; }
.star-empty  { color: #D1D5DB; }
.rating-num  { font-size: 0.78rem; color: var(--text-secondary); margin-left: 4px; }
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
.textarea { resize: vertical; font-family: inherit; }
</style>
