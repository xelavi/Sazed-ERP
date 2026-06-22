<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useInbox } from '@/composables/useInbox'
import {
  Home, Package, Users, Link2,
  Globe, Settings, ChevronDown, ChevronRight,
  Menu, Search, Bell, HelpCircle, ShoppingBag,
  ClipboardList, TrendingUp,
  Receipt, FileText, Share2, AtSign, Image, Target, Star,
  Upload, ExternalLink, BarChart2, AlertTriangle, UserCheck, Truck,
  LayoutDashboard, BookOpen
} from 'lucide-vue-next'
import UserMenu from '@/components/UserMenu.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import { useToast } from '@/composables/useToast'
import odooApi from '@/services/odoo'

const route = useRoute()
const { isAuthenticated, hasCompany, canViewModule, activeCompany } = useAuth()
const { unreadTotal, refresh: refreshInbox } = useInbox()
const toast = useToast()

const openingOdoo = ref(false)
async function openAccounting() {
  if (!activeCompany.value?.id || openingOdoo.value) return
  openingOdoo.value = true
  try {
    await odooApi.openOdooForCompany(activeCompany.value.id)
  } catch (err) {
    toast.error(err.message || 'No s\'ha pogut obrir la comptabilitat a Odoo')
  } finally {
    openingOdoo.value = false
  }
}
const isSidebarCollapsed = ref(false)
const expandedMenus = ref({})
const searchQuery = ref('')

const isAuthPage = computed(() => route.meta.layout === 'empty')

onMounted(() => {
  if (isAuthenticated.value) refreshInbox()
})
watch(isAuthenticated, (v) => {
  if (v) refreshInbox()
})
watch(() => route.fullPath, () => {
  if (isAuthenticated.value) refreshInbox()
})

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('ca-ES', { weekday: 'long', month: 'long', day: 'numeric' })
})

const menuItems = [
  {
    id: 'home',
    label: 'Inici',
    icon: Home,
    route: '/'
  },
  {
    id: 'dashboards',
    label: 'Dashboards',
    icon: LayoutDashboard,
    route: '/dashboards'
  },
  {
    id: 'catalog',
    label: 'Catàleg',
    icon: Package,
    submenu: [
      { label: 'Productes', route: '/products', icon: ShoppingBag, module: 'products' },
      { label: 'Inventari', route: '/inventory', icon: ClipboardList, module: 'inventory' }
    ]
  },
  {
    id: 'sales',
    label: 'Vendes',
    icon: Receipt,
    submenu: [
      { label: 'Factures', route: '/invoices', icon: FileText, module: 'invoices' },
      { label: 'Pressupostos', route: '/quotes', icon: ClipboardList, module: 'quotes' }
    ]
  },
  {
    id: 'purchases',
    label: 'Compres',
    icon: ShoppingBag,
    submenu: [
      { label: 'Factures de compra', route: '/purchase-invoices', icon: FileText, module: 'purchase_invoices' },
      { label: 'Pressupostos', route: '/purchase-quotes', icon: ClipboardList, module: 'purchase_quotes' }
    ]
  },
  {
    id: 'customers',
    label: 'Clients',
    icon: Users,
    route: '/customers',
    module: 'customers'
  },
  {
    id: 'providers',
    label: 'Proveïdors',
    icon: Truck,
    route: '/providers',
    module: 'providers'
  },
  {
    id: 'personnel',
    label: 'Personal',
    icon: UserCheck,
    route: '/personnel',
    module: 'personnel'
  },
  {
    id: 'social-crm',
    label: 'Social CRM',
    icon: Share2,
    module: 'social_crm',
    submenu: [
      { label: 'Resum',       route: '/social-crm',             icon: BarChart2 },
      { label: 'Comptes',     route: '/social-crm/accounts',    icon: Link2 },
      { label: 'Contingut',   route: '/social-crm/content',     icon: Image },
      { label: 'Campanyes',   route: '/social-crm/campaigns',   icon: Target },
      { label: 'Influencers', route: '/social-crm/influencers', icon: Star },
      { label: 'Atribució',   route: '/social-crm/attribution', icon: TrendingUp },
    ]
  }
]

// Accounts without a company see no modules — the sidebar stays empty.
// Otherwise modules are filtered by the active role's view permissions.
// (Items without a `module` key — like Home — are always shown.)
const visibleMenuItems = computed(() => {
  if (!hasCompany.value) return []
  return menuItems.reduce((acc, item) => {
    if (item.submenu) {
      // A submenu item is gated by its own `module`; the group's `module`
      // (if any) gates the whole group.
      if (item.module && !canViewModule(item.module)) return acc
      const submenu = item.submenu.filter(
        sub => !sub.module || canViewModule(sub.module),
      )
      if (submenu.length) acc.push({ ...item, submenu })
      return acc
    }
    if (item.module && !canViewModule(item.module)) return acc
    acc.push(item)
    return acc
  }, [])
})

const toggleMenu = (menuId) => {
  expandedMenus.value[menuId] = !expandedMenus.value[menuId]
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<template>
  <!-- Auth pages (login, register) — no sidebar/header -->
  <div v-if="isAuthPage" id="app">
    <router-view />
    <ToastContainer />
  </div>

  <!-- App pages — full layout -->
  <div v-else id="app" class="erp-layout">
    <!-- Top Bar (dark) -->
    <header class="top-bar">
      <div class="topbar-left">
        <button class="topbar-btn" @click="toggleSidebar" aria-label="Mostra o amaga el menú lateral">
          <Menu :size="20" />
        </button>
        <div class="topbar-search">
          <Search :size="16" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Cercar"
            class="search-input"
          />
        </div>
      </div>
      <div class="topbar-right">
        <button class="topbar-btn" aria-label="Ajuda">
          <HelpCircle :size="20" />
        </button>
        <router-link
          to="/inbox"
          class="topbar-btn notification-btn"
          aria-label="Bústia"
          :class="{ 'has-unread': unreadTotal > 0 }"
        >
          <Bell :size="20" />
          <span v-if="unreadTotal > 0" class="notification-badge">
            {{ unreadTotal > 9 ? '9+' : unreadTotal }}
          </span>
        </router-link>
        <button class="topbar-btn lang-btn">
          <Globe :size="16" />
          <span class="lang-label">CA</span>
        </button>
        <div class="topbar-divider"></div>
        <UserMenu />
      </div>
    </header>

    <div class="layout-body">
      <!-- Sidebar (dark) -->
      <aside class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
        <div class="sidebar-header">
          <div class="logo">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <span v-if="!isSidebarCollapsed" class="logo-text">Seshat ERP</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <ul class="nav-list">
            <li v-for="item in visibleMenuItems" :key="item.id" class="nav-item">
              <router-link 
                v-if="!item.submenu" 
                :to="item.route" 
                class="nav-link"
                active-class="active"
              >
                <component :is="item.icon" :size="20" class="nav-icon" />
                <span v-if="!isSidebarCollapsed" class="nav-label">{{ item.label }}</span>
              </router-link>
              <div v-else>
                <div 
                  class="nav-link" 
                  :class="{ 'has-submenu': true, 'expanded': expandedMenus[item.id] }"
                  @click="toggleMenu(item.id)"
                >
                  <component :is="item.icon" :size="20" class="nav-icon" />
                  <span v-if="!isSidebarCollapsed" class="nav-label">{{ item.label }}</span>
                  <component 
                    v-if="!isSidebarCollapsed"
                    :is="expandedMenus[item.id] ? ChevronDown : ChevronRight" 
                    :size="16" 
                    class="expand-icon" 
                  />
                </div>
                <ul v-if="expandedMenus[item.id] && !isSidebarCollapsed" class="submenu">
                  <li v-for="subitem in item.submenu" :key="subitem.route">
                    <router-link :to="subitem.route" class="submenu-link" active-class="active">
                      <component :is="subitem.icon" :size="16" class="submenu-icon" />
                      {{ subitem.label }}
                    </router-link>
                  </li>
                </ul>
              </div>
            </li>

            <!-- Acceso externo a la contabilidad en Odoo -->
            <li v-if="hasCompany" class="nav-item">
              <button
                type="button"
                class="nav-link nav-link-button"
                :disabled="openingOdoo"
                @click="openAccounting"
                title="Obre el mòdul de comptabilitat a Odoo"
              >
                <BookOpen :size="20" class="nav-icon" />
                <span v-if="!isSidebarCollapsed" class="nav-label">Comptabilitat</span>
                <ExternalLink v-if="!isSidebarCollapsed" :size="14" class="nav-external-icon" />
              </button>
            </li>
          </ul>

        </nav>

        <div v-if="hasCompany" class="sidebar-footer">
          <router-link to="/settings" class="nav-link" active-class="active">
            <Settings :size="20" class="nav-icon" />
            <span v-if="!isSidebarCollapsed" class="nav-label">Configuració</span>
          </router-link>
        </div>
      </aside>

      <!-- Mobile Overlay -->
      <div 
        class="sidebar-overlay" 
        :class="{ hidden: isSidebarCollapsed }" 
        @click="toggleSidebar"
      ></div>

      <!-- Main Content Area -->
      <div class="main-wrapper" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <main class="main-content">
          <router-view />
        </main>
      </div>
    </div>

    <ToastContainer />
  </div>
</template>

<style scoped>
/* ============================
   LAYOUT
   ============================ */
.erp-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-primary);
}

.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ============================
   TOP BAR (dark, full width)
   ============================ */
.top-bar {
  height: 56px;
  background: var(--topbar-bg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  flex-shrink: 0;
  z-index: 1100;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.topbar-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.topbar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.topbar-search {
  position: relative;
  max-width: 320px;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.25rem;
  background: #2D2D2D;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: var(--font-size-sm);
  color: #fff;
  font-family: var(--font-family);
  transition: all var(--transition-fast);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.search-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.2);
  background: #3D3D3D;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.notification-btn {
  position: relative;
  text-decoration: none;
}

.notification-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 18px;
  height: 18px;
  padding: 0 0.3rem;
  background: var(--accent-orange);
  color: white;
  border-radius: 9999px;
  font-size: 0.625rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  border: 2px solid var(--topbar-bg);
}

.notification-btn.has-unread {
  color: #fff;
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-family: var(--font-family);
}

.lang-label {
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

.topbar-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.15);
  margin: 0 0.5rem;
}

/* ============================
   SIDEBAR (dark)
   ============================ */
.sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-x: hidden;
  overflow-y: auto;
  flex-shrink: 0;
  height: calc(100vh - 56px);
}

.sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  padding: 1.5rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

/* ============================
   NAVIGATION
   ============================ */
.sidebar-nav {
  flex: 1;
  padding: 0.25rem 0;
  overflow-y: auto;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 2px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1.25rem;
  color: var(--text-sidebar);
  text-decoration: none;
  transition: all var(--transition-fast);
  cursor: pointer;
  position: relative;
  border-radius: 8px;
  margin: 0 0.5rem;
  font-weight: 400;
  font-size: var(--font-size-sm);
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-weight: 500;
}

.nav-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-label {
  flex: 1;
  white-space: nowrap;
}

/* Botón de acción (Contabilidad/Odoo) con apariencia de nav-link */
.nav-link-button {
  width: calc(100% - 1rem);
  background: none;
  border: none;
  font-family: inherit;
  text-align: left;
}

.nav-link-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-external-icon {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.3);
}

.expand-icon {
  color: rgba(255, 255, 255, 0.3);
  transition: transform 0.2s ease;
}

.submenu {
  list-style: none;
  padding: 0.25rem 0 0.25rem 0;
  margin: 0.125rem 0.5rem;
}

.submenu-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  color: var(--text-sidebar);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
  border-radius: 6px;
  margin: 1px 0;
}

.submenu-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.submenu-link.active {
  color: #fff;
  font-weight: 500;
}

.submenu-icon {
  flex-shrink: 0;
}

/* ============================
   SIDEBAR FOOTER
   ============================ */
.sidebar-footer {
  padding: 0.75rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: auto;
}

/* ============================
   MAIN CONTENT
   ============================ */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background: var(--bg-primary);
  height: calc(100vh - 56px);
}

.main-content {
  flex: 1;
  padding: var(--spacing-xl) clamp(1.25rem, 2.5vw, 2.5rem);
  width: 100%;
}

/* ============================
   MOBILE OVERLAY
   ============================ */
.sidebar-overlay {
  display: none;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 56px;
    z-index: 1050;
    transform: translateX(0);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 260px;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    top: 56px;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1040;
    opacity: 1;
    transition: opacity 0.3s ease;
  }

  .sidebar-overlay.hidden {
    display: none;
    opacity: 0;
  }

  .main-wrapper {
    margin-left: 0 !important;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: var(--spacing-lg) var(--spacing-md);
  }

  .topbar-search {
    max-width: 200px;
  }

  .lang-btn .lang-label {
    display: none;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: var(--spacing-md) var(--spacing-sm);
  }

  .topbar-search {
    display: none;
  }

  .top-bar {
    padding: 0 0.75rem;
  }
}
</style>
