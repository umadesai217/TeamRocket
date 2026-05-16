<template>
  <svg width="33" height="39" viewBox="0 0 33 39" fill="none" xmlns="http://www.w3.org/2000/svg" @click="emit('select')" :class="{ 'is-on': isOn }">
    <path d="M5.52072 4.40914C6.81486 3.42686 7.87861 3.19413 8.83154 3.36001C9.83557 3.53491 10.903 4.18298 12.1112 5.34197C13.3125 6.49445 14.5602 8.06042 15.9426 9.91982C17.2992 11.7445 18.8198 13.8994 20.4628 16.064C22.0944 18.2137 23.7741 20.2837 25.1434 22.0644C26.5497 23.893 27.7056 25.5125 28.4762 26.9754C29.2508 28.4458 29.5737 29.6445 29.4627 30.6575C29.3569 31.6219 28.8374 32.5861 27.5407 33.5703C26.244 34.5545 25.1725 34.7975 24.2109 34.6412C23.2018 34.4771 22.1308 33.8452 20.9198 32.7072C19.7146 31.5746 18.4615 30.0291 17.0758 28.1855C15.7362 26.4033 14.1732 24.2048 12.5519 22.0686C11.7228 20.9764 10.9026 19.9277 10.1171 18.9255C9.3301 17.9213 8.57965 16.9658 7.88221 16.0489C6.4815 14.2073 5.33044 12.569 4.56535 11.0878C3.7966 9.59939 3.4764 8.37954 3.59168 7.34821C3.70161 6.36508 4.22697 5.39118 5.52072 4.40914Z" fill="url(#paint0_linear_57_936)" stroke="black" stroke-width="2.3"/>
    <defs>
      <linearGradient id="paint0_linear_57_936" x1="5" y1="4" x2="28.5" y2="34.5" gradientUnits="userSpaceOnUse">
        <stop stop-color="#FF918D"/>
        <stop offset="0.298077" stop-color="#FF4846"/>
        <stop offset="0.649038" stop-color="#FF2423"/>
        <stop offset="1" stop-color="#FF0000"/>
      </linearGradient>
    </defs>
  </svg>
</template>

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
  filter: brightness(2) drop-shadow(0 0 6px rgba(255, 100, 100, 1));
}
svg.is-on:active {
  filter: brightness(0.9) drop-shadow(0 0 4px rgba(255, 255, 255, 0.5));
}
</style>

<script setup>
const props = defineProps(['isOn'])
const emit = defineEmits(['select'])
</script>