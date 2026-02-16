<script setup>
import { ref, computed } from 'vue'
import { 
  Home, Package, DollarSign, Users, Megaphone, 
  Globe, Link, Settings, ChevronDown, ChevronRight,
  Menu, Search, Bell, HelpCircle, Eye, ShoppingBag, Archive,
  ClipboardList, Wallet, CreditCard, TrendingUp, FolderOpen, Plus
} from 'lucide-vue-next'

const isSidebarCollapsed = ref(false)
const expandedMenus = ref({})
const searchQuery = ref('')

const currentDate = computed(() => {
  const now = new Date()
  return now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const menuItems = [
  { 
    id: 'home', 
    label: 'Home', 
    icon: Home, 
    route: '/' 
  },
  { 
    id: 'catalog', 
    label: 'Catalog', 
    icon: Package, 
    submenu: [
      { label: 'Products', route: '/products', icon: ShoppingBag },
      { label: 'Collections', route: '/collections', icon: Archive },
      { label: 'Inventory', route: '/inventory', icon: ClipboardList },
      { label: 'Orders', route: '/orders', icon: ClipboardList }
    ]
  },
  { 
    id: 'finances', 
    label: 'Finances', 
    icon: DollarSign, 
    submenu: [
      { label: 'Wallet', route: '/wallet', icon: Wallet },
      { label: 'Uvodo Card', route: '/card', icon: CreditCard },
      { label: 'Payout', route: '/payout', icon: TrendingUp }
    ]
  },
  { 
    id: 'customers', 
    label: 'Customers', 
    icon: Users, 
    route: '/customers' 
  },
  { 
    id: 'marketing', 
    label: 'Marketing', 
    icon: Megaphone, 
    route: '/marketing' 
  }
]

const salesChannels = [
  { id: 'online-store', label: 'Online Store', icon: Globe, route: '/online-store' },
  { id: 'sell-link', label: 'Sell Via Link', icon: Link, route: '/sell-link' }
]

const projects = [
  { id: '1', name: 'Website Redesign', color: '#8B5CF6' },
  { id: '2', name: 'Mobile App', color: '#EC4899' },
  { id: '3', name: 'Marketing Campaign', color: '#10B981' },
  { id: '4', name: 'Product Launch', color: '#F59E0B' },
]

const toggleMenu = (menuId) => {
  expandedMenus.value[menuId] = !expandedMenus.value[menuId]
}

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}
</script>

<template>
  <div id="app" class="erp-layout">
    <!-- Top Bar (dark) -->
    <header class="top-bar">
      <div class="topbar-left">
        <button class="topbar-btn" @click="toggleSidebar" aria-label="Toggle sidebar">
          <Menu :size="20" />
        </button>
        <div class="topbar-search">
          <Search :size="16" class="search-icon" />
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search" 
            class="search-input"
          />
        </div>
      </div>
      <div class="topbar-right">
        <button class="topbar-btn" aria-label="Help">
          <HelpCircle :size="20" />
        </button>
        <button class="topbar-btn notification-btn" aria-label="Notifications">
          <Bell :size="20" />
          <span class="notification-dot"></span>
        </button>
        <button class="topbar-btn lang-btn">
          <Globe :size="16" />
          <span class="lang-label">EN</span>
        </button>
        <div class="topbar-divider"></div>
        <button class="avatar-btn">
          <div class="user-avatar">A</div>
        </button>
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
            <span v-if="!isSidebarCollapsed" class="logo-text">Sazed ERP</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <ul class="nav-list">
            <li v-for="item in menuItems" :key="item.id" class="nav-item">
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
          </ul>

          <div class="nav-divider">
            <span v-if="!isSidebarCollapsed" class="divider-label">Sales channels</span>
          </div>

          <ul class="nav-list">
            <li v-for="channel in salesChannels" :key="channel.id" class="nav-item">
              <router-link :to="channel.route" class="nav-link" active-class="active">
                <component :is="channel.icon" :size="20" class="nav-icon" />
                <span v-if="!isSidebarCollapsed" class="nav-label">{{ channel.label }}</span>
                <Eye v-if="!isSidebarCollapsed" :size="16" class="channel-eye" />
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- Projects section -->
        <div v-if="!isSidebarCollapsed" class="sidebar-projects">
          <div class="projects-header">
            <span class="divider-label">Projects</span>
            <button class="projects-add-btn">
              <Plus :size="16" />
            </button>
          </div>
          <ul class="projects-list">
            <li v-for="project in projects" :key="project.id">
              <button class="project-item">
                <span class="project-dot" :style="{ backgroundColor: project.color }"></span>
                <span class="project-name">{{ project.name }}</span>
              </button>
            </li>
          </ul>
        </div>

        <div class="sidebar-footer">
          <router-link to="/settings" class="nav-link" active-class="active">
            <Settings :size="20" class="nav-icon" />
            <span v-if="!isSidebarCollapsed" class="nav-label">Settings</span>
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
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: var(--accent-orange);
  border-radius: 50%;
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

.avatar-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  border-radius: 50%;
  transition: all var(--transition-fast);
}

.avatar-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-sm);
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

.nav-divider {
  padding: 1.25rem 1.25rem 0.5rem;
  margin-top: 0.25rem;
}

.divider-label {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.35);
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.08em;
}

.channel-eye {
  margin-left: auto;
  opacity: 0.35;
  color: rgba(255, 255, 255, 0.5);
}

/* ============================
   PROJECTS SECTION
   ============================ */
.sidebar-projects {
  padding: 0 0.5rem;
  margin-top: 0.5rem;
}

.projects-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.75rem;
  margin-bottom: 0.375rem;
}

.projects-add-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.35);
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
}

.projects-add-btn:hover {
  color: #fff;
}

.projects-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.project-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: var(--font-size-sm);
  background: none;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
  text-align: left;
}

.project-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.project-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.project-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
