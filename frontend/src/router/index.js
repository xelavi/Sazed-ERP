import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import { useAuth } from '@/composables/useAuth'

const routes = [
  // ── Auth (empty layout) ───────────────────────
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/LoginView.vue'),
    meta: { layout: 'empty', guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/RegisterView.vue'),
    meta: { layout: 'empty', guest: true },
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: () => import('../views/auth/OnboardingView.vue'),
    meta: { layout: 'empty', requiresAuth: true },
  },

  // ── App (default layout) ─────────────────────
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true },
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('../views/Products.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/collections',
    name: 'Collections',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('../views/Inventory.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('../views/Wallet.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/card',
    name: 'Card',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/payout',
    name: 'Payout',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: () => import('../views/Invoices.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/customers',
    name: 'Customers',
    component: () => import('../views/Customers.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/marketing',
    name: 'Marketing',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/online-store',
    name: 'OnlineStore',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/sell-link',
    name: 'SellLink',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/About.vue'), // Placeholder
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings/company',
    name: 'CompanySettings',
    component: () => import('../views/CompanySettingsView.vue'),
    meta: { requiresAuth: true, requiresRole: ['owner', 'admin'] },
  },

  // ── Social CRM ───────────────────────────────
  {
    path: '/social-crm',
    name: 'SocialCrmDashboard',
    component: () => import('../views/social-crm/SocialCrmDashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/accounts',
    name: 'SocialAccounts',
    component: () => import('../views/social-crm/SocialAccounts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/posts',
    name: 'SocialPosts',
    component: () => import('../views/social-crm/SocialPosts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/posts/:id',
    name: 'SocialPostDetail',
    component: () => import('../views/social-crm/SocialPostDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/campaigns',
    name: 'SocialCampaigns',
    component: () => import('../views/social-crm/SocialCampaigns.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/campaigns/:id',
    name: 'SocialCampaignDetail',
    component: () => import('../views/social-crm/SocialCampaignDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/influencers',
    name: 'SocialInfluencers',
    component: () => import('../views/social-crm/SocialInfluencers.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/influencers/:id',
    name: 'SocialInfluencerDetail',
    component: () => import('../views/social-crm/SocialInfluencerDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/collaborations',
    name: 'SocialCollaborations',
    component: () => import('../views/social-crm/SocialCollaborations.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/collaborations/:id',
    name: 'SocialCollaborationDetail',
    component: () => import('../views/social-crm/SocialCollaborationDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/metrics',
    name: 'SocialMetrics',
    component: () => import('../views/social-crm/SocialMetrics.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/links',
    name: 'SocialLinks',
    component: () => import('../views/social-crm/SocialLinks.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/links/:id',
    name: 'SocialLinkDetail',
    component: () => import('../views/social-crm/SocialLinkDetail.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/analytics',
    name: 'SocialAnalytics',
    component: () => import('../views/social-crm/SocialAnalytics.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/reports',
    name: 'SocialReports',
    component: () => import('../views/social-crm/SocialReports.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/alerts',
    name: 'SocialAlerts',
    component: () => import('../views/social-crm/SocialAlerts.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/social-crm/settings',
    name: 'SocialCrmSettings',
    component: () => import('../views/social-crm/SocialCrmSettings.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ── Navigation guard ─────────────────────────
let initialAuthChecked = false

router.beforeEach(async (to, from, next) => {
  const { isAuthenticated, fetchMe, isLoading, activeRole, hasCompany } = useAuth()

  // On first navigation, try to restore session
  if (!initialAuthChecked) {
    initialAuthChecked = true
    try {
      await fetchMe()
    } catch {
      // Not authenticated — will be handled below
    }
  }

  // Guest-only routes: redirect authenticated users to home
  if (to.meta.guest && isAuthenticated.value) {
    return next('/')
  }

  // Protected routes: redirect unauthenticated users to login
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  // Onboarding: authenticated users without companies must set up first
  if (isAuthenticated.value && !hasCompany.value && to.name !== 'Onboarding' && to.meta.requiresAuth) {
    return next('/onboarding')
  }

  // If user already has companies and visits onboarding, redirect to home
  if (to.name === 'Onboarding' && isAuthenticated.value && hasCompany.value) {
    return next('/')
  }

  // Role-gated routes
  if (to.meta.requiresRole && !to.meta.requiresRole.includes(activeRole.value)) {
    return next('/')
  }

  next()
})

export default router

