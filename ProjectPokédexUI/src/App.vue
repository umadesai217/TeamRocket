<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

// --- Login state ---
const loggedIn = ref(false)
const username = ref('')

// --- Page state ---
const currentPage = ref('camera') // 'camera' or 'scans'

// --- Camera and video ---
const cameraActive = ref(false)
const videoRef = ref(null)
let stream = null

// --- Scans ---
const scans = ref([])
const loadScans = () => {
  const stored = JSON.parse(localStorage.getItem('scans') || '[]')
  scans.value = stored
}

// --- Messages ---
const message = ref('Welcome!')

// --- Camera functions ---
const toggleCamera = async () => {
  if (cameraActive.value) stopCamera()
  else await startCamera()
}

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    videoRef.value.srcObject = stream
    cameraActive.value = true
    message.value = 'Camera is live.'
  } catch (err) {
    console.error(err)
    message.value = 'Error accessing camera.'
  }
}

const stopCamera = () => {
  if (stream) stream.getTracks().forEach(track => track.stop())
  cameraActive.value = false
  message.value = 'Camera stopped.'
}

const capturePhoto = () => {
  if (!cameraActive.value) return
  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoRef.value, 0, 0)
  const dataUrl = canvas.toDataURL('image/png')
  scans.value.push(dataUrl)
  localStorage.setItem('scans', JSON.stringify(scans.value))
  message.value = 'Pokédex entry captured!'
}

// --- Clear scans ---
const clearScans = () => {
  scans.value = []
  localStorage.removeItem('scans')
  message.value = 'All Pokédex entries cleared.'
}

// Load scans on mount
onMounted(() => loadScans())

// Stop camera when leaving
onBeforeUnmount(() => stopCamera())
</script>

<template>
  <div v-if="!loggedIn" class="login-container">
    <h2>Pokédex Login</h2>
    <input type="text" v-model="username" placeholder="Trainer Name" />
    <button @click="loggedIn = true">Login</button>
  </div>

  <div v-else class="app-container">
    <header class="toolbar">
      <h1>Pokédex App</h1>
      <div class="toolbar-buttons">
        <button @click="currentPage = 'camera'" :disabled="currentPage === 'camera'">Camera</button>
        <button @click="currentPage = 'scans'" :disabled="currentPage === 'scans'">Scans</button>
      </div>
    </header>

    <div v-if="currentPage === 'camera'" class="page camera-page">
      <div class="camera-box">
        <video ref="videoRef" autoplay playsinline></video>
        <div class="camera-controls">
          <button @click="toggleCamera">{{ cameraActive ? 'Stop Camera' : 'Start Camera' }}</button>
          <button @click="capturePhoto" :disabled="!cameraActive">Capture</button>
        </div>
      </div>
      <div class="message-box">
        <p>{{ message }}</p>
      </div>
    </div>

    <div v-if="currentPage === 'scans'" class="page scans-page">
      <div class="scans-box">
        <h3>Pokédex Entries</h3>
        <div class="scans-list">
          <img v-for="(scan, index) in scans" :key="index" :src="scan" />
        </div>
        <button @click="clearScans" :disabled="scans.length === 0">Clear All Entries</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- Login --- */
.login-container {
  max-width: 300px;
  margin: 50px auto;
  text-align: center;
}

/* --- App container --- */
.app-container {
  padding: 10px;
  max-width: 600px;
  margin: 0 auto;
}

/* --- Toolbar --- */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.toolbar-buttons button {
  margin-left: 5px;
}

/* --- Camera box --- */
.camera-box {
  border: 2px solid #333;
  padding: 10px;
  margin-bottom: 10px;
}

.camera-box video {
  width: 100%;
  max-height: 300px;
  background: #000;
}

.camera-controls {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

/* --- Message box --- */
.message-box {
  border: 2px solid #333;
  padding: 10px;
  margin-bottom: 10px;
}

/* --- Scans box --- */
.scans-box {
  border: 2px solid #333;
  padding: 10px;
}

.scans-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.scans-list img {
  width: 100px;
  height: 100px;
  object-fit: cover;
}
</style>