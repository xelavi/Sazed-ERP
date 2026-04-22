/**
 * Core/Config API service
 * For tax rates, warehouses, sales channels, tags, etc.
 */
import { createResource, get, post } from './api'

export default {
  /**
   * Tax Rates
   */
  taxRates: {
    async getAll() {
      return get('/tax-rates/')
    },
    async create(data) {
      return post('/tax-rates/', data)
    },
  },

  /**
   * Warehouses
   */
  warehouses: {
    async getAll() {
      return get('/warehouses/')
    },
    async create(data) {
      return post('/warehouses/', data)
    },
  },

  /**
   * Sales Channels
   */
  salesChannels: {
    async getAll() {
      return get('/sales-channels/')
    },
    async create(data) {
      return post('/sales-channels/', data)
    },
  },

  /**
   * Tags
   */
  tags: {
    async getAll() {
      return get('/tags/')
    },
    async create(data) {
      return post('/tags/', data)
    },
  },
}
