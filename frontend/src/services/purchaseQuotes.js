/**
 * Purchase Quotes (Presupuestos de compra) API service
 */
import { createResource, post } from './api'

const resource = createResource('/purchases/quote-docs/')

export default {
  ...resource,

  async convertToInvoice(quoteId) {
    return post(`/purchases/quote-docs/${quoteId}/convert-to-invoice/`, {})
  },
}
