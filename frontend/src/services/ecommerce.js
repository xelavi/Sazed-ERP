/**
 * E-commerce integration API service (PrestaShop).
 *
 * Gestiona la connexió d'una empresa amb la seva botiga online:
 * probar credencials, crear/actualitzar i esborrar la StoreConnection,
 * i llançar una sincronització completa ERP → PrestaShop.
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

  /**
   * Sincronització completa ERP → PrestaShop:
   * 1. Esborra productes orfes de la botiga.
   * 2. Puja tots els productes de la Company (amb imatge i estoc).
   * 3. Puja tots els clients de la Company.
   *
   * Retorna { purged, products_ok, products_err, customers_ok, customers_err }.
   * Si `companyId` no s'especifica el backend utilitza la primera empresa
   * de la qual l'usuari és administrador.
   */
  async fullSync(companyId = null) {
    const body = companyId ? { company_id: companyId } : {}
    return post('/integrations/store/full-sync/', body)
  },
}

