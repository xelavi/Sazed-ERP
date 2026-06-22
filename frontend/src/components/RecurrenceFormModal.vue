<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="rec-overlay" @click.self="$emit('close')">
        <div class="rec-panel">
          <div class="rec-header">
            <div>
              <h3 class="rec-title">
                <Repeat :size="18" />
                Fer recurrent
              </h3>
              <p class="rec-sub" v-if="sourceInvoice">
                Plantilla a partir de
                <strong>{{ sourceInvoice.number || 'esborrany' }}</strong>
                · {{ formatCurrency(sourceInvoice.totalAmount) }}
              </p>
            </div>
            <button class="rec-icon-btn" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <div class="rec-body">
            <p class="rec-hint">
              Es generarà i aprovarà automàticament una factura amb aquestes
              línies a cada venciment. La factura original no es modifica.
            </p>

            <div class="rec-field">
              <label class="rec-label">Freqüència</label>
              <div class="rec-row">
                <span class="rec-prefix">Cada</span>
                <input
                  class="rec-input rec-input-num"
                  type="number"
                  min="1"
                  v-model.number="form.interval"
                />
                <select class="rec-select" v-model="form.frequency">
                  <option value="weekly">setmana(es)</option>
                  <option value="monthly">mes(os)</option>
                  <option value="quarterly">trimestre(s)</option>
                  <option value="semiannual">semestre(s)</option>
                  <option value="yearly">any(s)</option>
                </select>
              </div>
            </div>

            <div class="rec-field">
              <label class="rec-label">Primera emissió</label>
              <input class="rec-input" type="date" v-model="form.start_date" />
            </div>

            <div class="rec-field">
              <label class="rec-label">Venciment de pagament</label>
              <div class="rec-row">
                <input
                  class="rec-input rec-input-num"
                  type="number"
                  min="0"
                  v-model.number="form.payment_term_days"
                />
                <span class="rec-suffix">dies després de l'emissió</span>
              </div>
            </div>

            <div class="rec-field">
              <label class="rec-label">Finalització</label>
              <select class="rec-select rec-select-full" v-model="endMode">
                <option value="never">Sense fi (fins a pausar-la)</option>
                <option value="until">En una data concreta</option>
                <option value="count">Després d'un nre. de factures</option>
              </select>
            </div>

            <div v-if="endMode === 'until'" class="rec-field">
              <label class="rec-label">Fins al</label>
              <input class="rec-input" type="date" v-model="form.end_date" />
            </div>

            <div v-if="endMode === 'count'" class="rec-field">
              <label class="rec-label">Nombre de factures</label>
              <input
                class="rec-input rec-input-num"
                type="number"
                min="1"
                v-model.number="form.max_occurrences"
              />
            </div>

            <p v-if="error" class="rec-error">{{ error }}</p>
          </div>

          <div class="rec-footer">
            <button class="btn btn-secondary" @click="$emit('close')">Cancel·lar</button>
            <button class="btn btn-primary" :disabled="submitting" @click="submit">
              <Repeat :size="16" />
              {{ submitting ? 'Creant…' : 'Crear recurrència' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Repeat, X } from 'lucide-vue-next'

const props = defineProps({
  open: { type: Boolean, default: false },
  sourceInvoice: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'create'])

const endMode = ref('never')
const error = ref('')

function blankForm() {
  return {
    frequency: 'monthly',
    interval: 1,
    payment_term_days: 30,
    start_date: new Date().toISOString().split('T')[0],
    end_date: null,
    max_occurrences: null,
  }
}

const form = reactive(blankForm())

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    Object.assign(form, blankForm())
    endMode.value = 'never'
    error.value = ''
  }
})

function submit() {
  error.value = ''
  if (!form.start_date) {
    error.value = 'Indica la data de la primera emissió.'
    return
  }
  if (!form.interval || form.interval < 1) {
    error.value = 'L\'interval ha de ser com a mínim 1.'
    return
  }
  const payload = {
    source_invoice: props.sourceInvoice?.id,
    frequency: form.frequency,
    interval: form.interval,
    payment_term_days: form.payment_term_days ?? 30,
    start_date: form.start_date,
    end_date: null,
    max_occurrences: null,
  }
  if (endMode.value === 'until') {
    if (!form.end_date) {
      error.value = 'Indica la data de finalització.'
      return
    }
    payload.end_date = form.end_date
  } else if (endMode.value === 'count') {
    if (!form.max_occurrences || form.max_occurrences < 1) {
      error.value = 'Indica quantes factures s\'han de generar.'
      return
    }
    payload.max_occurrences = form.max_occurrences
  }
  emit('create', payload)
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(value)
}
</script>

<style scoped>
.rec-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.rec-panel {
  width: 460px;
  max-width: 94vw;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 3rem);
}

.rec-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.rec-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.rec-sub {
  margin: 0.375rem 0 0;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.rec-icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 0.25rem;
  border-radius: 6px;
}
.rec-icon-btn:hover { background: #f0f2f5; color: var(--text-primary); }

.rec-body {
  padding: 1.25rem 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rec-hint {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  line-height: 1.5;
  background: var(--bg-secondary);
  padding: 0.625rem 0.75rem;
  border-radius: var(--border-radius-sm);
}

.rec-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.rec-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--text-secondary);
}

.rec-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rec-prefix, .rec-suffix {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  white-space: nowrap;
}

.rec-input, .rec-select {
  padding: 0.5rem 0.625rem;
  font-size: var(--font-size-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-family: var(--font-family);
  color: var(--text-primary);
  background: white;
}

.rec-input { width: 100%; }
.rec-input-num { width: 90px; text-align: right; }
.rec-select { flex: 1; }
.rec-select-full { width: 100%; }

.rec-input:focus, .rec-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.rec-error {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--error-color);
}

.rec-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
