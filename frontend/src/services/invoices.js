/**
 * Invoices API service
 */
import { createResource, get, post, getBlob } from './api'

const invoicesResource = createResource('/invoices/')

export default {
  ...invoicesResource,

  /**
   * Approve invoice (Draft → Approved)
   */
  async approve(invoiceId) {
    return post(`/invoices/${invoiceId}/approve/`, {})
  },

  /**
   * Void invoice (Approved → Void)
   */
  async void(invoiceId) {
    return post(`/invoices/${invoiceId}/void/`, {})
  },

  /**
   * Duplicate invoice as draft
   */
  async duplicate(invoiceId) {
    return post(`/invoices/${invoiceId}/duplicate/`, {})
  },

  /**
   * Create credit note (rectificative invoice)
   */
  async rectify(invoiceId) {
    return post(`/invoices/${invoiceId}/rectify/`, {})
  },

  /**
   * Send invoice by email
   */
  async send(invoiceId) {
    return post(`/invoices/${invoiceId}/send/`, {})
  },

  /**
   * Download invoice PDF (returns Blob)
   */
  async downloadPdf(invoiceId) {
    return getBlob(`/invoices/${invoiceId}/pdf/`)
  },

  /**
   * Submit invoice to mock AEAT (VeriFactu)
   */
  async verifactuSubmit(invoiceId) {
    return post(`/invoices/${invoiceId}/verifactu-submit/`, {})
  },

  /**
   * Get VeriFactu XML for invoice
   */
  async getVerifactuXml(invoiceId) {
    return getBlob(`/invoices/${invoiceId}/verifactu-xml/`)
  },

  /**
   * Get invoice payments
   */
  async getPayments(invoiceId) {
    return get(`/invoices/${invoiceId}/payments/`)
  },

  /**
   * Record payment for invoice
   */
  async createPayment(invoiceId, data) {
    return post(`/invoices/${invoiceId}/payments/`, data)
  },

  /**
   * Bulk approve invoices
   */
  async bulkApprove(invoiceIds) {
    return post('/invoices/bulk-approve/', { ids: invoiceIds })
  },

  /**
   * Bulk delete draft invoices
   */
  async bulkDelete(invoiceIds) {
    return post('/invoices/bulk-delete/', { ids: invoiceIds })
  },

  /**
   * Export invoices to CSV
   */
  async export(filters = {}) {
    return get('/invoices/export/', filters)
  },

  /**
   * Get invoice series
   */
  async getSeries() {
    return get('/invoices/series/')
  },

  /**
   * Create invoice series
   */
  async createSeries(data) {
    return post('/invoices/series/', data)
  },

  /**
   * Search invoices
   */
  async search(query, filters = {}) {
    return get('/invoices/', { search: query, ...filters })
  },
}
