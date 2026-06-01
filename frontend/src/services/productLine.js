/**
 * Helpers compartidos para autorellenar líneas de presupuestos/facturas
 * a partir de un producto del catálogo.
 */

/** Extrae el porcentaje de impuesto de un producto (p.ej. "IVA 21%" -> 21). */
export function taxPercentFromProduct(product) {
  if (!product) return null
  const raw = product.tax ?? product.tax_rate_name ?? ''
  const match = String(raw).match(/([\d.]+)\s*%/)
  if (match) return parseFloat(match[1])
  return null
}

/** Devuelve la etiqueta de impuesto usada en facturas ("IVA 21%" | "Exempt"). */
export function lineTaxFromProduct(product, fallback = 'IVA 21%') {
  const pct = taxPercentFromProduct(product)
  if (pct === null) return fallback
  if (pct === 0) return 'Exempt'
  if ([21, 10, 4].includes(pct)) return `IVA ${pct}%`
  return fallback
}

/** Precio base de venta (sin impuestos) de un producto. */
export function salePriceOf(product) {
  if (!product) return 0
  return Number(product.priceExclTax ?? product.price ?? 0) || 0
}

/** Precio de compra (coste medio) de un producto. */
export function costPriceOf(product) {
  if (!product) return 0
  return Number(product.cost ?? product.price ?? 0) || 0
}

/** Precio a usar según el contexto del documento. */
export function priceForMode(product, mode = 'sale') {
  return mode === 'purchase' ? costPriceOf(product) : salePriceOf(product)
}
