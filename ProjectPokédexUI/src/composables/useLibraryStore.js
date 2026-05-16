import { ref, computed } from 'vue'
import { supabase } from '../lib/supabase.js'
import { useAppState } from './useAppState.js'

const cards = ref([])
const scans = ref([])

// Browsing state for the Library tab — kept module-level so it survives panel
// open/close cycles.
const searchQuery = ref('')
const sortKey     = ref('date')   // 'date' | 'name' | 'set' | 'value'
const groupBySet  = ref(false)

// Sets tab — catalog of all sets, plus drill-down state
const setsCatalog   = ref([])     // [{ id, name, total }] from sets+cardinfo
const selectedSetId = ref(null)   // null = show grid; setId = show set detail
const setDetailCards = ref([])    // cards for the currently-drilled set

// Sets we have logos for in public/sets/<id>.png — only these appear in the
// Sets grid. Add an entry here whenever you drop a new logo into that folder.
const SETS_WITH_LOGOS = new Set([
  // Scarlet & Violet
  'sv1', 'sv2', 'sv3', 'sv3pt5', 'sv4', 'sv4pt5', 'sv5', 'sv6',
  'sv6pt5', 'sv7', 'sv8', 'sv8pt5', 'sv9', 'sv10',
  'rsv10pt5', 'zsv10pt5',
  // Mega Evolution
  'me1', 'me2',
])

function cardImageUrl(setId, number) {
  if (!setId || !number) return null
  const num = String(number).split('/')[0]
  return `https://images.pokemontcg.io/${setId}/${num}_hires.png`
}

async function fetchCardinfoMap(cardIds) {
  const unique = [...new Set(cardIds.filter(Boolean))]
  if (!unique.length) return new Map()

  // Pull the set name (for grouping/labels) and market price (for collection
  // value) in one round-trip via PostgREST joins.
  const { data, error } = await supabase
    .from('cardinfo')
    .select('id, card_name, number, set_id, sets(id, name), tcgplayer(price_market)')
    .in('id', unique)

  if (error) {
    console.error('[LibraryStore] fetchCardinfoMap', error)
    return new Map()
  }
  return new Map((data ?? []).map(i => [i.id, i]))
}

// Natural sort for set numbers: "2" before "10", "001" before "100/162".
function compareSetNumber(a, b) {
  const an = parseInt(String(a ?? '').split('/')[0], 10)
  const bn = parseInt(String(b ?? '').split('/')[0], 10)
  if (Number.isFinite(an) && Number.isFinite(bn) && an !== bn) return an - bn
  return String(a ?? '').localeCompare(String(b ?? ''))
}

export function useLibraryStore() {
  const { currentUser } = useAppState()

  async function loadLibrary() {
    if (!currentUser.value?.id) {
      cards.value = []
      return
    }

    const { data: rows, error } = await supabase
      .from('library')
      .select('id, card_id, tag, created_at')
      .eq('user_id', currentUser.value.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('[LibraryStore] loadLibrary', error)
      return
    }

    const infoMap = await fetchCardinfoMap((rows ?? []).map(r => r.card_id))

    cards.value = (rows ?? []).map(row => {
      const info = infoMap.get(row.card_id) ?? {}
      const setRow = info.sets ?? null
      const priceRow = info.tcgplayer ?? null
      return {
        id:        row.id,
        cardId:    row.card_id,
        name:      info.card_name ?? row.card_id,
        setNumber: info.number ?? null,
        setId:     info.set_id ?? null,
        setName:   setRow?.name ?? info.set_id ?? 'Unknown set',
        price:     priceRow?.price_market ?? null,
        image:     cardImageUrl(info.set_id, info.number),
        tag:       row.tag,
        addedAt:   new Date(row.created_at),
      }
    })
  }

  async function loadScans() {
    if (!currentUser.value?.id) {
      scans.value = []
      return
    }

    const { data: rows, error } = await supabase
      .from('scans')
      .select('id, card_id, tag, image_url, created_at')
      .eq('user_id', currentUser.value.id)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('[LibraryStore] loadScans', error)
      return
    }

    const infoMap = await fetchCardinfoMap((rows ?? []).map(r => r.card_id))

    scans.value = (rows ?? []).map(row => {
      const info = infoMap.get(row.card_id) ?? {}
      return {
        id:         row.id,
        cardId:     row.card_id,
        name:       info.card_name ?? row.card_id ?? 'Unknown',
        image:      row.image_url,
        tag:        row.tag,
        capturedAt: new Date(row.created_at),
      }
    })
  }

  // ── Sets catalog ─────────────────────────────────────────────────────────
  async function loadSetsCatalog() {
    if (setsCatalog.value.length) return  // already cached
    // Pull the authoritative `total` straight from the sets table; cardinfo is
    // incomplete and would undercount the official set size.
    const { data, error } = await supabase
      .from('sets')
      .select('id, name, series, total, printed_total')
    if (error) { console.error('[LibraryStore] sets', error); return }

    setsCatalog.value = (data ?? []).map(s => ({
      id:     s.id,
      name:   s.name,
      series: s.series ?? '',
      // Prefer total (includes secret rares), fall back to printed_total.
      total:  s.total ?? s.printed_total ?? 0,
    }))
  }

  // Live per-set progress derived from setsCatalog + the user's library.
  const setsList = computed(() => {
    const owned = new Map()
    for (const c of cards.value) {
      if (c.tag === 'owned' && c.setId) {
        owned.set(c.setId, (owned.get(c.setId) ?? 0) + 1)
      }
    }
    return setsCatalog.value
      .filter(s => SETS_WITH_LOGOS.has(s.id))
      .map(s => ({ ...s, owned: owned.get(s.id) ?? 0 }))
      .sort((a, b) => b.owned / Math.max(b.total, 1) - a.owned / Math.max(a.total, 1)
        || a.name.localeCompare(b.name))
  })

  async function loadSetDetail(setId) {
    selectedSetId.value = setId
    setDetailCards.value = []
    if (!setId) return

    const [cardsRes, libRes] = await Promise.all([
      supabase
        .from('cardinfo')
        .select('id, card_name, number, set_id, tcgplayer(price_market)')
        .eq('set_id', setId),
      supabase
        .from('library')
        .select('id, card_id, tag')
        .eq('user_id', currentUser.value?.id),
    ])
    if (cardsRes.error) { console.error('[LibraryStore] set detail cards', cardsRes.error); return }

    const libMap = new Map((libRes.data ?? []).map(l => [l.card_id, l]))

    setDetailCards.value = (cardsRes.data ?? [])
      .map(c => {
        const lib = libMap.get(c.id)
        return {
          id:        lib?.id ?? c.id,
          cardId:    c.id,
          name:      c.card_name,
          setNumber: c.number,
          setId:     c.set_id,
          price:     c.tcgplayer?.price_market ?? null,
          image:     cardImageUrl(c.set_id, c.number),
          tag:       lib?.tag ?? null,   // null → undiscovered
          addedAt:   null,
        }
      })
      .sort((a, b) => compareSetNumber(a.setNumber, b.setNumber))
  }

  function clearSetDetail() {
    selectedSetId.value = null
    setDetailCards.value = []
  }

  // ── Collection summary ───────────────────────────────────────────────────
  const stats = computed(() => {
    let owned = 0, unowned = 0, value = 0
    for (const c of cards.value) {
      if (c.tag === 'owned') {
        owned++
        if (c.price) value += c.price
      } else if (c.tag === 'unowned') {
        unowned++
      }
    }
    return { owned, unowned, value }
  })

  // ── Library list pipeline (filter → search → sort) ───────────────────────
  function processedCards(activeFilter) {
    let result = cards.value

    if (activeFilter) {
      result = result.filter(c => c.tag === activeFilter)
    }

    const q = searchQuery.value.trim().toLowerCase()
    if (q) {
      result = result.filter(c =>
        c.name.toLowerCase().includes(q) ||
        (c.setName ?? '').toLowerCase().includes(q) ||
        (c.cardId ?? '').toLowerCase().includes(q),
      )
    }

    const sorted = [...result]
    switch (sortKey.value) {
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name))
        break
      case 'set':
        sorted.sort((a, b) =>
          (a.setName ?? '').localeCompare(b.setName ?? '') ||
          compareSetNumber(a.setNumber, b.setNumber),
        )
        break
      case 'value':
        sorted.sort((a, b) => (b.price ?? 0) - (a.price ?? 0))
        break
      case 'date':
      default:
        sorted.sort((a, b) => b.addedAt - a.addedAt)
    }
    return sorted
  }

  // Returns an array of { setName, cards } groups. When groupBySet is off
  // there's just one group with setName: null.
  function groupedCards(activeFilter) {
    const flat = processedCards(activeFilter)
    if (!groupBySet.value) return [{ setName: null, cards: flat }]

    const groups = new Map()
    for (const c of flat) {
      const key = c.setName || 'Unknown set'
      if (!groups.has(key)) groups.set(key, [])
      groups.get(key).push(c)
    }
    return [...groups.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([setName, list]) => ({ setName, cards: list }))
  }

  // Scans use 'known'/'unknown' tags; the filter UI uses owned/unowned slots.
  function filteredScans(activeFilter) {
    if (!activeFilter) return scans.value
    const tagMap = { owned: 'known', unowned: 'unknown' }
    return scans.value.filter(s => s.tag === tagMap[activeFilter])
  }

  return {
    cards, scans,
    stats,
    searchQuery, sortKey, groupBySet,
    processedCards, groupedCards,
    filteredScans,
    // Sets
    setsList, selectedSetId, setDetailCards,
    loadSetsCatalog, loadSetDetail, clearSetDetail,
    // Lifecycle
    loadLibrary, loadScans,
  }
}
