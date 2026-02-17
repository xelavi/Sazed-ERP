<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ isEditing ? 'Editar producto' : 'Nuevo producto' }}</h2>
            <button class="modal-close" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- ==================== MAIN COLUMN ==================== -->
            <div class="modal-main">

              <!-- ── Información básica ── -->
              <section class="form-section">
                <h3 class="section-title">Información básica</h3>
                <p class="section-desc">Describe tu producto. Podrás utilizarlo en documentos y en tu catálogo.</p>

                <div class="field">
                  <label class="field-label">Nombre del producto <span class="required">*</span></label>
                  <input class="input" type="text" placeholder="Añade un nombre a tu producto" v-model="form.name" />
                </div>

                <div class="field">
                  <label class="field-label">SKU</label>
                  <input class="input" type="text" placeholder="Ej: ERP-011" v-model="form.sku" />
                </div>

                <div class="field">
                  <label class="field-label">Descripción</label>
                  <textarea class="input textarea" rows="3" placeholder="Especifica las características del artículo" v-model="form.description"></textarea>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Tipo</label>
                    <select class="select" v-model="form.type">
                      <option value="Product">Producto</option>
                      <option value="Service">Servicio</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Estado</label>
                    <select class="select" v-model="form.status">
                      <option value="Active">Activo</option>
                      <option value="Inactive">Inactivo</option>
                      <option value="Archived">Archivado</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Unidad</label>
                    <input class="input" type="text" placeholder="ud, kg, hora…" v-model="form.unit" />
                  </div>
                </div>
              </section>

              <!-- ── Ventas ── -->
              <section class="form-section">
                <h3 class="section-title">Ventas</h3>
                <p class="section-desc">Indica el subtotal y el impuesto aplicable. El importe total se calculará de forma automática.</p>

                <div class="subsection-label">TARIFA PRINCIPAL</div>
                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Subtotal</label>
                    <div class="input-suffix">
                      <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="form.priceExclTax" />
                      <span class="suffix">€</span>
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Impuestos</label>
                    <select class="select" v-model="form.tax">
                      <option value="21% IVA">IVA 21%</option>
                      <option value="10% IVA">IVA 10%</option>
                      <option value="4% IVA">IVA 4%</option>
                      <option value="0% IVA">Exento</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Total (PVP)</label>
                    <div class="input-suffix">
                      <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="form.price" />
                      <span class="suffix">€</span>
                    </div>
                  </div>
                </div>
              </section>

              <!-- ── Compras ── -->
              <section class="form-section">
                <h3 class="section-title">Compras</h3>
                <p class="section-desc">Establece el coste medio y el precio de compra para documentos de compra.</p>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Coste medio</label>
                    <div class="input-suffix">
                      <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="form.cost" />
                      <span class="suffix">€</span>
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Proveedor por defecto</label>
                    <input class="input" type="text" placeholder="Busca y selecciona proveedores" v-model="form.supplier" />
                  </div>
                </div>
              </section>

              <!-- ── Inventario ── -->
              <section class="form-section">
                <h3 class="section-title">Inventario</h3>
                <p class="section-desc">Controla las existencias, puntos de pedido y ubicación en almacén.</p>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Stock actual</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.stock" />
                  </div>
                  <div class="field">
                    <label class="field-label">Stock mínimo</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.minStock" />
                  </div>
                  <div class="field">
                    <label class="field-label">Punto de pedido</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.reorderPoint" />
                  </div>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Almacén</label>
                    <input class="input" type="text" placeholder="Ej: Warehouse Madrid" v-model="form.warehouse" />
                  </div>
                  <div class="field">
                    <label class="field-label">Ubicación</label>
                    <input class="input" type="text" placeholder="Ej: A-12-03" v-model="form.location" />
                  </div>
                </div>

                <div class="field-row">
                  <label class="toggle-field">
                    <input type="checkbox" class="checkbox" v-model="form.lotTracking" />
                    <span>Seguimiento por lotes</span>
                  </label>
                </div>
              </section>

              <!-- ── Envío ── -->
              <section class="form-section">
                <h3 class="section-title">Envío</h3>
                <p class="section-desc">Peso, dimensiones y clase de envío del producto.</p>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Peso</label>
                    <input class="input" type="text" placeholder="Ej: 0.18 kg" v-model="form.weight" />
                  </div>
                  <div class="field">
                    <label class="field-label">Dimensiones</label>
                    <input class="input" type="text" placeholder="Ej: 30 × 25 × 2 cm" v-model="form.dimensions" />
                  </div>
                  <div class="field">
                    <label class="field-label">Clase de envío</label>
                    <select class="select" v-model="form.shippingClass">
                      <option value="Standard">Standard</option>
                      <option value="Bulky">Bulky</option>
                      <option value="Fragile">Fragile</option>
                    </select>
                  </div>
                </div>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.digital" />
                  <span>Producto digital (sin envío físico)</span>
                </label>
              </section>

              <!-- ── Notas ── -->
              <section class="form-section">
                <h3 class="section-title">Notas internas</h3>
                <textarea class="input textarea" rows="3" placeholder="Añade notas internas sobre este producto…" v-model="form.notes"></textarea>
              </section>
            </div>

            <!-- ==================== SIDEBAR COLUMN ==================== -->
            <div class="modal-sidebar">

              <!-- ── Categorización ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Categorización</h4>
                <p class="sidebar-card-desc">Información adicional para completar la ficha del producto.</p>

                <div class="field">
                  <label class="field-label">Categoría</label>
                  <select class="select" v-model="form.category">
                    <option value="">Selecciona categoría</option>
                    <option value="Clothing">Clothing</option>
                    <option value="Footwear">Footwear</option>
                    <option value="Accessories">Accessories</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Food & Drink">Food & Drink</option>
                    <option value="Furniture">Furniture</option>
                    <option value="Beauty">Beauty</option>
                    <option value="Services">Services</option>
                  </select>
                </div>

                <div class="field">
                  <label class="field-label">Marca</label>
                  <input class="input" type="text" placeholder="Nombre de la marca" v-model="form.brand" />
                </div>

                <div class="field">
                  <label class="field-label">Etiquetas</label>
                  <input class="input" type="text" placeholder="Busca o crea tags" v-model="tagInput" @keydown.enter.prevent="addTag" />
                  <div v-if="form.tags.length" class="tags-list">
                    <span v-for="(tag, i) in form.tags" :key="i" class="tag-chip">
                      {{ tag }}
                      <button class="tag-remove" @click="removeTag(i)">
                        <X :size="12" />
                      </button>
                    </span>
                  </div>
                </div>
              </div>

              <!-- ── Canales de venta ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Canales de venta</h4>
                <p class="sidebar-card-desc">Selecciona dónde se publicará este producto.</p>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="channelWeb" />
                  <Globe :size="16" class="toggle-icon" />
                  <span>Web / Online Store</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="channelMarketplace" />
                  <Store :size="16" class="toggle-icon" />
                  <span>Marketplace</span>
                </label>
              </div>

              <!-- ── Imagen del producto ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Imagen del producto</h4>
                <p class="sidebar-card-desc">Sube una imagen de tu producto. Podrás utilizarla en documentos y en tu catálogo.</p>

                <div class="image-upload-area">
                  <Upload :size="28" class="upload-icon" />
                  <span class="upload-text">Selecciona o arrastra aquí tus archivos</span>
                  <span class="upload-hint">Hasta 30 MB y 7680 × 4320 píxeles<br>(JPEG, JPG, PNG)</span>
                </div>
              </div>

              <!-- ── Opciones ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Opciones</h4>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.sellable" />
                  <span>Se puede vender</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.purchasable" />
                  <span>Se puede comprar</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('close')">Descartar</button>
            <button class="btn btn-primary" @click="handleSave">
              <Check :size="18" />
              <span>Guardar</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { X, Upload, Globe, Store, Check } from 'lucide-vue-next'
import Swal from 'sweetalert2'

const props = defineProps({
  open: { type: Boolean, default: false },
  product: { type: Object, default: null }
})

const emit = defineEmits(['close', 'save'])

const isEditing = computed(() => !!props.product)

/* ── Default blank form ── */
function blankForm() {
  return {
    name: '',
    sku: '',
    description: '',
    type: 'Product',
    status: 'Active',
    unit: 'ud',
    category: '',
    brand: '',
    tags: [],
    price: null,
    priceExclTax: null,
    tax: '21% IVA',
    cost: null,
    supplier: '',
    stock: null,
    minStock: null,
    reorderPoint: null,
    warehouse: '',
    location: '',
    lotTracking: false,
    weight: '',
    dimensions: '',
    shippingClass: 'Standard',
    digital: false,
    notes: '',
    sellable: true,
    purchasable: true
  }
}

const form = reactive(blankForm())
const tagInput = ref('')
const channelWeb = ref(false)
const channelMarketplace = ref(false)

/* ── Populate form when editing ── */
watch(() => props.open, (isOpen) => {
  if (isOpen && props.product) {
    const p = props.product
    Object.assign(form, {
      name: p.name,
      sku: p.sku,
      description: p.detail?.description || '',
      type: p.type,
      status: p.status,
      unit: p.detail?.unit || 'ud',
      category: p.category,
      brand: p.detail?.brand || '',
      tags: [...(p.detail?.tags || [])],
      price: p.price,
      priceExclTax: p.detail?.priceExclTax || null,
      tax: p.tax,
      cost: p.cost,
      supplier: p.supplier || '',
      stock: p.stock,
      minStock: p.detail?.minStock || null,
      reorderPoint: p.detail?.reorderPoint || null,
      warehouse: p.detail?.warehouse || '',
      location: p.detail?.location || '',
      lotTracking: p.detail?.lotTracking || false,
      weight: p.detail?.weight || '',
      dimensions: p.detail?.dimensions || '',
      shippingClass: p.detail?.shippingClass || 'Standard',
      digital: p.detail?.digital || false,
      notes: p.detail?.notes || '',
      sellable: p.detail?.sellable ?? true,
      purchasable: p.detail?.purchasable ?? true
    })
    channelWeb.value = p.channels?.includes('Web') || false
    channelMarketplace.value = p.channels?.includes('Marketplace') || false
  } else if (isOpen) {
    Object.assign(form, blankForm())
    channelWeb.value = false
    channelMarketplace.value = false
    tagInput.value = ''
  }
})

/* ── Tags ── */
function addTag() {
  const val = tagInput.value.trim()
  if (val && !form.tags.includes(val)) {
    form.tags.push(val)
  }
  tagInput.value = ''
}

function removeTag(index) {
  form.tags.splice(index, 1)
}

/* ── Save ── */
function handleSave() {
  const errors = []
  if (!form.name.trim()) errors.push('Product name is required')
  if (form.price !== null && form.price < 0) errors.push('Price cannot be negative')
  if (form.cost !== null && form.cost < 0) errors.push('Cost cannot be negative')

  if (errors.length) {
    Swal.fire({
      icon: 'warning',
      title: 'Required fields missing',
      html: `<ul style="text-align:left;margin:0;padding-left:1.2em">${errors.map(e => `<li>${e}</li>`).join('')}</ul>`,
      confirmButtonText: 'OK',
      confirmButtonColor: '#667eea',
      customClass: { popup: 'swal-erp-popup' },
      backdrop: `rgba(0,0,0,0.15)`,
      target: document.body,
      heightAuto: false
    })
    return
  }

  const channels = []
  if (channelWeb.value) channels.push('Web')
  if (channelMarketplace.value) channels.push('Marketplace')

  emit('save', { ...form, channels })
  emit('close')
}
</script>

<style scoped>
/* ============================
   OVERLAY & CONTAINER
   ============================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 960px;
  max-height: calc(100vh - 4rem);
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px -12px rgba(0, 0, 0, 0.2);
}

/* ============================
   HEADER
   ============================ */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--border-radius-sm);
  border: none;
  background: none;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* ============================
   BODY (scroll area)
   ============================ */
.modal-body {
  display: flex;
  gap: 1.75rem;
  padding: 1.75rem;
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}

.modal-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.modal-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ============================
   FORM SECTIONS
   ============================ */
.form-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
}

.section-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}

.section-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0 0 1.25rem;
}

/* ============================
   FIELDS
   ============================ */
.field {
  margin-bottom: 1rem;
}

.field:last-child {
  margin-bottom: 0;
}

.field-label {
  display: block;
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 0.375rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.required {
  color: var(--error-color);
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.field-row:last-child {
  margin-bottom: 0;
}

.field-row .field {
  margin-bottom: 0;
}

.field-row-3 {
  grid-template-columns: repeat(3, 1fr);
}

.subsection-label {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-tertiary);
  margin-bottom: 0.75rem;
}

/* Input with suffix (€) */
.input-suffix {
  position: relative;
}

.input-suffix .input {
  padding-right: 2.25rem;
}

.suffix {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  pointer-events: none;
}

.textarea {
  resize: vertical;
  min-height: 72px;
  line-height: 1.5;
}

/* Toggle (checkbox + label) */
.toggle-field {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.toggle-field:last-child {
  margin-bottom: 0;
}

.toggle-icon {
  color: var(--text-tertiary);
}

/* ============================
   SIDEBAR CARDS
   ============================ */
.sidebar-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  padding: 1.25rem;
}

.sidebar-card-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.25rem;
}

.sidebar-card-desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin: 0 0 1rem;
}

/* Tags */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--primary-light);
  color: var(--primary-color);
  font-size: var(--font-size-xs);
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.tag-remove {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  padding: 0;
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}

.tag-remove:hover {
  opacity: 1;
}

/* Image upload */
.image-upload-area {
  border: 2px dashed var(--border-color);
  border-radius: var(--border-radius-sm);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  text-align: center;
  cursor: pointer;
  transition: border-color var(--transition-base);
}

.image-upload-area:hover {
  border-color: var(--primary-color);
}

.upload-icon {
  color: var(--text-tertiary);
}

.upload-text {
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  font-weight: 500;
}

.upload-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  line-height: 1.4;
}

/* ============================
   FOOTER
   ============================ */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.75rem;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

/* ============================
   TRANSITION
   ============================ */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: translateY(16px) scale(0.97);
  opacity: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 1rem;
  }

  .modal-body {
    flex-direction: column;
    padding: 1.25rem;
  }

  .modal-sidebar {
    width: 100%;
  }

  .field-row,
  .field-row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
