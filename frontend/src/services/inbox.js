/**
 * Inbox API service — notifications, messages, invitations, user search.
 */
import { get, post, del } from './api'

// DRF returns paginated lists as { count, results: [...] } for viewsets.
// Normalize so callers always get an array.
function asArray(data) {
  if (Array.isArray(data)) return data
  if (data && Array.isArray(data.results)) return data.results
  return []
}

export default {
  // Summary (unread counts)
  async summary() {
    return get('/inbox/summary/')
  },

  // Notifications
  async listNotifications() {
    return asArray(await get('/notifications/'))
  },
  async markNotificationRead(id) {
    return post(`/notifications/${id}/read/`, {})
  },
  async markAllNotificationsRead() {
    return post('/notifications/read-all/', {})
  },

  // Messages
  async listMessages() {
    return asArray(await get('/messages/'))
  },
  async getMessage(id) {
    return get(`/messages/${id}/`)
  },
  async sendMessage({ recipient_id, subject, body, parent = null }) {
    return post('/messages/', { recipient_id, subject, body, parent })
  },
  async markMessageRead(id) {
    return post(`/messages/${id}/read/`, {})
  },
  async markAllMessagesRead() {
    return post('/messages/read-all/', {})
  },

  // Invitations
  async listInvitations() {
    return asArray(await get('/invitations/'))
  },
  async createInvitation({ email, role }) {
    return post('/invitations/', { email, role })
  },
  async acceptInvitation(id) {
    return post(`/invitations/${id}/accept/`, {})
  },
  async rejectInvitation(id) {
    return post(`/invitations/${id}/reject/`, {})
  },

  // User search (autocomplete in active company)
  async searchUsers(q) {
    const qs = q ? `?q=${encodeURIComponent(q)}` : ''
    return asArray(await get(`/users/search/${qs}`))
  },
}
