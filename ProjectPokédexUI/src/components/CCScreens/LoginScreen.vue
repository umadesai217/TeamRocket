<template>
  <div class="screen">

    <h1 class="title">Login</h1>

    <div class="fields">
      <div class="field-group">
        <label class="field-label">Email</label>
        <input
          class="field-input"
          type="email"
          v-model="email"
          placeholder="you@example.com"
          autocomplete="email"
          :disabled="busy"
        />
      </div>
      <div class="field-group">
        <label class="field-label">Password</label>
        <input
          class="field-input"
          type="password"
          v-model="password"
          placeholder="••••••••"
          autocomplete="current-password"
          :disabled="busy"
          @keydown.enter="handleLogin"
        />
      </div>
    </div>

    <!-- Error / status message -->
    <p class="msg error" v-if="errorMsg">{{ errorMsg }}</p>
    <p class="msg success" v-if="successMsg">{{ successMsg }}</p>

    <div class="buttons">
      <button
        class="btn"
        :class="{ pressed: submitPressed }"
        :disabled="busy"
        @click="handleLogin"
        @pointerdown="submitPressed = true"
        @pointerup="submitPressed = false"
        @pointerleave="submitPressed = false"
      >
        {{ busy ? '...' : 'Submit' }}
      </button>
      <button
        class="btn"
        :class="{ pressed: createPressed }"
        :disabled="busy"
        @click="handleSignup"
        @pointerdown="createPressed = true"
        @pointerup="createPressed = false"
        @pointerleave="createPressed = false"
      >
        Create Account
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../../composables/useAuth.js'

const { login, signup } = useAuth()

const email      = ref('')
const password   = ref('')
const busy       = ref(false)
const errorMsg   = ref('')
const successMsg = ref('')
const submitPressed = ref(false)
const createPressed = ref(false)

function clearMessages() {
  errorMsg.value   = ''
  successMsg.value = ''
}

async function handleLogin() {
  clearMessages()
  if (!email.value || !password.value) {
    errorMsg.value = 'Please enter your email and password.'
    return
  }
  busy.value = true
  try {
    await login(email.value.trim(), password.value)
    // on success, useAuth sets screen to 'default' and this component unmounts
  } catch (err) {
    errorMsg.value = friendlyError(err.message)
  }
  busy.value = false
}

async function handleSignup() {
  clearMessages()
  if (!email.value || !password.value) {
    errorMsg.value = 'Please enter an email and password.'
    return
  }
  if (password.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters.'
    return
  }
  busy.value = true
  try {
    const data = await signup(email.value.trim(), password.value)
    // If email confirmation is enabled, session will be null
    if (!data.session) {
      successMsg.value = 'Account created! Check your email to confirm.'
    }
    // If disabled, useAuth already navigated to default screen
  } catch (err) {
    errorMsg.value = friendlyError(err.message)
  }
  busy.value = false
}

function friendlyError(msg) {
  if (msg.includes('Invalid login'))   return 'Incorrect email or password.'
  if (msg.includes('already registered')) return 'An account with that email already exists.'
  if (msg.includes('User already registered')) return 'An account with that email already exists.'
  if (msg.includes('Password should')) return 'Password must be at least 6 characters.'
  return msg
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #084236;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 16px 12px;
  box-sizing: border-box;
  gap: 14px;
}

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 32px;
  font-weight: 400;
  color: #ffffff;
  margin: 0;
  letter-spacing: 1px;
}

.fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.field-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.field-label {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #ffffff;
}

.field-input {
  width: 80%;
  height: 22px;
  background: transparent;
  border: 1.5px solid #ffffff;
  border-radius: 3px;
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #ffffff;
  padding: 0 8px;
  box-sizing: border-box;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  caret-color: #ffffff;
}

.field-input::placeholder { color: rgba(255, 255, 255, 0.3); }
.field-input:disabled     { opacity: 0.5; }

.msg {
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  text-align: center;
  margin: 0;
  padding: 0 8px;
}
.msg.error   { color: #ff8080; }
.msg.success { color: #7fff9e; }

.buttons {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 25px;
  width: 100%;
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

.btn:disabled {
  opacity: 0.5;
  cursor: default;
}

.btn.pressed {
  filter: brightness(0.6);
  transform: scale(0.96);
}
</style>
