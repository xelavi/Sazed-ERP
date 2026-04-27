import { createResource, get, post } from './api'

const providersResource = createResource('/providers/')

export default {
  ...providersResource,

  async getNotes(providerId) {
    return get(`/providers/${providerId}/notes/`)
  },

  async createNote(providerId, data) {
    return post(`/providers/${providerId}/notes/`, data)
  },

  async getActivities(providerId) {
    return get(`/providers/${providerId}/activities/`)
  },

  async createActivity(providerId, data) {
    return post(`/providers/${providerId}/activities/`, data)
  },

  async getPurchaseOrders(providerId) {
    return get(`/providers/${providerId}/purchase-orders/`)
  },

  async createPurchaseOrder(providerId, data) {
    return post(`/providers/${providerId}/purchase-orders/`, data)
  },

  async search(query, filters = {}) {
    return get('/providers/', { search: query, ...filters })
  },
}
