/**
 * Products API service
 */
import { createResource, get, post } from './api'

const productsResource = createResource('/products/')

export default {
  ...productsResource,

  /**
   * Get product stock movements
   */
  async getStockMovements(productId) {
    return get(`/products/${productId}/stock-movements/`)
  },

  /**
   * Create stock movement
   */
  async createStockMovement(productId, data) {
    return post(`/products/${productId}/stock-movements/`, data)
  },

  /**
   * Export products to CSV
   */
  async export(filters = {}) {
    return get('/products/export/', filters)
  },

  /**
   * Get all categories
   */
  async getCategories() {
    return get('/categories/')
  },

  /**
   * Create category
   */
  async createCategory(data) {
    return post('/categories/', data)
  },

  /**
   * Search products
   */
  async search(query, filters = {}) {
    return get('/products/', { search: query, ...filters })
  },
}
