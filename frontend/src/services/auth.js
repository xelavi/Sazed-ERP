/**
 * Auth API service
 */
import { get, post, patch, apiFetch } from './api'

export default {
  async login(email, password) {
    return post('/auth/login/', { email, password })
  },

  async register(data) {
    return post('/auth/register/', data)
  },

  async logout() {
    return post('/auth/logout/', {})
  },

  async me() {
    return get('/auth/me/')
  },

  async updateProfile(data) {
    if (data instanceof FormData) {
      return apiFetch('/auth/profile/', {
        method: 'PATCH',
        body: data,
      })
    }
    return patch('/auth/profile/', data)
  },

  async changePassword(currentPassword, newPassword) {
    return post('/auth/change-password/', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  async switchCompany(companyId) {
    return post('/companies/switch/', { company_id: companyId })
  },

  async getCompany(id) {
    return get(`/companies/${id}/`)
  },

  async updateCompany(id, data) {
    if (data instanceof FormData) {
      return apiFetch(`/companies/${id}/`, {
        method: 'PATCH',
        body: data,
      })
    }
    return patch(`/companies/${id}/`, data)
  },

  async createCompany(data) {
    return post('/companies/', data)
  },

  async getMembers(companyId) {
    return get(`/companies/${companyId}/members/`)
  },

  async inviteMember(companyId, email, role) {
    return post(`/companies/${companyId}/members/`, { email, role })
  },
}
