<template>
  <div class="screen">
    <div class="inner">
      <span class="title">POKÉDEX</span>
      <div class="divider" />
      <span class="msg">{{ displayText }}</span>
      <div class="bar-track">
        <div class="bar-fill" :style="{ width: progress + '%' }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const progress    = ref(0)
const displayText = ref('Initialising systems...')

const messages = [
  'Initialising systems...',
  'Loading Pokédex data...',
  'Calibrating scanner...',
  'Ready.',
]

let rafId = null
let start = null
const DURATION = 1900  // slightly under the 2s screen switch

function step(ts) {
  if (!start) start = ts
  const elapsed = ts - start
  progress.value = Math.min((elapsed / DURATION) * 100, 100)
  const msgIndex = Math.min(
    Math.floor((elapsed / DURATION) * messages.length),
    messages.length - 1
  )
  displayText.value = messages[msgIndex]
  if (elapsed < DURATION) rafId = requestAnimationFrame(step)
}

onMounted(() => { rafId = requestAnimationFrame(step) })
onBeforeUnmount(() => { if (rafId) cancelAnimationFrame(rafId) })
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #0a1a0a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.inner {
  width: 80%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 26px;
  color: #FFD624;
  -webkit-text-stroke: 0.5px #005B98;
  letter-spacing: 3px;
}

.divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.msg {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.7);
  letter-spacing: 1px;
  min-height: 14px;
}

.bar-track {
  width: 100%;
  height: 3px;
  background: rgba(47, 171, 208, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.bar-fill {
  height: 100%;
  background: #2FABD0;
  border-radius: 2px;
  transition: width 0.1s linear;
  box-shadow: 0 0 6px rgba(47, 171, 208, 0.7);
}
</style>
