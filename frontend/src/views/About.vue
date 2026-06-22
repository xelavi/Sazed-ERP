<template>
  <div class="about-view">
    <div class="view-header">
      <h1 class="view-title">Quant a</h1>
    </div>

    <div class="content-wrapper">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Quant a aquest ERP</h3>
        </div>
        <div class="card-body">
          <p>Aquest és un sistema ERP web modern i senzill construït amb Vue 3 i Vite.</p>
          <p>Característiques principals:</p>
          <ul class="feature-list">
            <li>✅ Gestió de productes</li>
            <li>✅ Control d'inventari</li>
            <li>✅ Gestió de pagaments i cartera</li>
            <li>✅ Sistema de clients</li>
            <li>✅ Màrqueting i vendes</li>
            <li>✅ Dashboard intuïtiu</li>
          </ul>
        </div>
      </div>

      <div class="card mt-3">
        <div class="card-header">
          <h3 class="card-title">Tecnologies utilitzades</h3>
        </div>
        <div class="tech-grid">
          <div class="tech-item">
            <div class="tech-icon">⚡</div>
            <h4 class="tech-name">Vite</h4>
            <p class="tech-description">Eina de build ràpida i moderna</p>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🎨</div>
            <h4 class="tech-name">Vue 3</h4>
            <p class="tech-description">Framework progressiu per a la UI</p>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🛣️</div>
            <h4 class="tech-name">Vue Router</h4>
            <p class="tech-description">Navegació SPA integrada</p>
          </div>
          <div class="tech-item">
            <div class="tech-icon">🎭</div>
            <h4 class="tech-name">CSS Variables</h4>
            <p class="tech-description">Sistema de disseny flexible</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Lógica del componente aquí
</script>

<style scoped>
.about-view {
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
}

.feature-list li {
  padding: 0.5rem 0;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  padding: 1.5rem;
}

.tech-item {
  text-align: center;
}

.tech-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.tech-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.tech-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .view-title {
    font-size: 1.5rem;
  }
  .tech-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .view-title {
    font-size: 1.25rem;
  }
  .tech-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>

