<script setup>
import { ref, computed, onMounted } from 'vue'
import { formatValue, CATEGORY_PALETTE } from '@/config/dashboardKpis'

const props = defineProps({
  series: { type: Array, required: true },
  color: { type: String, default: '#667eea' },
  unit: { type: String, default: 'number' },
  mono: { type: Boolean, default: false },
})

const mounted = ref(false)
onMounted(() => requestAnimationFrame(() => requestAnimationFrame(() => (mounted.value = true))))

const max = computed(() => Math.max(...props.series.map((d) => d.value), 1))
const rows = computed(() =>
  props.series.map((d, i) => ({
    ...d,
    pct: (d.value / max.value) * 100,
    color: props.mono ? props.color : CATEGORY_PALETTE[i % CATEGORY_PALETTE.length],
  })),
)
</script>

<template>
  <div class="hbar-host">
    <div v-for="(r, i) in rows" :key="i" class="hbar-row">
      <span class="hbar-label">{{ r.label }}</span>
      <div class="hbar-track">
        <div
          class="hbar-fill"
          :style="{
            width: (mounted ? r.pct : 0) + '%',
            background: `linear-gradient(90deg, ${r.color}cc, ${r.color})`,
            transitionDelay: `${i * 70}ms`,
          }"
        />
      </div>
      <span class="hbar-value">{{ formatValue(r.value, unit) }}</span>
    </div>
  </div>
</template>

<style scoped>
.hbar-host {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.7rem;
  width: 100%;
  height: 100%;
  padding: 0.25rem 0;
}
.hbar-row {
  display: grid;
  grid-template-columns: 130px 1fr auto;
  align-items: center;
  gap: 0.75rem;
}
.hbar-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: right;
}
.hbar-track {
  height: 14px;
  background: var(--bg-secondary);
  border-radius: 7px;
  overflow: hidden;
}
.hbar-fill {
  height: 100%;
  border-radius: 7px;
  transition: width 800ms cubic-bezier(0.22, 1, 0.36, 1);
}
.hbar-value {
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  min-width: 56px;
  text-align: right;
}
@media (max-width: 480px) {
  .hbar-row { grid-template-columns: 90px 1fr auto; }
}
</style>
