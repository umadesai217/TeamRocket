<template>
  <div class="screen">
    <h1 class="title">APPLICATION</h1>

    <div class="row">
      <span class="label">Rotom provider</span>
      <select class="select" v-model="provider">
        <option value="claude">Claude (Anthropic)</option>
        <option value="gemini">Gemini (Google)</option>
      </select>
    </div>

    <div class="row">
      <span class="label">Rotom model</span>
      <select class="select" v-model="model">
        <option v-for="m in availableModels" :key="m.id" :value="m.id">{{ m.label }}</option>
      </select>
    </div>

    <div class="row">
      <span class="label">Refresh data</span>
      <button class="action" @click="refresh" :disabled="refreshing">
        {{ refreshing ? '...' : refreshed ? 'DONE' : 'GO' }}
      </button>
    </div>

    <div class="row">
      <span class="label">Clear scan history</span>
      <button
        class="action"
        :class="{ danger: clearConfirm, busy: clearing }"
        @click="clearScans"
        :disabled="clearing"
      >
        {{ clearing ? '...' : clearConfirm ? 'CONFIRM' : 'CLEAR' }}
      </button>
    </div>

    <div v-if="clearError" class="error">{{ clearError }}</div>

    <div class="about">
      <div class="about-row">
        <span class="about-key">Account</span>
        <span class="about-val">{{ email }}</span>
      </div>
      <div class="about-row">
        <span class="about-key">Version</span>
        <span class="about-val">{{ version }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { supabase } from '../../lib/supabase.js'
import { useAppState } from '../../composables/useAppState.js'
import { useLibraryStore } from '../../composables/useLibraryStore.js'
import { useSettings } from '../../composables/useSettings.js'
import { CLAUDE_MODELS } from '../../lib/claude.js'
import { GEMINI_MODELS } from '../../lib/gemini.js'

const { currentUser } = useAppState()
const { loadLibrary, loadScans } = useLibraryStore()
const { provider, model } = useSettings()

const availableModels = computed(() =>
  provider.value === 'gemini' ? GEMINI_MODELS : CLAUDE_MODELS,
)

const version = '1.0.0'
const email = currentUser.value?.email ?? '—'

// ── Refresh ──
const refreshing = ref(false)
const refreshed  = ref(false)
let refreshTimer = null

async function refresh() {
  if (refreshing.value) return
  refreshing.value = true
  refreshed.value  = false
  try {
    await Promise.all([loadLibrary(), loadScans()])
    refreshed.value = true
    clearTimeout(refreshTimer)
    refreshTimer = setTimeout(() => { refreshed.value = false }, 1500)
  } finally {
    refreshing.value = false
  }
}

// ── Clear scan history (two-tap confirm) ──
const clearConfirm = ref(false)
const clearing     = ref(false)
const clearError   = ref('')
let confirmTimer = null

async function clearScans() {
  if (clearing.value) return

  if (!clearConfirm.value) {
    clearConfirm.value = true
    clearError.value = ''
    clearTimeout(confirmTimer)
    confirmTimer = setTimeout(() => { clearConfirm.value = false }, 4000)
    return
  }

  clearTimeout(confirmTimer)
  clearConfirm.value = false
  clearing.value = true
  clearError.value = ''

  try {
    const { error } = await supabase
      .from('scans')
      .delete()
      .eq('user_id', currentUser.value?.id)

    if (error) throw error
    await loadScans()
  } catch (err) {
    console.error('[AppSettings] clearScans', err)
    clearError.value = 'Could not clear scan history. Try again.'
  } finally {
    clearing.value = false
  }
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #0f1a1a;
  color: #E3F4EE;
  font-family: 'Jura', sans-serif;
  padding: 12px 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 9px;
  overflow-y: auto;
}

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 20px;
  font-weight: 400;
  color: #FFD624;
  -webkit-text-stroke: 1px #005B98;
  margin: 0 0 4px;
  letter-spacing: 1.5px;
  text-align: center;
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.label {
  font-size: 11px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.select {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #E3F4EE;
  background: #101F13;
  border: 1.5px solid #A2A3B1;
  border-radius: 3px;
  padding: 2px 4px;
  outline: none;
  flex: 1 1 auto;
  min-width: 0;
  text-align: right;
}

.action {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  letter-spacing: 1.5px;
  color: #FFD624;
  background: transparent;
  border: 1.5px solid rgba(255, 214, 36, 0.55);
  border-radius: 3px;
  padding: 3px 12px;
  min-width: 64px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease, color 0.15s ease, border-color 0.15s ease;
}
.action:not(:disabled):active {
  filter: brightness(0.6);
  transform: scale(0.97);
}
.action:disabled {
  opacity: 0.5;
  cursor: default;
}
.action.danger {
  color: #ff7f7f;
  border-color: rgba(255, 127, 127, 0.7);
}
.action.busy {
  opacity: 0.6;
}

.error {
  font-size: 10px;
  color: #FF8A82;
  text-align: right;
  margin-top: -4px;
}

.about {
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid rgba(127, 217, 194, 0.25);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.about-row {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
}

.about-key {
  color: rgba(227, 244, 238, 0.55);
  letter-spacing: 0.5px;
}

.about-val {
  font-family: 'Iceland', sans-serif;
  color: #7FD9C2;
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
