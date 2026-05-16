<template>
  <Transition name="fade">
    <div v-if="visible" class="welcome-overlay" @click.self="dismiss">
      <div class="welcome-card">
        <button class="close-btn" @click="dismiss" aria-label="Close">×</button>

        <h1 class="title">Welcome, Trainer</h1>
        <div class="divider" />

        <ul class="steps">
          <li>
            <span class="dot red" />
            <div class="step-text">
              <div class="step-title">Scan a card</div>
              <div class="step-desc">
                Tap the round red <strong>Camera</strong> in the bottom-left. Answer <strong>YES / NO</strong> when prompted to save it to your Library.
                <em>Scanner offline? Tap <strong>DEV</strong> in the camera view and type a card ID.</em>
              </div>
            </div>
          </li>

          <li>
            <span class="dot yellow" />
            <div class="step-text">
              <div class="step-title">Library &amp; Scans</div>
              <div class="step-desc">
                Drag the silver <strong>tab on the right edge</strong> to slide the panel open. Use the bottom buttons to switch between Library and Scans. Tap any card to open it on the main screen.
              </div>
            </div>
          </li>

          <li>
            <span class="dot green" />
            <div class="step-text">
              <div class="step-title">Ask Rotom</div>
              <div class="step-desc">
                Type a question in the green <strong>Pokédex</strong> window at the bottom and press <strong>Enter</strong>. Rotom answers as a Pokédex.
              </div>
            </div>
          </li>

          <li>
            <span class="dot blue" />
            <div class="step-text">
              <div class="step-title">Hear a bio</div>
              <div class="step-desc">
                Open a card, then tap the round <strong>Rotom face</strong> (next to the input) to hear a spoken Pokédex entry. Tap again to stop.
              </div>
            </div>
          </li>

          <li>
            <span class="dot grey" />
            <div class="step-text">
              <div class="step-title">Settings</div>
              <div class="step-desc">
                Tap your <strong>profile icon</strong> (top-left), then the colored buttons for Profile, Accessibility, and App settings.
              </div>
            </div>
          </li>
        </ul>

        <button class="got-it" @click="dismiss">GOT IT</button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { useSettings } from '../composables/useSettings.js'
import { useAppState } from '../composables/useAppState.js'

const { onboardingDismissed } = useSettings()
const { currentUser, activeScreen } = useAppState()

const visible = computed(() => {
  if (onboardingDismissed.value) return false
  if (!currentUser.value) return false
  // Wait until the boot/welcome animations have settled
  if (activeScreen.value === 'booting' || activeScreen.value === 'welcome') return false
  return true
})

function dismiss() {
  onboardingDismissed.value = true
}
</script>

<style scoped>
.welcome-overlay {
  position: absolute;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 10, 14, 0.65);
  backdrop-filter: blur(2px);
  pointer-events: all;
}

.welcome-card {
  position: relative;
  width: min(86%, 340px);
  max-height: 86%;
  overflow-y: auto;
  background: #E3F4EE;
  border: 3px solid #000;
  border-radius: 6px;
  box-shadow: 0 0 0 3px #919191, 0 6px 20px rgba(0, 0, 0, 0.6);
  padding: 18px 18px 16px;
  font-family: 'Jura', sans-serif;
  color: #1a1a1a;
}

.close-btn {
  position: absolute;
  top: 4px;
  right: 8px;
  width: 22px;
  height: 22px;
  background: transparent;
  border: none;
  font-family: 'Iceland', sans-serif;
  font-size: 22px;
  line-height: 1;
  color: #1a1a1a;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  padding: 0;
}
.close-btn:active { filter: brightness(0.6); }

.title {
  font-family: 'Jaro', sans-serif;
  font-size: 26px;
  font-weight: 400;
  color: #FFD624;
  -webkit-text-stroke: 1.5px #005B98;
  margin: 0 0 4px;
  letter-spacing: 1.5px;
  text-align: center;
}

.divider {
  height: 2px;
  background: #1a1a1a;
  margin: 0 0 12px;
  border-radius: 1px;
}

.steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 11px;
}

.steps li {
  display: flex;
  align-items: flex-start;
  gap: 9px;
}

.step-text {
  flex: 1;
  min-width: 0;
}

.step-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.3px;
  color: #1a1a1a;
  margin-bottom: 1px;
}

.step-desc {
  font-size: 11px;
  line-height: 1.45;
  color: #2a2a2a;
}

.step-desc strong {
  font-weight: 700;
  color: #1a1a1a;
}

.step-desc em {
  display: block;
  margin-top: 3px;
  font-style: italic;
  font-size: 10.5px;
  color: #5a5a5a;
}

.dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
  border: 1.5px solid #1a1a1a;
}
.dot.red    { background: #FF2423; }
.dot.yellow { background: #FFD624; }
.dot.green  { background: #33CC57; }
.dot.blue   { background: #2FABD0; }
.dot.grey   { background: #B1B1B1; }

.got-it {
  display: block;
  margin: 16px auto 0;
  font-family: 'Iceland', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
  color: #FFD624;
  background: #1a0205;
  border: 2px solid #1a1a1a;
  border-radius: 4px;
  padding: 6px 26px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease;
}
.got-it:active {
  filter: brightness(0.7);
  transform: scale(0.97);
}

.fade-enter-from,
.fade-leave-to   { opacity: 0; }
.fade-enter-active,
.fade-leave-active { transition: opacity 0.25s ease; }
</style>
