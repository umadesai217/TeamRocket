<template>
  <div class="center-console">
    <!-- Stretchy background shape -->
    <svg class="bg" :class="{ 'chrome-dimmed': !currentUser }" viewBox="-2 -2 104 104" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Shadow layer -->
      <polygon points="0,0 100,0 100,100 9.2,100 0,84" fill="#919191" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
      <polygon points="0,0 96,0 96,97.3 7.7,97.3 0,84" fill="#E3F4EE" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
    </svg>

    <!-- Content sits on top -->
    <div class="content">
      <div class="LCD-frame" :class="{ 'lcd-highlight': !currentUser }">
        <div class="LCD-screen">
          <WelcomeScreen             v-if="activeScreen === 'welcome'" />
          <BootingScreen             v-else-if="activeScreen === 'booting'" />
          <CameraScreen              v-else-if="activeScreen === 'camera'" />
          <DefaultScreen             v-else-if="activeScreen === 'default'" />
          <LoginScreen               v-else-if="activeScreen === 'login'" />
          <CardViewerScreen          v-else-if="activeScreen === 'card-viewer'" />
          <MetaViewerScreen          v-else-if="activeScreen === 'meta-viewer'" />
          <TradeViewerScreen         v-else-if="activeScreen === 'trade-viewer'" />
          <UserSettingsScreen        v-else-if="activeScreen === 'user-settings'" />
          <ProfileSettingsScreen     v-else-if="activeScreen === 'profile-settings'" />
          <AccessibilitySettingsScreen v-else-if="activeScreen === 'accessibility-settings'" />
          <ApplicationSettingsScreen v-else-if="activeScreen === 'application-settings'" />
        </div>
      </div>
      <div class="camera-button" :class="{ 'chrome-dimmed': !currentUser }">
        <CameraButton />
        <span class="camera-label">Camera</span>
      </div>
      <svg class="hinge-dots" :class="{ 'chrome-dimmed': !currentUser }" width="50" height="11" viewBox="0 0 26 11" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5.5166 1C8.05411 1.00002 10.033 2.95464 10.0332 5.27148C10.0332 7.5885 8.05425 9.54393 5.5166 9.54395C2.97893 9.54395 1 7.58851 1 5.27148C1.00023 2.95463 2.97908 1 5.5166 1Z" fill="#961C17" stroke="black" stroke-width="2"/>
        <g transform="translate(25, 0)">
          <path d="M5.5166 1C8.05411 1.00002 10.033 2.95464 10.0332 5.27148C10.0332 7.5885 8.05425 9.54393 5.5166 9.54395C2.97893 9.54395 1 7.58851 1 5.27148C1.00023 2.95463 2.97908 1 5.5166 1Z" fill="#961C17" stroke="black" stroke-width="2"/>
        </g>
      </svg>
      <svg class="lines" :class="{ 'chrome-dimmed': !currentUser }" width="121" height="27" viewBox="0 0 36 27" fill="none" xmlns="http://www.w3.org/2000/svg">
        <line x1="0" y1="3"  x2="74" y2="3"  stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
        <line x1="0" y1="10" x2="74" y2="10" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
        <line x1="0" y1="17" x2="74" y2="17" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
        <line x1="0" y1="24" x2="74" y2="24" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.center-console {
  flex: 1;
  position: relative;
  display: flexbox;
  margin: 0px 32px 0 32px;
}

.bg {
  position: absolute;
  width: 100%;
  height: 100%;
}

.content {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  z-index: 1;
  overflow: hidden;
}

.LCD-frame {
  width: 80%;
  height: 74%;
  margin-top: 30px;
  margin-right: 7px;
  background-color: #3B4147;
  border-radius: 8px;
  border: 3px solid black;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-button {
  position: absolute;
  bottom: 33px;
  left: 40px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.camera-label {
  font-family: 'Jersey 25', sans-serif;
  font-size: 32px;
  color: #1a1a1a;
}

.lines {
  position: absolute;
  bottom: 33px;
  right: 35px;
}

.hinge-dots {
  position: absolute;
  top: 12px;
  left: 48%;
  transform: translateX(-50%);
}

.LCD-screen {
  width: 93.5%;
  height: 92%;
  border: 2.5px solid black;
  overflow: hidden;
}

.bg,
.camera-button,
.hinge-dots,
.lines {
  transition: filter 2s ease;
}

.chrome-dimmed {
  filter: brightness(0.2) saturate(0.3);
  pointer-events: none;
}

.LCD-frame {
  transition: filter 2s ease, box-shadow 2s ease;
}

.lcd-highlight {
  filter: brightness(1.5);
  box-shadow:
    0 0 24px 1px rgba(47, 171, 208, 0.3),
    0 0 48px 12px rgba(47, 171, 208, 0.12);
}
</style>

<script setup>
import { useAppState } from '../composables/useAppState'
import CameraButton from './buttons/CameraButton.vue'
import WelcomeScreen from './CCScreens/WelcomeScreen.vue'
import BootingScreen from './CCScreens/BootingScreen.vue'
import CameraScreen from './CCScreens/CameraScreen.vue'
import DefaultScreen from './CCScreens/DefaultScreen.vue'
import LoginScreen from './CCScreens/LoginScreen.vue'
import CardViewerScreen from './CCScreens/CardViewerScreen.vue'
import MetaViewerScreen from './CCScreens/MetaViewerScreen.vue'
import TradeViewerScreen from './CCScreens/TradeViewerScreen.vue'
import UserSettingsScreen from './CCScreens/UserSettingsScreen.vue'
import ProfileSettingsScreen from './CCScreens/ProfileSettingsScreen.vue'
import AccessibilitySettingsScreen from './CCScreens/AccessibilitySettingsScreen.vue'
import ApplicationSettingsScreen from './CCScreens/ApplicationSettingsScreen.vue'

const { activeScreen, currentUser } = useAppState()
</script>
