<script setup>
import { computed } from 'vue'
import { Inbox } from 'lucide-vue-next'
import { getKpiView } from '@/config/dashboardKpis'
import BarChart from './BarChart.vue'
import LineChart from './LineChart.vue'
import DonutChart from './DonutChart.vue'
import HBarChart from './HBarChart.vue'
import KpiStat from './KpiStat.vue'

const props = defineProps({
  analytics: { type: Object, default: null },
  kpi: { type: String, required: true },
  chart: { type: String, required: true },
  groupBy: { type: String, default: null },
})

const view = computed(() => getKpiView(props.analytics, props.kpi, props.chart, props.groupBy))
</script>

<template>
  <div v-if="!analytics" class="chart-skeleton">
    <span class="sk-pulse" />
  </div>

  <div v-else-if="view.empty" class="chart-empty">
    <Inbox :size="26" />
    <span>Sense dades en aquest període</span>
  </div>

  <KpiStat
    v-else-if="chart === 'stat'"
    :series="view.series" :color="view.color" :unit="view.unit"
    :headline="view.headline" :delta="view.delta"
  />
  <LineChart
    v-else-if="chart === 'line'"
    :series="view.series" :color="view.color" :unit="view.unit"
  />
  <BarChart
    v-else-if="chart === 'bar'"
    :series="view.series" :color="view.color" :unit="view.unit"
  />
  <DonutChart
    v-else-if="chart === 'donut'"
    :series="view.series" :unit="view.unit"
  />
  <HBarChart
    v-else-if="chart === 'hbar'"
    :series="view.series" :color="view.color" :unit="view.unit" mono
  />
</template>

<style scoped>
.chart-skeleton {
  width: 100%; height: 100%; min-height: 80px;
  display: flex; align-items: center; justify-content: center;
}
.sk-pulse {
  width: 100%; height: 100%; border-radius: var(--border-radius-sm);
  background: linear-gradient(90deg, var(--bg-secondary) 25%, var(--bg-hover) 50%, var(--bg-secondary) 75%);
  background-size: 200% 100%;
  animation: sk 1.3s ease-in-out infinite;
}
@keyframes sk { 0% { background-position: 200% 0 } 100% { background-position: -200% 0 } }
.chart-empty {
  width: 100%; height: 100%; min-height: 80px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.5rem; color: var(--text-tertiary); font-size: var(--font-size-sm);
}
</style>
