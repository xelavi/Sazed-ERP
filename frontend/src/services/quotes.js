/**
 * Sales Quotes (Presupuestos) API service
 */
import { createResource, post } from './api'

const quotesResource = createResource('/invoices/quotes/')

export default {
  ...quotesResource,

  async convertToInvoice(quoteId) {
    return post(`/invoices/quotes/${quoteId}/convert-to-invoice/`, {})
  },
}
