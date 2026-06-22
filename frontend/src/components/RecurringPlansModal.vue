<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="open" class="rp-overlay" @click.self="$emit('close')">
        <div class="rp-panel">
          <div class="rp-header">
            <h3 class="rp-title">
              <Repeat :size="18" />
              Factures recurrents
            </h3>
            <button class="rp-icon-btn" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <div class="rp-body">
            <p v-if="!plans.length" class="rp-empty">
              No hi ha plans de facturació recurrent.
              Crea'n un des del menú de qualsevol factura.
            </p>

            <div v-for="plan in plans" :key="plan.id" class="rp-card">
              <div class="rp-card-main">
                <div class="rp-card-top">
                  <span class="rp-name">{{ plan[nameField] || '—' }}</span>
                  <span :class="['rp-badge', plan.active ? 'rp-badge-on' : 'rp-badge-off']">
                    {{ plan.active ? 'Activa' : 'Pausada' }}
                  </span>
                </div>
                <div class="rp-meta">
                  <span>{{ frequencyText(plan) }}</span>
                  <span class="rp-dot">·</span>
                  <span>{{ formatCurrency(plan.template_total) }}</span>
                </div>
                <div class="rp-meta rp-meta-sub">
                  <span v-if="plan.active">Pròxima: <strong>{{ formatDate(plan.next_run) }}</strong></span>
                  <span v-else>Finalitzada</span>
                  <span class="rp-dot">·</span>
                  <span>{{ plan.occurrences }} emesa(es)<template v-if="plan.max_occurrences">/{{ plan.max_occurrences }}</template></span>
                  <template v-if="plan.end_date">
                    <span class="rp-dot">·</span>
                    <span>fins {{ formatDate(plan.end_date) }}</span>
                  </template>
                </div>
              </div>
              <div class="rp-card-actions">
                <button
                  v-if="plan.active"
                  class="rp-act"
                  title="Generar ara la factura següent"
                  @click="$emit('run', plan)"
                >
                  <Play :size="15" />
                </button>
                <button
                  v-if="plan.active"
                  class="rp-act"
                  title="Pausar"
                  @click="$emit('toggle', plan)"
                >
                  <Pause :size="15" />
                </button>
                <button
                  v-else-if="!plan.is_finished"
                  class="rp-act"
                  title="Reprendre"
                  @click="$emit('toggle', plan)"
                >
                  <Play :size="15" />
                </button>
                <button
                  class="rp-act rp-act-danger"
                  title="Eliminar el pla"
                  @click="$emit('remove', plan)"
                >
                  <Trash2 :size="15" />
                </button>
              </div>
            </div>
          </div>

          <div class="rp-footer">
            <span class="rp-foot-note">
              Les factures es generen automàticament cada dia mitjançant la tasca programada.
            </span>
            <button class="btn btn-secondary" @click="$emit('close')">Tancar</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { Repeat, X, Play, Pause, Trash2 } from 'lucide-vue-next'

defineProps({
  open: { type: Boolean, default: false },
  plans: { type: Array, default: () => [] },
  nameField: { type: String, default: 'customer_name' },
})

defineEmits(['close', 'run', 'toggle', 'remove'])

const FREQ = {
  weekly: 'setmana(es)',
  monthly: 'mes(os)',
  quarterly: 'trimestre(s)',
  semiannual: 'semestre(s)',
  yearly: 'any(s)',
}

function frequencyText(plan) {
  const unit = FREQ[plan.frequency] || plan.frequency_display
  return plan.interval > 1 ? `Cada ${plan.interval} ${unit}` : `Cada ${unit}`
}

function formatCurrency(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR' }).format(value)
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ca-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>

<style scoped>
.rp-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.rp-panel {
  width: 560px;
  max-width: 94vw;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 3rem);
}

.rp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.rp-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.rp-icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 0.25rem;
  border-radius: 6px;
}
.rp-icon-btn:hover { background: #f0f2f5; color: var(--text-primary); }

.rp-body {
  padding: 1rem 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.rp-empty {
  margin: 1.5rem 0;
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  line-height: 1.6;
}

.rp-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 0.75rem 0.875rem;
}

.rp-card-main { min-width: 0; flex: 1; }

.rp-card-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.rp-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.rp-badge {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 0.125rem 0.45rem;
  border-radius: 4px;
}
.rp-badge-on { background: var(--success-light, #e6f7ed); color: var(--success-color, #1a9d54); }
.rp-badge-off { background: #f0f2f5; color: var(--text-tertiary); }

.rp-meta {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
}
.rp-meta-sub { color: var(--text-tertiary); margin-top: 0.15rem; }
.rp-dot { opacity: 0.5; }

.rp-card-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.rp-act {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}
.rp-act:hover { background: var(--bg-hover); color: var(--text-primary); }
.rp-act-danger:hover { background: var(--error-light); color: var(--error-color); border-color: var(--error-color); }

.rp-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.rp-foot-note {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
