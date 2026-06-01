/**
 * Shared, cached access to the dashboard analytics payload.
 * The data is fetched once and reused across every widget on the page.
 */
import { ref } from 'vue'
import dashboardApi from '@/services/dashboard'

const analytics = ref(null)
const loading = ref(false)
const error = ref(null)
let inflight = null

export function useDashboardData() {
  async function load(force = false) {
    if (analytics.value && !force) return analytics.value
    if (inflight) return inflight
    loading.value = true
    error.value = null
    inflight = dashboardApi
      .getAnalytics()
      .then((d) => {
        analytics.value = d
        return d
      })
      .catch((e) => {
        error.value = e
        throw e
      })
      .finally(() => {
        loading.value = false
        inflight = null
      })
    return inflight
  }

  return { analytics, loading, error, load }
}
