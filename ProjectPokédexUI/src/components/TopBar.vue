<template>
  <div class="top-bar">
    <!-- Stretchy background shape -->
    <svg class="bg" viewBox="0 0 100 22.6" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Shadow layer -->
      <path d="
        M 0,0 L 100,0
        L 100,12.5 Q 100,14 98.5,14
        L 56.5,14 Q 55,14 53.64,14.64
        L 39.36,21.36 Q 38,22 36.5,22
        L 1.5,22 Q 0,22 0,20.5
        L 0,0 Z
      " fill="#961C17" stroke="black" stroke-width="0.6"/>
      <!-- Main layer -->
      <path d="
        M 0,0 L 100,0
        L 100,10.5 Q 100,12 98.5,12
        L 56.5,12 Q 55,12 53.64,12.64
        L 39.36,19.36 Q 38,20 36.5,20
        L 1.5,20 Q 0,20 0,18.5
        L 0,0 Z
      " fill="#D40B41" stroke="black" stroke-width="0.6"/>
    </svg>

    <!-- Buttons sit on top -->
    <div class="buttons">
      <ProfileButton class="profile" />
      <div class="settings">
        <Settings1 :is-on="activeSettings === 1" @select="selectSettings(1)" />
        <Settings2 :is-on="activeSettings === 2" @select="selectSettings(2)" />
        <Settings3 :is-on="activeSettings === 3" @select="selectSettings(3)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppState } from '../composables/useAppState'
import ProfileButton from './buttons/ProfileButton.vue'
import Settings1 from './buttons/Settings1.vue'
import Settings2 from './buttons/Settings2.vue'
import Settings3 from './buttons/Settings3.vue'

const { setScreen, profileActive, activeSettings } = useAppState()

// Screen maps depending on whether profile is active
const normalScreens   = { 1: 'card-viewer',        2: 'meta-viewer',           3: 'trade-viewer' }
const profileScreens  = { 1: 'profile-settings',   2: 'accessibility-settings', 3: 'application-settings' }

function selectSettings(num) {
  const screens = profileActive.value ? profileScreens : normalScreens
  if (activeSettings.value === num) {
    activeSettings.value = null
    setScreen(profileActive.value ? 'user-settings' : 'default')
  } else {
    activeSettings.value = num
    setScreen(screens[num])
  }
}
</script>

<style scoped>
.top-bar {
  position: relative;
  height: 105px;
  display: flex;
  flex-shrink: 0;
}

.bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.buttons {
  position: relative;
  display: flex;
  width: 100%;
  padding-right: 10px;
  gap: 12px;
  z-index: 1;
}

.profile {
  flex-shrink: 0;
  margin-left: 60px;
  padding-top: 3px;
}

.settings {
  display: flex;
  gap: 25px;
  margin-left: auto;
  padding-top: 8px;
}
</style>
