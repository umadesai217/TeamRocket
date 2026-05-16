<template>
  <div class="lib-btn" :class="{ pressed }">
    <svg
      class="lib-svg"
      width="100%"
      height="100%"
      viewBox="0 0 199 68"
      preserveAspectRatio="none"
      fill="none"
      pointer-events="none"
      xmlns="http://www.w3.org/2000/svg"
      @click="emit('select')"
      @pointerdown="pressed = true"
      @pointerup="pressed = false"
      @pointerleave="pressed = false"
    >
      <!-- Main shape -->
      <path
        d="M4 0.5H106.424C107.177 0.500071 107.911 0.743227 108.515 1.19336L197.491 67.5H0.5V4C0.5 2.067 2.067 0.5 4 0.5Z"
        fill="#E3F4EE"
        stroke="black"
        vector-effect="non-scaling-stroke"
        pointer-events="painted"
      />
    </svg>
    <span class="lib-label">Library</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const pressed = ref(false)
const emit = defineEmits(['select'])
</script>

<style scoped>
.lib-btn {
  position: relative;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transition: filter 0.08s ease, transform 0.08s ease;
}
.lib-btn.pressed {
  filter: brightness(0.6);
  transform: scale(0.97);
}
.lib-svg {
  position: absolute;
  top: 0;
  left: 0;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}
.lib-label {
  position: absolute;
  top: 50%;
  left: 40%;
  transform: translate(-50%, -50%);
  font-family: 'Jura', sans-serif;
  font-size: 32px;
  color: black;
  pointer-events: none;
  white-space: nowrap;
}
</style>
