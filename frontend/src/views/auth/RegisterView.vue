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

      <h2 class="auth-title">Crear cuenta</h2>
      <p class="auth-subtitle">Crea tu cuenta personal. Luego podrás configurar tus empresas</p>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div v-if="generalError" class="alert alert-error" role="alert">
          <AlertCircle :size="16" />
          <span>{{ generalError }}</span>
        </div>

        <!-- Personal info -->
        <fieldset class="form-fieldset">
          <legend class="form-legend">Datos personales</legend>

          <div class="form-row">
            <div class="form-group">
              <label for="first_name" class="form-label">Nombre <span class="required">*</span></label>
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                class="input"
                :class="{ 'input-error': errors.first_name }"
                placeholder="Juan"
                required
                autocomplete="given-name"
                @input="clearError('first_name')"
              />
              <span v-if="errors.first_name" class="field-error">{{ errors.first_name }}</span>
            </div>
            <div class="form-group">
              <label for="last_name" class="form-label">Apellidos</label>
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                class="input"
                placeholder="Pérez García"
                autocomplete="family-name"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="reg_email" class="form-label">Email <span class="required">*</span></label>
            <input
              id="reg_email"
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
            <label for="reg_password" class="form-label">Contraseña <span class="required">*</span></label>
            <div class="password-wrapper">
              <input
                id="reg_password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="input"
                :class="{ 'input-error': errors.password }"
                placeholder="Mínimo 8 caracteres"
                required
                autocomplete="new-password"
                @input="clearError('password')"
              />
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Ocultar' : 'Mostrar'"
              >
                <EyeOff v-if="showPassword" :size="18" />
                <Eye v-else :size="18" />
              </button>
            </div>
            <div class="password-hints">
              <span :class="['hint', { valid: form.password.length >= 8 }]">
                <CheckCircle2 v-if="form.password.length >= 8" :size="12" />
                <Circle v-else :size="12" />
                Mínimo 8 caracteres
              </span>
            </div>
            <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
          </div>

          <div class="form-group">
            <label for="confirm_password" class="form-label">Confirmar contraseña <span class="required">*</span></label>
            <input
              id="confirm_password"
              v-model="form.confirmPassword"
              type="password"
              class="input"
              :class="{ 'input-error': errors.confirmPassword }"
              placeholder="Repite la contraseña"
              required
              autocomplete="new-password"
              @input="clearError('confirmPassword')"
            />
            <span v-if="errors.confirmPassword" class="field-error">{{ errors.confirmPassword }}</span>
          </div>
        </fieldset>

        <button type="submit" class="btn btn-primary btn-block" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="loading-spinner loading-spinner-sm"></span>
          <span>{{ isSubmitting ? 'Creando cuenta...' : 'Crear cuenta' }}</span>
        </button>
      </form>

      <p class="auth-switch">
        ¿Ya tienes cuenta?
        <router-link to="/login" class="auth-link">Inicia sesión</router-link>
      </p>

      <p class="auth-footer-text">
        © {{ new Date().getFullYear() }} Sazed ERP
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Eye, EyeOff, AlertCircle, CheckCircle2, Circle } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const { register } = useAuth()
const toast = useToast()

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({})
const generalError = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)

function clearError(field) {
  delete errors[field]
  generalError.value = ''
}

function validate() {
  let valid = true
  if (!form.first_name.trim()) { errors.first_name = 'El nombre es obligatorio'; valid = false }
  if (!form.email.trim()) { errors.email = 'El email es obligatorio'; valid = false }
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'Formato de email inválido'; valid = false }
  if (!form.password) { errors.password = 'La contraseña es obligatoria'; valid = false }
  else if (form.password.length < 8) { errors.password = 'Mínimo 8 caracteres'; valid = false }
  if (form.password !== form.confirmPassword) { errors.confirmPassword = 'Las contraseñas no coinciden'; valid = false }
  return valid
}

async function handleRegister() {
  generalError.value = ''
  Object.keys(errors).forEach(k => delete errors[k])

  if (!validate()) return

  isSubmitting.value = true
  try {
    await register({
      first_name: form.first_name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      password: form.password,
    })
    toast.success('¡Cuenta creada! Configura tu primera empresa')
    router.push('/onboarding')
  } catch (err) {
    if (err.data?.email) {
      errors.email = Array.isArray(err.data.email) ? err.data.email[0] : err.data.email
    } else if (err.data?.non_field_errors) {
      generalError.value = err.data.non_field_errors[0]
    } else {
      generalError.value = err.message || 'Error al crear la cuenta. Reintenta.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* Reuse auth-page styles from LoginView */
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

.auth-card-wide {
  max-width: 500px;
}

.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
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
  margin-bottom: 1.5rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-fieldset {
  border: none;
  padding: 0;
  margin: 0;
}

.form-legend {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-color);
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-bottom: 0.5rem;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required {
  color: var(--error-color);
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

.password-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hint {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  transition: color var(--transition-fast);
}

.hint.valid {
  color: var(--success-color);
}

.input-error {
  border-color: var(--error-color) !important;
}

.field-error {
  font-size: var(--font-size-xs);
  color: var(--error-color);
}

.field-hint {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
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
  margin-top: 0.5rem;
}

.loading-spinner-sm {
  width: 1rem;
  height: 1rem;
  border-width: 2px;
  border-color: rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
}

.auth-switch {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: 1.25rem;
  margin-bottom: 0;
}

.auth-link {
  color: var(--primary-color);
  font-weight: 600;
  text-decoration: none;
}

.auth-link:hover {
  text-decoration: underline;
}

.auth-footer-text {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  margin-top: 1.25rem;
  margin-bottom: 0;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 1.75rem 1.25rem;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
