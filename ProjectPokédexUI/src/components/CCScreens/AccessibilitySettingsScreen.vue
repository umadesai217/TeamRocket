<template>
  <div class="screen">
    <h1 class="title">ACCESSIBILITY</h1>

    <div class="row">
      <span class="label">Auto-speak chat</span>
      <button
        class="toggle"
        :class="{ on: autoSpeakAnswers }"
        @click="autoSpeakAnswers = !autoSpeakAnswers"
      >
        <span class="knob" />
      </button>
    </div>

    <div class="row">
      <span class="label">Auto-speak bio</span>
      <button
        class="toggle"
        :class="{ on: autoSpeakBio }"
        @click="autoSpeakBio = !autoSpeakBio"
      >
        <span class="knob" />
      </button>
    </div>

    <div class="row slider-row">
      <span class="label">Rate</span>
      <input class="slider" type="range" min="0.5" max="2" step="0.05" v-model.number="rate" />
      <span class="value">{{ rate.toFixed(2) }}×</span>
    </div>

    <div class="row slider-row">
      <span class="label">Pitch</span>
      <input class="slider" type="range" min="0.5" max="2" step="0.05" v-model.number="pitch" />
      <span class="value">{{ pitch.toFixed(2) }}</span>
    </div>

    <div class="row select-row">
      <span class="label">Voice</span>
      <select class="select" v-model="voiceURI">
        <option value="">Default</option>
        <option v-for="v in englishVoices" :key="v.voiceURI" :value="v.voiceURI">
          {{ v.name }}
        </option>
      </select>
    </div>

    <button class="test-btn" @click="testVoice" :disabled="isSpeaking">
      {{ isSpeaking ? 'Speaking...' : '▶ Test voice' }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSettings } from '../../composables/useSettings.js'
import { useRotom } from '../../composables/useRotom.js'

const { autoSpeakAnswers, autoSpeakBio, rate, pitch, voiceURI, voices } = useSettings()
const { speak, isSpeaking } = useRotom()

const englishVoices = computed(() => {
  const list = voices.value ?? []
  const en = list.filter(v => /^en/i.test(v.lang))
  return en.length ? en : list
})

function testVoice() {
  speak('Pokédex online. Voice synthesis active.')
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #084236;
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
  gap: 8px;
}

.label {
  font-size: 11px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.value {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  color: #7FD9C2;
  min-width: 36px;
  text-align: right;
}

/* ── Toggle ── */
.toggle {
  width: 32px;
  height: 16px;
  border-radius: 9px;
  border: 1.5px solid #A2A3B1;
  background: #101F13;
  position: relative;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  padding: 0;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}
.toggle.on {
  background: #2FABD0;
  border-color: #FFD624;
}
.knob {
  position: absolute;
  top: 1px;
  left: 1px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #E3F4EE;
  transition: transform 0.15s ease;
}
.toggle.on .knob {
  transform: translateX(15px);
  background: #FFD624;
}

/* ── Slider ── */
.slider-row .slider {
  flex: 1 1 auto;
  min-width: 0;
}
.slider {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 2px;
  background: #101F13;
  outline: none;
  border: 1px solid #A2A3B1;
}
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #FFD624;
  border: 1.5px solid #005B98;
  cursor: pointer;
}
.slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #FFD624;
  border: 1.5px solid #005B98;
  cursor: pointer;
}

/* ── Select ── */
.select-row .select {
  flex: 1 1 auto;
  min-width: 0;
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
}

/* ── Test button ── */
.test-btn {
  margin-top: auto;
  font-family: 'Iceland', sans-serif;
  font-size: 13px;
  color: #FFD624;
  background: transparent;
  border: 1.5px solid #FFD624;
  border-radius: 3px;
  padding: 5px 10px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  letter-spacing: 1.5px;
  transition: filter 0.08s ease, transform 0.08s ease;
}
.test-btn:disabled {
  opacity: 0.5;
  cursor: default;
}
.test-btn:not(:disabled):active {
  filter: brightness(0.6);
  transform: scale(0.97);
}
</style>
