import { createResource, get, post, del, patch, getBlob } from './api'

const purchasesResource = createResource('/purchases/')

export default {
  ...purchasesResource,

  async approve(invoiceId) {
    return post(`/purchases/${invoiceId}/approve/`, {})
  },

  // Recurring purchase invoice plans
  async listRecurring() {
    return get('/purchases/recurring/')
  },
  async createRecurring(data) {
    return post('/purchases/recurring/', data)
  },
  async updateRecurring(id, data) {
    return patch(`/purchases/recurring/${id}/`, data)
  },
  async deleteRecurring(id) {
    return del(`/purchases/recurring/${id}/`)
  },
  async runRecurring(id) {
    return post(`/purchases/recurring/${id}/run/`, {})
  },

  async void(invoiceId) {
    return post(`/purchases/${invoiceId}/void/`, {})
  },

  async duplicate(invoiceId) {
    return post(`/purchases/${invoiceId}/duplicate/`, {})
  },

  async rectify(invoiceId) {
    return post(`/purchases/${invoiceId}/rectify/`, {})
  },

  async getPayments(invoiceId) {
    return get(`/purchases/${invoiceId}/payments/`)
  },

  async createPayment(invoiceId, data) {
    return post(`/purchases/${invoiceId}/payments/`, data)
  },

  async bulkApprove(invoiceIds) {
    return post('/purchases/bulk-approve/', { ids: invoiceIds })
  },

  async bulkDelete(invoiceIds) {
    return post('/purchases/bulk-delete/', { ids: invoiceIds })
  },

  async getSeries() {
    return get('/purchases/series/')
  },

  async createSeries(data) {
    return post('/purchases/series/', data)
  },

  async getQuotes(filters = {}) {
    return get('/purchases/quotes/', filters)
  },

  async createQuote(data) {
    return post('/purchases/quotes/', data)
  },

  async search(query, filters = {}) {
    return get('/purchases/', { search: query, ...filters })
  },

  async export(filters = {}) {
    return getBlob('/purchases/export/', filters)
  },
}
