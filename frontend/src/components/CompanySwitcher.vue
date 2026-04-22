<template>
  <div class="company-switcher" ref="containerRef">
    <button class="switcher-trigger" @click="isOpen = !isOpen" :aria-expanded="isOpen">
      <div class="user-avatar-sm">
        <img v-if="user?.avatar" :src="user.avatar" :alt="user.full_name" />
        <span v-else>{{ user?.initials || '?' }}</span>
      </div>
      <ChevronDown :size="14" class="switcher-arrow" :class="{ rotated: isOpen }" />
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="switcher-dropdown">
        <!-- User header -->
        <div class="dropdown-user">
          <p class="dropdown-user-name">{{ user?.full_name || 'Mi cuenta' }}</p>
          <p class="dropdown-user-email">{{ user?.email }}</p>
        </div>

        <div class="dropdown-divider"></div>

        <!-- Company list -->
        <div class="dropdown-section-label">Empresas</div>
        <div class="dropdown-companies">
          <button
            v-for="company in companies"
            :key="company.id"
            class="dropdown-company"
            :class="{ active: company.id === activeCompany?.id }"
            @click="handleSwitch(company.id)"
            :disabled="switching"
          >
            <div class="company-icon-sm">
              <img v-if="company.logo" :src="company.logo" :alt="company.name" />
              <span v-else>{{ company.name?.charAt(0) }}</span>
            </div>
            <span class="company-label">{{ company.name }}</span>
            <Check v-if="company.id === activeCompany?.id" :size="14" class="check-icon" />
          </button>
        </div>

        <div class="dropdown-divider"></div>

        <!-- Actions -->
        <router-link to="/profile" class="dropdown-item" @click="isOpen = false">
          <UserIcon :size="16" />
          Mi cuenta
        </router-link>
        <router-link
          v-if="activeRole === 'owner' || activeRole === 'admin'"
          to="/settings/company"
          class="dropdown-item"
          @click="isOpen = false"
        >
          <Settings :size="16" />
          Configuración de empresa
        </router-link>
        <div class="dropdown-divider"></div>
        <button class="dropdown-item dropdown-item-danger" @click="handleLogout">
          <LogOut :size="16" />
          Cerrar sesión
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChevronDown, Check, User as UserIcon, Settings, LogOut,
} from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { user, companies, activeCompany, activeRole, switchCompany, logout } = useAuth()
const toast = useToast()

const isOpen = ref(false)
const containerRef = ref(null)
const switching = ref(false)

async function handleSwitch(companyId) {
  if (companyId === activeCompany.value?.id) { isOpen.value = false; return }
  switching.value = true
  try {
    await switchCompany(companyId)
    toast.success('Empresa cambiada')
    isOpen.value = false
  } catch {
    toast.error('Error al cambiar de empresa')
  } finally {
    switching.value = false
  }
}

async function handleLogout() {
  isOpen.value = false
  await logout()
  router.push('/login')
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
.company-switcher {
  position: relative;
}

.switcher-trigger {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 9999px;
  transition: all var(--transition-fast);
}

.switcher-trigger:hover {
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

.switcher-arrow {
  color: rgba(255, 255, 255, 0.6);
  transition: transform var(--transition-fast);
}

.switcher-arrow.rotated {
  transform: rotate(180deg);
}

/* Dropdown */
.switcher-dropdown {
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

.dropdown-user {
  padding: 0.875rem 1rem;
}

.dropdown-user-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  margin: 0 0 0.125rem;
}

.dropdown-user-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin: 0;
}

.dropdown-divider {
  height: 1px;
  background: var(--border-color);
}

.dropdown-section-label {
  padding: 0.5rem 1rem 0.25rem;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dropdown-companies {
  padding: 0.25rem 0.5rem;
  max-height: 180px;
  overflow-y: auto;
}

.dropdown-company {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem;
  background: none;
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-family: var(--font-family);
  font-size: var(--font-size-sm);
  color: var(--text-primary);
  transition: background var(--transition-fast);
  text-align: left;
}

.dropdown-company:hover {
  background: var(--bg-hover);
}

.dropdown-company.active {
  background: var(--primary-light);
}

.company-icon-sm {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  overflow: hidden;
  flex-shrink: 0;
}

.company-icon-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.company-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.check-icon {
  color: var(--primary-color);
  flex-shrink: 0;
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
