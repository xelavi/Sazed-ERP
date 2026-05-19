/**
 * Global inbox state — unread counters shared across the app.
 */
import { ref, computed, readonly } from 'vue'
import inboxApi from '@/services/inbox'

const counts = ref({ notifications: 0, messages: 0, invitations: 0, total: 0 })
const isLoading = ref(false)

async function refresh() {
  isLoading.value = true
  try {
    counts.value = await inboxApi.summary()
  } catch {
    // silent — keep last known counts
  } finally {
    isLoading.value = false
  }
}

export function useInbox() {
  return {
    counts: readonly(counts),
    unreadTotal: computed(() => counts.value.total),
    unreadNotifications: computed(() => counts.value.notifications),
    unreadMessages: computed(() => counts.value.messages),
    pendingInvitations: computed(() => counts.value.invitations),
    refresh,
    isLoading: readonly(isLoading),
  }
}
