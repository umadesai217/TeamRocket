<template>
  <svg
    width="27" height="27" viewBox="0 0 27 27" fill="none"
    xmlns="http://www.w3.org/2000/svg"
    :class="{ 'is-on': isOn }"
    @click="handleClick"
  >
    <circle cx="13.5" cy="13.5" r="12.5" fill="url(#paint0_radial_63_121)" stroke="black" stroke-width="2"/>
    <defs>
      <radialGradient id="paint0_radial_63_121" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse"
        gradientTransform="translate(4 2) rotate(59.0362) scale(29.1548)">
        <stop offset="0.0144231" stop-color="#FF918D"/>
        <stop offset="0.3125"    stop-color="#FF6F6A"/>
        <stop offset="0.346154"  stop-color="#FF4D47"/>
        <stop offset="0.788462"  stop-color="#FF3C35"/>
        <stop offset="0.8125"    stop-color="#FF2B23"/>
        <stop offset="1"         stop-color="#FF0900"/>
      </radialGradient>
    </defs>
  </svg>
</template>

<script setup>
import { computed } from 'vue'
import { useAppState } from '../../composables/useAppState'
import { useCardConfirmation } from '../../composables/useCardConfirmation'

const { activeScreen, setScreen, profileActive, activeSettings } = useAppState()
const { abandonConfirmation } = useCardConfirmation()

const isOn = computed(() => activeScreen.value === 'camera')

function handleClick() {
  if (activeScreen.value === 'camera') {
    setScreen('default')
  } else {
    abandonConfirmation()   // save defaults for any unanswered confirmation steps
    profileActive.value  = false
    activeSettings.value = null
    setScreen('camera')
  }
}
</script>

<style scoped>
svg {
  cursor: pointer;
  transition: filter 0.08s ease, transform 0.08s ease;
  user-select: none;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}
svg:active {
  filter: brightness(0.6);
  transform: scale(0.93);
}
svg.is-on {
  filter: brightness(1.4) drop-shadow(0 0 10px rgba(255, 50, 50, 1));
}
svg.is-on:active {
  filter: brightness(0.9) drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
}
</style>
