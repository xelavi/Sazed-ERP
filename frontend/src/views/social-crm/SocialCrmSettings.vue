<template>
  <div class="settings-view">
    <div class="view-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="view-title">Configuración — Social CRM</h1>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="saveSettings">Guardar cambios</button>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="settings-layout">
        <!-- Sidebar nav -->
        <div class="settings-nav">
          <button v-for="s in sections" :key="s.id" :class="['nav-item', { active: activeSection === s.id }]" @click="activeSection = s.id">
            <component :is="s.icon" :size="18" />
            <span>{{ s.label }}</span>
          </button>
        </div>

        <!-- Content -->
        <div class="settings-content">

          <!-- Section: Redes y APIs -->
          <div v-if="activeSection === 'networks'" class="section-panel">
            <h2 class="section-title">Redes sociales y APIs</h2>
            <div class="network-list">
              <div v-for="net in networkConnections" :key="net.key" class="network-card card">
                <div class="net-icon-wrap" :style="{ background: net.bg }">
                  <component :is="net.icon" :size="20" :style="{ color: net.color }" />
                </div>
                <div class="net-info">
                  <div class="net-name">{{ net.name }}</div>
                  <div class="net-status">
                    <span :class="['status-dot', net.connected ? 'connected' : 'disconnected']"></span>
                    <span class="status-text">{{ net.connected ? 'Conectado' : 'Desconectado' }}</span>
                  </div>
                </div>
                <div class="net-actions">
                  <div v-if="net.connected">
                    <div class="field-inline">
                      <label class="field-label-sm">Sincronización</label>
                      <select class="select-sm" v-model="net.syncFreq">
                        <option value="manual">Manual</option>
                        <option value="daily">Diaria</option>
                        <option value="realtime">Tiempo real</option>
                      </select>
                    </div>
                    <button class="btn btn-secondary btn-sm" @click="disconnect(net)">Desconectar</button>
                  </div>
                  <button v-else class="btn btn-primary btn-sm" @click="connect(net)">Conectar</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Section: Catálogos -->
          <div v-if="activeSection === 'catalogs'" class="section-panel">
            <h2 class="section-title">Catálogos y taxonomía</h2>
            <div class="catalog-grid">
              <div class="card catalog-card" v-for="cat in catalogs" :key="cat.id">
                <div class="card-header">
                  <h3 class="card-title">{{ cat.name }}</h3>
                  <button class="btn btn-secondary btn-sm" @click="addCatalogItem(cat)"><Plus :size="14" /><span>Añadir</span></button>
                </div>
                <div class="cat-items">
                  <div v-for="(item, i) in cat.items" :key="i" class="cat-item">
                    <span class="cat-label">{{ item }}</span>
                    <button class="icon-btn-xs" @click="cat.items.splice(i, 1)"><X :size="12" /></button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Section: Permisos -->
          <div v-if="activeSection === 'permissions'" class="section-panel">
            <h2 class="section-title">Roles y permisos</h2>
            <div class="roles-table card">
              <div class="roles-header">
                <div class="role-col role-label">Módulo</div>
                <div class="role-col" v-for="r in roles" :key="r">{{ r }}</div>
              </div>
              <div v-for="perm in permissions" :key="perm.module" class="roles-row">
                <div class="role-col role-label">{{ perm.module }}</div>
                <div class="role-col" v-for="r in roles" :key="r">
                  <input type="checkbox" v-model="perm[r]" class="checkbox" />
                </div>
              </div>
            </div>
          </div>

          <!-- Section: Notificaciones -->
          <div v-if="activeSection === 'notifications'" class="section-panel">
            <h2 class="section-title">Notificaciones y alertas automáticas</h2>
            <div class="card notif-card">
              <div class="notif-row" v-for="n in notifications" :key="n.key">
                <div class="notif-info">
                  <div class="notif-name">{{ n.name }}</div>
                  <div class="notif-desc">{{ n.desc }}</div>
                </div>
                <div class="notif-controls">
                  <label class="toggle">
                    <input type="checkbox" v-model="n.enabled" />
                    <span class="toggle-slider"></span>
                  </label>
                  <select v-if="n.enabled" class="select-sm" v-model="n.channel">
                    <option value="inapp">In-app</option>
                    <option value="email">Email</option>
                    <option value="both">Ambos</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Globe, BookOpen, Shield, Bell, Plus, X, Instagram, Youtube, Linkedin, Twitter, Rss } from 'lucide-vue-next'

const activeSection = ref('networks')

const sections = [
  { id: 'networks',      label: 'Redes y APIs',           icon: Globe },
  { id: 'catalogs',      label: 'Catálogos',              icon: BookOpen },
  { id: 'permissions',   label: 'Permisos',               icon: Shield },
  { id: 'notifications', label: 'Notificaciones',         icon: Bell },
]

const networkConnections = reactive([
  { key: 'instagram', name: 'Instagram', icon: Instagram, color: '#E4405F', bg: '#fdf0f3', connected: true,  syncFreq: 'daily' },
  { key: 'tiktok',    name: 'TikTok',    icon: Rss,       color: '#000000', bg: '#f5f5f5', connected: false, syncFreq: 'manual' },
  { key: 'twitter',   name: 'X / Twitter', icon: Twitter, color: '#1DA1F2', bg: '#eff9fe', connected: true,  syncFreq: 'daily' },
  { key: 'facebook',  name: 'Facebook',  icon: Globe,     color: '#1877F2', bg: '#eff5ff', connected: false, syncFreq: 'manual' },
  { key: 'youtube',   name: 'YouTube',   icon: Youtube,   color: '#FF0000', bg: '#fff5f5', connected: true,  syncFreq: 'daily' },
  { key: 'linkedin',  name: 'LinkedIn',  icon: Linkedin,  color: '#0A66C2', bg: '#eff6ff', connected: false, syncFreq: 'manual' },
])

function connect(net) { net.connected = true; alert(`Conectando con ${net.name}... (simulado)`) }
function disconnect(net) { if (confirm(`¿Desconectar ${net.name}?`)) net.connected = false }

const catalogs = reactive([
  { id: 'types',       name: 'Tipos de contenido',          items: ['Imagen', 'Vídeo', 'Reel', 'Story', 'Carrusel', 'Tweet', 'Hilo'] },
  { id: 'statuses',    name: 'Estados de colaboración',     items: ['Borrador', 'Pendiente', 'Activa', 'Completada', 'Cancelada'] },
  { id: 'categories',  name: 'Categorías de influencer',    items: ['Lifestyle', 'Moda', 'Tecnología', 'Fitness', 'Gastronomía', 'Gaming'] },
  { id: 'objectives',  name: 'Objetivos de campaña',        items: ['Awareness', 'Tráfico', 'Conversiones', 'Engagement', 'Captación'] },
])
function addCatalogItem(cat) { const v = prompt('Nombre del nuevo item:'); if (v?.trim()) cat.items.push(v.trim()) }

const roles = ['Admin', 'Marketing', 'Analista', 'Comercial']
const permissions = reactive([
  { module: 'Cuentas',        Admin: true,  Marketing: true,  Analista: false, Comercial: false },
  { module: 'Publicaciones',  Admin: true,  Marketing: true,  Analista: true,  Comercial: false },
  { module: 'Campañas',       Admin: true,  Marketing: true,  Analista: true,  Comercial: true  },
  { module: 'Influencers',    Admin: true,  Marketing: true,  Analista: true,  Comercial: true  },
  { module: 'Colaboraciones', Admin: true,  Marketing: true,  Analista: false, Comercial: true  },
  { module: 'Métricas',       Admin: true,  Marketing: true,  Analista: true,  Comercial: false },
  { module: 'Analítica',      Admin: true,  Marketing: true,  Analista: true,  Comercial: true  },
  { module: 'Informes',       Admin: true,  Marketing: true,  Analista: true,  Comercial: false },
  { module: 'Alertas',        Admin: true,  Marketing: true,  Analista: false, Comercial: false },
  { module: 'Configuración',  Admin: true,  Marketing: false, Analista: false, Comercial: false },
])

const notifications = reactive([
  { key: 'reach_drop',   name: 'Caída de alcance',         desc: 'Alerta cuando el alcance baja más del 20%',       enabled: true,  channel: 'inapp' },
  { key: 'broken_link',  name: 'Enlace roto',              desc: 'Alerta si un enlace trackeable falla',            enabled: true,  channel: 'both'  },
  { key: 'low_budget',   name: 'Presupuesto bajo',         desc: 'Alerta cuando queda menos del 10% del budget',    enabled: false, channel: 'email' },
  { key: 'neg_comments', name: 'Comentarios negativos',   desc: 'Alerta si el sentimiento negativo supera el 30%', enabled: false, channel: 'inapp' },
  { key: 'new_collab',   name: 'Nueva colaboración',       desc: 'Notificar al responsable al crear colaboración',  enabled: true,  channel: 'email' },
  { key: 'report_ready', name: 'Informe generado',         desc: 'Notificar cuando un informe automático está listo', enabled: true, channel: 'inapp' },
])

function saveSettings() { alert('Configuración guardada (simulado)') }
</script>

<style scoped>
.settings-view { display: flex; flex-direction: column; height: 100%; }
.view-header { padding: var(--spacing-lg) var(--spacing-xl); border-bottom: 1px solid var(--border-color); background: var(--bg-primary); }
.header-content { display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); }
.title-section { display: flex; align-items: center; gap: var(--spacing-sm); }
.view-title { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.header-actions { display: flex; gap: var(--spacing-sm); }
.content-wrapper { flex: 1; overflow-y: auto; padding: var(--spacing-xl); }
.settings-layout { display: grid; grid-template-columns: 200px 1fr; gap: var(--spacing-lg); }
.settings-nav { display: flex; flex-direction: column; gap: 4px; }
.nav-item { display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border: none; background: none; border-radius: var(--border-radius-sm); cursor: pointer; font-size: 0.875rem; color: var(--text-secondary); transition: all 0.15s; text-align: left; width: 100%; }
.nav-item:hover { background: var(--bg-secondary); color: var(--text-primary); }
.nav-item.active { background: #eef2ff; color: var(--primary-color); font-weight: 600; }
.settings-content { min-height: 400px; }
.section-panel { display: flex; flex-direction: column; gap: var(--spacing-lg); }
.section-title { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0; }
.network-list { display: flex; flex-direction: column; gap: var(--spacing-sm); }
.network-card { display: flex; align-items: center; gap: var(--spacing-md); padding: var(--spacing-md) var(--spacing-lg); }
.net-icon-wrap { width: 40px; height: 40px; border-radius: var(--border-radius-sm); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.net-info { flex: 1; }
.net-name { font-weight: 600; font-size: 0.9rem; color: var(--text-primary); }
.net-status { display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.connected { background: #10B981; }
.status-dot.disconnected { background: #9CA3AF; }
.status-text { font-size: 0.78rem; color: var(--text-secondary); }
.net-actions { display: flex; align-items: center; gap: var(--spacing-sm); }
.field-inline { display: flex; align-items: center; gap: 6px; margin-right: var(--spacing-sm); }
.field-label-sm { font-size: 0.78rem; color: var(--text-secondary); white-space: nowrap; }
.select-sm { padding: 4px 8px; border: 1px solid var(--border-color); border-radius: 6px; background: var(--bg-primary); font-size: 0.8rem; color: var(--text-primary); cursor: pointer; }
.btn-sm { padding: 5px 10px; font-size: 0.8rem; }
.catalog-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.card-title { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.cat-items { padding: var(--spacing-md); display: flex; flex-wrap: wrap; gap: 8px; }
.cat-item { display: flex; align-items: center; gap: 4px; background: var(--bg-secondary); border-radius: var(--border-radius-sm); padding: 3px 8px; }
.cat-label { font-size: 0.82rem; color: var(--text-primary); }
.icon-btn-xs { display: flex; align-items: center; justify-content: center; width: 16px; height: 16px; border: none; background: none; cursor: pointer; color: var(--text-secondary); border-radius: 3px; }
.icon-btn-xs:hover { color: #EF4444; }
.roles-table { overflow-x: auto; }
.roles-header, .roles-row { display: grid; grid-template-columns: 200px repeat(4, 1fr); gap: var(--spacing-sm); padding: var(--spacing-sm) var(--spacing-md); border-bottom: 1px solid var(--border-color); align-items: center; }
.roles-header { font-size: 0.78rem; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); }
.role-col { display: flex; align-items: center; justify-content: center; }
.role-label { justify-content: flex-start; font-size: 0.875rem; color: var(--text-primary); }
.checkbox { width: 16px; height: 16px; cursor: pointer; accent-color: var(--primary-color); }
.notif-card { display: flex; flex-direction: column; }
.notif-row { display: flex; align-items: center; justify-content: space-between; padding: var(--spacing-md) var(--spacing-lg); border-bottom: 1px solid var(--border-color); }
.notif-row:last-child { border-bottom: none; }
.notif-name { font-weight: 600; font-size: 0.875rem; color: var(--text-primary); }
.notif-desc { font-size: 0.78rem; color: var(--text-secondary); margin-top: 2px; }
.notif-controls { display: flex; align-items: center; gap: var(--spacing-sm); }
.toggle { position: relative; display: inline-block; width: 36px; height: 20px; }
.toggle input { opacity: 0; width: 0; height: 0; }
.toggle-slider { position: absolute; cursor: pointer; inset: 0; background: #ccc; border-radius: 10px; transition: 0.3s; }
.toggle-slider::before { content: ''; position: absolute; width: 14px; height: 14px; left: 3px; top: 3px; background: white; border-radius: 50%; transition: 0.3s; }
input:checked + .toggle-slider { background: var(--primary-color); }
input:checked + .toggle-slider::before { transform: translateX(16px); }
</style>
