<template>
  <div class="screen">
    <h1 class="title">User Settings</h1>
    <p class="subtitle">press a settings button for the following pages</p>
    <ul class="page-list">
      <li class="page-item">
        <span class="dot red"></span>
        <span class="page-name">Profile Settings</span>
      </li>
      <li class="page-item">
        <span class="dot yellow"></span>
        <span class="page-name">Accessibility Settings</span>
      </li>
      <li class="page-item">
        <span class="dot green"></span>
        <span class="page-name">App Settings</span>
      </li>
    </ul>
    <button
      class="btn"
      :class="{ pressed: logoutPressed }"
      @pointerdown="logoutPressed = true"
      @pointerup="logoutPressed = false"
      @pointerleave="logoutPressed = false"
      @click="handleLogout"
    >
      Log Out
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../../composables/useAuth.js'

const { bootDown } = useAuth()

const logoutPressed = ref(false)

async function handleLogout() {
  logoutPressed.value = false
  await bootDown()
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #084236;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  gap: 10px;
}

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 26px;
  font-weight: 400;
  color: #ffffff;
  margin: 0;
  letter-spacing: 1px;
}

.subtitle {
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  color: #ffffff;
  margin: 0;
  text-align: center;
  opacity: 0.7;
  line-height: 1.4;
}

.page-list {
  list-style: none;
  margin: 4px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.page-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot.red    { background-color: #FF2423; }
.dot.yellow { background-color: #FFFF00; }
.dot.green  { background-color: #33FF00; }

.page-name {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #ffffff;
}

.btn {
  margin-top: 20px;
  background: transparent;
  border: 1.5px solid #ffffff;
  border-radius: 3px;
  font-family: 'Jura', sans-serif;
  font-size: 14px;
  color: #ffffff;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  transition: filter 0.08s ease, transform 0.08s ease;
}

.btn.pressed {
  filter: brightness(0.6);
  transform: scale(0.96);
}
</style>
