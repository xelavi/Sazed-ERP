/**
 * Data mappers between backend (snake_case) and frontend (camelCase) formats.
 */

// ── Helpers ───────────────────────────────────────────

/** Parse DRF validation errors into a single user-friendly string */
export function parseDrfErrors(data) {
  if (!data || typeof data !== 'object') return null
  if (data.detail) return data.detail
  const msgs = []
  for (const [field, errors] of Object.entries(data)) {
    const list = Array.isArray(errors) ? errors.join(', ') : errors
    msgs.push(`${field}: ${list}`)
  }
  return msgs.length ? msgs.join(' | ') : null
}

// ── Products ──────────────────────────────────────────

/** Map backend product list item → frontend table row */
export function mapProductFromApi(p) {
  return {
    id: p.id,
    sku: p.sku,
    name: p.name,
    status: p.status,
    type: p.product_type,
    category: p.category || '—',
    stock: p.stock,
    reserved: p.reserved,
    price: parseFloat(p.price) || null,
    priceFrom: p.price_from ? parseFloat(p.price_from) : null,
    hasVariants: p.has_variants,
    variantsCount: p.variants_count,
    cost: p.cost ? parseFloat(p.cost) : null,
    tax: p.tax || '—',
    supplier: p.supplier || null,
    channels: p.channels || [],
    updatedAt: p.updated_at,
    image: p.image,
    margin: p.margin ? parseFloat(p.margin) : null,
  }
}

/** Map backend product detail → frontend detail object */
export function mapProductDetailFromApi(p) {
  const base = mapProductFromApi(p)
  return {
    ...base,
    category: p.category?.name || p.category || '—',
    detail: {
      description: p.description || '',
      tags: (p.tags || []).map(t => t.name || t),
      unit: p.unit || 'ud',
      sellable: p.sellable,
      purchasable: p.purchasable,
      brand: p.brand || '',
      gallery: (p.gallery || []).map(img => img.image || img),
      priceExclTax: p.price_excl_tax ? parseFloat(p.price_excl_tax) : null,
      currency: p.currency || 'EUR',
      priceLists: (p.price_lists || []).map(pl => ({
        name: pl.name,
        price: parseFloat(pl.price),
        from: pl.valid_from,
        to: pl.valid_to,
      })),
      minStock: p.min_stock,
      reorderPoint: p.reorder_point,
      warehouse: p.warehouse?.name || p.warehouse || '—',
      location: p.location || '',
      lotTracking: p.lot_tracking || false,
      stockMovements: (p.stock_movements || []).map(sm => ({
        date: sm.created_at,
        type: sm.movement_type,
        document: sm.document_ref,
        qty: sm.quantity,
        user: sm.user || 'System',
      })),
      attributes: (p.attributes || []).map(a => ({
        name: a.name,
        values: (a.values || []).map(v => v.value || v),
      })),
      variants: (p.variants || []).map(v => ({
        name: v.name,
        sku: v.sku,
        price: parseFloat(v.price),
        stock: v.stock,
        ean: v.ean,
      })),
      suppliers: (p.suppliers || []).map(s => ({
        name: s.supplier_name || '',
        sku: s.supplier_sku,
        price: parseFloat(s.purchase_price),
        leadTime: s.lead_time ? `${s.lead_time} days` : '',
        minOrder: s.min_order,
        primary: s.is_primary,
      })),
      recentSales: (p.recent_sales || []).map(s => ({
        document: s.document,
        invoiceId: s.invoice_id,
        customer: s.customer,
        date: s.date,
        qty: parseFloat(s.qty) || 0,
        unitPrice: parseFloat(s.unit_price) || 0,
        total: parseFloat(s.total) || 0,
        status: s.status,
      })),
      returns: [],
      relatedProducts: [],
      weight: p.weight || '',
      dimensions: p.dimensions || '',
      shippingClass: p.shipping_class || 'Standard',
      digital: p.digital || false,
      attachments: (p.attachments || []).map(a => ({
        name: a.file_name, size: a.file_size,
      })),
      notes: p.notes || '',
      createdBy: p.created_by || '',
      createdAt: p.created_at,
      modifiedBy: p.modified_by || '',
    },
  }
}

/** Map frontend form data → backend write format */
export function mapProductToApi(formData) {
  const sku = formData.sku?.trim()
    || `PROD-${Date.now().toString(36).toUpperCase()}`

  // category: accept integer FK ID, discard string names
  const catRaw = formData.categoryId || formData.category
  const category = Number.isFinite(Number(catRaw)) && catRaw !== '' ? Number(catRaw) : null

  return {
    name: formData.name,
    sku,
    description: formData.description || '',
    product_type: formData.type || 'Product',
    status: formData.status || 'Active',
    unit: formData.unit || 'ud',
    category,
    brand: formData.brand || '',
    price: formData.price || null,
    price_excl_tax: formData.priceExclTax || null,
    cost: formData.cost || null,
    tax_rate: formData.taxRateId || null,
    currency: formData.currency || 'EUR',
    stock: formData.stock ?? null,
    min_stock: formData.minStock ?? null,
    reorder_point: formData.reorderPoint ?? null,
    location: formData.location || '',
    lot_tracking: formData.lotTracking || false,
    weight: formData.weight || '',
    dimensions: formData.dimensions || '',
    shipping_class: formData.shippingClass || 'Standard',
    digital: formData.digital || false,
    sellable: formData.sellable ?? true,
    purchasable: formData.purchasable ?? true,
    notes: formData.notes || '',
  }
}

// ── Customers ─────────────────────────────────────────

/** Map backend customer list item → frontend table row */
export function mapCustomerFromApi(c) {
  return {
    id: c.id,
    name: c.name,
    type: c.contact_type,
    email: c.email,
    city: c.city || '',
    status: c.status,
    vatId: c.vat_id || null,
    avatarColor: c.avatar_color || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    initials: c.initials || c.name?.substring(0, 2).toUpperCase() || '?',
    linked: c.linked || [],
    isCustomer: c.is_customer,
    isSupplier: c.is_supplier,
    createdAt: c.created_at,
    updatedAt: c.updated_at,
  }
}

/** Map backend customer detail → frontend detail object */
export function mapCustomerDetailFromApi(c) {
  const base = mapCustomerFromApi(c)
  return {
    ...base,
    detail: {
      phone: c.phone || '',
      website: c.website || '',
      address: c.address || '',
      province: c.province || '',
      postalCode: c.postal_code || '',
      country: c.country || 'España',
      legalName: c.legal_name || '',
      paymentMethod: c.payment_method || 'Transferencia 30 días',
      bankAccount: c.bank_account || '',
      internalNotes: c.internal_notes || '',
      tags: (c.tags || []).map(t => t.name || t),
      isCustomer: c.is_customer,
      isSupplier: c.is_supplier,
      totalInvoiced: parseFloat(c.total_invoiced) || 0,
      pendingBalance: parseFloat(c.pending_balance) || 0,
      totalDocuments: c.total_documents || 0,
      notes: (c.notes || []).map(n => ({
        id: n.id,
        date: n.created_at,
        author: n.author,
        content: n.content,
      })),
      quotes: (c.quotes || []).map(q => ({
        id: q.id,
        number: q.number,
        concept: q.concept,
        amount: parseFloat(q.amount),
        date: q.date,
        validDays: q.valid_days,
        notes: q.notes || '',
        status: q.status,
      })),
      invoices: (c.invoices || []).map(inv => ({
        id: inv.id,
        number: inv.number,
        date: inv.date,
        dueDate: inv.due_date,
        amount: parseFloat(inv.amount) || 0,
        balanceDue: parseFloat(inv.balance_due) || 0,
        status: inv.status,
        series: inv.series || '',
      })),
      activities: (c.activities || []).map(a => ({
        id: a.id,
        type: a.activity_type,
        date: a.date,
        subject: a.subject,
        notes: a.notes || '',
      })),
      purchases: [],
    },
  }
}

/** Map frontend form data → backend write format */
export function mapCustomerToApi(formData) {
  return {
    name: formData.name,
    contact_type: formData.type,
    email: formData.email,
    phone: formData.phone || '',
    website: formData.website || '',
    status: formData.status || 'Active',
    vat_id: formData.vatId || '',
    legal_name: formData.legalName || '',
    address: formData.address || '',
    city: formData.city || '',
    province: formData.province || '',
    postal_code: formData.postalCode || '',
    country: formData.country || 'España',
    payment_method: formData.paymentMethod || 'Transferencia 30 días',
    bank_account: formData.bankAccount || '',
    is_customer: formData.isCustomer ?? true,
    is_supplier: formData.isSupplier ?? false,
    avatar_color: formData.avatarColor || '',
    initials: formData.initials || '',
    internal_notes: formData.internalNotes || '',
  }
}

// ── Invoices ──────────────────────────────────────────

/** Map backend invoice list item → frontend table row */
export function mapInvoiceFromApi(inv) {
  return {
    id: inv.id,
    type: inv.invoice_type || 'Standard',
    status: inv.status,
    series: inv.series_prefix || inv.series || '',
    number: inv.number,
    customer: {
      id: inv.customer,
      name: inv.customer_name || '',
      vatId: inv.customer_vat_id || null,
      email: '',
      avatarColor: inv.customer_avatar_color || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      initials: inv.customer_initials || '?',
    },
    issueDate: inv.issue_date,
    dueDate: inv.due_date,
    paymentMethod: inv.payment_method || '',
    currency: inv.currency || 'EUR',
    subtotal: parseFloat(inv.subtotal) || 0,
    totalTax: parseFloat(inv.total_tax) || 0,
    totalAmount: parseFloat(inv.total_amount) || 0,
    paidAmount: parseFloat(inv.paid_amount) || 0,
    balanceDue: parseFloat(inv.balance_due) || 0,
    isOverdue: inv.is_overdue || false,
    // VeriFactu
    tipoFacturaVf: inv.tipo_factura_verifactu || '',
    estadoAeat: inv.estado_aeat || 'Pendiente',
    hashActual: inv.hash_actual || '',
    createdAt: inv.created_at,
  }
}

/** Map backend invoice detail → full frontend object */
export function mapInvoiceDetailFromApi(inv) {
  const customerData = inv.customer_data || {}
  return {
    id: inv.id,
    type: inv.invoice_type || 'Standard',
    status: inv.status,
    series: inv.series_data?.prefix || '',
    seriesId: inv.series_data?.id || null,
    number: inv.number,
    customer: {
      id: customerData.id || inv.customer,
      name: customerData.name || '',
      vatId: customerData.vat_id || null,
      email: customerData.email || '',
      avatarColor: customerData.avatar_color || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      initials: customerData.initials || '?',
    },
    issueDate: inv.issue_date,
    dueDate: inv.due_date,
    paymentMethod: inv.payment_method || '',
    currency: inv.currency || 'EUR',
    lines: (inv.lines || []).map(l => ({
      id: l.id,
      description: l.description,
      quantity: l.quantity,
      unitPrice: parseFloat(l.unit_price),
      discount: l.discount_value ? `${l.discount_value}%` : null,
      tax: (l.taxes || []).map(t => t.tax_name).join(', ') || '—',
      subtotal: parseFloat(l.subtotal),
    })),
    subtotal: parseFloat(inv.subtotal) || 0,
    discountAmount: parseFloat(inv.discount_amount) || 0,
    taxSummary: (inv.tax_summary || []),
    totalTax: parseFloat(inv.total_tax) || 0,
    totalAmount: parseFloat(inv.total_amount) || 0,
    paidAmount: parseFloat(inv.paid_amount) || 0,
    balanceDue: parseFloat(inv.balance_due) || 0,
    payments: (inv.payments || []).map(p => ({
      id: p.id,
      date: p.date,
      amount: parseFloat(p.amount),
      method: p.method,
      reference: p.reference || null,
      notes: p.notes || null,
    })),
    customerNotes: inv.customer_notes || '',
    internalNotes: inv.internal_notes || '',
    lockedAt: inv.locked_at || null,
    // VeriFactu
    tipoFacturaVf: inv.tipo_factura_verifactu || '',
    estadoAeat: inv.estado_aeat || 'Pendiente',
    hashActual: inv.hash_actual || '',
    hashAnterior: inv.hash_anterior || '',
    fechaGeneracion: inv.fecha_generacion_registro || null,
    verifactuCsv: inv.verifactu_csv || '',
    isSealed: !!(inv.hash_actual),
    timeline: (inv.timeline || []).map(t => ({
      type: t.event_type,
      action: t.action,
      actor: t.actor,
      date: t.date,
    })),
  }
}

/** Map frontend invoice form → backend write format */
export function mapInvoiceToApi(formData) {
  // series & customer must be integer FK IDs
  const seriesRaw = formData.seriesId || formData.series
  const series = Number.isFinite(Number(seriesRaw)) && seriesRaw !== '' ? Number(seriesRaw) : null
  const customerRaw = formData.customerId || formData.customer?.id
  const customer = Number.isFinite(Number(customerRaw)) && customerRaw !== '' ? Number(customerRaw) : null

  return {
    invoice_type: formData.type || 'Standard',
    series,
    customer,
    issue_date: formData.issueDate,
    due_date: formData.dueDate,
    payment_method: formData.paymentMethod || 'Transfer 30 days',
    currency: formData.currency || 'EUR',
    customer_notes: formData.customerNotes || '',
    internal_notes: formData.internalNotes || '',
    lines: (formData.lines || []).map(l => ({
      description: l.description,
      quantity: l.quantity,
      unit_price: l.unitPrice,
      discount_type: l.discountType || 'Percent',
      discount_value: l.discountValue || 0,
    })),
  }
}

// ── Providers ────────────────────────────────────────

export function mapProviderFromApi(p) {
  return {
    id: p.id,
    name: p.name,
    type: p.contact_type,
    email: p.email,
    city: p.city || '',
    status: p.status,
    vatId: p.vat_id || null,
    avatarColor: p.avatar_color || 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
    initials: p.initials || p.name?.substring(0, 2).toUpperCase() || '?',
    linked: p.linked || [],
    createdAt: p.created_at,
    updatedAt: p.updated_at,
  }
}

export function mapProviderDetailFromApi(p) {
  const base = mapProviderFromApi(p)
  return {
    ...base,
    detail: {
      phone: p.phone || '',
      website: p.website || '',
      address: p.address || '',
      province: p.province || '',
      postalCode: p.postal_code || '',
      country: p.country || 'España',
      legalName: p.legal_name || '',
      paymentMethod: p.payment_method || 'Transferencia 30 días',
      bankAccount: p.bank_account || '',
      internalNotes: p.internal_notes || '',
      tags: (p.tags || []).map(t => t.name || t),
      totalPurchased: parseFloat(p.total_purchased) || 0,
      pendingBalance: parseFloat(p.pending_balance) || 0,
      totalDocuments: p.total_documents || 0,
      notes: (p.notes || []).map(n => ({
        id: n.id,
        date: n.created_at,
        author: n.author,
        content: n.content,
      })),
      purchaseOrders: (p.purchase_orders || []).map(po => ({
        id: po.id,
        number: po.number,
        concept: po.concept,
        totalAmount: parseFloat(po.total_amount),
        balanceDue: parseFloat(po.balance_due),
        date: po.date,
        notes: po.notes || '',
        status: po.status,
      })),
      activities: (p.activities || []).map(a => ({
        id: a.id,
        type: a.activity_type,
        date: a.date,
        subject: a.subject,
        notes: a.notes || '',
      })),
    },
  }
}

export function mapProviderToApi(formData) {
  return {
    name: formData.name,
    contact_type: formData.type,
    email: formData.email,
    phone: formData.phone || '',
    website: formData.website || '',
    status: formData.status || 'Active',
    vat_id: formData.vatId || '',
    legal_name: formData.legalName || '',
    address: formData.address || '',
    city: formData.city || '',
    province: formData.province || '',
    postal_code: formData.postalCode || '',
    country: formData.country || 'España',
    payment_method: formData.paymentMethod || 'Transferencia 30 días',
    bank_account: formData.bankAccount || '',
    avatar_color: formData.avatarColor || '',
    initials: formData.initials || '',
    internal_notes: formData.internalNotes || '',
  }
}

// ── Purchase Invoices ────────────────────────────────

export function mapPurchaseInvoiceFromApi(inv) {
  return {
    id: inv.id,
    type: inv.invoice_type || 'Standard',
    status: inv.status,
    series: inv.series_prefix || inv.series || '',
    number: inv.number,
    provider: {
      id: inv.provider,
      name: inv.provider_name || '',
      vatId: inv.provider_vat_id || null,
      email: '',
      avatarColor: inv.provider_avatar_color || 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
      initials: inv.provider_initials || '?',
    },
    issueDate: inv.issue_date,
    dueDate: inv.due_date,
    paymentMethod: inv.payment_method || '',
    currency: inv.currency || 'EUR',
    subtotal: parseFloat(inv.subtotal) || 0,
    totalTax: parseFloat(inv.total_tax) || 0,
    totalAmount: parseFloat(inv.total_amount) || 0,
    paidAmount: parseFloat(inv.paid_amount) || 0,
    balanceDue: parseFloat(inv.balance_due) || 0,
    isOverdue: inv.is_overdue || false,
    createdAt: inv.created_at,
  }
}

export function mapPurchaseInvoiceDetailFromApi(inv) {
  const providerData = inv.provider_data || {}
  return {
    id: inv.id,
    type: inv.invoice_type || 'Standard',
    status: inv.status,
    series: inv.series_data?.prefix || '',
    seriesId: inv.series_data?.id || null,
    number: inv.number,
    provider: {
      id: providerData.id || inv.provider,
      name: providerData.name || '',
      vatId: providerData.vat_id || null,
      email: providerData.email || '',
      avatarColor: providerData.avatar_color || 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
      initials: providerData.initials || '?',
    },
    issueDate: inv.issue_date,
    dueDate: inv.due_date,
    paymentMethod: inv.payment_method || '',
    currency: inv.currency || 'EUR',
    lines: (inv.lines || []).map(l => ({
      id: l.id,
      description: l.description,
      quantity: l.quantity,
      unitPrice: parseFloat(l.unit_price),
      discount: l.discount_value ? `${l.discount_value}%` : null,
      tax: (l.taxes || []).map(t => t.tax_name).join(', ') || '—',
      subtotal: parseFloat(l.subtotal),
    })),
    subtotal: parseFloat(inv.subtotal) || 0,
    discountAmount: parseFloat(inv.discount_amount) || 0,
    taxSummary: (inv.tax_summary || []),
    totalTax: parseFloat(inv.total_tax) || 0,
    totalAmount: parseFloat(inv.total_amount) || 0,
    paidAmount: parseFloat(inv.paid_amount) || 0,
    balanceDue: parseFloat(inv.balance_due) || 0,
    payments: (inv.payments || []).map(p => ({
      id: p.id,
      date: p.date,
      amount: parseFloat(p.amount),
      method: p.method,
      reference: p.reference || null,
      notes: p.notes || null,
    })),
    providerNotes: inv.provider_notes || '',
    internalNotes: inv.internal_notes || '',
    lockedAt: inv.locked_at || null,
    timeline: (inv.timeline || []).map(t => ({
      type: t.event_type,
      action: t.action,
      actor: t.actor,
      date: t.date,
    })),
  }
}

export function mapPurchaseInvoiceToApi(formData) {
  const seriesRaw = formData.seriesId || formData.series
  const series = Number.isFinite(Number(seriesRaw)) && seriesRaw !== '' ? Number(seriesRaw) : null
  const providerRaw = formData.providerId || formData.provider?.id
  const provider = Number.isFinite(Number(providerRaw)) && providerRaw !== '' ? Number(providerRaw) : null

  return {
    invoice_type: formData.type || 'Standard',
    series,
    provider,
    issue_date: formData.issueDate,
    due_date: formData.dueDate,
    payment_method: formData.paymentMethod || 'Transfer 30 days',
    currency: formData.currency || 'EUR',
    provider_notes: formData.providerNotes || '',
    internal_notes: formData.internalNotes || '',
    lines: (formData.lines || []).map(l => ({
      description: l.description,
      quantity: l.quantity,
      unit_price: l.unitPrice,
      discount_type: l.discountType || 'Percent',
      discount_value: l.discountValue || 0,
    })),
  }
}
