<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="close">
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h3>{{ isReply ? 'Respondre' : 'Nou missatge' }}</h3>
            <p v-if="isReply" class="reply-context">
              A {{ replyTo.recipient_name }} · Re: {{ replyTo.subject }}
            </p>
          </div>
          <button class="modal-close" @click="close">
            <X :size="20" />
          </button>
        </div>

        <form @submit.prevent="submit" class="modal-body">
          <!-- Recipient -->
          <div v-if="!isReply" class="form-group recipient-group" ref="recipientWrap">
            <label class="form-label">Per a <span class="required">*</span></label>
            <div class="recipient-input-wrap">
              <div v-if="selectedRecipient" class="recipient-pill">
                <div class="pill-avatar">
                  <img v-if="selectedRecipient.avatar" :src="selectedRecipient.avatar" :alt="selectedRecipient.full_name" />
                  <span v-else>{{ selectedRecipient.initials }}</span>
                </div>
                <span class="pill-name">{{ selectedRecipient.full_name }}</span>
                <span class="pill-email">{{ selectedRecipient.email }}</span>
                <button type="button" class="pill-remove" @click="clearRecipient">
                  <X :size="14" />
                </button>
              </div>
              <input
                v-else
                v-model="search"
                class="input"
                placeholder="Nom o correu del company"
                autocomplete="off"
                @input="onSearchInput"
                @focus="showSuggestions = true"
              />
            </div>
            <div
              v-if="!selectedRecipient && showSuggestions && (searching || suggestions.length || search)"
              class="suggestions"
            >
              <div v-if="searching" class="suggestion-empty">Cercant…</div>
              <div v-else-if="!suggestions.length" class="suggestion-empty">
                Sense resultats en aquesta empresa
              </div>
              <button
                v-for="user in suggestions"
                :key="user.id"
                type="button"
                class="suggestion-item"
                @click="pickRecipient(user)"
              >
                <div class="suggestion-avatar">
                  <img v-if="user.avatar" :src="user.avatar" :alt="user.full_name" />
                  <span v-else>{{ user.initials }}</span>
                </div>
                <div class="suggestion-info">
                  <span class="suggestion-name">{{ user.full_name || user.email }}</span>
                  <span class="suggestion-email">{{ user.email }}</span>
                </div>
              </button>
            </div>
          </div>

          <!-- Subject -->
          <div class="form-group">
            <label class="form-label">Assumpte <span class="required">*</span></label>
            <input
              v-model="subject"
              class="input"
              required
              maxlength="200"
              placeholder="Títol del missatge"
            />
          </div>

          <!-- Body -->
          <div class="form-group">
            <label class="form-label">Missatge <span class="required">*</span></label>
            <textarea
              v-model="body"
              class="input textarea"
              required
              rows="8"
              placeholder="Escriu aquí…"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn btn-ghost" @click="close">Cancel·lar</button>
            <button type="submit" class="btn btn-primary" :disabled="!canSend || sending">
              <Send :size="14" />
              {{ sending ? 'Enviant…' : 'Enviar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { X, Send } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'
import inboxApi from '@/services/inbox'

const props = defineProps({
  // When replying: { id, recipient_id, recipient_name, subject }
  replyTo: { type: Object, default: null },
})
const emit = defineEmits(['close', 'sent'])

const toast = useToast()

const isReply = computed(() => !!props.replyTo)

const search = ref('')
const suggestions = ref([])
const searching = ref(false)
const showSuggestions = ref(false)
const selectedRecipient = ref(null)
let searchTimer = null

const subject = ref(isReply.value ? `Re: ${props.replyTo.subject}` : '')
const body = ref('')
const sending = ref(false)
const recipientWrap = ref(null)

const canSend = computed(() => {
  if (!subject.value.trim() || !body.value.trim()) return false
  if (isReply.value) return true
  return !!selectedRecipient.value
})

function onSearchInput() {
  showSuggestions.value = true
  if (searchTimer) clearTimeout(searchTimer)
  const q = search.value.trim()
  searching.value = true
  searchTimer = setTimeout(async () => {
    try {
      suggestions.value = await inboxApi.searchUsers(q)
    } catch {
      suggestions.value = []
    } finally {
      searching.value = false
    }
  }, 180)
}

function pickRecipient(user) {
  selectedRecipient.value = user
  showSuggestions.value = false
  suggestions.value = []
  search.value = ''
}

function clearRecipient() {
  selectedRecipient.value = null
  search.value = ''
  suggestions.value = []
}

function close() {
  emit('close')
}

async function submit() {
  if (!canSend.value || sending.value) return
  sending.value = true
  try {
    const payload = {
      subject: subject.value.trim(),
      body: body.value.trim(),
    }
    if (isReply.value) {
      payload.recipient_id = props.replyTo.recipient_id
      payload.parent = props.replyTo.id
    } else {
      payload.recipient_id = selectedRecipient.value.id
    }
    const message = await inboxApi.sendMessage(payload)
    toast.success('Missatge enviat')
    emit('sent', message)
  } catch (err) {
    toast.error(err.message || 'Error en enviar el missatge')
  } finally {
    sending.value = false
  }
}

function onClickOutside(e) {
  if (recipientWrap.value && !recipientWrap.value.contains(e.target)) {
    showSuggestions.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
  if (searchTimer) clearTimeout(searchTimer)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9000;
  padding: var(--spacing-lg);
}

.modal-card {
  background: white;
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 560px;
  max-height: 92vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  gap: 1rem;
}

.modal-header h3 { margin: 0 0 0.125rem; }

.reply-context {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: var(--border-radius-sm);
  display: flex;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.modal-body {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  position: relative;
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.required { color: var(--error-color); }

.textarea {
  resize: vertical;
  min-height: 120px;
  font-family: var(--font-family);
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.25rem;
}

/* Recipient autocomplete */
.recipient-group { position: relative; }

.recipient-input-wrap { position: relative; }

.recipient-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem 0.25rem 0.25rem;
  background: var(--primary-light);
  border-radius: 9999px;
  font-size: var(--font-size-sm);
}

.pill-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.6875rem;
  overflow: hidden;
  flex-shrink: 0;
}

.pill-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.pill-name {
  font-weight: 500;
  color: var(--text-primary);
}

.pill-email {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
}

.pill-remove {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-tertiary);
}

.pill-remove:hover {
  background: rgba(0, 0, 0, 0.12);
  color: var(--text-primary);
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  max-height: 240px;
  overflow-y: auto;
  z-index: 10;
}

.suggestion-empty {
  padding: 0.75rem 1rem;
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  background: none;
  border: none;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  text-align: left;
  font-family: var(--font-family);
  transition: background var(--transition-fast);
}

.suggestion-item:hover {
  background: var(--bg-hover);
}

.suggestion-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.75rem;
  overflow: hidden;
  flex-shrink: 0;
}

.suggestion-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.suggestion-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.suggestion-name {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.suggestion-email {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}
</style>
