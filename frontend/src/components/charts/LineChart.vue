<script setup>
import { ref, computed, onMounted } from 'vue'
import { formatValue, formatCompact } from '@/config/dashboardKpis'

const props = defineProps({
  series: { type: Array, required: true },
  color: { type: String, default: '#667eea' },
  unit: { type: String, default: 'number' },
})

const W = 640
const H = 280
const PAD = { top: 18, right: 12, bottom: 28, left: 44 }
const plotW = W - PAD.left - PAD.right
const plotH = H - PAD.top - PAD.bottom

const uid = Math.random().toString(36).slice(2, 8)
const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => requestAnimationFrame(() => (mounted.value = true))))

const max = computed(() => Math.max(...props.series.map((d) => d.value), 1))
const min = computed(() => Math.min(...props.series.map((d) => d.value), 0))
const niceMax = computed(() => {
  const pow = Math.pow(10, Math.floor(Math.log10(max.value || 1)))
  return Math.ceil((max.value * 1.1) / pow) * pow
})

const ticks = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => {
    const v = (niceMax.value / steps) * i
    return { v, y: PAD.top + plotH - (v / niceMax.value) * plotH }
  })
})

const points = computed(() => {
  const n = props.series.length
  return props.series.map((d, i) => ({
    ...d,
    x: PAD.left + (plotW / (n - 1)) * i,
    y: PAD.top + plotH - (d.value / niceMax.value) * plotH,
  }))
})

// Smooth path via Catmull-Rom → cubic Bézier
function smoothPath(pts) {
  if (pts.length < 2) return ''
  let d = `M ${pts[0].x},${pts[0].y}`
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[i - 1] || pts[i]
    const p1 = pts[i]
    const p2 = pts[i + 1]
    const p3 = pts[i + 2] || p2
    const t = 0.18
    const c1x = p1.x + (p2.x - p0.x) * t
    const c1y = p1.y + (p2.y - p0.y) * t
    const c2x = p2.x - (p3.x - p1.x) * t
    const c2y = p2.y - (p3.y - p1.y) * t
    d += ` C ${c1x},${c1y} ${c2x},${c2y} ${p2.x},${p2.y}`
  }
  return d
}

const linePath = computed(() => smoothPath(points.value))
const areaPath = computed(() => {
  if (!points.value.length) return ''
  const base = PAD.top + plotH
  const first = points.value[0]
  const last = points.value[points.value.length - 1]
  return `${linePath.value} L ${last.x},${base} L ${first.x},${base} Z`
})

const hover = ref(-1)
const tip = computed(() => {
  if (hover.value < 0) return null
  const p = points.value[hover.value]
  return {
    left: (p.x / W) * 100,
    top: (p.y / H) * 100,
    label: p.label,
    value: formatValue(p.value, props.unit),
  }
})
const slot = computed(() => plotW / (props.series.length - 1 || 1))
</script>

<template>
  <div class="chart-host">
    <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none" class="chart-svg">
      <defs>
        <linearGradient :id="`area-${uid}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.32" />
          <stop offset="100%" :stop-color="color" stop-opacity="0" />
        </linearGradient>
      </defs>

      <g class="grid">
        <line
          v-for="(t, i) in ticks" :key="`g${i}`"
          :x1="PAD.left" :x2="W - PAD.right" :y1="t.y" :y2="t.y"
        />
        <text
          v-for="(t, i) in ticks" :key="`t${i}`"
          :x="PAD.left - 8" :y="t.y + 3" text-anchor="end" class="axis-label"
        >{{ formatCompact(t.v, unit) }}</text>
      </g>

      <path :d="areaPath" :fill="`url(#area-${uid})`" class="area" :class="{ in: mounted }" />
      <path
        :d="linePath" fill="none" :stroke="color" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round"
        class="line" :class="{ in: mounted }"
      />

      <!-- markers -->
      <g v-for="(p, i) in points" :key="i">
        <circle
          v-if="hover === i"
          :cx="p.x" :cy="p.y" r="5.5" :fill="color"
          stroke="#fff" stroke-width="2.5" class="dot-active"
        />
        <rect
          :x="p.x - slot / 2" :y="PAD.top" :width="slot" :height="plotH"
          fill="transparent" @mouseenter="hover = i" @mouseleave="hover = -1"
        />
      </g>

      <line
        v-if="hover > -1"
        :x1="points[hover].x" :x2="points[hover].x"
        :y1="PAD.top" :y2="PAD.top + plotH" class="crosshair"
      />

      <text
        v-for="(p, i) in points" :key="`x${i}`"
        :x="p.x" :y="H - 8" text-anchor="middle" class="axis-label"
        :class="{ strong: hover === i }"
      >{{ p.label }}</text>
    </svg>

    <transition name="tip">
      <div
        v-if="tip" class="chart-tip"
        :style="{ left: tip.left + '%', top: tip.top + '%' }"
      >
        <span class="tip-label">{{ tip.label }}</span>
        <span class="tip-value">{{ tip.value }}</span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.chart-host { position: relative; width: 100%; height: 100%; }
.chart-svg { width: 100%; height: 100%; display: block; overflow: visible; }
.grid line { stroke: var(--border-color); stroke-width: 1; shape-rendering: crispEdges; }
.grid line:last-of-type { stroke: transparent; }
.axis-label {
  fill: var(--text-tertiary);
  font-size: 11px;
  font-family: var(--font-family);
  transition: fill var(--transition-fast);
}
.axis-label.strong { fill: var(--text-primary); font-weight: 600; }
.line {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  transition: stroke-dashoffset 1100ms cubic-bezier(0.22, 1, 0.36, 1);
}
.line.in { stroke-dashoffset: 0; }
.area { opacity: 0; transition: opacity 900ms ease 350ms; }
.area.in { opacity: 1; }
.crosshair { stroke: var(--border-color); stroke-width: 1; stroke-dasharray: 3 3; }
.dot-active { filter: drop-shadow(0 1px 3px rgba(0,0,0,.25)); }
.chart-tip {
  position: absolute;
  transform: translate(-50%, -130%);
  background: var(--text-primary);
  color: #fff;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  pointer-events: none;
  white-space: nowrap;
  box-shadow: var(--shadow-lg);
  display: flex; flex-direction: column; gap: 1px;
  z-index: 5;
}
.chart-tip::after {
  content: ''; position: absolute; left: 50%; top: 100%;
  transform: translateX(-50%);
  border: 5px solid transparent; border-top-color: var(--text-primary);
}
.tip-label { font-size: 0.7rem; opacity: 0.7; }
.tip-value { font-size: 0.875rem; font-weight: 700; }
.tip-enter-active, .tip-leave-active { transition: opacity 120ms ease; }
.tip-enter-from, .tip-leave-to { opacity: 0; }
</style>
