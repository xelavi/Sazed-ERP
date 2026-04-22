<template>
  <div class="social-posts-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Publicaciones</h1>
          <span class="count-badge">{{ filtered.length }}</span>
        </div>
        <div class="header-actions">
          <button class="btn btn-secondary">
            <Download :size="18" /><span>Exportar</span>
          </button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="filters-bar">
        <select class="select" v-model="platformFilter">
          <option value="all">Todas las redes</option>
          <option v-for="(p, key) in PLATFORMS" :key="key" :value="key">{{ p.label }}</option>
        </select>
        <select class="select" v-model="typeFilter">
          <option value="all">Todos los tipos</option>
          <option v-for="t in CONTENT_TYPES" :key="t" :value="t">{{ t }}</option>
        </select>
        <select class="select" v-model="campaignFilter">
          <option value="all">Todas las campañas</option>
          <option value="none">Sin campaña</option>
          <option v-for="c in socialCampaigns" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
        </select>
        <select class="select" v-model="sortKey">
          <option value="date">Fecha</option>
          <option value="reach">Alcance</option>
          <option value="engagement">Engagement</option>
          <option value="clicks">Clics</option>
        </select>
      </div>

      <div class="card table-card">
        <div class="table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Red</th>
                <th>Cuenta</th>
                <th>Publicación</th>
                <th>Tipo</th>
                <th>Campaña</th>
                <th class="text-right">Likes</th>
                <th class="text-right">Comentarios</th>
                <th class="text-right">Compartidos</th>
                <th class="text-right">Guardados</th>
                <th class="text-right">Alcance</th>
                <th class="text-right">Clics</th>
                <th class="text-right">Engagement</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="post in filtered" :key="post.id">
                <td class="text-sm text-secondary">{{ formatDate(post.date) }}</td>
                <td><span class="platform-pill" :style="platformStyle(post.platform)">{{ getPlatform(post.platform).label }}</span></td>
                <td class="text-sm text-secondary">{{ post.accountName }}</td>
                <td class="post-title-cell">
                  <span class="post-title">{{ post.title }}</span>
                </td>
                <td><span class="badge badge-info">{{ post.type }}</span></td>
                <td class="text-sm text-secondary">{{ post.campaignName || '—' }}</td>
                <td class="text-right">{{ formatNumber(post.likes) }}</td>
                <td class="text-right">{{ formatNumber(post.comments) }}</td>
                <td class="text-right">{{ formatNumber(post.shares) }}</td>
                <td class="text-right">{{ formatNumber(post.saves) }}</td>
                <td class="text-right font-medium">{{ formatNumber(post.reach) }}</td>
                <td class="text-right">{{ formatNumber(post.clicks) }}</td>
                <td class="text-right">
                  <span class="eng-val" :class="engClass(post.engagement)">{{ post.engagement }}%</span>
                </td>
                <td>
                  <div class="row-actions">
                    <button class="icon-btn" @click="$router.push('/social-crm/posts/' + post.id)" title="Ver detalle">
                      <Eye :size="15" />
                    </button>
                    <button class="icon-btn" title="Asociar campaña">
                      <Link :size="15" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Download, Eye, Link } from 'lucide-vue-next'
import { socialPosts, socialCampaigns, PLATFORMS, CONTENT_TYPES, getPlatform, formatNumber, formatDate } from '@/services/socialCrmData'

const platformFilter = ref('all')
const typeFilter     = ref('all')
const campaignFilter = ref('all')
const sortKey        = ref('date')

const filtered = computed(() => {
  let list = [...socialPosts]
  if (platformFilter.value !== 'all') list = list.filter(p => p.platform === platformFilter.value)
  if (typeFilter.value !== 'all')     list = list.filter(p => p.type === typeFilter.value)
  if (campaignFilter.value === 'none') list = list.filter(p => !p.campaignId)
  else if (campaignFilter.value !== 'all') list = list.filter(p => p.campaignId === Number(campaignFilter.value))
  return list.sort((a, b) => {
    if (sortKey.value === 'date')       return new Date(b.date) - new Date(a.date)
    if (sortKey.value === 'reach')      return b.reach - a.reach
    if (sortKey.value === 'engagement') return b.engagement - a.engagement
    if (sortKey.value === 'clicks')     return b.clicks - a.clicks
    return 0
  })
})

function platformStyle(key) {
  const p = getPlatform(key)
  return { background: p.bg, color: p.color }
}

function engClass(v) {
  if (v >= 6) return 'eng-high'
  if (v >= 3) return 'eng-mid'
  return 'eng-low'
}
</script>

<style scoped>
.social-posts-view { display: flex; flex-direction: column; height: 100%; }
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
.platform-pill { font-size: 0.75rem; font-weight: 600; padding: 3px 8px; border-radius: 10px; white-space: nowrap; }
.post-title-cell { max-width: 220px; }
.post-title { font-size: 0.85rem; color: var(--text-primary); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.text-secondary { color: var(--text-secondary); }
.text-sm { font-size: 0.85rem; }
.text-right { text-align: right; }
.font-medium { font-weight: 600; }
.row-actions { display: flex; gap: 4px; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border: none; background: none; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: background 0.15s; }
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.eng-val { font-weight: 700; font-size: 0.85rem; }
.eng-high { color: #10B981; }
.eng-mid  { color: #F59E0B; }
.eng-low  { color: #EF4444; }
</style>
