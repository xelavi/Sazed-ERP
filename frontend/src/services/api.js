/**
 * Base API service for connecting to Django backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// ── Active company (X-Company header) ─────────────────
let activeCompanyId = null

export function setActiveCompany(companyId) {
  activeCompanyId = companyId
  if (companyId) {
    sessionStorage.setItem('activeCompanyId', String(companyId))
  } else {
    sessionStorage.removeItem('activeCompanyId')
  }
}

export function getActiveCompanyId() {
  return activeCompanyId || sessionStorage.getItem('activeCompanyId')
}

// ── CSRF token reader ─────────────────────────────────
function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : null
}

/**
 * Generic fetch wrapper with error handling
 * @param {string} endpoint - API endpoint (e.g., '/products/')
 * @param {object} options - fetch options
 * @returns {Promise<any>}
 */
export async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  const isFormData = options.body instanceof FormData
  const headers = { ...options.headers }

  // Only set Content-Type for non-FormData (browser sets multipart boundary)
  if (!isFormData && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  // Add X-Company header for data endpoints
  const exemptPaths = ['/auth/', '/companies/']
  const companyId = getActiveCompanyId()
  if (companyId && !exemptPaths.some(p => endpoint.startsWith(p))) {
    headers['X-Company'] = companyId
  }

  // Add CSRF token for mutating methods
  const method = (options.method || 'GET').toUpperCase()
  if (method !== 'GET' && method !== 'HEAD') {
    const csrf = getCsrfToken()
    if (csrf) {
      headers['X-CSRFToken'] = csrf
    }
  }

  const config = {
    credentials: 'include',
    ...options,
    headers,
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const error = new Error(errorData.detail || errorData.message || `Error ${response.status}: ${response.statusText}`)
      error.status = response.status
      error.data = errorData
      throw error
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null
    }

    return await response.json()
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error)
    throw error
  }
}

/**
 * GET request — returns parsed JSON
 */
export async function get(endpoint, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${endpoint}?${queryString}` : endpoint
  return apiFetch(url, { method: 'GET' })
}

/**
 * GET request — returns a raw Blob (for file downloads: PDF, ZIP, etc.)
 */
export async function getBlob(endpoint, params = {}) {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  const queryString = new URLSearchParams(params).toString()
  const fullEndpoint = queryString ? `${endpoint}?${queryString}` : endpoint
  const url = `${API_BASE_URL}${fullEndpoint}`

  const headers = {}
  const companyId = getActiveCompanyId()
  if (companyId) headers['X-Company'] = companyId

  const response = await fetch(url, { method: 'GET', credentials: 'include', headers })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    const error = new Error(errorData.detail || errorData.error || `Error ${response.status}`)
    error.status = response.status
    error.data = errorData
    throw error
  }
  return response.blob()
}

/**
 * POST request
 */
export async function post(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * PUT request
 */
export async function put(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/**
 * PATCH request
 */
export async function patch(endpoint, data) {
  return apiFetch(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/**
 * DELETE request
 */
export async function del(endpoint) {
  return apiFetch(endpoint, { method: 'DELETE' })
}

/**
 * Generic CRUD operations for any resource
 */
export function createResource(resourcePath) {
  return {
    /**
     * Get all items
     */
    async getAll(filters = {}) {
      return get(resourcePath, filters)
    },

    /**
     * Get single item by ID
     */
    async getById(id) {
      return get(`${resourcePath}${id}/`)
    },

    /**
     * Create new item
     */
    async create(data) {
      return post(resourcePath, data)
    },

    /**
     * Update existing item
     */
    async update(id, data) {
      return put(`${resourcePath}${id}/`, data)
    },

    /**
     * Partial update
     */
    async partialUpdate(id, data) {
      return patch(`${resourcePath}${id}/`, data)
    },

    /**
     * Delete item
     */
    async delete(id) {
      return del(`${resourcePath}${id}/`)
    },
  }
}

export default {
  get,
  post,
  put,
  patch,
  del,
  createResource,
}
