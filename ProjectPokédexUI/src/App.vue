<template>
  <div class="app" :class="{ 'app-dimmed': !currentUser }">
    <TopBar        class="ui-transition" :class="{ 'ui-dimmed': !currentUser }" />
    <CenterConsole />
    <BottomDisplay class="ui-transition" :class="{ 'ui-dimmed': !currentUser }" />
    <LibraryPanel  :class="{ 'ui-dimmed': !currentUser }" />
    <WelcomeOverlay />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import TopBar        from './components/TopBar.vue'
import CenterConsole from './components/CenterConsole.vue'
import BottomDisplay from './components/BottomDisplay.vue'
import LibraryPanel  from './components/LibraryPanel.vue'
import WelcomeOverlay from './components/WelcomeOverlay.vue'
import { useAuth }     from './composables/useAuth.js'
import { useAppState } from './composables/useAppState.js'

const { checkSession } = useAuth()
const { currentUser }  = useAppState()

onMounted(() => checkSession())
</script>

<style scoped>
.app {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #D40B41;
  box-sizing: border-box;
  transition: background-color 2s ease;
}

.app.app-dimmed {
  background-color: #1a0205;
}
</style>

<!-- Global (non-scoped) so the class works on component root elements -->
<style>
.ui-transition {
  transition: filter 2s ease;
}

.ui-dimmed {
  filter: brightness(0.2) saturate(0.3);
  pointer-events: none;
}
</style>
