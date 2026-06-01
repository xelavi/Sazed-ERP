<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="rec-overlay" @click.self="$emit('close')">
        <div class="rec-panel">
          <div class="rec-header">
            <div>
              <h3 class="rec-title">
                <Repeat :size="18" />
                Hacer recurrente
              </h3>
              <p class="rec-sub" v-if="sourceInvoice">
                Plantilla a partir de
                <strong>{{ sourceInvoice.number || 'borrador' }}</strong>
                · {{ formatCurrency(sourceInvoice.totalAmount) }}
              </p>
            </div>
            <button class="rec-icon-btn" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <div class="rec-body">
            <p class="rec-hint">
              Se generará y aprobará automáticamente una factura con estas
              líneas en cada vencimiento. La factura original no se modifica.
            </p>

            <div class="rec-field">
              <label class="rec-label">Frecuencia</label>
              <div class="rec-row">
                <span class="rec-prefix">Cada</span>
                <input
                  class="rec-input rec-input-num"
                  type="number"
                  min="1"
                  v-model.number="form.interval"
                />
                <select class="rec-select" v-model="form.frequency">
                  <option value="weekly">semana(s)</option>
                  <option value="monthly">mes(es)</option>
                  <option value="quarterly">trimestre(s)</option>
                  <option value="semiannual">semestre(s)</option>
                  <option value="yearly">año(s)</option>
                </select>
              </div>
            </div>

            <div class="rec-field">
              <label class="rec-label">Primera emisión</label>
              <input class="rec-input" type="date" v-model="form.start_date" />
            </div>

            <div class="rec-field">
              <label class="rec-label">Vencimiento de pago</label>
              <div class="rec-row">
                <input
                  class="rec-input rec-input-num"
                  type="number"
                  min="0"
                  v-model.number="form.payment_term_days"
                />
                <span class="rec-suffix">días tras la emisión</span>
              </div>
            </div>

            <div class="rec-field">
              <label class="rec-label">Finalización</label>
              <select class="rec-select rec-select-full" v-model="endMode">
                <option value="never">Sin fin (hasta pausarla)</option>
                <option value="until">En una fecha concreta</option>
                <option value="count">Tras un nº de facturas</option>
              </select>
            </div>

            <div v-if="endMode === 'until'" class="rec-field">
              <label class="rec-label">Hasta el</label>
              <input class="rec-input" type="date" v-model="form.end_date" />
            </div>

            <div v-if="endMode === 'count'" class="rec-field">
              <label class="rec-label">Número de facturas</label>
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
            <button class="btn btn-secondary" @click="$emit('close')">Cancelar</button>
            <button class="btn btn-primary" :disabled="submitting" @click="submit">
              <Repeat :size="16" />
              {{ submitting ? 'Creando…' : 'Crear recurrencia' }}
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
    error.value = 'Indica la fecha de la primera emisión.'
    return
  }
  if (!form.interval || form.interval < 1) {
    error.value = 'El intervalo debe ser al menos 1.'
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
      error.value = 'Indica la fecha de finalización.'
      return
    }
    payload.end_date = form.end_date
  } else if (endMode.value === 'count') {
    if (!form.max_occurrences || form.max_occurrences < 1) {
      error.value = 'Indica cuántas facturas generar.'
      return
    }
    payload.max_occurrences = form.max_occurrences
  }
  emit('create', payload)
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(value)
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
