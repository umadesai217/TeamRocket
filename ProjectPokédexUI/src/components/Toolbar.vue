<script setup>
import { ref } from 'vue'
const profileOn = ref(false)
const redOn = ref(false)
const yellowOn = ref(false)
const greenOn = ref(false)

const clickLibrary = () => {
  // action placeholder
}

const toggleProfile = () => { profileOn.value = !profileOn.value }
const toggleRed = () => { redOn.value = !redOn.value }
const toggleYellow = () => { yellowOn.value = !yellowOn.value }
const toggleGreen = () => { greenOn.value = !greenOn.value }
</script>

<template>
  <div class="fixed top-0 left-0 right-0 h-16 z-50 flex items-center px-4 bg-[#d61b3b] shadow-md">
    <!-- Library button (non-toggle) -->
    <button
      @click="clickLibrary"
      class="w-12 h-10 bg-white rounded-md flex items-center justify-center mr-4"
      aria-label="Library"
    >
      <div class="w-6 h-6 flex flex-col justify-between">
        <span class="block w-5 h-0.5 bg-gray-400 rounded"></span>
        <span class="block w-5 h-0.5 bg-gray-400 rounded"></span>
        <span class="block w-5 h-0.5 bg-gray-400 rounded"></span>
      </div>
    </button>

    <!-- Profile orb (toggle) -->
    <button
      @click="toggleProfile"
      :class="['w-12 h-12 rounded-full flex items-center justify-center mr-6 transition-all duration-200',
               profileOn ? 'bg-linear-to-br from-sky-300 to-sky-600 ring-4 ring-sky-300' : 'bg-sky-100']"
      aria-pressed="profileOn"
      aria-label="Profile"
    >
      <svg v-if="!profileOn" xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-gray-700" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4 0-7 2-7 4v2h14v-2c0-2-3-4-7-4z"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-white drop-shadow-sm" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5zm0 2c-4 0-7 2-7 4v2h14v-2c0-2-3-4-7-4z"/>
      </svg>
    </button>

    <!-- Spacer to push colored buttons to the right -->
    <div class="flex-1"></div>

    <!-- Colored indicator buttons -->
    <div class="flex items-center gap-3">
      <button
        @click="toggleRed"
        :class="['w-10 h-6 rounded-full transition-all duration-150', redOn ? 'bg-red-400 ring-4 ring-red-300 shadow-[0_0_8px_rgba(255,0,0,0.45)]' : 'bg-red-600']"
        aria-pressed="redOn"
        aria-label="Red"
      ></button>

      <button
        @click="toggleYellow"
        :class="['w-10 h-6 rounded-full transition-all duration-150', yellowOn ? 'bg-yellow-300 ring-4 ring-yellow-200 shadow-[0_0_8px_rgba(255,230,0,0.45)]' : 'bg-yellow-500']"
        aria-pressed="yellowOn"
        aria-label="Yellow"
      ></button>

      <button
        @click="toggleGreen"
        :class="['w-10 h-6 rounded-full transition-all duration-150', greenOn ? 'bg-green-300 ring-4 ring-green-200 shadow-[0_0_8px_rgba(0,255,50,0.35)]' : 'bg-green-500']"
        aria-pressed="greenOn"
        aria-label="Green"
      ></button>
    </div>
  </div>
</template>