<template>
  <div class="company-settings-view">
    <div class="view-header">
      <div>
        <h1>Configuració de l'empresa</h1>
        <p class="view-subtitle">{{ activeCompany?.name }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <component :is="tab.icon" :size="16" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab: General -->
    <div v-if="activeTab === 'general'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Dades generals</h3>
          <p class="card-subtitle">Informació bàsica de l'empresa</p>
        </div>
        <div class="role-info-row">
          <span class="role-info-label">El teu rol</span>
          <span class="badge" :class="roleBadgeClass(activeRole)">{{ roleLabel(activeRole) }}</span>
        </div>
        <form @submit.prevent="saveGeneral" class="settings-form">
          <div class="form-group logo-group">
            <label class="form-label">Logotip de l'empresa</label>
            <div class="logo-upload">
              <div class="logo-preview" @click="$refs.logoInput.click()">
                <img v-if="logoPreview" :src="logoPreview" alt="Logo" />
                <Building2 v-else :size="28" class="logo-placeholder-icon" />
                <div class="logo-overlay">
                  <Camera :size="18" />
                </div>
              </div>
              <input
                ref="logoInput"
                type="file"
                accept="image/*"
                class="hidden-input"
                @change="onLogoChange"
              />
              <span class="text-xs text-tertiary">Recomanat: 256x256px, PNG o SVG</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Nom comercial <span class="required">*</span></label>
              <input v-model="generalForm.name" class="input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Raó social</label>
              <input v-model="generalForm.legal_name" class="input" placeholder="Empresa SL" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">CIF / NIF</label>
              <input v-model="generalForm.tax_id" class="input" placeholder="B12345678" />
            </div>
            <div class="form-group">
              <label class="form-label">Correu de contacte</label>
              <input v-model="generalForm.email" type="email" class="input" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Telèfon</label>
              <input v-model="generalForm.phone" class="input" placeholder="+34 600 000 000" />
            </div>
            <div class="form-group">
              <label class="form-label">Lloc web</label>
              <input v-model="generalForm.website" class="input" placeholder="https://lamevaempresa.com" />
            </div>
          </div>

          <div class="form-section-title">Adreça</div>

          <div class="form-group">
            <label class="form-label">Adreça</label>
            <input v-model="generalForm.address" class="input" placeholder="Carrer Principal 1" />
          </div>

          <div class="form-row form-row-3">
            <div class="form-group">
              <label class="form-label">Ciutat</label>
              <input v-model="generalForm.city" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Província</label>
              <input v-model="generalForm.province" class="input" />
            </div>
            <div class="form-group">
              <label class="form-label">Codi postal</label>
              <input v-model="generalForm.postal_code" class="input" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">País</label>
            <input v-model="generalForm.country" class="input" />
          </div>

          <div class="form-section-title">Personalització</div>

          <div class="form-group">
            <label class="form-label">Color principal</label>
            <div class="color-picker-row">
              <input type="color" v-model="generalForm.primary_color" class="color-input" />
              <input v-model="generalForm.primary_color" class="input color-text-input" maxlength="7" />
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingGeneral">
              {{ savingGeneral ? 'Desant…' : 'Desar canvis' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tab: Billing / Invoicing -->
    <div v-if="activeTab === 'billing'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Facturació</h3>
          <p class="card-subtitle">Configuració de moneda i numeració de factures</p>
        </div>
        <form @submit.prevent="saveBilling" class="settings-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Moneda</label>
              <select v-model="billingForm.currency" class="select">
                <option value="EUR">EUR - Euro</option>
                <option value="USD">USD - Dòlar</option>
                <option value="GBP">GBP - Lliura</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Prefix de factura</label>
              <input v-model="billingForm.invoice_prefix" class="input" placeholder="FAC" maxlength="10" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Inici de l'any fiscal</label>
            <select v-model="billingForm.fiscal_year_start" class="select">
              <option v-for="(m, i) in months" :key="i" :value="i + 1">{{ m }}</option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="savingBilling">
              {{ savingBilling ? 'Desant…' : 'Desar canvis' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tab: Members -->
    <div v-if="activeTab === 'members'" class="tab-content">
      <div class="card">
        <div class="card-header flex items-center justify-between">
          <div>
            <h3 class="card-title">Membres</h3>
            <p class="card-subtitle">{{ members.length }} membre{{ members.length !== 1 ? 's' : '' }}</p>
          </div>
          <button class="btn btn-primary btn-sm" @click="showInviteModal = true">
            <UserPlus :size="14" />
            Convidar
          </button>
        </div>
        <div class="members-table-wrapper">
          <table class="table">
            <thead>
              <tr>
                <th>Usuari</th>
                <th>Rol</th>
                <th>Des de</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in members" :key="m.id">
                <td>
                  <div class="member-cell">
                    <div class="member-avatar">
                      <img v-if="m.user?.avatar" :src="m.user.avatar" :alt="m.user.full_name" />
                      <span v-else>{{ m.user?.initials || '?' }}</span>
                    </div>
                    <div>
                      <p class="member-name">{{ m.user?.full_name || m.user?.email }}</p>
                      <p class="member-email">{{ m.user?.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="roleBadgeClass(m.role)">{{ roleLabel(m.role) }}</span>
                </td>
                <td class="text-sm text-secondary">{{ formatDate(m.joined_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="loadingMembers" class="loading-center">
            <div class="loading-spinner"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: Integraciones API (solo staff) -->
    <div v-if="activeTab === 'integrations'" class="tab-content">

      <!-- Facebook -->
      <div class="card api-card">
        <div class="api-card-head">
          <div class="api-icon tone-fb"><Facebook :size="20" /></div>
          <div>
            <h3 class="card-title">Facebook</h3>
            <p class="card-subtitle">Credencials de l'app a developers.facebook.com</p>
          </div>
          <span class="status-dot" :class="apiStatus.facebook ? 'ok' : 'idle'" />
        </div>
        <form class="settings-form" @submit.prevent="saveApi('facebook')">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">App ID</label>
              <input v-model="apiForms.facebook.app_id" class="input" placeholder="123456789" />
            </div>
            <div class="form-group">
              <label class="form-label">App Secret</label>
              <input v-model="apiForms.facebook.app_secret" class="input mono" type="password"
                     :placeholder="apiStatus.facebook ? '•••••••• (deixa-ho buit per no canviar-ho)' : 'Enganxa el secret'" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Versió de la Graph API</label>
            <input v-model="apiForms.facebook.graph_version" class="input" placeholder="v19.0" style="max-width:140px" />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="apiSaving.facebook">
              <Loader2 v-if="apiSaving.facebook" :size="14" class="spin" />
              <Check v-else :size="14" />
              Desar
            </button>
          </div>
        </form>
      </div>

      <!-- YouTube -->
      <div class="card api-card">
        <div class="api-card-head">
          <div class="api-icon tone-yt"><Youtube :size="20" /></div>
          <div>
            <h3 class="card-title">YouTube / Google</h3>
            <p class="card-subtitle">Credencials OAuth 2.0 de Google Cloud Console</p>
          </div>
          <span class="status-dot" :class="apiStatus.youtube ? 'ok' : 'idle'" />
        </div>
        <form class="settings-form" @submit.prevent="saveApi('youtube')">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Client ID</label>
              <input v-model="apiForms.youtube.client_id" class="input" placeholder="xxxx.apps.googleusercontent.com" />
            </div>
            <div class="form-group">
              <label class="form-label">Client Secret</label>
              <input v-model="apiForms.youtube.client_secret" class="input mono" type="password"
                     :placeholder="apiStatus.youtube ? '•••••••• (deixa-ho buit per no canviar-ho)' : 'GOCSPX-...'" />
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="apiSaving.youtube">
              <Loader2 v-if="apiSaving.youtube" :size="14" class="spin" />
              <Check v-else :size="14" />
              Desar
            </button>
          </div>
        </form>
      </div>

      <!-- X (Twitter) -->
      <div class="card api-card">
        <div class="api-card-head">
          <div class="api-icon tone-x"><Twitter :size="20" /></div>
          <div>
            <h3 class="card-title">X (Twitter)</h3>
            <p class="card-subtitle">Credencials OAuth 2.0 de developer.twitter.com</p>
          </div>
          <span class="status-dot" :class="apiStatus.twitter ? 'ok' : 'idle'" />
        </div>
        <form class="settings-form" @submit.prevent="saveApi('twitter')">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Client ID</label>
              <input v-model="apiForms.twitter.client_id" class="input" placeholder="Client ID de la teva app" />
            </div>
            <div class="form-group">
              <label class="form-label">Client Secret</label>
              <input v-model="apiForms.twitter.client_secret" class="input mono" type="password"
                     :placeholder="apiStatus.twitter ? '•••••••• (deixa-ho buit per no canviar-ho)' : 'Client Secret'" />
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="apiSaving.twitter">
              <Loader2 v-if="apiSaving.twitter" :size="14" class="spin" />
              <Check v-else :size="14" />
              Desar
            </button>
          </div>
        </form>
      </div>

      <!-- TikTok -->
      <div class="card api-card">
        <div class="api-card-head">
          <div class="api-icon tone-tt"><Music2 :size="20" /></div>
          <div>
            <h3 class="card-title">TikTok</h3>
            <p class="card-subtitle">Credencials OAuth 2.0 de developers.tiktok.com</p>
          </div>
          <span class="status-dot" :class="apiStatus.tiktok ? 'ok' : 'idle'" />
        </div>
        <form class="settings-form" @submit.prevent="saveApi('tiktok')">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Client Key</label>
              <input v-model="apiForms.tiktok.client_key" class="input" placeholder="Client Key de la teva app" />
            </div>
            <div class="form-group">
              <label class="form-label">Client Secret</label>
              <input v-model="apiForms.tiktok.client_secret" class="input mono" type="password"
                     :placeholder="apiStatus.tiktok ? '•••••••• (deixa-ho buit per no canviar-ho)' : 'Client Secret'" />
            </div>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-sm" :disabled="apiSaving.tiktok">
              <Loader2 v-if="apiSaving.tiktok" :size="14" class="spin" />
              <Check v-else :size="14" />
              Desar
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Tab: Plan -->
    <div v-if="activeTab === 'plan'" class="tab-content">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Pla actual</h3>
          <p class="card-subtitle">Gestiona la teva subscripció</p>
        </div>
        <div class="plan-display">
          <div class="plan-badge">
            <Crown :size="20" />
            <span class="plan-name">{{ planLabel(activeCompany?.plan) }}</span>
          </div>
          <p class="plan-description">
            Estàs utilitzant el pla <strong>{{ planLabel(activeCompany?.plan) }}</strong>.
            Per canviar de pla, contacta amb el suport.
          </p>
        </div>
      </div>
    </div>

    <!-- Invite Member Modal -->
    <Teleport to="body">
      <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3>Convidar un membre</h3>
            <button class="modal-close" @click="showInviteModal = false">
              <X :size="20" />
            </button>
          </div>
          <form @submit.prevent="handleInvite" class="modal-body">
            <div class="form-group">
              <label class="form-label">Correu de l'usuari <span class="required">*</span></label>
              <input v-model="inviteForm.email" type="email" class="input" required placeholder="usuari@correu.com" />
            </div>
            <div class="form-group">
              <label class="form-label">Rol</label>
              <select v-model="inviteForm.role" class="select">
                <option value="admin">Administrador</option>
                <option value="editor">Editor</option>
                <option value="viewer">Només lectura</option>
              </select>
            </div>
            <div class="modal-actions">
              <button type="button" class="btn btn-ghost" @click="showInviteModal = false">Cancel·lar</button>
              <button type="submit" class="btn btn-primary" :disabled="inviting">
                {{ inviting ? 'Convidant…' : 'Enviar invitació' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import {
  Building2, Camera, UserPlus, Crown, X,
  Settings2, Receipt, Users, Sparkles, Plug,
  Facebook, Youtube, Twitter, Music2, Loader2, Check,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import authApi from '@/services/auth'
import inboxApi from '@/services/inbox'
import { get, patch } from '@/services/api'

const { activeCompany, activeRole, user } = useAuth()
const toast = useToast()

const canManageApiKeys = computed(() =>
  user.value?.is_staff || ['owner', 'admin'].includes(activeRole.value),
)

// ── Tabs ────────────────────────────────────
const tabs = computed(() => [
  { id: 'general', label: 'General', icon: Settings2 },
  { id: 'billing', label: 'Facturació', icon: Receipt },
  { id: 'members', label: 'Membres', icon: Users },
  { id: 'plan', label: 'Pla', icon: Sparkles },
  ...(canManageApiKeys.value ? [{ id: 'integrations', label: 'API Keys', icon: Plug }] : []),
])
const activeTab = ref('general')

// ── General settings ────────────────────────
const generalForm = reactive({
  name: '', legal_name: '', tax_id: '',
  email: '', phone: '', website: '',
  address: '', city: '', province: '', postal_code: '', country: '',
  primary_color: '#667eea',
})
const logoFile = ref(null)
const logoPreview = ref(null)
const savingGeneral = ref(false)

function loadCompanyData(company) {
  if (!company) return
  const fields = [
    'name', 'legal_name', 'tax_id', 'email', 'phone', 'website',
    'address', 'city', 'province', 'postal_code', 'country', 'primary_color',
  ]
  fields.forEach(f => { generalForm[f] = company[f] || '' })
  if (!generalForm.primary_color) generalForm.primary_color = '#667eea'
  logoPreview.value = company.logo || null

  billingForm.currency = company.currency || 'EUR'
  billingForm.invoice_prefix = company.invoice_prefix || 'FAC'
  billingForm.fiscal_year_start = company.fiscal_year_start || 1
}

function onLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    toast.error('La imatge no pot superar els 2 MB')
    return
  }
  logoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

async function saveGeneral() {
  savingGeneral.value = true
  try {
    let payload
    if (logoFile.value) {
      payload = new FormData()
      Object.entries(generalForm).forEach(([k, v]) => payload.append(k, v))
      payload.append('logo', logoFile.value)
    } else {
      payload = { ...generalForm }
    }
    await authApi.updateCompany(activeCompany.value.id, payload)
    toast.success('Dades actualitzades')
    logoFile.value = null
  } catch {
    toast.error('Error en desar les dades')
  } finally {
    savingGeneral.value = false
  }
}

// ── Billing settings ────────────────────────
const billingForm = reactive({ currency: 'EUR', invoice_prefix: 'FAC', fiscal_year_start: 1 })
const savingBilling = ref(false)
const months = [
  'Gener', 'Febrer', 'Març', 'Abril', 'Maig', 'Juny',
  'Juliol', 'Agost', 'Setembre', 'Octubre', 'Novembre', 'Desembre',
]

async function saveBilling() {
  savingBilling.value = true
  try {
    await authApi.updateCompany(activeCompany.value.id, {
      currency: billingForm.currency,
      invoice_prefix: billingForm.invoice_prefix,
      fiscal_year_start: billingForm.fiscal_year_start,
    })
    toast.success('Configuració de facturació actualitzada')
  } catch {
    toast.error('Error en desar')
  } finally {
    savingBilling.value = false
  }
}

// ── Members ─────────────────────────────────
const members = ref([])
const loadingMembers = ref(false)

async function fetchMembers() {
  if (!activeCompany.value) return
  loadingMembers.value = true
  try {
    const data = await authApi.getMembers(activeCompany.value.id)
    members.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    toast.error('Error en carregar els membres')
  } finally {
    loadingMembers.value = false
  }
}

// ── Invite ──────────────────────────────────
const showInviteModal = ref(false)
const inviting = ref(false)
const inviteForm = reactive({ email: '', role: 'editor' })

async function handleInvite() {
  if (!inviteForm.email.trim()) return
  inviting.value = true
  try {
    await inboxApi.createInvitation({ email: inviteForm.email.trim(), role: inviteForm.role })
    toast.success('Invitació enviada. L\'usuari la veurà a la seva bústia.')
    showInviteModal.value = false
    inviteForm.email = ''
    inviteForm.role = 'editor'
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'Error en convidar')
  } finally {
    inviting.value = false
  }
}

// ── API Keys (staff only) ────────────────────
const apiForms = reactive({
  facebook: { app_id: '', app_secret: '', graph_version: 'v19.0' },
  youtube:  { client_id: '', client_secret: '' },
  twitter:  { client_id: '', client_secret: '' },
  tiktok:   { client_key: '', client_secret: '' },
})
const apiStatus = reactive({ facebook: false, youtube: false, twitter: false, tiktok: false })
const apiSaving = reactive({ facebook: false, youtube: false, twitter: false, tiktok: false })

async function loadApiSettings() {
  try {
    const [fb, yt, tw, tt] = await Promise.all([
      get('/settings/facebook/'),
      get('/settings/youtube/'),
      get('/settings/twitter/'),
      get('/settings/tiktok/'),
    ])
    apiForms.facebook.app_id = fb.facebook_app_id || ''
    apiForms.facebook.graph_version = fb.facebook_graph_version || 'v19.0'
    apiStatus.facebook = !!(fb.facebook_app_id && fb.facebook_app_secret_set)

    apiForms.youtube.client_id = yt.youtube_client_id || ''
    apiStatus.youtube = !!(yt.youtube_client_id && yt.youtube_client_secret_set)

    apiForms.twitter.client_id = tw.twitter_client_id || ''
    apiStatus.twitter = !!(tw.twitter_client_id && tw.twitter_client_secret_set)

    apiForms.tiktok.client_key = tt.tiktok_client_key || ''
    apiStatus.tiktok = !!(tt.tiktok_client_key && tt.tiktok_client_secret_set)
  } catch {
    // non-staff — ignore silently
  }
}

async function saveApi(platform) {
  apiSaving[platform] = true
  try {
    const payloadMap = {
      facebook: {
        facebook_app_id: apiForms.facebook.app_id,
        ...(apiForms.facebook.app_secret ? { facebook_app_secret: apiForms.facebook.app_secret } : {}),
        facebook_graph_version: apiForms.facebook.graph_version || 'v19.0',
      },
      youtube: {
        youtube_client_id: apiForms.youtube.client_id,
        ...(apiForms.youtube.client_secret ? { youtube_client_secret: apiForms.youtube.client_secret } : {}),
      },
      twitter: {
        twitter_client_id: apiForms.twitter.client_id,
        ...(apiForms.twitter.client_secret ? { twitter_client_secret: apiForms.twitter.client_secret } : {}),
      },
      tiktok: {
        tiktok_client_key: apiForms.tiktok.client_key,
        ...(apiForms.tiktok.client_secret ? { tiktok_client_secret: apiForms.tiktok.client_secret } : {}),
      },
    }
    await patch(`/settings/${platform}/`, payloadMap[platform])
    toast.success('Credencials desades. Els canvis s\'apliquen immediatament.')
    // Clear secrets from form after save (don't keep plaintext)
    if (platform === 'facebook') apiForms.facebook.app_secret = ''
    if (platform === 'youtube') apiForms.youtube.client_secret = ''
    if (platform === 'twitter') apiForms.twitter.client_secret = ''
    if (platform === 'tiktok') apiForms.tiktok.client_secret = ''
    await loadApiSettings()
  } catch (err) {
    toast.error(err.data?.detail || err.message || 'No s\'ha pogut desar.')
  } finally {
    apiSaving[platform] = false
  }
}

// ── Helpers ─────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ca-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function roleLabel(role) {
  const map = { owner: 'Propietari', admin: 'Admin', editor: 'Editor', viewer: 'Lector' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = { owner: 'badge-primary', admin: 'badge-success', editor: 'badge-warning', viewer: 'badge-gray' }
  return map[role] || 'badge-gray'
}

function planLabel(plan) {
  const map = { free: 'Gratuït', starter: 'Starter', pro: 'Pro' }
  return map[plan] || 'Gratuït'
}

// ── Lifecycle ───────────────────────────────
watch(activeTab, (tab) => {
  if (tab === 'members' && !members.value.length) fetchMembers()
  if (tab === 'integrations') loadApiSettings()
})

watch(activeCompany, (company) => {
  if (company) {
    loadCompanyData(company)
    if (activeTab.value === 'members') fetchMembers()
  }
}, { immediate: false })

onMounted(async () => {
  if (activeCompany.value) {
    // Fetch full company details
    try {
      const full = await authApi.getCompany(activeCompany.value.id)
      loadCompanyData(full)
    } catch {
      loadCompanyData(activeCompany.value)
    }
  }
})
</script>

<style scoped>
.company-settings-view {
  max-width: 800px;
}

.view-header {
  margin-bottom: var(--spacing-lg);
}

.view-header h1 {
  margin-bottom: 0.25rem;
}

.view-subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin: 0;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 2px solid var(--border-color);
  margin-bottom: var(--spacing-lg);
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: var(--font-size-sm);
  font-weight: 500;
  font-family: var(--font-family);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

/* Role info */
.role-info-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: var(--spacing-sm) 0 var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: var(--spacing-md);
}

.role-info-label {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

/* Form styles */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-row-3 {
  grid-template-columns: 1fr 1fr 1fr;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--error-color);
}

.form-section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
}

/* Logo upload */
.logo-group {
  margin-bottom: 0.5rem;
}

.logo-upload {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.logo-preview {
  width: 64px;
  height: 64px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  position: relative;
  cursor: pointer;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--border-color);
}

.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.logo-placeholder-icon {
  color: var(--text-tertiary);
}

.logo-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.logo-preview:hover .logo-overlay {
  opacity: 1;
}

.hidden-input {
  display: none;
}

/* Color picker */
.color-picker-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.color-input {
  width: 40px;
  height: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  padding: 2px;
}

.color-text-input {
  max-width: 120px;
}

/* Members table */
.members-table-wrapper {
  overflow-x: auto;
}

.member-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xs);
  font-weight: 600;
  overflow: hidden;
  flex-shrink: 0;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.member-name {
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
  font-size: var(--font-size-sm);
}

.member-email {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
  margin: 0;
}

.loading-center {
  display: flex;
  justify-content: center;
  padding: var(--spacing-xl);
}

/* Plan display */
.plan-display {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.plan-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-light);
  color: var(--primary-color);
  border-radius: 9999px;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.plan-name {
  font-size: var(--font-size-lg);
}

.plan-description {
  color: var(--text-secondary);
  max-width: 400px;
  margin: 0 auto;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9000;
  padding: var(--spacing-lg);
}

.modal-card {
  background: white;
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--border-radius-sm);
  display: flex;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

/* API Keys tab */
.api-card { margin-bottom: var(--spacing-md); }
.api-card:last-child { margin-bottom: 0; }

.api-card-head {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding-bottom: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}
.api-card-head > div { flex: 1; }
.api-card-head .card-title { margin: 0; font-size: var(--font-size-base); }
.api-card-head .card-subtitle { margin: 0; }

.api-icon {
  width: 38px; height: 38px;
  border-radius: 9px;
  display: grid; place-items: center;
  flex-shrink: 0;
}
.tone-fb  { background: #e7f0ff; color: #1877f2; }
.tone-yt  { background: #fff0f0; color: #ff0000; }
.tone-x   { background: var(--bg-secondary); color: var(--text-primary); }
.tone-tt  { background: #f0f9ff; color: #010101; }

.status-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.ok   { background: var(--success-color); }
.status-dot.idle { background: var(--border-color); }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 640px) {
  .tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .form-row,
  .form-row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
