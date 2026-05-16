import { supabase } from '../lib/supabase.js'
import { useAppState } from './useAppState.js'
import { useLibraryStore } from './useLibraryStore.js'

const API_URL = import.meta.env.VITE_API_URL

// Normalise a value that may be a string, comma-separated string, or array
function toArray(v) {
  if (!v) return []
  if (Array.isArray(v)) return v
  return String(v).split(',').map(s => s.trim()).filter(Boolean)
}

function cardImageUrl(setId, number) {
  if (!setId || !number) return null
  const num = String(number).split('/')[0]
  return `https://images.pokemontcg.io/${setId}/${num}_hires.png`
}

export function useCardScanner() {
  const { scannedCard, cardMeta, cardTrade, scanStatus, setScreen, activeSettings, profileActive, confirmStep, pendingCardId, pendingCard, pendingImageUrl, pendingLibraryId, currentUser } = useAppState()
  const { loadScans } = useLibraryStore()

  // ── Full data fetch: attacks + set + price ────────────────────────────────
  // Called immediately for known cards, or after scan confirmation for new ones
  async function fetchCardData(card) {
    const [
      { data: attacks },
      { data: set },
      { data: price },
    ] = await Promise.all([
      supabase.from('attacks').select('*').eq('card_id', card.id),
      supabase.from('sets').select('*').eq('id', card.set_id).single(),
      supabase.from('tcgplayer').select('*').eq('card_id', card.id).single(),
    ])

    if (attacks) attacks.forEach(a => {
      a.cost = toArray(a.cost)
      a.type = toArray(a.type)
    })

    cardMeta.value  = { ...card, attacks: attacks ?? [], set: set ?? null }
    cardTrade.value = price ?? null
  }

  // ── Phase 1: show card image, decide whether to confirm ───────────────────
  async function _processCard(imageUrl, card) {
    const cardId = card.id

    // Normalise array fields on the cardinfo row
    card.subtypes      = toArray(card.subtypes)
    card.pokemon_types = toArray(card.pokemon_types)
    card.retreat_cost  = toArray(card.retreat_cost)

    // Show the card image immediately
    scannedCard.value = { imageUrl, name: card.card_name }

    // Check if this user already has this card in their library
    const { data: libraryEntry } = await supabase
      .from('library')
      .select('id, tag')
      .eq('card_id', cardId)
      .eq('user_id', currentUser.value?.id)
      .maybeSingle()

    if (libraryEntry?.tag === 'owned') {
      // Already owned — fetch all data, no confirmation needed
      await fetchCardData(card)
      confirmStep.value      = null
      pendingCardId.value    = null
      pendingCard.value      = null
      pendingImageUrl.value  = null
      pendingLibraryId.value = null
    } else if (libraryEntry?.tag === 'unowned') {
      // Previously unowned — log the scan as known and prompt for ownership update
      await fetchCardData(card)
      const { error: scanErr } = await supabase.from('scans').insert({
        user_id:   currentUser.value?.id,
        card_id:   cardId,
        tag:       'known',
        image_url: imageUrl,
      })
      if (scanErr) console.error('[CardScanner] rescan scan insert', scanErr)
      else loadScans()

      pendingCard.value      = card
      pendingImageUrl.value  = imageUrl
      pendingCardId.value    = cardId
      pendingLibraryId.value = libraryEntry.id
      confirmStep.value      = 'ownership'
    } else {
      // New card — hold the card row for phase 2, wait for user confirmation
      // before hitting attacks / sets / tcgplayer
      pendingCard.value      = card
      pendingImageUrl.value  = imageUrl
      pendingCardId.value    = cardId
      pendingLibraryId.value = null
      confirmStep.value      = 'scan'
    }

    // Switch to card viewer with Settings1 lit
    profileActive.value  = false
    activeSettings.value = 1
    setScreen('card-viewer')
    scanStatus.value = 'idle'
  }

  // ── Real scan: POST image to TeamRocket /upload/ → look up by id ──────────
  // API contract:
  //   POST {file: image} → { URL: <imagekit url>, FileName: <set>-<num> }
  //   On match failure the API returns 200 with { error: "<message>" }.
  // FileName matches cardinfo.id exactly (e.g. "sv1-100").
  async function scanImage(blob) {
    scanStatus.value = 'scanning'
    try {
      if (!API_URL) throw new Error('VITE_API_URL is not set')

      const formData = new FormData()
      formData.append('file', blob, 'capture.png')

      const apiRes = await fetch(API_URL, { method: 'POST', body: formData })
      if (!apiRes.ok) throw new Error(`API ${apiRes.status}`)

      const body = await apiRes.json()
      if (body?.error) throw new Error(body.error)

      const { URL: imageUrl, FileName: cardId } = body
      if (!cardId) throw new Error('API response missing FileName')

      const { data: card, error: cardErr } = await supabase
        .from('cardinfo')
        .select('*')
        .eq('id', cardId)
        .single()

      if (cardErr) throw cardErr
      await _processCard(imageUrl, card)

    } catch (err) {
      console.error('[CardScanner]', err)
      scanStatus.value = 'error'
    }
  }

  // ── Mock scan: query by id, skip API entirely ──────────────────────────────
  async function mockScan(cardId) {
    scanStatus.value = 'scanning'
    try {
      const { data: card, error: cardErr } = await supabase
        .from('cardinfo')
        .select('*')
        .eq('id', cardId)
        .single()

      if (cardErr) throw cardErr

      const imageUrl = cardImageUrl(card.set_id, card.number)
      await _processCard(imageUrl, card)

    } catch (err) {
      console.error('[CardScanner mock]', err)
      scanStatus.value = 'error'
    }
  }

  // ── View an existing library card (no confirmation, just display) ─────────
  async function viewCard(cardId, imageUrl) {
    scanStatus.value = 'scanning'
    try {
      const { data: card, error } = await supabase
        .from('cardinfo')
        .select('*')
        .eq('id', cardId)
        .single()
      if (error) throw error

      card.subtypes      = toArray(card.subtypes)
      card.pokemon_types = toArray(card.pokemon_types)
      card.retreat_cost  = toArray(card.retreat_cost)

      const finalImageUrl = imageUrl || cardImageUrl(card.set_id, card.number)
      scannedCard.value = { imageUrl: finalImageUrl, name: card.card_name }

      await fetchCardData(card)

      confirmStep.value      = null
      pendingCardId.value    = null
      pendingCard.value      = null
      pendingImageUrl.value  = null
      pendingLibraryId.value = null

      profileActive.value  = false
      activeSettings.value = 1
      setScreen('card-viewer')
      scanStatus.value = 'idle'
    } catch (err) {
      console.error('[CardScanner] viewCard', err)
      scanStatus.value = 'error'
    }
  }

  return { scanImage, mockScan, viewCard, scanStatus, fetchCardData }
}
