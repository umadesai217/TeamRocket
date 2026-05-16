import { ref } from 'vue'

// Global singleton state - import this anywhere to read or change the active screen
const activeScreen   = ref('loading')  // starts blank while session is checked
const currentUser    = ref(null)       // Supabase User object when logged in
const profileActive  = ref(false)
const activeSettings = ref(null)

const scannedCard    = ref(null)   // { imageUrl, name } - populated after a scan
const cardMeta       = ref(null)   // full cardinfo + attacks + set from Supabase
const cardTrade      = ref(null)   // tcgplayer price row from Supabase
const scanStatus     = ref('idle') // 'idle' | 'scanning' | 'error'

// Confirmation flow - shown in CardViewerScreen for new (unlibrary'd) cards
const confirmStep    = ref(null)   // null | 'scan' | 'ownership'
const pendingCardId  = ref(null)   // card_id currently awaiting confirmation
const pendingCard    = ref(null)   // full cardinfo row held between confirmation phases
const pendingImageUrl = ref(null)  // image URL held between confirmation phases
const pendingLibraryId = ref(null) // existing library row id when re-confirming ownership (re-scan flow)

export function useAppState() {
  function setScreen(screen) {
    activeScreen.value = screen
  }

  function resetButtons() {
    profileActive.value  = false
    activeSettings.value = null
  }

  return {
    activeScreen, setScreen,
    currentUser,
    profileActive, activeSettings,
    resetButtons,
    scannedCard, cardMeta, cardTrade, scanStatus,
    confirmStep, pendingCardId, pendingCard, pendingImageUrl, pendingLibraryId,
  }
}
