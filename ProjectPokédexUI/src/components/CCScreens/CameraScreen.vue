<template>
  <div class="screen">

    <!-- Camera feed + capture button -->
    <template v-if="status === 'active'">
      <video ref="videoRef" class="feed" autoplay playsinline muted />
      <button class="capture-btn" @click="capturePhoto" />
    </template>

    <!-- Acquiring camera -->
    <div v-else-if="status === 'loading'" class="overlay">
      <span class="msg">Acquiring camera...</span>
    </div>

    <!-- Scanning / waiting for API -->
    <div v-else-if="status === 'scanning'" class="overlay">
      <span class="msg">Identifying card...</span>
    </div>

    <!-- Error (camera or scan) -->
    <div v-else-if="status === 'error'" class="overlay">
      <span class="msg error">{{ errorMsg }}</span>
      <button class="retry-btn" @click="startCamera">Try Again</button>
    </div>

    <!-- Dev test panel — remove when model is live -->
    <div class="test-panel" v-if="status !== 'scanning'">
      <button class="test-toggle" @click="testOpen = !testOpen">DEV</button>
      <div class="test-form" v-if="testOpen">
        <input
          class="test-input"
          v-model="testId"
          placeholder="Card ID..."
          type="text"
          @keydown.enter="runMock"
        />
        <button class="test-go" @click="runMock">GO</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useCardScanner } from '../../composables/useCardScanner.js'

const { scanImage, mockScan, scanStatus } = useCardScanner()

const videoRef = ref(null)
const status   = ref('loading')  // 'loading' | 'active' | 'scanning' | 'error'
const errorMsg = ref('')
let stream = null

//------Dev test panel---------
const testOpen = ref(false)
const testId   = ref('')

async function runMock() {
  const id = testId.value.trim()
  if (!id) return
  testOpen.value = false
  stopCamera()
  status.value = 'scanning'
  await mockScan(id)
  if (scanStatus.value === 'error') {
    errorMsg.value = 'Mock scan failed — check card ID'
    status.value = 'error'
  }
}

// -----Camera-----------
async function startCamera() {
  status.value = 'loading'
  errorMsg.value = ''
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } }
    })
    status.value = 'active'
    await nextTick()
    videoRef.value.srcObject = stream
  } catch (err) {
    console.error('[CameraScreen]', err)
    errorMsg.value = 'Failed to acquire camera'
    status.value = 'error'
  }
}

function stopCamera() {
  if (stream) {
    stream.getTracks().forEach(t => t.stop())
    stream = null
  }
}

// ------ Capture -----------
async function capturePhoto() {
  if (!videoRef.value) return

  // Draw current frame to canvas
  const canvas = document.createElement('canvas')
  canvas.width  = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  canvas.getContext('2d').drawImage(videoRef.value, 0, 0)

  // Stop camera immediately, show scanning state
  stopCamera()
  status.value = 'scanning'

  // Convert canvas to blob and fire off the scan
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'))
  await scanImage(blob)

  // If the scan failed, scanStatus will be 'error' and the screen hasn't switched
  if (scanStatus.value === 'error') {
    errorMsg.value = 'Failed to identify card'
    status.value = 'error'
  }
  // On success, useCardScanner already called setScreen('card-viewer'),
  // so this component will unmount — nothing more to do here.
}

onMounted(() => startCamera())
onBeforeUnmount(() => stopCamera())
</script>

<style scoped>
.screen {
  position: relative;
  width: 100%;
  height: 100%;
  background-color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* ── Overlays ── */
.overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  width: 100%;
  height: 100%;
}

.msg {
  font-family: 'Jura', sans-serif;
  font-size: 12px;
  color: rgba(214, 244, 255, 0.6);
  text-align: center;
  padding: 0 12px;
}

.msg.error {
  color: #ff6b6b;
}

.retry-btn {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #ffffff;
  background: transparent;
  border: 1.5px solid #ffffff;
  border-radius: 3px;
  padding: 4px 14px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease;
}

.retry-btn:active {
  filter: brightness(0.6);
  transform: scale(0.96);
}

/* ── Capture button ── */
.capture-btn {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  border: 2px solid rgba(255, 255, 255, 0.4);
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.08s ease, background 0.08s ease;
}

.capture-btn::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
}

.capture-btn:active {
  transform: translateX(-50%) scale(0.9);
  background: rgba(255, 255, 255, 0.5);
}

/* ── Dev test panel ── */
.test-panel {
  position: absolute;
  top: 6px;
  right: 6px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  z-index: 10;
}

.test-toggle {
  font-family: 'Iceland', sans-serif;
  font-size: 9px;
  color: rgba(255, 214, 36, 0.6);
  background: transparent;
  border: 1px solid rgba(255, 214, 36, 0.3);
  border-radius: 2px;
  padding: 1px 5px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  letter-spacing: 1px;
}

.test-form {
  display: flex;
  gap: 3px;
  align-items: center;
}

.test-input {
  font-family: 'Jura', sans-serif;
  font-size: 9px;
  color: #fff;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  padding: 2px 5px;
  width: 80px;
  outline: none;
  caret-color: #fff;
  -webkit-tap-highlight-color: transparent;
}

.test-input::placeholder { color: rgba(255,255,255,0.3); }

.test-go {
  font-family: 'Iceland', sans-serif;
  font-size: 9px;
  color: #FFD624;
  background: transparent;
  border: 1px solid rgba(255, 214, 36, 0.4);
  border-radius: 2px;
  padding: 2px 6px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.test-go:active {
  filter: brightness(0.6);
}
</style>
