<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="currentColor"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <span class="logo-text">Sazed ERP</span>
      </div>

      <h2 class="auth-title">Iniciar sesión</h2>
      <p class="auth-subtitle">Accede a tu cuenta para gestionar tu empresa</p>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div v-if="generalError" class="alert alert-error" role="alert">
          <AlertCircle :size="16" />
          <span>{{ generalError }}</span>
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="input"
            :class="{ 'input-error': errors.email }"
            placeholder="tu@empresa.com"
            required
            autocomplete="email"
            @input="clearError('email')"
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Contraseña</label>
          <div class="password-wrapper">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': errors.password }"
              placeholder="••••••••"
              required
              autocomplete="current-password"
              @input="clearError('password')"
            />
            <button
              type="button"
              class="password-toggle"
              @click="showPassword = !showPassword"
              :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            >
              <EyeOff v-if="showPassword" :size="18" />
              <Eye v-else :size="18" />
            </button>
          </div>
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="loading-spinner loading-spinner-sm"></span>
          <span>{{ isSubmitting ? 'Iniciando sesión...' : 'Iniciar sesión' }}</span>
        </button>
      </form>

      <div class="auth-divider">
        <span>o</span>
      </div>

      <router-link to="/register" class="btn btn-secondary btn-block">
        Crear cuenta
      </router-link>

      <p class="auth-footer-text">
        © {{ new Date().getFullYear() }} Sazed ERP
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Eye, EyeOff, AlertCircle } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const { login } = useAuth()
const toast = useToast()

const form = reactive({ email: '', password: '' })
const errors = reactive({})
const generalError = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)

function clearError(field) {
  delete errors[field]
  generalError.value = ''
}

async function handleLogin() {
  // Reset
  generalError.value = ''
  Object.keys(errors).forEach(k => delete errors[k])

  // Validate
  if (!form.email) { errors.email = 'El email es obligatorio'; return }
  if (!form.password) { errors.password = 'La contraseña es obligatoria'; return }

  isSubmitting.value = true
  try {
    await login(form.email, form.password)
    toast.success('Sesión iniciada')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    if (err.status === 400 || err.data) {
      generalError.value = err.data?.non_field_errors?.[0] || err.message || 'Credenciales incorrectas'
    } else {
      generalError.value = 'No se pudo conectar al servidor. Reintenta.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* ============================
   AUTH PAGE — shared layout
   ============================ */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: var(--border-radius-lg);
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.auth-logo .logo-icon {
  width: 36px;
  height: 36px;
  color: var(--primary-color);
}

.auth-logo .logo-icon svg {
  width: 100%;
  height: 100%;
}

.auth-logo .logo-text {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.auth-title {
  text-align: center;
  margin-bottom: 0.25rem;
  font-size: var(--font-size-2xl);
}

.auth-subtitle {
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: 1.75rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.125rem;
}

/* Form elements */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.password-wrapper {
  position: relative;
}

.password-wrapper .input {
  padding-right: 2.75rem;
}

.password-toggle {
  position: absolute;
  right: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
}

.password-toggle:hover {
  color: var(--text-secondary);
}

.input-error {
  border-color: var(--error-color) !important;
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--error-color);
}

.alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
}

.alert-error {
  background: var(--error-light);
  color: var(--error-color);
}

.btn-block {
  width: 100%;
}

.loading-spinner-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
  border-top-color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
}

/* Divider */
.auth-divider {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 1.25rem 0;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm);
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border-color);
}

.auth-footer-text {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 1.5rem;
  margin-bottom: 0;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 480px) {
  .auth-card {
    padding: 1.75rem 1.25rem;
  }
}
</style>
