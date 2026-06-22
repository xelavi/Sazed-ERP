<template>
  <div class="oauth-done">
    <div v-if="success" class="state ok">
      <CheckCircle2 :size="48" />
      <p>Connectat correctament. Tancant…</p>
    </div>
    <div v-else-if="errorMsg" class="state err">
      <AlertCircle :size="48" />
      <p>{{ errorMsg }}</p>
      <p class="sub">Pots tancar aquesta finestra.</p>
    </div>
    <div v-else class="state loading">
      <Loader2 :size="48" class="spin" />
      <p>Processant…</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { CheckCircle2, AlertCircle, Loader2 } from 'lucide-vue-next'

const route = useRoute()
const success = ref(false)
const errorMsg = ref('')

onMounted(() => {
  const { platform, success: s, error } = route.query

  if (s === '1') {
    success.value = true
    if (window.opener) {
      window.opener.postMessage(
        { type: 'oauth_callback', platform, success: true },
        window.location.origin,
      )
      setTimeout(() => window.close(), 800)
    }
  } else {
    errorMsg.value = error ? decodeURIComponent(error) : 'Error desconegut.'
    if (window.opener) {
      window.opener.postMessage(
        { type: 'oauth_callback', platform, success: false, error: errorMsg.value },
        window.location.origin,
      )
      setTimeout(() => window.close(), 2500)
    }
  }
})
</script>

<style scoped>
.oauth-done {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg-primary, #fff);
  font-family: var(--font-sans, sans-serif);
}
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}
.state p { margin: 0; font-size: 1rem; color: var(--text-primary, #111); }
.state .sub { font-size: 0.85rem; color: var(--text-secondary, #666); }
.state.ok  { color: var(--success-color, #16a34a); }
.state.err { color: var(--error-color, #dc2626); }
.state.loading { color: var(--text-secondary, #666); }
.spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
