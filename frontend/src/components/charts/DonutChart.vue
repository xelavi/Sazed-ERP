<script setup>
import { ref, computed, onMounted } from 'vue'
import { formatValue, formatCompact, CATEGORY_PALETTE } from '@/config/dashboardKpis'

const props = defineProps({
  series: { type: Array, required: true },
  unit: { type: String, default: 'number' },
})

const SIZE = 220
const R = 80
const STROKE = 26
const C = 2 * Math.PI * R

const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => requestAnimationFrame(() => (mounted.value = true))))

const total = computed(() => props.series.reduce((s, d) => s + d.value, 0) || 1)

const segments = computed(() => {
  let acc = 0
  return props.series.map((d, i) => {
    const frac = d.value / total.value
    const seg = {
      ...d,
      color: CATEGORY_PALETTE[i % CATEGORY_PALETTE.length],
      pct: frac * 100,
      dash: frac * C,
      offset: -acc * C,
    }
    acc += frac
    return seg
  })
})

const hover = ref(-1)
const center = computed(() => {
  if (hover.value > -1) {
    const s = segments.value[hover.value]
    return { value: formatCompact(s.value, props.unit), label: s.label }
  }
  return { value: formatCompact(total.value, props.unit), label: 'Total' }
})
</script>

<template>
  <div class="donut-host">
    <div class="donut-wrap">
      <svg :viewBox="`0 0 ${SIZE} ${SIZE}`" class="donut-svg">
        <g :transform="`translate(${SIZE / 2}, ${SIZE / 2}) rotate(-90)`">
          <circle :r="R" fill="none" stroke="var(--bg-secondary)" :stroke-width="STROKE" />
          <circle
            v-for="(s, i) in segments" :key="i"
            :r="R" fill="none"
            :stroke="s.color"
            :stroke-width="hover === i ? STROKE + 6 : STROKE"
            :stroke-dasharray="`${mounted ? s.dash : 0} ${C}`"
            :stroke-dashoffset="s.offset"
            stroke-linecap="butt"
            class="seg"
            :class="{ dim: hover > -1 && hover !== i }"
            :style="{ transitionDelay: `${i * 60}ms` }"
            @mouseenter="hover = i" @mouseleave="hover = -1"
          />
        </g>
      </svg>
      <div class="donut-center">
        <span class="center-value">{{ center.value }}</span>
        <span class="center-label">{{ center.label }}</span>
      </div>
    </div>

    <ul class="legend">
      <li
        v-for="(s, i) in segments" :key="i"
        class="legend-row" :class="{ active: hover === i, dim: hover > -1 && hover !== i }"
        @mouseenter="hover = i" @mouseleave="hover = -1"
      >
        <span class="legend-dot" :style="{ background: s.color }" />
        <span class="legend-label">{{ s.label }}</span>
        <span class="legend-pct">{{ s.pct.toFixed(1) }}%</span>
        <span class="legend-value">{{ formatValue(s.value, unit) }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.donut-host {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  width: 100%;
  height: 100%;
  flex-wrap: wrap;
}
.donut-wrap {
  position: relative;
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}
.donut-svg { width: 100%; height: 100%; display: block; }
.seg {
  transition: stroke-dasharray 900ms cubic-bezier(0.22, 1, 0.36, 1),
              stroke-width 180ms ease, opacity 180ms ease;
  cursor: pointer;
}
.seg.dim { opacity: 0.35; }
.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.center-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); line-height: 1.1; }
.center-label {
  font-size: 0.7rem; color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;
}
.legend {
  list-style: none; margin: 0; padding: 0;
  flex: 1; min-width: 180px;
  display: flex; flex-direction: column; gap: 2px;
}
.legend-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-areas: 'dot label pct' 'dot value value';
  column-gap: 0.5rem;
  align-items: center;
  padding: 0.35rem 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background var(--transition-fast), opacity var(--transition-fast);
}
.legend-row.active { background: var(--bg-secondary); }
.legend-row.dim { opacity: 0.5; }
.legend-dot { grid-area: dot; width: 10px; height: 10px; border-radius: 3px; }
.legend-label {
  grid-area: label; font-size: var(--font-size-sm); color: var(--text-primary);
  font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.legend-pct { grid-area: pct; font-size: var(--font-size-sm); font-weight: 700; color: var(--text-primary); }
.legend-value { grid-area: value; font-size: var(--font-size-xs); color: var(--text-secondary); }
</style>
