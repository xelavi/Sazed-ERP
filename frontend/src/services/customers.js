/**
 * Customers API service
 */
import { createResource, get, post } from './api'

const customersResource = createResource('/customers/')

export default {
  ...customersResource,

  /**
   * Get customer notes
   */
  async getNotes(customerId) {
    return get(`/customers/${customerId}/notes/`)
  },

  /**
   * Create customer note
   */
  async createNote(customerId, data) {
    return post(`/customers/${customerId}/notes/`, data)
  },

  /**
   * Get customer activities
   */
  async getActivities(customerId) {
    return get(`/customers/${customerId}/activities/`)
  },

  /**
   * Create customer activity
   */
  async createActivity(customerId, data) {
    return post(`/customers/${customerId}/activities/`, data)
  },

  /**
   * Get customer quotes
   */
  async getQuotes(customerId) {
    return get(`/customers/${customerId}/quotes/`)
  },

  /**
   * Create customer quote
   */
  async createQuote(customerId, data) {
    return post(`/customers/${customerId}/quotes/`, data)
  },

  /**
   * Get customer invoices
   */
  async getInvoices(customerId) {
    return get(`/customers/${customerId}/invoices/`)
  },

  /**
   * Export customers to CSV
   */
  async export(filters = {}) {
    return get('/customers/export/', filters)
  },

  /**
   * Search customers
   */
  async search(query, filters = {}) {
    return get('/customers/', { search: query, ...filters })
  },
}
