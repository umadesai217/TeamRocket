<template>
  <div class="filter-btn" :class="{ pressed, 'is-on': isOn }" @click="emit('select')" @pointerdown="pressed = true" @pointerup="pressed = false" @pointerleave="pressed = false">
    <svg
      class="filter-svg"
      width="100%"
      height="100%"
      viewBox="0 0 99 33"
      preserveAspectRatio="none"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <filter id="fbtn2-inner" x="0" y="0" width="99" height="33" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
          <feFlood flood-opacity="0" result="BackgroundImageFix"/>
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset dx="2" dy="4"/>
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.33 0"/>
          <feBlend mode="normal" in2="shape" result="effect1_innerShadow"/>
        </filter>
        <linearGradient id="fbtn2-grad" x1="14.123" y1="-2.14057e-06" x2="-5.23575" y2="64.0944" gradientUnits="userSpaceOnUse">
          <stop stop-color="#2FABD0"/>
          <stop offset="0.37" stop-color="#008DB9"/>
          <stop offset="0.38" stop-color="#0089B2"/>
          <stop offset="0.706631" stop-color="#0084AC"/>
          <stop offset="0.706731" stop-color="#007092"/>
          <stop offset="1" stop-color="#00495F"/>
        </linearGradient>
      </defs>
      <!-- Fill with inner shadow -->
      <g filter="url(#fbtn2-inner)">
        <path d="M99 18H88.1989C87.2659 18 86.3623 17.6739 85.6444 17.078L66.1774 0.921956C65.4594 0.326127 64.5558 0 63.6228 0H1.00006C0.447777 0 6.10352e-05 0.447715 6.10352e-05 1V32C6.10352e-05 32.5523 0.447777 33 1.00006 33H81.207C95.8343 31.5 99 18 99 18Z" fill="url(#fbtn2-grad)"/>
      </g>
      <!-- Stroke -->
      <path d="M63.623 1H1V32H81.1465C88.098 31.2747 92.2987 27.7232 94.7832 24.3447C96.0333 22.6447 96.8487 20.9872 97.3506 19.7559C97.4626 19.4809 97.5579 19.2269 97.6396 19H88.1992C87.033 19 85.9033 18.5924 85.0059 17.8477L65.5391 1.69141C65.0007 1.24458 64.3227 1.00005 63.623 1Z" stroke="black" stroke-width="2" fill="none" vector-effect="non-scaling-stroke"/>
    </svg>
    <span class="filter-label">{{ label }}</span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const pressed = ref(false)
const props = defineProps(['isOn', 'label'])
const emit = defineEmits(['select'])
</script>

<style scoped>
.filter-btn {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  transition: filter 0.08s ease, transform 0.08s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}
.filter-btn.pressed {
  filter: brightness(0.7);
  transform: scale(0.96);
}
.filter-btn.is-on {
  filter: brightness(1.35) drop-shadow(0 0 6px rgba(47, 171, 208, 0.95));
}
.filter-btn.is-on.pressed {
  filter: brightness(0.9) drop-shadow(0 0 3px rgba(47, 171, 208, 0.5));
}
.filter-svg {
  display: block;
  width: 100%;
  height: 100%;
}
.filter-label {
  position: absolute;
  top: 50%;
  left: 42%;
  transform: translate(-50%, -50%);
  font-family: 'Jura', sans-serif;
  font-size: clamp(14px, 3vw, 28px);
  color: white;
  pointer-events: none;
  white-space: nowrap;
}
</style>
