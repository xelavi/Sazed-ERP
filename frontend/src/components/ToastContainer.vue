<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          :class="['toast-item', `toast-${t.type}`]"
          role="alert"
        >
          <component :is="iconMap[t.type]" :size="18" class="toast-icon" />
          <span class="toast-msg">{{ t.message }}</span>
          <button class="toast-close" @click="remove(t.id)" aria-label="Cerrar">
            <X :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 12000;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 380px;
  width: 100%;
  pointer-events: none;
}

.toast-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-sm);
  background: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.14);
  border-left: 4px solid;
  pointer-events: auto;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.toast-success { border-left-color: var(--success-color); }
.toast-error   { border-left-color: var(--error-color); }
.toast-warning { border-left-color: var(--warning-color); }
.toast-info    { border-left-color: var(--info-color); }

.toast-success .toast-icon { color: var(--success-color); }
.toast-error   .toast-icon { color: var(--error-color); }
.toast-warning .toast-icon { color: var(--warning-color); }
.toast-info    .toast-icon { color: var(--info-color); }

.toast-msg {
  flex: 1;
}

.toast-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
}

.toast-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* Transitions */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(50px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(50px);
}
</style>
