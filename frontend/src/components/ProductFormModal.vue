<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <!-- Header -->
          <div class="modal-header">
            <h2 class="modal-title">{{ isEditing ? 'Editar producte' : 'Nou producte' }}</h2>
            <button class="modal-close" @click="$emit('close')">
              <X :size="20" />
            </button>
          </div>

          <!-- Body -->
          <div class="modal-body">
            <!-- ==================== MAIN COLUMN ==================== -->
            <div class="modal-main">

              <!-- ── Informació bàsica ── -->
              <section class="form-section">
                <h3 class="section-title">Informació bàsica</h3>
                <p class="section-desc">Descriu el teu producte. El podràs utilitzar en documents i al teu catàleg.</p>

                <div class="field">
                  <label class="field-label">Nom del producte <span class="required">*</span></label>
                  <input class="input" type="text" placeholder="Afegeix un nom al teu producte" v-model="form.name" />
                </div>

                <div class="field">
                  <label class="field-label">SKU</label>
                  <input class="input" type="text" placeholder="Ex: ERP-011" v-model="form.sku" />
                </div>

                <div class="field">
                  <label class="field-label">Descripció</label>
                  <textarea class="input textarea" rows="3" placeholder="Especifica les característiques de l'article" v-model="form.description"></textarea>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Tipus</label>
                    <select class="select" v-model="form.type">
                      <option value="Product">Producte</option>
                      <option value="Service">Servei</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Estat</label>
                    <select class="select" v-model="form.status">
                      <option value="Active">Actiu</option>
                      <option value="Inactive">Inactiu</option>
                      <option value="Archived">Arxivat</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Unitat</label>
                    <input class="input" type="text" placeholder="u, kg, hora…" v-model="form.unit" />
                  </div>
                </div>
              </section>

              <!-- ── Vendes ── -->
              <section class="form-section">
                <h3 class="section-title">Vendes</h3>
                <p class="section-desc">Indica el subtotal i l'impost aplicable. L'import total es calcularà automàticament.</p>

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
                    <label class="field-label">Impostos</label>
                    <select class="select" v-model="form.tax">
                      <option value="21% IVA">IVA 21%</option>
                      <option value="10% IVA">IVA 10%</option>
                      <option value="4% IVA">IVA 4%</option>
                      <option value="0% IVA">Exempt</option>
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

              <!-- ── Compres ── -->
              <section class="form-section">
                <h3 class="section-title">Compres</h3>
                <p class="section-desc">Estableix el cost mitjà i el preu de compra per als documents de compra.</p>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Cost mitjà</label>
                    <div class="input-suffix">
                      <input class="input" type="number" step="0.01" min="0" placeholder="0" v-model.number="form.cost" />
                      <span class="suffix">€</span>
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">Proveïdor per defecte</label>
                    <select class="select" v-model="form.supplier">
                      <option value="">Sense proveïdor</option>
                      <option v-for="prov in providers" :key="prov.id" :value="prov.name">{{ prov.name }}</option>
                    </select>
                  </div>
                </div>
              </section>

              <!-- ── Inventari ── -->
              <section class="form-section">
                <h3 class="section-title">Inventari</h3>
                <p class="section-desc">Controla les existències, els punts de comanda i la ubicació al magatzem.</p>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Estoc actual</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.stock" />
                  </div>
                  <div class="field">
                    <label class="field-label">Estoc mínim</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.minStock" />
                  </div>
                  <div class="field">
                    <label class="field-label">Punt de comanda</label>
                    <input class="input" type="number" min="0" placeholder="0" v-model.number="form.reorderPoint" />
                  </div>
                </div>

                <div class="field-row">
                  <div class="field">
                    <label class="field-label">Magatzem</label>
                    <select class="select" v-model="form.warehouseId" @change="onWarehouseChange">
                      <option :value="null">Sense magatzem</option>
                      <option v-for="wh in warehouses" :key="wh.id" :value="wh.id">{{ wh.name }}</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">Ubicació</label>
                    <input class="input" type="text" placeholder="Ex: A-12-03" v-model="form.location" />
                  </div>
                </div>

                <div class="field-row">
                  <label class="toggle-field">
                    <input type="checkbox" class="checkbox" v-model="form.lotTracking" />
                    <span>Seguiment per lots</span>
                  </label>
                </div>
              </section>

              <!-- ── Enviament ── -->
              <section class="form-section">
                <h3 class="section-title">Enviament</h3>
                <p class="section-desc">Pes, dimensions i classe d'enviament del producte.</p>

                <div class="field-row field-row-3">
                  <div class="field">
                    <label class="field-label">Pes</label>
                    <input class="input" type="text" placeholder="Ex: 0,18 kg" v-model="form.weight" />
                  </div>
                  <div class="field">
                    <label class="field-label">Dimensions</label>
                    <input class="input" type="text" placeholder="Ex: 30 × 25 × 2 cm" v-model="form.dimensions" />
                  </div>
                  <div class="field">
                    <label class="field-label">Classe d'enviament</label>
                    <select class="select" v-model="form.shippingClass">
                      <option value="Standard">Estàndard</option>
                      <option value="Bulky">Voluminós</option>
                      <option value="Fragile">Fràgil</option>
                    </select>
                  </div>
                </div>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.digital" />
                  <span>Producte digital (sense enviament físic)</span>
                </label>
              </section>

              <!-- ── Notes ── -->
              <section class="form-section">
                <h3 class="section-title">Notes internes</h3>
                <textarea class="input textarea" rows="3" placeholder="Afegeix notes internes sobre aquest producte…" v-model="form.notes"></textarea>
              </section>
            </div>

            <!-- ==================== SIDEBAR COLUMN ==================== -->
            <div class="modal-sidebar">

              <!-- ── Categorització ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Categorització</h4>
                <p class="sidebar-card-desc">Informació addicional per completar la fitxa del producte.</p>

                <div class="field">
                  <label class="field-label">Categoria</label>
                  <select class="select" v-model="form.categoryId">
                    <option :value="null">Selecciona una categoria</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>

                <div class="field">
                  <label class="field-label">Marca</label>
                  <input class="input" type="text" placeholder="Nom de la marca" v-model="form.brand" />
                </div>

                <div class="field">
                  <label class="field-label">Etiquetes</label>
                  <input class="input" type="text" placeholder="Cerca o crea etiquetes" v-model="tagInput" @keydown.enter.prevent="addTag" />
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

              <!-- ── Canals de venda ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Canals de venda</h4>
                <p class="sidebar-card-desc">Selecciona on es publicarà aquest producte.</p>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="channelWeb" />
                  <Globe :size="16" class="toggle-icon" />
                  <span>Web / Botiga en línia</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="channelMarketplace" />
                  <Store :size="16" class="toggle-icon" />
                  <span>Marketplace</span>
                </label>
              </div>

              <!-- ── Imatge del producte ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Imatge del producte</h4>
                <p class="sidebar-card-desc">Puja una imatge del teu producte. La podràs utilitzar en documents i al teu catàleg.</p>

                <input
                  ref="fileInput"
                  type="file"
                  accept="image/jpeg,image/jpg,image/png"
                  class="file-input-hidden"
                  @change="onFileChange"
                />

                <div v-if="form.imagePreview" class="image-preview">
                  <img :src="form.imagePreview" alt="Vista prèvia" />
                  <button class="image-remove" type="button" @click="removeImage">
                    <X :size="14" />
                  </button>
                </div>

                <div
                  v-else
                  class="image-upload-area"
                  :class="{ 'is-dragging': isDragging }"
                  @click="fileInput?.click()"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @drop.prevent="onDrop"
                >
                  <Upload :size="28" class="upload-icon" />
                  <span class="upload-text">Selecciona o arrossega aquí els teus fitxers</span>
                  <span class="upload-hint">Fins a 30 MB i 7680 × 4320 píxels<br>(JPEG, JPG, PNG)</span>
                </div>
              </div>

              <!-- ── Opcions ── -->
              <div class="sidebar-card">
                <h4 class="sidebar-card-title">Opcions</h4>

                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.sellable" />
                  <span>Es pot vendre</span>
                </label>
                <label class="toggle-field">
                  <input type="checkbox" class="checkbox" v-model="form.purchasable" />
                  <span>Es pot comprar</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="$emit('close')">Descartar</button>
            <button class="btn btn-primary" @click="handleSave">
              <Check :size="18" />
              <span>Desar</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted, nextTick } from 'vue'
import { X, Upload, Globe, Store, Check } from 'lucide-vue-next'
import Swal from 'sweetalert2'
import productsApi from '@/services/products'
import coreApi from '@/services/core'
import providersApi from '@/services/providers'

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
    unit: 'u',
    category: '',
    categoryId: null,
    brand: '',
    tags: [],
    price: null,
    priceExclTax: null,
    tax: '21% IVA',
    taxRateId: null,
    cost: null,
    supplier: '',
    stock: null,
    minStock: null,
    reorderPoint: null,
    warehouseId: null,
    location: '',
    lotTracking: false,
    weight: '',
    dimensions: '',
    shippingClass: 'Standard',
    digital: false,
    notes: '',
    sellable: true,
    purchasable: true,
    imageFile: null,
    imagePreview: ''
  }
}

const form = reactive(blankForm())
const tagInput = ref('')

/* ── Càlcul automàtic del total (PVP) a partir del subtotal i l'IVA ── */
const round2 = (n) => Math.round((Number(n) + Number.EPSILON) * 100) / 100

const taxRate = computed(() => {
  const m = String(form.tax || '').match(/(\d+(?:[.,]\d+)?)/)
  return m ? parseFloat(m[1].replace(',', '.')) / 100 : 0
})

// Evita recalcular mentre es carrega un producte existent al formulari
let suppressPriceSync = false

watch(
  () => [form.priceExclTax, form.tax],
  () => {
    if (suppressPriceSync) return
    if (form.priceExclTax === null || form.priceExclTax === '' || isNaN(form.priceExclTax)) return
    form.price = round2(Number(form.priceExclTax) * (1 + taxRate.value))
  }
)

const channelWeb = ref(false)
const channelMarketplace = ref(false)
const fileInput = ref(null)
const isDragging = ref(false)
const categories = ref([])
const warehouses = ref([])
const providers = ref([])

onMounted(async () => {
  try {
    const data = await productsApi.getCategories()
    categories.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    categories.value = []
  }
  try {
    const data = await coreApi.warehouses.getAll()
    warehouses.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    warehouses.value = []
  }
  try {
    const data = await providersApi.getAll()
    providers.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    providers.value = []
  }
})

/* ── Image upload ── */
function setImage(file) {
  if (!file) return
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!validTypes.includes(file.type)) {
    Swal.fire({ icon: 'warning', title: 'Format no vàlid', text: 'Només s\'admeten fitxers JPEG, JPG o PNG.', confirmButtonColor: '#667eea', target: document.body, heightAuto: false })
    return
  }
  if (file.size > 30 * 1024 * 1024) {
    Swal.fire({ icon: 'warning', title: 'Fitxer massa gran', text: 'La imatge no pot superar els 30 MB.', confirmButtonColor: '#667eea', target: document.body, heightAuto: false })
    return
  }
  form.imageFile = file
  form.imagePreview = URL.createObjectURL(file)
}

function onFileChange(e) {
  setImage(e.target.files?.[0])
}

function onDrop(e) {
  isDragging.value = false
  setImage(e.dataTransfer?.files?.[0])
}

function removeImage() {
  form.imageFile = null
  form.imagePreview = ''
  if (fileInput.value) fileInput.value.value = ''
}

/* ── Populate form when editing ── */
watch(() => props.open, (isOpen) => {
  if (isOpen && props.product) {
    const p = props.product
    suppressPriceSync = true
    Object.assign(form, {
      name: p.name,
      sku: p.sku,
      description: p.detail?.description || '',
      type: p.type,
      status: p.status,
      unit: p.detail?.unit || 'u',
      category: p.category,
      categoryId: p.categoryId || null,
      brand: p.detail?.brand || '',
      tags: [...(p.detail?.tags || [])],
      price: p.price,
      priceExclTax: p.detail?.priceExclTax || null,
      tax: p.tax,
      taxRateId: p.taxRateId || null,
      cost: p.cost,
      supplier: p.supplier || '',
      stock: p.stock,
      minStock: p.detail?.minStock || null,
      reorderPoint: p.detail?.reorderPoint || null,
      warehouseId: p.detail?.warehouseId || null,
      location: p.detail?.location || '',
      lotTracking: p.detail?.lotTracking || false,
      weight: p.detail?.weight || '',
      dimensions: p.detail?.dimensions || '',
      shippingClass: p.detail?.shippingClass || 'Standard',
      digital: p.detail?.digital || false,
      notes: p.detail?.notes || '',
      sellable: p.detail?.sellable ?? true,
      purchasable: p.detail?.purchasable ?? true,
      imageFile: null,
      imagePreview: p.image || ''
    })
    channelWeb.value = p.channels?.includes('Web') || false
    channelMarketplace.value = p.channels?.includes('Marketplace') || false
  } else if (isOpen) {
    Object.assign(form, blankForm())
    channelWeb.value = false
    channelMarketplace.value = false
    tagInput.value = ''
  }
  // Reactiva el càlcul automàtic un cop el formulari ja s'ha poblat
  nextTick(() => { suppressPriceSync = false })
})

/* ── Warehouse ── */
function onWarehouseChange() {
  const wh = warehouses.value.find(w => w.id === form.warehouseId)
  if (wh?.address) form.location = wh.address
}

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
  if (!form.name.trim()) errors.push('El nom del producte és obligatori')
  if (form.price !== null && form.price < 0) errors.push('El preu no pot ser negatiu')
  if (form.cost !== null && form.cost < 0) errors.push('El cost no pot ser negatiu')

  if (errors.length) {
    Swal.fire({
      icon: 'warning',
      title: 'Falten camps obligatoris',
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

.image-upload-area:hover,
.image-upload-area.is-dragging {
  border-color: var(--primary-color);
  background: var(--bg-hover);
}

.file-input-hidden {
  display: none;
}

.image-preview {
  position: relative;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.image-preview img {
  display: block;
  width: 100%;
  height: 160px;
  object-fit: contain;
  background: var(--bg-secondary);
}

.image-remove {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.image-remove:hover {
  background: rgba(0, 0, 0, 0.75);
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
