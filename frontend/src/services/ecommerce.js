/**
 * E-commerce integration API service (PrestaShop).
 *
 * Gestiona la conexión de una empresa con su tienda online:
 * probar credenciales, crear/actualizar y borrar la StoreConnection.
 */
import { get, post, put, del } from './api'

export default {
  /**
   * Devuelve la StoreConnection de una empresa, o null si no tiene.
   * El endpoint lista todas las conexiones administrables; filtramos por company.
   */
  async getConnectionForCompany(companyId) {
    const data = await get('/integrations/store/connections/')
    const list = Array.isArray(data) ? data : (data.results || [])
    return list.find(c => String(c.company) === String(companyId)) || null
  },

  /**
   * Verifica credenciales sin persistir. Devuelve { ok, shop_name, resources }.
   * En caso de fallo, el backend responde 400 y `apiFetch` lanza un Error con
   * `error.data.error` como detalle.
   */
  async testConnection({ platform = 'prestashop', base_url, api_key }) {
    return post('/integrations/store/test-connection/', { platform, base_url, api_key })
  },

  async createConnection(payload) {
    return post('/integrations/store/connections/', payload)
  },

  async updateConnection(id, payload) {
    return put(`/integrations/store/connections/${id}/`, payload)
  },

  async deleteConnection(id) {
    return del(`/integrations/store/connections/${id}/`)
  },
}
