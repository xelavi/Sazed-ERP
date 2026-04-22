/**
 * Lightweight toast notification composable.
 * Renders a stack of auto-dismissing messages.
 *
 * Usage:
 *   import { useToast } from '@/composables/useToast'
 *   const toast = useToast()
 *   toast.success('Done!')
 *   toast.error('Oops')
 */
import { ref, readonly } from 'vue'

const toasts = ref([])
let nextId = 1

function add(message, type = 'info', duration = 4000) {
  const id = nextId++
  toasts.value.push({ id, message, type })
  if (duration > 0) {
    setTimeout(() => remove(id), duration)
  }
}

function remove(id) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

export function useToast() {
  return {
    toasts: readonly(toasts),
    success: (msg) => add(msg, 'success'),
    error: (msg) => add(msg, 'error'),
    warning: (msg) => add(msg, 'warning'),
    info: (msg) => add(msg, 'info'),
    remove,
  }
}
