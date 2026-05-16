<template>
  <div class="lib-btn-wrap" :class="{ pressed }">
    <svg
      class="lib-btn"
      width="100%"
      height="100%"
      viewBox="0 -4 178 90"
      preserveAspectRatio="none"
      fill="none"
      pointer-events="none"
      xmlns="http://www.w3.org/2000/svg"
      @click="emit('select')"
      @pointerdown="pressed = true"
      @pointerup="pressed = false"
      @pointerleave="pressed = false"
    >
      <!-- Shadow layer -->
      <g transform="translate(0, -4)">
        <path
          d="M154.145 1L177.5 19.9756V25.0049L89.9941 91.7461L1 25V19.9932L25.8379 1H154.145Z"
          fill="#961C17"
          stroke="black"
          stroke-width="1"
          pointer-events="none"
        />
      </g>
      <!-- Main shape -->
      <path
        d="M154.323 0.5L177.691 19.4873L89.9971 86.3721L0.828125 19.4961L25.6699 0.5H154.323Z"
        fill="#F63C3B"
        stroke="black"
        vector-effect="non-scaling-stroke"
        pointer-events="painted"
      />
    </svg>
    <span class="lib-label">Sets</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const pressed = ref(false)
const emit = defineEmits(['select'])
</script>

<style scoped>
.lib-btn-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transition: filter 0.08s ease, transform 0.08s ease;
}
.lib-btn-wrap.pressed {
  filter: brightness(0.6);
  transform: scale(0.97);
}
.lib-btn {
  top: 0;
  left: 0;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}
.lib-label {
  position: absolute;
  top: 42%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Jura', sans-serif;
  font-size: 32px;
  color: white;
  pointer-events: none;
  white-space: nowrap;
}
</style>
