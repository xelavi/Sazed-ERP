<template>
  <div class="product-ac" ref="root">
    <input
      class="input input-sm product-ac-input"
      type="text"
      :placeholder="placeholder"
      :value="modelValue"
      @input="onInput"
      @focus="onFocus"
      @keydown.down.prevent="move(1)"
      @keydown.up.prevent="move(-1)"
      @keydown.enter.prevent="chooseHighlighted"
      @keydown.esc="close"
    />
    <button
      v-if="linkedProductId"
      type="button"
      class="product-ac-badge"
      title="Producto del catálogo vinculado. Pulsa para desvincular."
      @click="clearLink"
    >
      <Package :size="12" />
    </button>

    <Teleport to="body">
      <ul
        v-if="openList && filtered.length"
        class="product-ac-menu"
        :style="menuStyle"
      >
        <li
          v-for="(p, i) in filtered"
          :key="p.id"
          class="product-ac-item"
          :class="{ 'is-active': i === highlight }"
          @mousedown.prevent="choose(p)"
          @mouseenter="highlight = i"
        >
          <span class="product-ac-name">{{ p.name }}</span>
          <span class="product-ac-meta">
            <span v-if="p.sku" class="product-ac-sku">{{ p.sku }}</span>
            <span class="product-ac-price">{{ formatCurrency(priceOf(p)) }}</span>
          </span>
        </li>
      </ul>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import { Package } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: String, default: '' },
  products: { type: Array, default: () => [] },
  placeholder: { type: String, default: 'Producto o servicio...' },
  // 'sale' -> usa precio base (price_excl_tax/price); 'purchase' -> usa coste
  priceMode: { type: String, default: 'sale' },
  linkedProductId: { type: [Number, String], default: null },
})

const emit = defineEmits(['update:modelValue', 'select', 'clear'])

const root = ref(null)
const openList = ref(false)
const highlight = ref(-1)
const menuStyle = ref({})

const filtered = computed(() => {
  const q = (props.modelValue || '').trim().toLowerCase()
  const list = props.products
  if (!q) return list.slice(0, 50)
  return list
    .filter(p =>
      (p.name && p.name.toLowerCase().includes(q)) ||
      (p.sku && String(p.sku).toLowerCase().includes(q)),
    )
    .slice(0, 50)
})

function priceOf(p) {
  if (props.priceMode === 'purchase') {
    return p.cost ?? p.price ?? 0
  }
  return p.priceExclTax ?? p.price ?? 0
}

function formatCurrency(v) {
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(v || 0)
}

async function positionMenu() {
  await nextTick()
  const el = root.value
  if (!el) return
  const r = el.getBoundingClientRect()
  menuStyle.value = {
    position: 'fixed',
    top: `${r.bottom + 4}px`,
    left: `${r.left}px`,
    width: `${Math.max(r.width, 240)}px`,
  }
}

function onInput(e) {
  emit('update:modelValue', e.target.value)
  // Escribir manualmente desvincula el producto del catálogo
  if (props.linkedProductId) emit('clear')
  openList.value = true
  highlight.value = -1
  positionMenu()
}

function onFocus() {
  openList.value = true
  highlight.value = -1
  positionMenu()
}

function move(delta) {
  if (!openList.value) { openList.value = true; positionMenu() }
  const n = filtered.value.length
  if (!n) return
  highlight.value = (highlight.value + delta + n) % n
}

function chooseHighlighted() {
  if (highlight.value >= 0 && filtered.value[highlight.value]) {
    choose(filtered.value[highlight.value])
  }
}

function choose(p) {
  emit('update:modelValue', p.name)
  emit('select', p)
  close()
}

function clearLink() {
  emit('clear')
}

function close() {
  openList.value = false
  highlight.value = -1
}

function onDocClick(e) {
  if (root.value && !root.value.contains(e.target)) close()
}
document.addEventListener('mousedown', onDocClick)
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>

<style scoped>
.product-ac {
  position: relative;
  width: 100%;
}
.product-ac-input {
  width: 100%;
  padding-right: 1.75rem;
}
.product-ac-badge {
  position: absolute;
  right: 0.35rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 5px;
  border: none;
  background: var(--primary-light, #eef0ff);
  color: var(--primary-color, #667eea);
  cursor: pointer;
}
.product-ac-badge:hover { opacity: 0.8; }
</style>

<style>
/* Teleported menu (not scoped so it renders on body) */
.product-ac-menu {
  list-style: none;
  margin: 0;
  padding: 0.25rem;
  background: #fff;
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.25);
  max-height: 280px;
  overflow-y: auto;
  z-index: 10000;
}
.product-ac-item {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.4rem 0.55rem;
  border-radius: 6px;
  cursor: pointer;
}
.product-ac-item.is-active,
.product-ac-item:hover {
  background: var(--bg-hover, #f3f4f6);
}
.product-ac-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
}
.product-ac-meta {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.7rem;
  color: var(--text-secondary, #6b7280);
}
.product-ac-sku { font-family: 'JetBrains Mono', monospace; }
.product-ac-price { font-weight: 600; }
</style>
