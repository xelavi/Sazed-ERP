<script setup>
import { computed } from 'vue'
import { ArrowUpRight, ArrowDownRight } from 'lucide-vue-next'
import { formatValue } from '@/config/dashboardKpis'

const props = defineProps({
  series: { type: Array, required: true },
  color: { type: String, default: '#667eea' },
  unit: { type: String, default: 'number' },
  headline: { type: Number, default: 0 },
  delta: { type: Number, default: 0 },
})

const uid = Math.random().toString(36).slice(2, 8)
const positive = computed(() => props.delta >= 0)

// mini sparkline (last values)
const W = 240
const Hs = 56
const spark = computed(() => {
  const data = props.series.slice(-12)
  const max = Math.max(...data.map((d) => d.value), 1)
  const min = Math.min(...data.map((d) => d.value), 0)
  const range = max - min || 1
  const pts = data.map((d, i) => ({
    x: (W / (data.length - 1 || 1)) * i,
    y: Hs - 4 - ((d.value - min) / range) * (Hs - 10),
  }))
  let line = `M ${pts[0].x},${pts[0].y}`
  for (let i = 0; i < pts.length - 1; i++) {
    const p1 = pts[i], p2 = pts[i + 1]
    const cx = (p1.x + p2.x) / 2
    line += ` C ${cx},${p1.y} ${cx},${p2.y} ${p2.x},${p2.y}`
  }
  const area = `${line} L ${pts[pts.length - 1].x},${Hs} L ${pts[0].x},${Hs} Z`
  return { line, area }
})
</script>

<template>
  <div class="stat-host">
    <div class="stat-top">
      <span class="stat-value">{{ formatValue(headline, unit) }}</span>
      <span class="stat-delta" :class="positive ? 'up' : 'down'">
        <component :is="positive ? ArrowUpRight : ArrowDownRight" :size="15" />
        {{ Math.abs(delta).toFixed(1) }}%
      </span>
    </div>
    <span class="stat-sub">vs. període anterior</span>

    <svg :viewBox="`0 0 ${W} ${Hs}`" preserveAspectRatio="none" class="stat-spark">
      <defs>
        <linearGradient :id="`sp-${uid}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.28" />
          <stop offset="100%" :stop-color="color" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path :d="spark.area" :fill="`url(#sp-${uid})`" />
      <path
        :d="spark.line" fill="none" :stroke="color"
        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
      />
    </svg>
  </div>
</template>

<style scoped>
.stat-host {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  justify-content: center;
}
.stat-top { display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap; }
.stat-value {
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.5px;
}
.stat-delta {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  font-size: var(--font-size-sm);
  font-weight: 700;
  padding: 0.1rem 0.45rem 0.1rem 0.3rem;
  border-radius: 9999px;
}
.stat-delta.up { color: var(--success-color); background: var(--success-light); }
.stat-delta.down { color: var(--error-color); background: var(--error-light); }
.stat-sub {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 3px;
}
.stat-spark {
  width: 100%;
  height: 56px;
  margin-top: auto;
  display: block;
}
</style>
