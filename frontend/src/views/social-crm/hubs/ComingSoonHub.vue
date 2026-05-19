<template>
  <SocialHubLayout :title="hub.title" :subtitle="hub.subtitle">
    <div class="coming-soon">
      <div class="coming-soon-card">
        <div class="cs-icon-wrap">
          <component :is="hub.icon" :size="32" />
        </div>
        <h2 class="cs-title">Este hub está en migración</h2>
        <p class="cs-text">
          Mientras tanto, las pantallas que se consolidarán aquí siguen disponibles
          como rutas directas. Pronto verás todo unificado bajo
          <strong>{{ hub.title }}</strong>.
        </p>

        <div class="cs-pills">
          <router-link
            v-for="link in hub.legacy"
            :key="link.path"
            :to="link.path"
            class="cs-pill"
          >
            <component :is="link.icon" :size="14" />
            <span>{{ link.label }}</span>
            <ArrowUpRight :size="12" class="cs-pill-arrow" />
          </router-link>
        </div>
      </div>
    </div>
  </SocialHubLayout>
</template>

<script setup>
import { computed } from 'vue'
import {
  Image, AtSign, BarChart2, TrendingUp, Link as LinkIcon,
  FileText, Settings, AlertTriangle, ArrowUpRight,
} from 'lucide-vue-next'
import SocialHubLayout from './SocialHubLayout.vue'

const props = defineProps({
  hubKey: { type: String, required: true },
})

const HUBS = {
  content: {
    title: 'Contenido',
    subtitle: 'Publicaciones, cuentas conectadas y analítica de contenido en un solo lugar.',
    icon: Image,
    legacy: [
      { label: 'Publicaciones', path: '/social-crm/posts',     icon: Image },
      { label: 'Cuentas',       path: '/social-crm/accounts',  icon: AtSign },
      { label: 'Analítica',     path: '/social-crm/analytics', icon: BarChart2 },
    ],
  },
  attribution: {
    title: 'Atribución',
    subtitle: 'Trazabilidad por enlaces UTM, conversiones y reporting de ROI.',
    icon: TrendingUp,
    legacy: [
      { label: 'Enlaces',  path: '/social-crm/links',   icon: LinkIcon },
      { label: 'Informes', path: '/social-crm/reports', icon: FileText },
    ],
  },
  settings: {
    title: 'Ajustes',
    subtitle: 'Configuración del módulo, alertas activas y catálogos editables.',
    icon: Settings,
    legacy: [
      { label: 'Configuración', path: '/social-crm/settings', icon: Settings },
      { label: 'Alertas',       path: '/social-crm/alerts',   icon: AlertTriangle },
    ],
  },
}

const hub = computed(() => HUBS[props.hubKey] || HUBS.content)
</script>

<style scoped>
.coming-soon {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.coming-soon-card {
  max-width: 520px;
  text-align: center;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2.5rem 2rem;
  position: relative;
  overflow: hidden;
}

.coming-soon-card::before {
  content: '';
  position: absolute;
  top: -40%;
  left: 50%;
  transform: translateX(-50%);
  width: 140%;
  height: 200px;
  background: radial-gradient(ellipse at center, rgba(102,126,234,0.10), transparent 70%);
  pointer-events: none;
}

.cs-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.25rem;
  box-shadow: 0 8px 24px rgba(102,126,234,0.25);
  position: relative;
}

.cs-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
  letter-spacing: -0.01em;
  position: relative;
}

.cs-text {
  color: var(--text-secondary);
  font-size: 0.925rem;
  line-height: 1.55;
  margin: 0 0 1.5rem;
  position: relative;
}

.cs-text strong {
  color: var(--text-primary);
  font-weight: 600;
}

.cs-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  position: relative;
}

.cs-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  text-decoration: none;
  font-size: 0.825rem;
  font-weight: 500;
  border: 1px solid var(--border-color);
  transition: all 0.18s ease;
}

.cs-pill:hover {
  border-color: var(--primary-color);
  background: rgba(102,126,234,0.06);
  transform: translateY(-1px);
}

.cs-pill-arrow {
  opacity: 0.5;
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.cs-pill:hover .cs-pill-arrow {
  opacity: 1;
  transform: translate(2px, -2px);
}
</style>
