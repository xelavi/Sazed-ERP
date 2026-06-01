<template>
  <section class="integrations">
    <div class="card-header-row">
      <div>
        <h2 class="card-title">Conecta tus canales</h2>
        <p class="card-subtitle">Sincroniza el ERP con tu tienda online y tus redes</p>
      </div>
    </div>

    <div class="integration-grid">
      <!-- ── PrestaShop (funcional) ─────────────────── -->
      <div class="integration-card" :class="{ connected: isConnected }">
        <div class="integration-top">
          <div class="integration-icon tone-presta"><Store :size="22" /></div>
          <span v-if="isConnected" class="status-pill ok">
            <CheckCircle2 :size="13" /> Conectado
          </span>
          <span v-else class="status-pill idle">Sin conectar</span>
        </div>

        <h3 class="integration-name">Tienda PrestaShop</h3>
        <p class="integration-desc">
          <template v-if="isConnected">
            {{ connection.base_url }}
          </template>
          <template v-else>
            Crea productos y clientes en el ERP y aparecerán en tu tienda.
          </template>
        </p>

        <div class="integration-actions">
          <button class="btn btn-sm" :class="isConnected ? 'btn-secondary' : 'btn-primary'"
                  @click="openModal" :disabled="loading">
            <Plug :size="14" />
            {{ isConnected ? 'Gestionar' : 'Conectar' }}
          </button>
        </div>
      </div>

      <!-- ── Sociales (próximamente) ────────────────── -->
      <div v-for="s in socials" :key="s.key" class="integration-card soon">
        <div class="integration-top">
          <div class="integration-icon" :class="s.tone"><component :is="s.icon" :size="22" /></div>
          <span class="status-pill soon-pill">Próximamente</span>
        </div>
        <h3 class="integration-name">{{ s.name }}</h3>
        <p class="integration-desc">{{ s.desc }}</p>
        <div class="integration-actions">
          <button class="btn btn-sm btn-secondary" disabled>Conectar</button>
        </div>
      </div>
    </div>

    <!-- ── Modal conexión PrestaShop ────────────────── -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal-box">
          <div class="modal-head">
            <div class="modal-head-title">
              <div class="integration-icon tone-presta sm"><Store :size="18" /></div>
              <h3>Conectar con PrestaShop</h3>
            </div>
            <button class="icon-btn" @click="closeModal"><X :size="18" /></button>
          </div>

          <div class="modal-body">
            <label class="field">
              <span class="field-label">URL de la tienda</span>
              <input v-model.trim="form.base_url" type="url" class="input"
                     placeholder="http://localhost:8080" />
              <span class="field-hint">Sin <code>/api</code> al final.</span>
            </label>

            <label class="field">
              <span class="field-label">API key del Webservice</span>
              <input v-model.trim="form.api_key" type="text" class="input mono"
                     :placeholder="isConnected ? '•••••••• (déjalo vacío para no cambiarla)' : 'Pega aquí tu API key'" />
              <span class="field-hint">
                Back office → Parámetros avanzados → Webservice → tu clave.
              </span>
            </label>

            <!-- Resultado del test -->
            <div v-if="testResult" class="test-result" :class="testResult.ok ? 'ok' : 'err'">
              <CheckCircle2 v-if="testResult.ok" :size="16" />
              <AlertCircle v-else :size="16" />
              <span v-if="testResult.ok">
                Conexión correcta con <strong>{{ testResult.shop_name }}</strong>
                · {{ testResult.resources?.length || 0 }} recursos accesibles
              </span>
              <span v-else>{{ testResult.error }}</span>
            </div>
          </div>

          <div class="modal-foot">
            <button v-if="isConnected" class="btn btn-sm btn-ghost-danger"
                    @click="onDisconnect" :disabled="busy">
              <Trash2 :size="14" /> Desconectar
            </button>
            <div class="foot-right">
              <button class="btn btn-sm btn-secondary" @click="onTest" :disabled="busy || !canTest">
                <Loader2 v-if="testing" :size="14" class="spin" />
                <Plug v-else :size="14" />
                Probar conexión
              </button>
              <button class="btn btn-sm btn-primary" @click="onSave" :disabled="busy || !canSave">
                <Loader2 v-if="saving" :size="14" class="spin" />
                <Check v-else :size="14" />
                Guardar
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
  Store, Plug, CheckCircle2, AlertCircle, X, Trash2, Check, Loader2,
  Facebook, Instagram, Twitter,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import ecommerceApi from '@/services/ecommerce'

const { activeCompany } = useAuth()
const toast = useToast()

const socials = [
  { key: 'fb', name: 'Facebook', icon: Facebook, tone: 'tone-fb', desc: 'Publica y sincroniza tu catálogo con tu página.' },
  { key: 'ig', name: 'Instagram', icon: Instagram, tone: 'tone-ig', desc: 'Conecta tu catálogo con Instagram Shopping.' },
  { key: 'x', name: 'X', icon: Twitter, tone: 'tone-x', desc: 'Comparte novedades de tu tienda automáticamente.' },
]

const loading = ref(true)
const connection = ref(null)
const isConnected = computed(() => !!connection.value)

const showModal = ref(false)
const form = reactive({ base_url: 'http://localhost:8080', api_key: '' })
const testResult = ref(null)
const testing = ref(false)
const saving = ref(false)
const busy = computed(() => testing.value || saving.value)

const canTest = computed(() => !!form.base_url && !!form.api_key)
const canSave = computed(() =>
  !!form.base_url && (isConnected.value || !!form.api_key),
)

async function load() {
  if (!activeCompany.value) { loading.value = false; return }
  loading.value = true
  try {
    connection.value = await ecommerceApi.getConnectionForCompany(activeCompany.value.id)
  } catch {
    connection.value = null
  } finally {
    loading.value = false
  }
}

function openModal() {
  testResult.value = null
  form.api_key = ''
  form.base_url = connection.value?.base_url || 'http://localhost:8080'
  showModal.value = true
}

function closeModal() {
  if (busy.value) return
  showModal.value = false
}

async function onTest() {
  testing.value = true
  testResult.value = null
  try {
    const res = await ecommerceApi.testConnection({
      base_url: form.base_url, api_key: form.api_key,
    })
    testResult.value = { ok: true, ...res }
  } catch (err) {
    testResult.value = { ok: false, error: err.data?.error || err.message || 'No se pudo conectar.' }
  } finally {
    testing.value = false
  }
}

async function onSave() {
  saving.value = true
  try {
    if (isConnected.value) {
      const payload = {
        company: activeCompany.value.id,
        platform: 'prestashop',
        base_url: form.base_url,
      }
      if (form.api_key) payload.api_key = form.api_key
      connection.value = await ecommerceApi.updateConnection(connection.value.id, payload)
      toast.success('Conexión actualizada')
    } else {
      connection.value = await ecommerceApi.createConnection({
        company: activeCompany.value.id,
        platform: 'prestashop',
        base_url: form.base_url,
        api_key: form.api_key,
      })
      toast.success('Tienda conectada. Tus productos y clientes ya se sincronizan.')
    }
    showModal.value = false
  } catch (err) {
    toast.error(err.data?.error || err.message || 'No se pudo guardar la conexión.')
  } finally {
    saving.value = false
  }
}

async function onDisconnect() {
  if (!connection.value) return
  saving.value = true
  try {
    await ecommerceApi.deleteConnection(connection.value.id)
    connection.value = null
    showModal.value = false
    toast.success('Tienda desconectada')
  } catch (err) {
    toast.error(err.message || 'No se pudo desconectar.')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.integrations { margin-bottom: var(--spacing-lg); }

.integration-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.integration-card {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--bg-primary);
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}
.integration-card:hover { box-shadow: var(--shadow-md); }
.integration-card.connected { border-color: var(--success-color); }
.integration-card.soon { opacity: 0.72; }

.integration-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.integration-icon {
  width: 42px; height: 42px; border-radius: 11px;
  display: grid; place-items: center; flex-shrink: 0;
}
.integration-icon.sm { width: 32px; height: 32px; border-radius: 8px; }
.tone-presta { background: #eef2ff; color: #4338ca; }
.tone-fb { background: #e7f0ff; color: #1877f2; }
.tone-ig { background: #fdecf3; color: #c13584; }
.tone-x { background: var(--bg-secondary); color: var(--text-primary); }

.integration-name {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}
.integration-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}
.integration-actions { margin-top: 0.25rem; }
.integration-actions .btn { display: inline-flex; align-items: center; gap: 5px; width: 100%; justify-content: center; }

.status-pill {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.68rem; font-weight: 600;
  padding: 0.18rem 0.5rem; border-radius: 9999px;
  text-transform: uppercase; letter-spacing: 0.4px;
}
.status-pill.ok { background: var(--success-light); color: var(--success-color); }
.status-pill.idle { background: var(--bg-secondary); color: var(--text-secondary); }
.status-pill.soon-pill { background: var(--warning-light); color: var(--warning-color); }

/* ── Modal ─────────────────────────────────────── */
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
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}
.modal-head-title { display: flex; align-items: center; gap: 0.625rem; }
.modal-head-title h3 { margin: 0; font-size: var(--font-size-lg); font-weight: 600; color: var(--text-primary); }
.icon-btn {
  background: none; border: none; cursor: pointer; color: var(--text-secondary);
  padding: 4px; border-radius: 6px; display: grid; place-items: center;
}
.icon-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }

.modal-body {
  padding: var(--spacing-lg);
  display: flex; flex-direction: column; gap: var(--spacing-md);
}
.field { display: flex; flex-direction: column; gap: 0.3rem; }
.field-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--text-primary); }
.field-hint { font-size: var(--font-size-xs); color: var(--text-tertiary); }
.field-hint code { background: var(--bg-secondary); padding: 0 4px; border-radius: 4px; }
.input {
  width: 100%; padding: 0.5rem 0.7rem;
  border: 1px solid var(--border-color); border-radius: var(--border-radius);
  font-size: var(--font-size-sm); color: var(--text-primary); background: var(--bg-primary);
}
.input:focus { outline: none; border-color: var(--primary-color); }
.input.mono { font-family: var(--font-mono, monospace); letter-spacing: 0.3px; }

.test-result {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: var(--font-size-sm); line-height: 1.4;
  padding: 0.625rem 0.75rem; border-radius: var(--border-radius);
}
.test-result.ok { background: var(--success-light); color: var(--success-color); }
.test-result.err { background: var(--error-light); color: var(--error-color); }

.modal-foot {
  display: flex; align-items: center; justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  gap: var(--spacing-sm);
}
.foot-right { display: flex; gap: var(--spacing-sm); margin-left: auto; }
.modal-foot .btn { display: inline-flex; align-items: center; gap: 5px; }
.btn-ghost-danger {
  background: none; border: 1px solid transparent; color: var(--error-color);
}
.btn-ghost-danger:hover { background: var(--error-light); }

.spin { animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .integration-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .integration-grid { grid-template-columns: 1fr; }
}
</style>
