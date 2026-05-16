<template>
  <div class="screen">

    <span v-if="!scannedCard" class="label">CARD VIEWER</span>

    <template v-else>
      <!-- Card image always fills the screen -->
      <img
        :src="scannedCard.imageUrl"
        :alt="scannedCard.name"
        class="card-img"
        draggable="false"
      />

      <!-- Question header — slides down from top -->
      <Transition name="slide-top">
        <div v-if="confirmStep" class="confirm-header">
          <span class="confirm-question">
            {{ confirmStep === 'scan' ? 'Is this correct?' : 'Do you own it?' }}
          </span>
        </div>
      </Transition>

      <!-- Answer buttons footer — slides up from bottom -->
      <Transition name="slide-bottom">
        <div v-if="confirmStep" class="confirm-footer">
          <button
            class="confirm-btn yes"
            :disabled="saving"
            @click="handleYes"
          >YES</button>
          <button
            class="confirm-btn no"
            :disabled="saving"
            @click="handleNo"
          >NO</button>
        </div>
      </Transition>
    </template>

  </div>
</template>

<script setup>
import { useAppState } from '../../composables/useAppState'
import { useCardConfirmation } from '../../composables/useCardConfirmation'

const { scannedCard, confirmStep } = useAppState()
const { saving, answerScan, answerOwnership } = useCardConfirmation()

function handleYes() {
  if (confirmStep.value === 'scan')      answerScan(true)
  else if (confirmStep.value === 'ownership') answerOwnership(true)
}

function handleNo() {
  if (confirmStep.value === 'scan')      answerScan(false)
  else if (confirmStep.value === 'ownership') answerOwnership(false)
}
</script>

<style scoped>
.screen {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1a0a0a;
  overflow: hidden;
}

.label {
  font-family: 'Iceland', sans-serif;
  font-size: 18px;
  color: #E3F4EE;
  opacity: 0.4;
  letter-spacing: 2px;
}

.card-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

/* ── Confirmation overlays ── */

.confirm-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(to bottom, rgba(0,0,0,0.78) 60%, transparent);
  z-index: 10;
}

.confirm-question {
  font-family: 'Iceland', sans-serif;
  font-size: 16px;
  color: #E3F4EE;
  letter-spacing: 1.5px;
}

.confirm-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  background: linear-gradient(to top, rgba(0,0,0,0.78) 60%, transparent);
  z-index: 10;
}

.confirm-btn {
  font-family: 'Iceland', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
  padding: 5px 22px;
  border-radius: 3px;
  border: 1.5px solid;
  background: transparent;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease;
}

.confirm-btn:disabled {
  opacity: 0.4;
  cursor: default;
}

.confirm-btn.yes {
  color: #7fff9e;
  border-color: rgba(127, 255, 158, 0.55);
}

.confirm-btn.no {
  color: #ff7f7f;
  border-color: rgba(255, 127, 127, 0.55);
}

.confirm-btn:not(:disabled):active {
  filter: brightness(0.6);
  transform: scale(0.94);
}

/* ── Slide transitions ── */

.slide-top-enter-from,
.slide-top-leave-to {
  transform: translateY(-100%);
}
.slide-top-enter-active,
.slide-top-leave-active {
  transition: transform 0.28s ease;
}
.slide-top-enter-to,
.slide-top-leave-from {
  transform: translateY(0);
}

.slide-bottom-enter-from,
.slide-bottom-leave-to {
  transform: translateY(100%);
}
.slide-bottom-enter-active,
.slide-bottom-leave-active {
  transition: transform 0.28s ease;
}
.slide-bottom-enter-to,
.slide-bottom-leave-from {
  transform: translateY(0);
}
</style>
