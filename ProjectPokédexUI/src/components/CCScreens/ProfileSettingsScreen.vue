<template>
  <div class="screen">
    <div class="scroll-content">

      <h1 class="title">Profile</h1>
      <div class="divider"></div>

      <div class="columns">

        <div class="left-col">
          <div class="avatar-circle" @click="openAvatarPicker">
            <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" alt="Avatar" draggable="false" />
            <span v-else class="avatar-plus">+</span>
          </div>
          <input
            ref="avatarInput"
            class="avatar-input"
            type="file"
            accept="image/*"
            @change="onAvatarSelected"
          />
        </div>

        <div class="right-col">

          <!-- Editable fields (username / name / phone) -->
          <div class="field-row" v-for="f in fields" :key="f.key">
            <span class="bullet">•</span>

            <template v-if="f.editing">
              <input
                class="inline-input"
                :type="f.inputType"
                v-model="f.draft"
                :placeholder="f.value || f.placeholder"
                @keydown.enter="save(f)"
                @keydown.esc="cancelEdit(f)"
                @blur="save(f)"
                :ref="el => { if (el) el.focus() }"
              />
            </template>
            <template v-else>
              <span class="field-text" :class="{ muted: !f.value }">
                {{ f.value || f.placeholder }}
              </span>
            </template>

            <svg
              v-if="!f.editing"
              class="edit-btn"
              :class="{ pressed: f.pressed }"
              width="13" height="11"
              viewBox="0 0 13 11"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              @click="startEdit(f)"
              @pointerdown="f.pressed = true"
              @pointerup="f.pressed = false"
              @pointerleave="f.pressed = false"
            >
              <polygon points="0,0 9,0 13,5.5 9,11 0,11" fill="none" stroke="rgba(255,255,255,0.55)" stroke-width="1"/>
              <line x1="3" y1="3.5" x2="8" y2="3.5" stroke="rgba(255,255,255,0.55)" stroke-width="1" stroke-linecap="round"/>
              <line x1="3" y1="5.5" x2="7" y2="5.5" stroke="rgba(255,255,255,0.55)" stroke-width="1" stroke-linecap="round"/>
              <line x1="3" y1="7.5" x2="6" y2="7.5" stroke="rgba(255,255,255,0.55)" stroke-width="1" stroke-linecap="round"/>
            </svg>
          </div>

          <!-- Email (read-only) -->
          <div class="field-row">
            <span class="bullet">•</span>
            <span class="field-text muted">{{ email || '—' }}</span>
          </div>

        </div>
      </div>

      <h2 class="subtitle">Description</h2>
      <div class="divider"></div>
      <div class="bio-wrapper">
        <textarea
          class="bio-input"
          v-model="bioDraft"
          placeholder="Enter a bio..."
          @focus="bioFocused = true"
          @blur="onBioBlur"
        ></textarea>
        <div class="send-wrapper" :class="{ visible: bioFocused || bioDirty }">
          <span v-if="bioStatus" class="bio-status">{{ bioStatus }}</span>
          <svg
            class="send-btn"
            :class="{ pressed: sendPressed, disabled: bioSaving || !bioDirty }"
            width="18" height="14"
            viewBox="0 0 18 14"
            xmlns="http://www.w3.org/2000/svg"
            @pointerdown="sendPressed = true"
            @pointerup="sendPressed = false"
            @pointerleave="sendPressed = false"
            @click="submitBio"
          >
            <polygon points="0,0 18,7 0,14 4,7" fill="white"/>
          </svg>
        </div>
      </div>

      <h2 class="subtitle">Security</h2>
      <div class="divider"></div>

      <div v-if="!passwordOpen">
        <button
          class="btn"
          :class="{ pressed: changePassPressed }"
          @pointerdown="changePassPressed = true"
          @pointerup="changePassPressed = false"
          @pointerleave="changePassPressed = false"
          @click="passwordOpen = true"
        >
          Change Password
        </button>
      </div>

      <div v-else class="password-form">
        <input
          class="password-input"
          type="password"
          v-model="newPassword"
          placeholder="New password (min 6 chars)"
          @keydown.enter="submitPassword"
          @keydown.esc="closePassword"
          ref="passwordInput"
        />
        <div class="password-actions">
          <button class="btn small" @click="submitPassword" :disabled="passwordSaving">
            {{ passwordSaving ? '...' : 'Save' }}
          </button>
          <button class="btn small ghost" @click="closePassword" :disabled="passwordSaving">
            Cancel
          </button>
        </div>
        <div v-if="passwordStatus" class="password-status" :class="{ error: passwordError }">
          {{ passwordStatus }}
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { supabase } from '../../lib/supabase.js'
import { useAppState } from '../../composables/useAppState.js'

const { currentUser } = useAppState()

const meta  = computed(() => currentUser.value?.user_metadata ?? {})
const email = computed(() => currentUser.value?.email ?? '')

// ── Local avatar (data URL in localStorage, keyed by user id) ─────────────
const AVATAR_KEY = (id) => `pokedex.avatar.${id || 'anon'}`
const avatarUrl  = ref('')
const avatarInput = ref(null)

watch(() => currentUser.value?.id, (id) => {
  try {
    avatarUrl.value = localStorage.getItem(AVATAR_KEY(id)) ?? ''
  } catch {
    avatarUrl.value = ''
  }
}, { immediate: true })

function openAvatarPicker() {
  avatarInput.value?.click()
}

async function onAvatarSelected(e) {
  const file = e.target.files?.[0]
  e.target.value = ''   // allow re-picking the same file later
  if (!file) return

  try {
    const dataUrl = await fileToResizedDataUrl(file, 128)
    localStorage.setItem(AVATAR_KEY(currentUser.value?.id), dataUrl)
    avatarUrl.value = dataUrl
  } catch (err) {
    console.error('[Profile] avatar save', err)
  }
}

function fileToResizedDataUrl(file, size) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = reject
    reader.onload = () => {
      const img = new Image()
      img.onerror = reject
      img.onload = () => {
        // Cover-crop to a centered square at `size`x`size`
        const minSide = Math.min(img.width, img.height)
        const sx = (img.width  - minSide) / 2
        const sy = (img.height - minSide) / 2

        const canvas = document.createElement('canvas')
        canvas.width = size
        canvas.height = size
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, sx, sy, minSide, minSide, 0, 0, size, size)
        resolve(canvas.toDataURL('image/jpeg', 0.85))
      }
      img.src = reader.result
    }
    reader.readAsDataURL(file)
  })
}

function defaultUsername() {
  if (meta.value.username) return meta.value.username
  return email.value ? email.value.split('@')[0] : ''
}

const fields = reactive([
  { key: 'username', inputType: 'text', placeholder: 'username', value: '', draft: '', editing: false, pressed: false },
  { key: 'name',     inputType: 'text', placeholder: 'name',     value: '', draft: '', editing: false, pressed: false },
  { key: 'phone',    inputType: 'tel',  placeholder: 'phone',    value: '', draft: '', editing: false, pressed: false },
])

watch([meta, email], () => {
  fields[0].value = defaultUsername()
  fields[1].value = meta.value.name  ?? ''
  fields[2].value = meta.value.phone ?? ''
}, { immediate: true })

async function persistMeta(patch) {
  const { data, error } = await supabase.auth.updateUser({
    data: { ...meta.value, ...patch },
  })
  if (error) {
    console.error('[Profile] updateUser', error)
    return false
  }
  if (data?.user) currentUser.value = data.user
  return true
}

function startEdit(f) {
  f.draft = f.value
  f.editing = true
}

function cancelEdit(f) {
  f.editing = false
}

let savingField = null
async function save(f) {
  if (savingField === f) return
  savingField = f

  const trimmed = f.draft.trim()
  if (trimmed === f.value) {
    f.editing = false
    savingField = null
    return
  }

  const ok = await persistMeta({ [f.key]: trimmed })
  if (ok) f.value = trimmed
  f.editing = false
  savingField = null
}

// ── Bio ────────────────────────────────────────────────────────────────────
const bioDraft   = ref(meta.value.bio ?? '')
const bioFocused = ref(false)
const sendPressed = ref(false)
const bioSaving  = ref(false)
const bioStatus  = ref('')
let bioBlurTimer = null
let bioStatusTimer = null

watch(meta, (m) => {
  if (!bioFocused.value && !bioSaving.value) bioDraft.value = m.bio ?? ''
})

const bioDirty = computed(() => (bioDraft.value ?? '') !== (meta.value.bio ?? ''))

function onBioBlur() {
  bioBlurTimer = setTimeout(() => { bioFocused.value = false }, 150)
}

async function submitBio() {
  clearTimeout(bioBlurTimer)
  if (bioSaving.value || !bioDirty.value) {
    bioFocused.value = false
    return
  }

  bioSaving.value = true
  const ok = await persistMeta({ bio: bioDraft.value })
  bioSaving.value = false
  bioFocused.value = false
  bioStatus.value = ok ? 'Saved' : 'Failed'
  clearTimeout(bioStatusTimer)
  bioStatusTimer = setTimeout(() => { bioStatus.value = '' }, 1500)
}

// ── Change password ────────────────────────────────────────────────────────
const changePassPressed = ref(false)
const passwordOpen   = ref(false)
const newPassword    = ref('')
const passwordSaving = ref(false)
const passwordStatus = ref('')
const passwordError  = ref(false)
const passwordInput  = ref(null)
let passwordStatusTimer = null

watch(passwordOpen, async (open) => {
  if (open) {
    await nextTick()
    passwordInput.value?.focus()
  }
})

function closePassword() {
  passwordOpen.value = false
  newPassword.value = ''
  passwordStatus.value = ''
  passwordError.value = false
}

async function submitPassword() {
  if (passwordSaving.value) return
  const pw = newPassword.value
  if (!pw || pw.length < 6) {
    passwordError.value = true
    passwordStatus.value = 'Password must be at least 6 characters.'
    return
  }

  passwordSaving.value = true
  const { error } = await supabase.auth.updateUser({ password: pw })
  passwordSaving.value = false

  if (error) {
    passwordError.value = true
    passwordStatus.value = error.message
    return
  }

  passwordError.value = false
  passwordStatus.value = 'Password updated.'
  newPassword.value = ''
  clearTimeout(passwordStatusTimer)
  passwordStatusTimer = setTimeout(() => { closePassword() }, 1200)
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #084236;
  overflow-y: auto;
  box-sizing: border-box;
}

.screen::-webkit-scrollbar { display: none; }
.screen { scrollbar-width: none; }

.scroll-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 10px 12px 16px;
  gap: 6px;
  box-sizing: border-box;
  min-height: 100%;
}

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 22px;
  font-weight: 400;
  color: #ffffff;
  margin: 0;
  letter-spacing: 1px;
}

.divider {
  width: 100%;
  height: 1px;
  background-color: rgba(255, 255, 255, 0.4);
  margin-bottom: 4px;
}

.columns {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
}

.left-col {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 2px;
}

.avatar-circle {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: 1.5px dashed rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  position: relative;
  background: rgba(0, 0, 0, 0.18);
  transition: filter 0.08s ease, transform 0.08s ease;
}

.avatar-circle:active {
  filter: brightness(0.8);
  transform: scale(0.97);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  pointer-events: none;
}

.avatar-plus {
  font-family: 'Jura', sans-serif;
  font-size: 20px;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1;
  user-select: none;
}

.avatar-input {
  display: none;
}

.right-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
}

.field-row {
  display: flex;
  align-items: center;
  gap: 4px;
  width: 100%;
}

.bullet {
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  color: #ffffff;
  flex-shrink: 0;
  line-height: 1;
}

.field-text {
  font-family: 'Jura', sans-serif;
  font-size: 9px;
  color: #ffffff;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.field-text.muted {
  color: rgba(255, 255, 255, 0.45);
}

.inline-input {
  flex: 1;
  min-width: 0;
  height: 14px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  font-family: 'Jura', sans-serif;
  font-size: 9px;
  color: #ffffff;
  padding: 0 2px;
  box-sizing: border-box;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  caret-color: #ffffff;
}

.inline-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.edit-btn {
  flex-shrink: 0;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease;
  margin-left: auto;
}

.edit-btn.pressed {
  filter: brightness(0.5);
  transform: scale(0.9);
}

.subtitle {
  font-family: 'Iceland', sans-serif;
  font-size: 14px;
  font-weight: 400;
  color: #ffffff;
  margin: 4px 0 0;
  letter-spacing: 0.5px;
}

.bio-wrapper {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  width: 100%;
}

.bio-input {
  width: 100%;
  height: 52px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.4);
  border-radius: 2px;
  font-family: 'Jura', sans-serif;
  font-size: 9px;
  color: #ffffff;
  padding: 4px 6px;
  box-sizing: border-box;
  outline: none;
  resize: none;
  -webkit-tap-highlight-color: transparent;
  caret-color: #ffffff;
  line-height: 1.4;
}

.bio-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.send-wrapper {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  overflow: hidden;
  max-height: 0;
  opacity: 0;
  transition: max-height 0.25s ease, opacity 0.2s ease;
}

.send-wrapper.visible {
  max-height: 22px;
  opacity: 1;
}

.bio-status {
  font-family: 'Iceland', sans-serif;
  font-size: 9px;
  color: #7FD9C2;
  letter-spacing: 0.5px;
}

.send-btn {
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease, opacity 0.15s ease;
}

.send-btn.disabled {
  opacity: 0.35;
  cursor: default;
}

.send-btn.pressed:not(.disabled) {
  filter: brightness(0.5);
  transform: scale(0.9);
}

.btn {
  width: fit-content;
  padding: 3px 12px;
  background: transparent;
  border: 1.5px solid #ffffff;
  border-radius: 3px;
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #ffffff;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  transition: filter 0.08s ease, transform 0.08s ease;
}

.btn.small {
  padding: 2px 8px;
  font-size: 10px;
}

.btn.ghost {
  border-color: rgba(255, 255, 255, 0.45);
  color: rgba(255, 255, 255, 0.7);
}

.btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.btn:not(:disabled).pressed,
.btn:not(:disabled):active {
  filter: brightness(0.6);
  transform: scale(0.96);
}

/* ── Password form ── */
.password-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.password-input {
  width: 100%;
  height: 18px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 2px;
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  color: #ffffff;
  padding: 0 6px;
  box-sizing: border-box;
  outline: none;
  caret-color: #ffffff;
  -webkit-tap-highlight-color: transparent;
}

.password-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.password-actions {
  display: flex;
  gap: 6px;
}

.password-status {
  font-family: 'Jura', sans-serif;
  font-size: 9px;
  color: #7FD9C2;
}

.password-status.error {
  color: #FF8A82;
}
</style>
