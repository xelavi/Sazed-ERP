<template>
  <div class="wallet-view">
    <div class="view-header">
      <div class="header-content">
        <h1 class="view-title">Wallet</h1>
        <button class="btn btn-primary">
          <DollarSign :size="18" />
          <span>Get paid</span>
        </button>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="info-banner">
        <div class="banner-icon">
          <Lightbulb :size="28" />
        </div>
        <div class="banner-content">
          <h3 class="banner-title">Kickstart your earnings!</h3>
          <p class="banner-text">
            Begin your journey by adding products or creating a payment link. It's your first step to collecting funds and growing your business.
          </p>
          <a href="#" class="banner-link">Sell via Link →</a>
        </div>
      </div>

      <div class="balance-cards">
        <div class="card balance-card">
          <div class="balance-header">
            <span class="balance-label">AVAILABLE</span>
            <div class="balance-icon">
              <Banknote :size="24" />
            </div>
          </div>
          <h2 class="balance-amount">$0.00</h2>
          <div class="balance-action">
            <a href="#" class="link-secondary">
              <CreditCard :size="16" />
              Create your <span class="link-highlight">Card</span>
            </a>
          </div>
        </div>

        <div class="card balance-card">
          <div class="balance-header">
            <span class="balance-label">UPCOMING</span>
            <div class="balance-icon">
              <TrendingUp :size="24" />
            </div>
          </div>
          <h2 class="balance-amount">$0.00</h2>
          <div class="balance-info">
            <Clock :size="16" class="info-icon" />
            <span class="info-text">$0.00 collected from 0 order(s)</span>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Recent Payments</h3>
        </div>
        <div class="empty-state">
          <div class="empty-icon">
            <DollarSign :size="48" />
          </div>
          <h4 class="empty-title">No recent payments</h4>
          <p class="empty-text">Currently, there are no recent payments recorded.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { DollarSign, Lightbulb, CreditCard, TrendingUp, Clock, Banknote } from 'lucide-vue-next'
</script>

<style scoped>
.wallet-view {
  width: 100%;
}

.view-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.view-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.info-banner {
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  border: 1px solid #c7d2fe;
  border-radius: 16px;
  padding: 1.75rem;
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.08);
}

.banner-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.banner-content {
  flex: 1;
}

.banner-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.banner-text {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.banner-link {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
  font-size: 0.9375rem;
  transition: color var(--transition-base);
}

.banner-link:hover {
  color: var(--primary-dark);
}

.balance-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.balance-card {
  position: relative;
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.balance-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.balance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.balance-label {
  font-size: 0.6875rem;
  font-weight: 700;
  color: var(--text-tertiary);
  letter-spacing: 0.08em;
}

.balance-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
}

.balance-amount {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.balance-action {
  display: flex;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.balance-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.info-icon {
  font-size: 1.125rem;
}

.info-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.link-secondary {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.9375rem;
  transition: color var(--transition-base);
  display: 4rem 2rem;
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  color: var(--text-primary);
}

.link-highlight {
  color: var(--primary-color);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.empty-text {
  color: var(--text-secondary);
  font-size: 0.9375rem;
  margin-bottom: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    gap: 1rem;
  }
  .view-title {
    font-size: 1.5rem;
  }
  .info-banner {
    flex-direction: column;
    gap: 1rem;
    padding: 1.25rem;
  }
  .balance-cards {
    grid-template-columns: 1fr;
  }
  .balance-amount {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .view-title {
    font-size: 1.25rem;
  }
  .balance-amount {
    font-size: 1.75rem;
  }
  .empty-state {
    padding: 2rem 1rem;
  }
}
</style>
