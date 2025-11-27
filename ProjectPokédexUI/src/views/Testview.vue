<script setup>

import { ref, onMounted, onBeforeUnmount } from 'vue'

// --- Login state ---
const loggedIn = ref(false)
const username = ref('')
const password = ref('')
const loginError = ref('')

// login function requiring username + password
const attemptLogin = () => {
  if (!username.value.trim() || !password.value) {
    loginError.value = "Nom d'utilisateur et mot de passe requis."
    return
  }
  loginError.value = ''
  loggedIn.value = true
}

// --- Page state ---
const currentPage = ref('camera') // 'camera' or 'scans'

// --- Camera and video ---
const cameraActive = ref(false)
const videoRef = ref(null)
let stream = null

// --- Scans ---
const scans = ref([])
// each scan will look like:
// { image: string, cardName: string, confidence: number, cardId: number | null }

const isLoading = ref(false)
const scanError = ref('')
const API_BASE_URL = 'https://98776641cde4.ngrok-free.app/upload/' // or wherever FastAPI runs

const loadScans = () => {
  const stored = JSON.parse(localStorage.getItem('scans') || '[]')
  scans.value = stored
}

//
const clearScans = () => {
  scans.value = []
  localStorage.removeItem('scans')
  message.value = 'All Pokédex entries cleared.'
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

const dataUrlToBlob = async (dataUrl) => {
  // re-fetch the data URL, browser gives you a Blob
  const res = await fetch(dataUrl)
  return await res.blob()
}

const capturePhoto = async () => {
  if (!cameraActive.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoRef.value.videoWidth
  canvas.height = videoRef.value.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoRef.value, 0, 0)

  const dataUrl = canvas.toDataURL('image/png')

  isLoading.value = true
  scanError.value = ''
  message.value = 'Analyzing card...'

  try {
    const blob = await dataUrlToBlob(dataUrl)
    const formData = new FormData()
    formData.append('file', blob, 'capture.png')

    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`)
    }

    const result = await response.json()
    // Adjust to match your FastAPI response keys
    const cardName = result.card_name || 'Unknown card'
    const confidence = result.confidence ?? null
    const cardId = result.card_id ?? null

    scans.value.push({
      image: dataUrl,
      cardName,
      confidence,
      cardId,
    })
    localStorage.setItem('scans', JSON.stringify(scans.value))

    const confText = confidence != null ? ` (${(confidence * 100).toFixed(1)}% sure)` : ''
    message.value = `Identified: ${cardName}${confText}`
  } catch (err) {
    console.error(err)
    scanError.value = 'Failed to identify card. Check the server / network.'
    message.value = 'Error while talking to Pokédex core.'
  } finally {
    isLoading.value = false
  }
}

// Stop camera when leaving
onBeforeUnmount(() => stopCamera())
</script>

<template>
  <!--login section-->
  <div v-if="!loggedIn" class="login-container">
    <h2>Pokédex Login</h2>
    <input type="text" v-model="username" placeholder="Trainer Name" />
    <input type="password" v-model="password" placeholder="Password" />
    <div v-if="loginError" class="text-red-600 mt-2">{{ loginError }}</div>
    <button @click="attemptLogin">Login</button>
  </div>

  <!--Main page-->
  <!--toolbar-->
  <div v-else class="app-container">
    <header class="toolbar">
      <h1>Pokédex App</h1>
      <div class="toolbar-buttons">
        <button @click="currentPage = 'camera'" :disabled="currentPage === 'camera'">Camera</button>
        <button @click="currentPage = 'scans'" :disabled="currentPage === 'scans'">Scans</button>
      </div>
    </header>

    <!--camera-->
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
        <p v-if="isLoading">Scanning card...</p>
        <p v-if="scanError" class="text-red-600 mt-2">{{ scanError }}</p>
      </div>
    </div>

    <!--scans page-->
    <div v-if="currentPage === 'scans'" class="page scans-page">
      <div class="scans-box">
        <h3>Pokédex Entries</h3>
        <div class="scans-list">
          <div
            v-for="(scan, index) in scans"
            :key="index"
            class="scan-item"
          >
            <img :src="scan.image" />
            <div class="scan-info">
              <p class="scan-name">
                {{ scan.cardName || 'Unknown card' }}
              </p>
              <p v-if="scan.confidence != null" class="scan-confidence">
                Confidence: {{ (scan.confidence * 100).toFixed(1) }}%
              </p>
              <p v-if="scan.cardId != null" class="scan-id">
                Card ID: {{ scan.cardId }}
              </p>
            </div>
          </div>
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