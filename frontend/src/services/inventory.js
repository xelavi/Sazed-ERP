/**
 * Inventory API service
 */
import { get, post } from './api'

export default {
  async getOverview() {
    return get('/inventory/overview/')
  },

  async getWarehouseStock(warehouseId) {
    return get(`/inventory/warehouses/${warehouseId}/stock/`)
  },

  async getAllStock(params = {}) {
    return get('/inventory/stock/', params)
  },

  async getReorderRules() {
    return get('/inventory/reorder-rules/')
  },

  async createReorderRule(data) {
    return post('/inventory/reorder-rules/create/', data)
  },

  async restockProduct(data) {
    return post('/inventory/restock/', data)
  },

  async adjustStock(data) {
    return post('/inventory/adjust/', data)
  },

  async transferStock(data) {
    return post('/inventory/transfer/', data)
  },

  async getMovements(limit = 50) {
    return get('/inventory/movements/', { limit })
  },
}
