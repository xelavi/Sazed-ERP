<template>
  <div class="hub-layout" :class="{ 'panel-open': panelOpen }">
    <!-- ── HUB HEADER ────────────────────────────────────────── -->
    <header class="hub-header">
      <div class="hub-header-row">
        <div class="hub-title-block">
          <div class="hub-eyebrow">Social CRM</div>
          <h1 class="hub-title">
            <slot name="title">{{ title }}</slot>
          </h1>
          <p v-if="subtitle || $slots.subtitle" class="hub-subtitle">
            <slot name="subtitle">{{ subtitle }}</slot>
          </p>
        </div>

        <div class="hub-header-actions">
          <slot name="actions"></slot>
        </div>
      </div>

      <!-- Tabs ─────────────────────────────────── -->
      <nav v-if="tabs?.length" class="hub-tabs" role="tablist">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          role="tab"
          :aria-selected="modelValue === tab.key"
          :class="['hub-tab', { active: modelValue === tab.key }]"
          @click="$emit('update:modelValue', tab.key)"
        >
          <component v-if="tab.icon" :is="tab.icon" :size="15" class="hub-tab-icon" />
          <span class="hub-tab-label">{{ tab.label }}</span>
          <span v-if="tab.count != null" class="hub-tab-count">{{ tab.count }}</span>
        </button>
        <div class="hub-tabs-spacer"></div>
        <div class="hub-tabs-extra">
          <slot name="tabs-extra"></slot>
        </div>
      </nav>
    </header>

    <!-- ── HUB BODY (split: content | side panel) ────────────── -->
    <div class="hub-body">
      <section class="hub-main">
        <slot></slot>
      </section>

      <!-- Side panel container -->
      <transition name="panel-slide">
        <aside
          v-if="panelOpen"
          class="hub-panel"
          role="complementary"
          aria-label="Detail panel"
        >
          <div class="hub-panel-handle" @click="$emit('close-panel')" title="Cerrar">
            <ChevronRight :size="16" />
          </div>
          <div class="hub-panel-content">
            <slot name="panel"></slot>
          </div>
        </aside>
      </transition>

      <!-- Mobile overlay when panel is open -->
      <div
        v-if="panelOpen"
        class="hub-panel-overlay"
        @click="$emit('close-panel')"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ChevronRight } from 'lucide-vue-next'

defineProps({
  title:      { type: String, default: '' },
  subtitle:   { type: String, default: '' },
  tabs:       { type: Array,  default: () => [] },
  modelValue: { type: String, default: '' },
  panelOpen:  { type: Boolean, default: false },
})

defineEmits(['update:modelValue', 'close-panel'])
</script>

<style scoped>
/* ── Layout ────────────────────────────────────── */
.hub-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  background: var(--bg-primary);
}

/* ── Header ────────────────────────────────────── */
.hub-header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  padding: 1.25rem clamp(1.25rem, 2.5vw, 2rem) 0;
  position: relative;
  z-index: 5;
}

.hub-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at top left, rgba(102,126,234,0.05), transparent 60%),
    radial-gradient(ellipse at top right, rgba(236,72,153,0.04), transparent 55%);
  pointer-events: none;
}

.hub-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
  position: relative;
}

.hub-title-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.hub-eyebrow {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--primary-color);
  opacity: 0.85;
}

.hub-title {
  font-size: clamp(1.5rem, 2.4vw, 1.875rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.15;
}

.hub-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 0;
  max-width: 56ch;
}

.hub-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* ── Tabs ──────────────────────────────────────── */
.hub-tabs {
  display: flex;
  align-items: center;
  gap: 0.125rem;
  margin-top: 1.25rem;
  position: relative;
  overflow-x: auto;
  scrollbar-width: none;
}
.hub-tabs::-webkit-scrollbar { display: none; }

.hub-tab {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.875rem;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  border-radius: 6px 6px 0 0;
  white-space: nowrap;
  transition: color 0.15s ease, background 0.15s ease;
}

.hub-tab:hover {
  color: var(--text-primary);
  background: rgba(102,126,234,0.04);
}

.hub-tab.active {
  color: var(--text-primary);
  font-weight: 600;
}

.hub-tab.active::after {
  content: '';
  position: absolute;
  left: 0.5rem;
  right: 0.5rem;
  bottom: -1px;
  height: 2px;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px 2px 0 0;
}

.hub-tab-icon {
  flex-shrink: 0;
  opacity: 0.85;
}

.hub-tab-count {
  font-size: 0.72rem;
  font-weight: 600;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  padding: 1px 7px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
  line-height: 1.4;
}

.hub-tab.active .hub-tab-count {
  background: rgba(102,126,234,0.12);
  color: var(--primary-color);
}

.hub-tabs-spacer { flex: 1; }
.hub-tabs-extra { display: flex; align-items: center; gap: 0.5rem; padding-bottom: 0.5rem; }

/* ── Body ──────────────────────────────────────── */
.hub-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  min-height: 0;
  overflow: hidden;
  position: relative;
  transition: grid-template-columns 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.hub-layout.panel-open .hub-body {
  grid-template-columns: 1fr 460px;
}

.hub-main {
  overflow-y: auto;
  padding: 1.5rem clamp(1.25rem, 2.5vw, 2rem);
  min-width: 0;
}

/* ── Side panel ────────────────────────────────── */
.hub-panel {
  position: relative;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: -8px 0 24px rgba(15, 23, 42, 0.04);
}

.hub-panel-handle {
  position: absolute;
  top: 1rem;
  left: -14px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 6;
  color: var(--text-secondary);
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
  transition: all 0.15s ease;
}

.hub-panel-handle:hover {
  color: var(--text-primary);
  border-color: var(--primary-color);
  transform: scale(1.05);
}

.hub-panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1.5rem 2rem;
}

.hub-panel-overlay {
  display: none;
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.35);
  z-index: 4;
}

/* ── Panel slide animation ─────────────────────── */
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              opacity 0.25s ease;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* ── Responsive ────────────────────────────────── */
@media (max-width: 1100px) {
  .hub-layout.panel-open .hub-body {
    grid-template-columns: 1fr;
  }
  .hub-panel {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: min(440px, 92vw);
    z-index: 5;
  }
  .hub-panel-overlay {
    display: block;
  }
}

@media (max-width: 640px) {
  .hub-header { padding: 1rem 1rem 0; }
  .hub-main { padding: 1rem; }
  .hub-tabs { margin-top: 0.875rem; }
  .hub-tab { padding: 0.5rem 0.625rem; font-size: 0.825rem; }
}
</style>
