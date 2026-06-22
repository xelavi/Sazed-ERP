/**
 * Products API service
 */
import { createResource, get, post, getBlob } from './api'

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
   * Export products to XLSX (returns Blob)
   */
  async export(filters = {}) {
    return getBlob('/products/export/', filters)
  },

  /**
   * Get all categories
   */
  async getCategories() {
    return get('/products/categories/')
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
