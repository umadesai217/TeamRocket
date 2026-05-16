<template>
  <div class="screen">
    <div class="inner">
      <div class="logo-row">
        <span class="logo-text">POKÉDEX</span>
      </div>
      <div class="divider" />
      <span class="sub">Team Rocket Edition</span>
      <div class="dots">
        <span class="dot" :class="{ lit: tick % 3 === 0 }" />
        <span class="dot" :class="{ lit: tick % 3 === 1 }" />
        <span class="dot" :class="{ lit: tick % 3 === 2 }" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const tick = ref(0)
let interval = null

onMounted(() => {
  interval = setInterval(() => { tick.value++ }, 400)
})
onBeforeUnmount(() => clearInterval(interval))
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.logo-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-text {
  font-family: 'Jaro', sans-serif;
  font-size: 28px;
  color: #FFD624;
  -webkit-text-stroke: 0.5px #005B98;
  letter-spacing: 3px;
}

.divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.sub {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.55);
  letter-spacing: 2px;
}

.dots {
  display: flex;
  gap: 6px;
  margin-top: 10px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(47, 171, 208, 0.25);
  transition: background 0.2s ease;
}

.dot.lit {
  background: #2FABD0;
  box-shadow: 0 0 6px rgba(47, 171, 208, 0.8);
}
</style>
