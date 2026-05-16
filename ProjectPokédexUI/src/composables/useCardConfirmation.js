import { ref } from 'vue'
import { supabase } from '../lib/supabase.js'
import { useAppState } from './useAppState.js'
import { useCardScanner } from './useCardScanner.js'
import { useLibraryStore } from './useLibraryStore.js'

// Module-level saving guard so the UI can disable buttons during DB writes
const saving = ref(false)

export function useCardConfirmation() {
  const { confirmStep, pendingCardId, pendingCard, pendingImageUrl, pendingLibraryId, currentUser, scannedCard } = useAppState()
  const { fetchCardData } = useCardScanner()
  const { loadLibrary, loadScans } = useLibraryStore()

  // ── Step 1: user answers "Is this correct?" ──────────────────────────────
  async function answerScan(isCorrect) {
    if (saving.value) return
    saving.value = true

    const { error: scanErr } = await supabase.from('scans').insert({
      user_id:   currentUser.value?.id,
      card_id:   isCorrect ? pendingCardId.value : null,
      tag:       isCorrect ? 'known' : 'unknown',
      image_url: scannedCard.value?.imageUrl ?? null,
    })
    if (scanErr) console.error('[Confirmation] scan insert', scanErr)

    if (isCorrect) {
      // Confirmed — now fetch attacks, set, and price data
      try {
        await fetchCardData(pendingCard.value)
      } catch (err) {
        console.error('[Confirmation] fetchCardData', err)
      }
      saving.value = false
      loadScans()
      confirmStep.value = 'ownership'
    } else {
      // Wrong card — discard pending, meta/trade stay blank
      saving.value          = false
      loadScans()
      confirmStep.value     = null
      pendingCardId.value   = null
      pendingCard.value     = null
      pendingImageUrl.value = null
    }
  }

  // ── Step 2: user answers "Do you own it?" ────────────────────────────────
  async function answerOwnership(isOwned) {
    if (saving.value) return
    saving.value = true

    const tag = isOwned ? 'owned' : 'unowned'
    const libErr = pendingLibraryId.value
      ? (await supabase.from('library').update({ tag }).eq('id', pendingLibraryId.value)).error
      : (await supabase.from('library').insert({
          user_id: currentUser.value?.id,
          card_id: pendingCardId.value,
          tag,
        })).error
    if (libErr) console.error('[Confirmation] library write', libErr)

    saving.value           = false
    loadLibrary()
    confirmStep.value      = null
    pendingCardId.value    = null
    pendingCard.value      = null
    pendingImageUrl.value  = null
    pendingLibraryId.value = null
  }

  // ── Abandonment: called when user navigates away mid-flow ─────────────────
  // step = 'scan'      → scan never answered: save as 'unknown', skip library
  // step = 'ownership' → scan was already saved; save library as 'unowned'
  async function abandonConfirmation() {
    if (!confirmStep.value) return

    if (confirmStep.value === 'scan') {
      const { error: scanErr } = await supabase.from('scans').insert({
        user_id:   currentUser.value?.id,
        card_id:   null,
        tag:       'unknown',
        image_url: scannedCard.value?.imageUrl ?? null,
      })
      if (scanErr) console.error('[Confirmation] abandon-scan insert', scanErr)
      loadScans()

    } else if (confirmStep.value === 'ownership') {
      // Re-scan abandon: existing row is already 'unowned', no write needed.
      if (!pendingLibraryId.value) {
        const { error: libErr } = await supabase.from('library').insert({
          user_id: currentUser.value?.id,
          card_id: pendingCardId.value,
          tag:     'unowned',
        })
        if (libErr) console.error('[Confirmation] abandon-ownership insert', libErr)
        loadLibrary()
      }
    }

    confirmStep.value      = null
    pendingCardId.value    = null
    pendingCard.value      = null
    pendingImageUrl.value  = null
    pendingLibraryId.value = null
  }

  return { saving, answerScan, answerOwnership, abandonConfirmation }
}
