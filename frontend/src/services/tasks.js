/**
 * Tasks API service
 */
import { createResource, get } from './api'

const tasksResource = createResource('/tasks/')

export default {
  ...tasksResource,

  /**
   * Get upcoming tasks
   */
  async getUpcoming() {
    return get('/tasks/', { upcoming: true })
  },

  /**
   * Get overdue tasks
   */
  async getOverdue() {
    return get('/tasks/', { overdue: true })
  },

  /**
   * Get completed tasks
   */
  async getCompleted() {
    return get('/tasks/', { completed: true })
  },

  /**
   * Get tasks by status
   */
  async getByStatus(status) {
    return get('/tasks/', { status })
  },
}
