<template>
  <section class="integrations">
    <!-- ── Botiga en línia ──────────────────────────── -->
    <div class="ig-group">
      <h4 class="ig-group-label">Botiga en línia</h4>

      <div class="ig-row" :class="{ connected: isPrestaConnected }">
        <div class="ig-row-left">
          <div class="ig-icon tone-presta"><Store :size="20" /></div>
          <div class="ig-text">
            <span class="ig-name">Botiga PrestaShop</span>
            <span class="ig-desc">
              <template v-if="isPrestaConnected">{{ prestaConnection.base_url }}</template>
              <template v-else>Sincronitza productes i clients amb la teva botiga.</template>
            </span>
          </div>
        </div>
        <div class="ig-row-right">
          <span v-if="isPrestaConnected" class="status-pill ok"><CheckCircle2 :size="12" /> Connectat</span>
          <span v-else class="status-pill idle">Sense connectar</span>
          <div class="ig-actions">
            <button class="btn btn-sm" :class="isPrestaConnected ? 'btn-secondary' : 'btn-primary'"
                    @click="openPrestaModal" :disabled="prestaLoading || syncBusy">
              <Plug :size="14" />
              {{ isPrestaConnected ? 'Gestionar' : 'Connectar' }}
            </button>
            <button v-if="isPrestaConnected"
                    class="btn btn-sm btn-secondary"
                    @click="onFullSync"
                    :disabled="syncBusy || prestaLoading"
                    title="Sincronitzar productes i clients">
              <Loader2 v-if="syncBusy" :size="14" class="spin" />
              <RefreshCw v-else :size="14" />
              Sync
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Xarxes socials ──────────────────────────── -->
    <div class="ig-group">
      <h4 class="ig-group-label">Xarxes socials</h4>

      <div v-for="p in SOCIAL_PLATFORMS" :key="p.key"
           class="ig-row"
           :class="{
             connected: socialStatus[p.key]?.connected && !isExpired(p.key),
             expired:   socialStatus[p.key]?.connected && isExpired(p.key),
           }">
        <div class="ig-row-left">
          <div class="ig-icon" :class="p.tone">
            <component :is="p.icon" :size="20" />
          </div>
          <div class="ig-text">
            <span class="ig-name">{{ p.label }}</span>
            <span class="ig-desc">
              {{ (socialStatus[p.key]?.connected && !isExpired(p.key))
                  ? (socialStatus[p.key]?.extra_data?.name
                    || socialStatus[p.key]?.extra_data?.display_name
                    || socialStatus[p.key]?.extra_data?.username
                    || p.desc)
                  : p.desc }}
            </span>
          </div>
        </div>
        <div class="ig-row-right">
          <!-- Status pill -->
          <span v-if="socialStatus[p.key]?.loading" class="status-pill idle">…</span>
          <span v-else-if="socialStatus[p.key]?.connected && isExpired(p.key)" class="status-pill warn">
            <AlertTriangle :size="11" /> Caducat
          </span>
          <span v-else-if="socialStatus[p.key]?.connected" class="status-pill ok">
            <CheckCircle2 :size="12" /> Connectat
          </span>
          <span v-else class="status-pill idle">Sense connectar</span>

          <div class="ig-actions">
            <!-- Token expirado → Reconectar -->
            <button v-if="socialStatus[p.key]?.connected && isExpired(p.key)"
                    class="btn btn-sm btn-warn"
                    :disabled="socialBusy[p.key]"
                    @click="handleConnect(p.key)">
              <Loader2 v-if="socialBusy[p.key]" :size="14" class="spin" />
              <RefreshCw v-else :size="14" />
              Reconnectar
            </button>
            <!-- Conectado → Desconectar -->
            <button v-else-if="socialStatus[p.key]?.connected"
                    class="btn btn-sm btn-ghost-danger"
                    :disabled="socialBusy[p.key]"
                    @click="disconnectSocial(p.key)">
              <Loader2 v-if="socialBusy[p.key]" :size="14" class="spin" />
              <Link2Off v-else :size="14" />
              Desconnectar
            </button>
            <!-- No conectado → Conectar -->
            <button v-else
                    class="btn btn-sm btn-primary"
                    :disabled="socialBusy[p.key]"
                    @click="handleConnect(p.key)">
              <Loader2 v-if="socialBusy[p.key]" :size="14" class="spin" />
              <Plug v-else :size="14" />
              Connectar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Modal: credenciales de plataforma ──────────── -->
    <Teleport to="body">
      <div v-if="configModal.visible" class="modal-overlay" @click.self="closeConfigModal">
        <div class="modal-box">
          <div class="modal-head">
            <div class="modal-head-title">
              <div class="ig-icon sm" :class="activeMeta?.tone">
                <component :is="activeMeta?.icon" :size="18" />
              </div>
              <div>
                <h3>Connectar {{ activeMeta?.label }}</h3>
                <p class="modal-subtitle">Introdueix les credencials de la teva app</p>
              </div>
            </div>
            <button class="icon-btn" @click="closeConfigModal"><X :size="18" /></button>
          </div>

          <div class="modal-body">
            <!-- Inputs trampa: evitan que el navegador rellene los campos reales -->
            <input type="text" style="display:none" tabindex="-1" autocomplete="username" aria-hidden="true" />
            <input type="password" style="display:none" tabindex="-1" autocomplete="new-password" aria-hidden="true" />

            <!-- Aviso con enlace a la guía -->
            <div class="hint-box">
              <KeyRound :size="15" />
              <span>{{ activeMeta?.hint }}
                <a v-if="activeMeta?.docsUrl" :href="activeMeta.docsUrl" target="_blank" rel="noopener" class="hint-link">
                  Obrir consola →
                </a>
              </span>
            </div>

            <!-- Campos dinámicos según plataforma -->
            <template v-for="field in activeMeta?.fields" :key="field.key">
              <label class="field">
                <span class="field-label">{{ field.label }}</span>
                <input
                  v-model="configModal.form[field.key]"
                  :type="field.type"
                  :placeholder="field.placeholder"
                  class="input"
                  :class="{ mono: field.type === 'password' }"
                  :autocomplete="field.type === 'password' ? 'new-password' : 'off'"
                  :name="field.key + '_' + configModal.platform"
                />
                <span v-if="field.hint" class="field-hint">{{ field.hint }}</span>
              </label>
            </template>
          </div>

          <div class="modal-foot">
            <button class="btn btn-sm btn-secondary" @click="closeConfigModal" :disabled="configModal.saving">
              Cancel·lar
            </button>
            <button class="btn btn-sm btn-primary" @click="saveConfigAndConnect"
                    :disabled="configModal.saving || !configFormValid">
              <Loader2 v-if="configModal.saving" :size="14" class="spin" />
              <Plug v-else :size="14" />
              Desar i connectar
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Modal: conexión PrestaShop ──────────────────── -->
    <Teleport to="body">
      <div v-if="showPrestaModal" class="modal-overlay" @click.self="closePrestaModal">
        <div class="modal-box">
          <div class="modal-head">
            <div class="modal-head-title">
              <div class="ig-icon tone-presta sm"><Store :size="18" /></div>
              <h3>Connectar amb PrestaShop</h3>
            </div>
            <button class="icon-btn" @click="closePrestaModal"><X :size="18" /></button>
          </div>
          <div class="modal-body">
            <label class="field">
              <span class="field-label">URL de la botiga</span>
              <input v-model.trim="prestaForm.base_url" type="url" class="input" placeholder="http://localhost:8080" />
              <span class="field-hint">Sense <code>/api</code> al final.</span>
            </label>
            <label class="field">
              <span class="field-label">Clau API del Webservice</span>
              <input v-model.trim="prestaForm.api_key" type="text" class="input mono"
                     :placeholder="isPrestaConnected ? '•••••••• (deixa-ho buit per no canviar-la)' : 'Enganxa aquí la teva clau API'" />
              <span class="field-hint">Back office → Paràmetres avançats → Webservice → la teva clau.</span>
            </label>
            <div v-if="prestaTestResult" class="test-result" :class="prestaTestResult.ok ? 'ok' : 'err'">
              <CheckCircle2 v-if="prestaTestResult.ok" :size="16" />
              <AlertCircle v-else :size="16" />
              <span v-if="prestaTestResult.ok">
                Connexió correcta amb <strong>{{ prestaTestResult.shop_name }}</strong>
                · {{ prestaTestResult.resources?.length || 0 }} recursos accessibles
              </span>
              <span v-else>{{ prestaTestResult.error }}</span>
            </div>
          </div>
          <div class="modal-foot">
            <button v-if="isPrestaConnected" class="btn btn-sm btn-ghost-danger"
                    @click="onPrestaDisconnect" :disabled="prestaBusy">
              <Trash2 :size="14" /> Desconnectar
            </button>
            <div class="foot-right">
              <button class="btn btn-sm btn-secondary" @click="onPrestaTest" :disabled="prestaBusy || !canPrestaTest">
                <Loader2 v-if="prestaTesting" :size="14" class="spin" />
                <Plug v-else :size="14" />
                Provar la connexió
              </button>
              <button class="btn btn-sm btn-primary" @click="onPrestaSave" :disabled="prestaBusy || !canPrestaSave">
                <Loader2 v-if="prestaSaving" :size="14" class="spin" />
                <Check v-else :size="14" />
                Desar
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  Store, Plug, CheckCircle2, AlertCircle, AlertTriangle, X, Trash2, Check,
  Loader2, Facebook, Twitter, Youtube, Music2, Link2Off, KeyRound, RefreshCw,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { get, post, patch } from '@/services/api'
import ecommerceApi from '@/services/ecommerce'
import { useFacebookSdk } from '@/composables/useFacebookSdk'
import { useYoutubeSdk } from '@/composables/useYoutubeSdk'
import { useXAuth } from '@/composables/useXAuth'
import { useTikTokAuth } from '@/composables/useTikTokAuth'

// ── Plataformas sociales ────────────────────────────────────────────────────
const SOCIAL_PLATFORMS = [
  {
    key: 'facebook',
    label: 'Facebook',
    icon: Facebook,
    tone: 'tone-fb',
    desc: 'Publica publicacions i sincronitza el teu catàleg amb la teva pàgina.',
  },
  {
    key: 'youtube',
    label: 'YouTube',
    icon: Youtube,
    tone: 'tone-yt',
    desc: 'Consulta estadístiques dels teus vídeos i canal des de l\'ERP.',
  },
  {
    key: 'twitter',
    label: 'X',
    icon: Twitter,
    tone: 'tone-x',
    desc: 'Comparteix novetats i consulta mètriques dels teus tuits.',
  },
  {
    key: 'tiktok',
    label: 'TikTok',
    icon: Music2,
    tone: 'tone-tt',
    desc: 'Analitza visualitzacions, m\'agrada i comentaris dels teus vídeos.',
  },
]

// Metadatos del modal de configuración por plataforma
const PLATFORM_META = {
  facebook: {
    label: 'Facebook',
    icon: Facebook,
    tone: 'tone-fb',
    hint: 'Crea la teva app a Facebook for Developers i copia l\'App ID i l\'App Secret.',
    docsUrl: 'https://developers.facebook.com/apps/',
    checkEndpoint: '/settings/facebook/app-id/',
    saveEndpoint: '/settings/facebook/',
    fields: [
      { key: 'facebook_app_id', label: 'App ID', type: 'text', placeholder: '123456789012345' },
      { key: 'facebook_app_secret', label: 'App Secret', type: 'password', placeholder: 'Secret de la teva app' },
    ],
  },
  youtube: {
    label: 'YouTube',
    icon: Youtube,
    tone: 'tone-yt',
    hint: 'A Google Cloud Console, activa la YouTube Data API v3 i crea credencials OAuth 2.0.',
    docsUrl: 'https://console.cloud.google.com/apis/credentials',
    checkEndpoint: '/settings/youtube/client-id/',
    saveEndpoint: '/settings/youtube/',
    fields: [
      { key: 'youtube_client_id', label: 'Client ID', type: 'text', placeholder: 'xxxx.apps.googleusercontent.com' },
      { key: 'youtube_client_secret', label: 'Client Secret', type: 'password', placeholder: 'GOCSPX-...' },
    ],
  },
  twitter: {
    label: 'X (Twitter)',
    icon: Twitter,
    tone: 'tone-x',
    hint: 'Al portal de desenvolupadors d\'X, crea una app i habilita OAuth 2.0.',
    docsUrl: 'https://developer.twitter.com/en/portal/dashboard',
    checkEndpoint: '/settings/twitter/client-id/',
    saveEndpoint: '/settings/twitter/',
    fields: [
      { key: 'twitter_client_id', label: 'Client ID', type: 'text', placeholder: 'Client ID de la teva app' },
      { key: 'twitter_client_secret', label: 'Client Secret', type: 'password', placeholder: 'Client Secret de la teva app' },
    ],
  },
  tiktok: {
    label: 'TikTok',
    icon: Music2,
    tone: 'tone-tt',
    hint: 'A TikTok for Developers, crea una app amb Login Kit i copia la Client Key i el Client Secret.',
    docsUrl: 'https://developers.tiktok.com/apps/',
    checkEndpoint: '/settings/tiktok/client-key/',
    saveEndpoint: '/settings/tiktok/',
    fields: [
      { key: 'tiktok_client_key', label: 'Client Key', type: 'text', placeholder: 'Client Key de la teva app' },
      { key: 'tiktok_client_secret', label: 'Client Secret', type: 'password', placeholder: 'Client Secret de la teva app' },
    ],
  },
}

// ── Setup ───────────────────────────────────────────────────────────────────
const { activeCompany } = useAuth()
const toast = useToast()

const fbSdk = useFacebookSdk()
const ytSdk = useYoutubeSdk()
const xAuth = useXAuth()
const ttAuth = useTikTokAuth()

// ── Social status ───────────────────────────────────────────────────────────
const socialStatus = reactive(
  Object.fromEntries(SOCIAL_PLATFORMS.map(p => [p.key, { connected: false, loading: true, extra_data: {} }])),
)
const socialBusy = reactive(Object.fromEntries(SOCIAL_PLATFORMS.map(p => [p.key, false])))

async function loadSocialStatus(platform) {
  socialStatus[platform].loading = true
  try {
    const data = await get(`/integrations/${platform}/status/`)
    Object.assign(socialStatus[platform], data, { loading: false })
  } catch {
    socialStatus[platform].connected = false
    socialStatus[platform].loading = false
  }
}

async function disconnectSocial(platform) {
  socialBusy[platform] = true
  try {
    await post(`/integrations/${platform}/disconnect/`)
    socialStatus[platform].connected = false
    socialStatus[platform].extra_data = {}
    const label = SOCIAL_PLATFORMS.find(p => p.key === platform)?.label || platform
    toast.success(`${label} desconnectat.`)
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'No s\'ha pogut desconnectar.')
  } finally {
    socialBusy[platform] = false
  }
}

// ── Config modal ────────────────────────────────────────────────────────────
const configModal = reactive({ visible: false, platform: '', form: {}, saving: false })

const activeMeta = computed(() => PLATFORM_META[configModal.platform] || null)

const configFormValid = computed(() => {
  const fields = activeMeta.value?.fields || []
  return fields.every(f => (configModal.form[f.key] || '').trim() !== '')
})

function openConfigModal(platform) {
  configModal.platform = platform
  configModal.form = {}
  configModal.saving = false
  configModal.visible = true
}

function closeConfigModal() {
  if (configModal.saving) return
  configModal.visible = false
}

async function saveConfigAndConnect() {
  const platform = configModal.platform
  const meta = activeMeta.value
  if (!meta) return

  configModal.saving = true
  try {
    await patch(meta.saveEndpoint, { ...configModal.form })
    configModal.visible = false
    toast.success('Credencials desades. Obrint l\'autorització…')
    await doConnect(platform)
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'No s\'ha pogut desar la configuració.')
  } finally {
    configModal.saving = false
  }
}

// ── Connect logic ────────────────────────────────────────────────────────────

function isExpired(platform) {
  const exp = socialStatus[platform]?.token_expires_at
  return !!exp && new Date(exp) < new Date()
}

async function isPlatformConfigured(platform) {
  try {
    const data = await get(PLATFORM_META[platform].checkEndpoint)
    return data.configured === true
  } catch {
    return false
  }
}

/** Entry point: checks config first, opens modal if missing, else connects directly. */
async function handleConnect(platform) {
  socialBusy[platform] = true
  try {
    const configured = await isPlatformConfigured(platform)
    if (!configured) {
      openConfigModal(platform)
      return          // socialBusy reset happens in doConnect after modal flow
    }
    await doConnect(platform)
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error inesperat.')
  } finally {
    socialBusy[platform] = false
  }
}

/** Runs the actual OAuth popup for the given platform. */
async function doConnect(platform) {
  socialBusy[platform] = true
  try {
    if (platform === 'facebook') {
      await fbSdk.ready()
      const auth = await fbSdk.login()
      await post('/integrations/facebook/connect/', { access_token: auth.accessToken })
    } else if (platform === 'youtube') {
      await ytSdk.ready()
      const { access_token } = await ytSdk.login()
      await post('/integrations/youtube/connect/', { access_token })
    } else if (platform === 'twitter') {
      await xAuth.login()
    } else if (platform === 'tiktok') {
      await ttAuth.login()
    }
    const label = SOCIAL_PLATFORMS.find(p => p.key === platform)?.label || platform
    toast.success(`${label} connectat correctament.`)
    await loadSocialStatus(platform)
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'No s\'ha pogut completar la connexió.')
  } finally {
    socialBusy[platform] = false
  }
}

// ── PrestaShop ───────────────────────────────────────────────────────────────
const prestaLoading = ref(true)
const prestaConnection = ref(null)
const isPrestaConnected = computed(() => !!prestaConnection.value)
const showPrestaModal = ref(false)
const prestaForm = reactive({ base_url: 'http://localhost:8080', api_key: '' })
const prestaTestResult = ref(null)
const prestaTesting = ref(false)
const prestaSaving = ref(false)
const prestaBusy = computed(() => prestaTesting.value || prestaSaving.value)
const canPrestaTest = computed(() => !!prestaForm.base_url && !!prestaForm.api_key)
const canPrestaSave = computed(() => !!prestaForm.base_url && (isPrestaConnected.value || !!prestaForm.api_key))

async function loadPresta() {
  if (!activeCompany.value) { prestaLoading.value = false; return }
  prestaLoading.value = true
  try {
    prestaConnection.value = await ecommerceApi.getConnectionForCompany(activeCompany.value.id)
  } catch {
    prestaConnection.value = null
  } finally {
    prestaLoading.value = false
  }
}

function openPrestaModal() {
  prestaTestResult.value = null
  prestaForm.api_key = ''
  prestaForm.base_url = prestaConnection.value?.base_url || 'http://localhost:8080'
  showPrestaModal.value = true
}

function closePrestaModal() { if (!prestaBusy.value) showPrestaModal.value = false }

async function onPrestaTest() {
  prestaTesting.value = true
  prestaTestResult.value = null
  try {
    const res = await ecommerceApi.testConnection({ base_url: prestaForm.base_url, api_key: prestaForm.api_key })
    prestaTestResult.value = { ok: true, ...res }
  } catch (err) {
    prestaTestResult.value = { ok: false, error: err.data?.error || err.message || 'No s\'ha pogut connectar.' }
  } finally {
    prestaTesting.value = false
  }
}

async function onPrestaSave() {
  prestaSaving.value = true
  try {
    if (isPrestaConnected.value) {
      const payload = { company: activeCompany.value.id, platform: 'prestashop', base_url: prestaForm.base_url }
      if (prestaForm.api_key) payload.api_key = prestaForm.api_key
      prestaConnection.value = await ecommerceApi.updateConnection(prestaConnection.value.id, payload)
      toast.success('Connexió actualitzada')
    } else {
      prestaConnection.value = await ecommerceApi.createConnection({
        company: activeCompany.value.id, platform: 'prestashop',
        base_url: prestaForm.base_url, api_key: prestaForm.api_key,
      })
      toast.success('Botiga connectada. Els teus productes i clients ja se sincronitzen.')
    }
    showPrestaModal.value = false
  } catch (err) {
    toast.error(err.data?.error || err.message || 'No s\'ha pogut desar la connexió.')
  } finally {
    prestaSaving.value = false
  }
}

async function onPrestaDisconnect() {
  if (!prestaConnection.value) return
  prestaSaving.value = true
  try {
    await ecommerceApi.deleteConnection(prestaConnection.value.id)
    prestaConnection.value = null
    showPrestaModal.value = false
    toast.success('Botiga desconnectada')
  } catch (err) {
    toast.error(err.message || 'No s\'ha pogut desconnectar.')
  } finally {
    prestaSaving.value = false
  }
}

// ── Full sync ─────────────────────────────────────────────────────────────────
const syncBusy = ref(false)

async function onFullSync() {
  if (!activeCompany.value) return
  syncBusy.value = true
  try {
    const res = await ecommerceApi.fullSync(activeCompany.value.id)
    const parts = []
    if (res.products_ok) parts.push(`${res.products_ok} producte${res.products_ok !== 1 ? 's' : ''}`)
    if (res.customers_ok) parts.push(`${res.customers_ok} client${res.customers_ok !== 1 ? 's' : ''}`)
    if (res.purged) parts.push(`${res.purged} esborrat${res.purged !== 1 ? 's' : ''} de la botiga`)
    const errCount = (res.products_err || 0) + (res.customers_err || 0)
    const summary = parts.length ? parts.join(' · ') : 'Res per sincronitzar'
    if (errCount) {
      toast.error(`Sincronitzat amb errors: ${summary} · ${errCount} error${errCount !== 1 ? 's' : ''}`)
    } else {
      toast.success(`Sincronitzat: ${summary}`)
    }
  } catch (err) {
    toast.error(err.data?.error || err.message || 'Error en la sincronització.')
  } finally {
    syncBusy.value = false
  }
}

onMounted(() => {
  loadPresta()
  SOCIAL_PLATFORMS.forEach(p => loadSocialStatus(p.key))
})
</script>

<style scoped>
.integrations { /* no extra margin — parent controls spacing */ }

/* ── Group ─────────────────────────────────────── */
.ig-group {
  margin-bottom: var(--spacing-md);
}
.ig-group:last-child { margin-bottom: 0; }

.ig-group-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 0.5rem;
  padding-left: 2px;
}

/* ── Integration row ───────────────────────────── */
.ig-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  margin-bottom: 6px;
  background: var(--bg-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.ig-row:last-child { margin-bottom: 0; }
.ig-row:hover { box-shadow: var(--shadow-sm); }
.ig-row.connected { border-color: var(--success-color); }
.ig-row.expired   { border-color: #ea580c; }

.ig-row-left {
  display: flex; align-items: center; gap: 0.625rem;
  min-width: 0; flex: 1;
}
.ig-row-right {
  display: flex; align-items: center; gap: 0.625rem;
  flex-shrink: 0;
}

/* Icon */
.ig-icon {
  width: 36px; height: 36px; border-radius: 9px;
  display: grid; place-items: center; flex-shrink: 0;
}
.ig-icon.sm { width: 32px; height: 32px; border-radius: 8px; }
.tone-presta { background: #eef2ff; color: #4338ca; }
.tone-fb     { background: #e7f0ff; color: #1877f2; }
.tone-yt     { background: #fff0f0; color: #ff0000; }
.tone-x      { background: var(--bg-secondary); color: var(--text-primary); }
.tone-tt     { background: #f0f9ff; color: #010101; }

/* Text */
.ig-text {
  display: flex; flex-direction: column; min-width: 0;
}
.ig-name {
  font-size: var(--font-size-sm); font-weight: 600; color: var(--text-primary);
  line-height: 1.3;
}
.ig-desc {
  font-size: var(--font-size-xs); color: var(--text-secondary);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

/* Actions */
.ig-actions {
  display: flex; gap: 0.375rem;
}
.ig-actions .btn {
  display: inline-flex; align-items: center; gap: 4px;
}

/* Status pill */
.status-pill {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.65rem; font-weight: 600;
  padding: 0.15rem 0.45rem; border-radius: 9999px;
  text-transform: uppercase; letter-spacing: 0.4px;
  white-space: nowrap; flex-shrink: 0;
}
.status-pill.ok   { background: var(--success-light); color: var(--success-color); }
.status-pill.idle { background: var(--bg-secondary); color: var(--text-secondary); }
.status-pill.warn { background: #fff7ed; color: #ea580c; }

/* ── Modal ──────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(15, 23, 42, 0.5);
  display: grid; place-items: center;
  padding: 1rem;
}
.modal-box {
  width: 100%; max-width: 480px;
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.modal-head {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  gap: 0.5rem;
}
.modal-head-title {
  display: flex; align-items: center; gap: 0.75rem;
}
.modal-head-title h3 { margin: 0; font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); }
.modal-subtitle { margin: 0.15rem 0 0; font-size: var(--font-size-xs); color: var(--text-secondary); }
.icon-btn {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  padding: 4px; border-radius: 6px; display: grid; place-items: center;
  flex-shrink: 0;
}
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.modal-body {
  padding: var(--spacing-lg);
  display: flex; flex-direction: column; gap: var(--spacing-md);
}
.modal-foot {
  display: flex; align-items: center; justify-content: flex-end; gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}
.foot-right { display: flex; gap: var(--spacing-sm); margin-left: auto; }

/* Hint box */
.hint-box {
  display: flex; align-items: flex-start; gap: 0.5rem;
  background: var(--bg-secondary);
  border-radius: var(--border-radius);
  padding: 0.625rem 0.75rem;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
}
.hint-box svg { flex-shrink: 0; margin-top: 1px; color: var(--primary-color); }
.hint-link { color: var(--primary-color); font-weight: 600; text-decoration: none; white-space: nowrap; }
.hint-link:hover { text-decoration: underline; }

/* Form fields */
.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--text-primary); }
.field-hint { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.input {
  width: 100%; padding: 0.5rem 0.7rem;
  border: 1px solid var(--border-color); border-radius: var(--border-radius);
  font-size: var(--font-size-sm); color: var(--text-primary); background: var(--bg-primary);
}
.input:focus { outline: none; border-color: var(--primary-color); }
.input.mono { font-family: var(--font-mono, monospace); letter-spacing: 0.3px; }

/* Test result (PrestaShop) */
.test-result {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: var(--font-size-sm); line-height: 1.4;
  padding: 0.625rem 0.75rem; border-radius: var(--border-radius);
}
.test-result.ok  { background: var(--success-light); color: var(--success-color); }
.test-result.err { background: var(--error-light); color: var(--error-color); }

.btn-ghost-danger {
  background: none; border: 1px solid transparent; color: var(--error-color);
}
.btn-ghost-danger:hover { background: var(--error-light); }

.btn-warn {
  background: #fff7ed; border: 1px solid #fed7aa; color: #ea580c;
  font-weight: 600;
}
.btn-warn:hover:not(:disabled) { background: #ffedd5; border-color: #ea580c; }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .ig-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .ig-row-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
