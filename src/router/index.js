import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('../views/Products.vue')
  },
  {
    path: '/collections',
    name: 'Collections',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/inventory',
    name: 'Inventory',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('../views/Wallet.vue')
  },
  {
    path: '/card',
    name: 'Card',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/payout',
    name: 'Payout',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/customers',
    name: 'Customers',
    component: () => import('../views/Customers.vue')
  },
  {
    path: '/marketing',
    name: 'Marketing',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/online-store',
    name: 'OnlineStore',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/sell-link',
    name: 'SellLink',
    component: () => import('../views/About.vue') // Placeholder
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/About.vue') // Placeholder
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

