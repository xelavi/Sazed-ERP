// Display labels for product categories. Backend stores the category names in
// English (see backend seed: Clothing, Footwear…); these map them to Catalan for
// the UI only — the stored value is never changed, so filters/badges keep working.
export const CATEGORY_LABELS = {
  Clothing: 'Roba',
  Footwear: 'Calçat',
  Accessories: 'Accessoris',
  Electronics: 'Electrònica',
  'Food & Drink': 'Alimentació i begudes',
  Furniture: 'Mobles',
  Beauty: 'Bellesa',
  Services: 'Serveis',
}

/** Catalan label for a category name; falls back to the original value. */
export function categoryLabel(name) {
  if (!name) return name
  return CATEGORY_LABELS[name] || name
}
