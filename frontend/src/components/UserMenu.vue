<template>
  <div class="user-menu" ref="containerRef">
    <button
      class="user-menu-trigger"
      @click="isOpen = !isOpen"
      :aria-expanded="isOpen"
      aria-label="Menú de usuario"
    >
      <div class="user-avatar-sm">
        <img v-if="user?.avatar" :src="user.avatar" :alt="user.full_name" />
        <span v-else>{{ user?.initials || '?' }}</span>
      </div>
      <ChevronDown :size="14" class="trigger-arrow" :class="{ rotated: isOpen }" />
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="user-menu-dropdown">
        <!-- Header -->
        <div class="dropdown-header">
          <div class="header-avatar">
            <img v-if="user?.avatar" :src="user.avatar" :alt="user.full_name" />
            <span v-else>{{ user?.initials || '?' }}</span>
          </div>
          <div class="header-info">
            <p class="header-name">{{ user?.full_name || 'Mi cuenta' }}</p>
            <p class="header-email">{{ user?.email }}</p>
            <span
              v-if="activeRole"
              class="header-role"
              :class="roleBadgeClass(activeRole)"
            >
              {{ roleLabel(activeRole) }}<span
                v-if="activeCompany?.name"
              > · {{ activeCompany.name }}</span>
            </span>
          </div>
        </div>

        <div class="dropdown-divider"></div>

        <!-- Actions -->
        <router-link to="/account" class="dropdown-item" @click="isOpen = false">
          <UserIcon :size="16" />
          <span>Gestión de cuenta</span>
        </router-link>
        <router-link to="/companies" class="dropdown-item" @click="isOpen = false">
          <Building2 :size="16" />
          <span>Gestión de empresas</span>
        </router-link>

        <div class="dropdown-divider"></div>

        <button class="dropdown-item dropdown-item-danger" @click="handleLogout">
          <LogOut :size="16" />
          <span>Cerrar sesión</span>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChevronDown, User as UserIcon, Building2, LogOut,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, activeCompany, activeRole, logout } = useAuth()

const isOpen = ref(false)
const containerRef = ref(null)

async function handleLogout() {
  isOpen.value = false
  await logout()
  router.push('/login')
}

function roleLabel(role) {
  const map = { owner: 'Propietario', admin: 'Admin', editor: 'Editor', viewer: 'Lector' }
  return map[role] || role
}

function roleBadgeClass(role) {
  const map = {
    owner: 'role-owner',
    admin: 'role-admin',
    editor: 'role-editor',
    viewer: 'role-viewer',
  }
  return map[role] || 'role-viewer'
}

function onClickOutside(e) {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-menu-trigger {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 9999px;
  transition: background var(--transition-fast);
}

.user-menu-trigger:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-avatar-sm {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-xs);
  overflow: hidden;
}

.user-avatar-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.trigger-arrow {
  color: rgba(255, 255, 255, 0.6);
  transition: transform var(--transition-fast);
}

.trigger-arrow.rotated {
  transform: rotate(180deg);
}

/* Dropdown */
.user-menu-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 280px;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid var(--border-color);
  z-index: 2000;
  overflow: hidden;
}

.dropdown-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
}

.header-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--font-size-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.header-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.header-info {
  flex: 1;
  min-width: 0;
}

.header-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin: 0 0 0.125rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0 0 0.375rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-role {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-role.role-owner {
  background: rgba(102, 126, 234, 0.12);
  color: var(--primary-color);
}

.header-role.role-admin {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.header-role.role-editor {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.header-role.role-viewer {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 1rem;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  text-decoration: none;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  font-family: var(--font-family);
  transition: background var(--transition-fast);
  text-align: left;
}

.dropdown-item:hover {
  background: var(--bg-hover);
}

.dropdown-item-danger {
  color: var(--error-color);
}

.dropdown-item-danger:hover {
  background: var(--error-light);
}

/* Transition */
.dropdown-enter-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.dropdown-leave-active {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.96);
}
</style>
