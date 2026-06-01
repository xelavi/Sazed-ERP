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
const PAD = { top: 16, right: 8, bottom: 28, left: 44 }
const plotW = W - PAD.left - PAD.right
const plotH = H - PAD.top - PAD.bottom

const uid = Math.random().toString(36).slice(2, 8)
const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => requestAnimationFrame(() => (mounted.value = true))))

const niceMax = computed(() => {
  const max = Math.max(...props.series.map((d) => d.value), 1)
  const pow = Math.pow(10, Math.floor(Math.log10(max)))
  const n = Math.ceil(max / pow) * pow
  return n === max ? n + pow / 2 : n
})

const ticks = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => {
    const v = (niceMax.value / steps) * i
    return { v, y: PAD.top + plotH - (v / niceMax.value) * plotH }
  })
})

const bars = computed(() => {
  const n = props.series.length
  const slot = plotW / n
  const bw = Math.min(slot * 0.62, 46)
  return props.series.map((d, i) => {
    const h = (d.value / niceMax.value) * plotH
    const x = PAD.left + slot * i + (slot - bw) / 2
    return {
      ...d, x, bw,
      h: Math.max(h, 2),
      y: PAD.top + plotH - Math.max(h, 2),
      cx: x + bw / 2,
    }
  })
})

const hover = ref(-1)
const tip = computed(() => {
  if (hover.value < 0) return null
  const b = bars.value[hover.value]
  return {
    left: ((b.cx) / W) * 100,
    top: (b.y / H) * 100,
    label: b.label,
    value: formatValue(b.value, props.unit),
  }
})
</script>

<template>
  <div class="chart-host">
    <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none" class="chart-svg">
      <defs>
        <linearGradient :id="`bar-${uid}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.95" />
          <stop offset="100%" :stop-color="color" stop-opacity="0.55" />
        </linearGradient>
      </defs>

      <!-- gridlines + y labels -->
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

      <!-- bars -->
      <g>
        <g v-for="(b, i) in bars" :key="i">
          <rect
            :x="b.x"
            :y="mounted ? b.y : PAD.top + plotH"
            :width="b.bw"
            :height="mounted ? b.h : 0"
            :rx="Math.min(b.bw / 2.4, 7)"
            :fill="`url(#bar-${uid})`"
            class="bar"
            :class="{ dim: hover > -1 && hover !== i }"
            :style="{ transitionDelay: `${i * 45}ms` }"
          />
          <rect
            :x="b.x - (plotW / series.length - b.bw) / 2"
            :y="PAD.top" :width="plotW / series.length" :height="plotH"
            fill="transparent"
            @mouseenter="hover = i" @mouseleave="hover = -1"
          />
        </g>
      </g>

      <!-- x labels -->
      <text
        v-for="(b, i) in bars" :key="`x${i}`"
        :x="b.cx" :y="H - 8" text-anchor="middle" class="axis-label"
        :class="{ strong: hover === i }"
      >{{ b.label }}</text>
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
.bar {
  transition: height 700ms cubic-bezier(0.22, 1, 0.36, 1),
              y 700ms cubic-bezier(0.22, 1, 0.36, 1),
              opacity var(--transition-fast);
}
.bar.dim { opacity: 0.35; }
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
