/**
 * Odoo integration API service.
 *
 * Maneja el polling del provisioning automático tras crear una empresa
 * y el auto-login (SSO) para abrir Odoo en una pestaña nueva apuntando
 * a la BD correcta.
 */
import { get, post } from './api'

export default {
  /**
   * Devuelve el job de provisioning más reciente para la company, o null
   * si nunca se ha encolado.
   *
   * Response shape:
   *   { id, company, status, database_name, attempts, max_attempts,
   *     logs, error_message, created_at, started_at, finished_at }
   *   donde status ∈ {pending, running, done, failed}
   */
  async getProvisioningStatus(companyId) {
    return get('/integrations/odoo/provisioning/', { company_id: companyId })
  },

  /**
   * Polls hasta que el provisioning termine (done|failed) o se agote el timeout.
   *
   * @param {number} companyId
   * @param {object} opts
   * @param {number} [opts.intervalMs=4000] - tiempo entre polls
   * @param {number} [opts.timeoutMs=300000] - timeout total (5 min)
   * @param {(job: object) => void} [opts.onProgress] - callback en cada poll
   * @returns {Promise<object>} - el job final
   */
  async waitForProvisioning(companyId, { intervalMs = 4000, timeoutMs = 300000, onProgress } = {}) {
    const start = Date.now()
    while (Date.now() - start < timeoutMs) {
      const job = await this.getProvisioningStatus(companyId)
      if (onProgress) onProgress(job)
      if (!job) {
        // Aún no se ha encolado o ya no existe: damos 1 poll más.
        await new Promise(r => setTimeout(r, intervalMs))
        continue
      }
      if (job.status === 'done' || job.status === 'failed') return job
      await new Promise(r => setTimeout(r, intervalMs))
    }
    throw new Error('Timeout esperando al provisioning de Odoo')
  },

  /**
   * Abre Odoo en una pestaña nueva con auto-login.
   *
   * El backend autentica contra `/web/session/authenticate` y devuelve la
   * cookie `session_id` EN SU PROPIA RESPUESTA (Set-Cookie de servidor, que
   * sí sobrescribe la cookie HttpOnly que deja Odoo). Como ERP y Odoo
   * comparten host `localhost`, la cookie viaja también a :8069 y al
   * navegar a /web Odoo reconoce la sesión sin pedir login.
   *
   * Nota: funciona porque todo es `localhost`. En producción con dominios
   * distintos haría falta un reverse proxy / subdominio compartido.
   */
  async openOdooForCompany(companyId) {
    const { base_url, redirect } = await post(
      '/integrations/odoo/sso-login/',
      { company_id: companyId },
    )

    const target = `${base_url}${redirect || '/web'}`
    const win = window.open(target, '_blank')
    if (!win) {
      throw new Error('Tu navegador bloqueó la pestaña. Permite popups en este sitio.')
    }
  },
}
