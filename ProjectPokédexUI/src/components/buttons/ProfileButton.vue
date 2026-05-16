<template>
  <div class="profile-btn" @click="toggle">

    <!-- Static background circle — no effects ever applied -->
    <svg class="profile-bg" width="83" height="83" viewBox="0 0 83 83" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="41.5" cy="41.5" r="40.5" fill="#E3F4EE" stroke="black" stroke-width="3" stroke-miterlimit="1.72205"/>
    </svg>

    <!-- Icon layer — receives all toggle and press effects -->
    <svg class="profile-icon" :class="{ 'is-on': isOn }" width="83" height="83" viewBox="0 0 83 83" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g filter="url(#filter0_i_38_35)">
        <circle cx="40.5" cy="39.5" r="33.5" fill="url(#paint0_radial_38_35)" stroke="black" stroke-width="3" stroke-miterlimit="1.72205"/>
        <path d="M39.7002 36.532C47.2663 36.5321 53.3994 42.666 53.3994 50.2321C53.3993 51.9077 52.6614 53.1383 51.4766 54.0915C50.2586 55.0713 48.5784 55.7421 46.8057 56.1892C45.0458 56.633 43.2716 56.837 41.9287 56.9284C41.2599 56.974 40.7036 56.9908 40.3164 56.9968C40.1229 56.9998 39.9713 57.0003 39.8701 56.9997C39.8198 56.9994 39.7815 56.9991 39.7568 56.9987C39.7448 56.9986 39.736 56.9979 39.7305 56.9978H39.6699C39.6643 56.9979 39.655 56.9986 39.6426 56.9987C39.6178 56.9991 39.5798 56.9994 39.5293 56.9997C39.4282 57.0003 39.2773 56.9998 39.084 56.9968C38.6968 56.9908 38.1398 56.974 37.4707 56.9284C36.1278 56.837 34.3545 56.6329 32.5947 56.1892C30.8219 55.7422 29.1419 55.0713 27.9238 54.0915C26.7389 53.1383 26.0001 51.9078 26 50.2321C26 42.6659 32.134 36.532 39.7002 36.532Z" fill="#2D2D2D" stroke="#2D2D2D" stroke-width="2"/>
        <circle cx="39.4225" cy="27.766" r="7.76597" fill="#2D2D2D" stroke="#2D2D2D" stroke-width="2"/>
      </g>
      <defs>
        <filter id="filter0_i_38_35" x="0" y="0" width="85" height="85" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
          <feFlood flood-opacity="0" result="BackgroundImageFix"/>
          <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
          <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
          <feOffset dx="2" dy="2"/>
          <feGaussianBlur stdDeviation="2"/>
          <feComposite in2="hardAlpha" operator="arithmetic" k2="-1" k3="1"/>
          <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"/>
          <feBlend mode="normal" in2="shape" result="effect1_innerShadow_38_35"/>
        </filter>
        <radialGradient id="paint0_radial_38_35" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(31 27) rotate(43.0021) scale(60.8482)">
          <stop stop-color="#E2FBFF"/>
          <stop offset="0.2499" stop-color="#AAE2E8"/>
          <stop offset="0.26" stop-color="#72CAD2"/>
          <stop offset="0.57" stop-color="#3AACB8"/>
          <stop offset="0.581731" stop-color="#028E9F"/>
          <stop offset="0.942308" stop-color="#017179"/>
        </radialGradient>
      </defs>
    </svg>

  </div>
</template>

<style scoped>
.profile-btn {
  position: relative;
  width: 83px;
  height: 83px;
  cursor: pointer;
  user-select: none;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.profile-bg {
  position: absolute;
  top: 0;
  left: 0;
}

.profile-icon {
  position: absolute;
  top: 0;
  left: 0;
  transition: filter 0.08s ease;
}

.profile-icon:active {
  filter: brightness(0.6);
  transform: scale(0.97);
}

.profile-icon.is-on {
  filter: brightness(1.4) drop-shadow(0 0 6px rgba(255, 255, 255, 0.8));
  transform: scale(1.03);
}

.profile-icon.is-on:active {
  filter: brightness(0.9) drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
  transform: scale(0.97);
}
</style>

<script setup>
import { computed } from 'vue'
import { useAppState } from '../../composables/useAppState'

const { setScreen, profileActive, activeSettings } = useAppState()

const isOn = computed(() => profileActive.value)

function toggle() {
  profileActive.value = !profileActive.value
  activeSettings.value = null  // always reset settings buttons
  setScreen(profileActive.value ? 'user-settings' : 'default')
}
</script>
