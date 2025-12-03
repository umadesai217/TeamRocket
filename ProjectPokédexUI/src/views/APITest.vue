<script setup>
import { ref } from 'vue'

const API_URL = 'https://65410b355040.ngrok-free.app/upload/'

const file = ref(null)
const status = ref('')
const result = ref(null)
const error = ref('')

const onFileChange = (e) => {
  file.value = e.target.files[0] || null
}

const sendTest = async () => {
  error.value = ''
  result.value = null
  status.value = 'Sending...'

  try {
    if (!file.value) {
      error.value = 'Pick a file first.'
      status.value = ''
      return
    }

    const formData = new FormData()
    formData.append('file', file.value, file.value.name)

    const res = await fetch(API_URL, {
      method: 'POST',
      body: formData,
    })

    status.value = `HTTP ${res.status}`

    const text = await res.text()
    // Try to parse JSON if possible
    try {
      result.value = JSON.parse(text)
    } catch {
      result.value = text
    }
  } catch (e) {
    console.error(e)
    error.value = String(e)
    status.value = 'Request failed'
  }
}
</script>

<template>
  <div style="border:1px solid #333; padding:10px; margin:10px 0;">
    <h3>API Test</h3>
    <input type="file" @change="onFileChange" />
    <button @click="sendTest">Send to API</button>

    <p v-if="status"><strong>Status:</strong> {{ status }}</p>
    <p v-if="error" style="color:red;">Error: {{ error }}</p>

    <pre v-if="result" style="white-space:pre-wrap; background:#f5f5f5; padding:8px;">
      {{ result }}
    </pre>
  </div>
</template>
