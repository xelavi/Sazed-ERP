/**
 * Global auth composable — singleton via module closure.
 *
 * Usage:
 *   import { useAuth } from '@/composables/useAuth'
 *   const { user, isAuthenticated, login, logout } = useAuth()
 */
import { ref, readonly, computed } from 'vue'
import authApi from '@/services/auth'
import { setActiveCompany } from '@/services/api'

// ── Singleton state (shared across all components) ────
const user = ref(null)
const companies = ref([])
const activeCompany = ref(null)
const activeRole = ref(null)
const isLoading = ref(true)
const isAuthenticated = computed(() => !!user.value)
const hasCompany = computed(() => companies.value.length > 0)

let fetchMePromise = null

// ── Helpers ───────────────────────────────────────────
function setSession(data) {
  user.value = data.user
  if (data.companies) {
    companies.value = data.companies
    const def = data.companies.find(c => c.is_default) || data.companies[0]
    if (def) {
      activeCompany.value = def
      activeRole.value = def.role
      setActiveCompany(def.id)
    }
  }
  if (data.company) {
    activeCompany.value = data.company
    activeRole.value = data.role
    setActiveCompany(data.company.id)
  }
}

function clearSession() {
  user.value = null
  companies.value = []
  activeCompany.value = null
  activeRole.value = null
  setActiveCompany(null)
}

// ── Public API ────────────────────────────────────────
export function useAuth() {
  async function login(email, password) {
    const data = await authApi.login(email, password)
    setSession(data)
    // Also fetch full company list
    try {
      const me = await authApi.me()
      companies.value = me.companies
    } catch { /* non-critical */ }
    return data
  }

  async function register(payload) {
    const data = await authApi.register(payload)
    // User is now authenticated but may have no company
    user.value = data.user
    if (data.company) {
      setSession(data)
      try {
        const me = await authApi.me()
        companies.value = me.companies
      } catch { /* non-critical */ }
    }
    return data
  }

  async function logout() {
    try { await authApi.logout() } catch { /* ignore */ }
    clearSession()
  }

  async function fetchMe() {
    if (fetchMePromise) return fetchMePromise

    isLoading.value = true
    fetchMePromise = authApi.me()
      .then(data => {
        user.value = data.user
        companies.value = data.companies || []
        const saved = sessionStorage.getItem('activeCompanyId')
        const def = (saved && data.companies?.find(c => String(c.id) === saved))
          || data.companies?.find(c => c.is_default)
          || data.companies?.[0]
        if (def) {
          activeCompany.value = def
          activeRole.value = def.role
          setActiveCompany(def.id)
        }
      })
      .catch(err => {
        clearSession()
        throw err
      })
      .finally(() => {
        isLoading.value = false
        fetchMePromise = null
      })

    return fetchMePromise
  }

  async function switchCompany(companyId) {
    const data = await authApi.switchCompany(companyId)
    activeCompany.value = { ...data.company, role: data.role, is_default: true }
    activeRole.value = data.role
    setActiveCompany(data.company.id)
    // Update companies list
    companies.value = companies.value.map(c => ({
      ...c,
      is_default: String(c.id) === String(companyId),
    }))
    return data
  }

  async function updateProfile(data) {
    let payload = data
    if (data.avatar instanceof File) {
      payload = new FormData()
      if (data.first_name !== undefined) payload.append('first_name', data.first_name)
      if (data.last_name !== undefined) payload.append('last_name', data.last_name)
      payload.append('avatar', data.avatar)
    }
    const updated = await authApi.updateProfile(payload)
    if (updated) {
      user.value = { ...user.value, ...updated }
    }
    return updated
  }

  async function changePassword(currentPassword, newPassword) {
    return authApi.changePassword(currentPassword, newPassword)
  }

  return {
    // State (reactive, readonly)
    user: readonly(user),
    companies: readonly(companies),
    activeCompany: readonly(activeCompany),
    activeRole: readonly(activeRole),
    isLoading: readonly(isLoading),
    isAuthenticated,
    hasCompany,

    // Methods
    login,
    register,
    logout,
    fetchMe,
    switchCompany,
    updateProfile,
    changePassword,
  }
}
