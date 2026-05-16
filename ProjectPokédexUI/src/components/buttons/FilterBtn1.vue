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
        <filter id="fbtn1-inner" x="0" y="0" width="99" height="33" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
          <feFlood flood-opacity="0" result="BackgroundImageFix"/>
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset dx="2" dy="4"/>
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.33 0"/>
          <feBlend mode="normal" in2="shape" result="effect1_innerShadow"/>
        </filter>
        <linearGradient id="fbtn1-grad" x1="84.877" y1="-2.14057e-06" x2="104.236" y2="64.0944" gradientUnits="userSpaceOnUse">
          <stop stop-color="#2FABD0"/>
          <stop offset="0.37" stop-color="#008DB9"/>
          <stop offset="0.38" stop-color="#0089B2"/>
          <stop offset="0.706631" stop-color="#0084AC"/>
          <stop offset="0.706731" stop-color="#007092"/>
          <stop offset="1" stop-color="#00495F"/>
        </linearGradient>
      </defs>
      <!-- Fill with inner shadow -->
      <g filter="url(#fbtn1-inner)">
        <path d="M0 18H10.8011C11.7341 18 12.6377 17.6739 13.3556 17.078L32.8226 0.921956C33.5406 0.326127 34.4442 0 35.3772 0H97.9999C98.5522 0 98.9999 0.447715 98.9999 1V32C98.9999 32.5523 98.5522 33 97.9999 33H17.793C3.16568 31.5 0 18 0 18Z" fill="url(#fbtn1-grad)"/>
      </g>
      <!-- Stroke -->
      <path d="M35.377 1H98V32H17.8535C10.902 31.2747 6.70133 27.7232 4.2168 24.3447C2.96668 22.6447 2.15125 20.9872 1.64941 19.7559C1.53736 19.4809 1.44208 19.2269 1.36035 19H10.8008C11.967 19 13.0967 18.5924 13.9941 17.8477L33.4609 1.69141C33.9993 1.24458 34.6773 1.00005 35.377 1Z" stroke="black" stroke-width="2" fill="none" vector-effect="non-scaling-stroke"/>
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
  left: 58%;
  transform: translate(-50%, -50%);
  font-family: 'Jura', sans-serif;
  font-size: clamp(14px, 3vw, 28px);
  color: white;
  pointer-events: none;
  white-space: nowrap;
}
</style>
