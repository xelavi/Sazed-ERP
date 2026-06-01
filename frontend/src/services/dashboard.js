/**
 * Dashboard API service
 */
import { get } from './api'

export default {
  /**
   * Get dashboard summary (KPIs)
   */
  async getSummary() {
    return get('/dashboard/summary/')
  },

  /**
   * Get wallet data (balance, pending, recent payments)
   */
  async getWallet() {
    return get('/dashboard/wallet/')
  },

  /**
   * Get analytics: 12-month series + breakdowns per metric (real company data)
   */
  async getAnalytics() {
    return get('/dashboard/analytics/')
  },
}
