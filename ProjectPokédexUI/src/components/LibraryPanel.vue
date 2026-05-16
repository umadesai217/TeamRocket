<template>
  <div
    class="library-panel"
    ref="panelRef"
    :class="{ dragging: isDragging }"
    :style="{ transform: `translateX(${offset}px)` }"
  >
    <!-- Bar is the drag handle — always pointer-interactive -->
    <!-- Blocks all interaction with the app underneath while panel is open -->
    <div v-if="isOpen" class="overlay" />

    <!-- Center screen — expands downward in sync with bottom bar -->
    <div class="library-screen" :class="{ visible: bottomVisible }">
      <!-- Scrollable card/scan content -->
      <LibraryContent :mode="panelMode" :active-filter="activeFilter" @select-card="onSelectCard" />

      <!-- Filter buttons — centered, flush together -->
      <div v-if="showFilters" class="filter-group" :class="{ visible: bottomVisible }">
        <FilterBtn1 :is-on="activeFilter === 'owned'"   :label="filterLabel1" @select="activeFilter = activeFilter === 'owned' ? null : 'owned'" />
        <FilterBtn2 :is-on="activeFilter === 'unowned'" :label="filterLabel2" @select="activeFilter = activeFilter === 'unowned' ? null : 'unowned'" />
      </div>
    </div>

    <LibraryBottomBar :sliding="isOpen" :visible="bottomVisible" @library="setMode('library')" @scans="setMode('scans')" @sets="setMode('sets')" />

    <div class="panel-bar">
      <span class="panel-title">{{ panelTitle }}</span>
      <!-- Drag handle — covers only the slider tab on the right -->
      <div class="drag-handle" @pointerdown="onPointerDown" />
      <svg
        class="bar-svg"
        viewBox="0 0 392 86"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Main shape — change translate(0, Y) to shift the shadow layer down -->
        <g transform="translate(0, 6)">
          <path d="M6 79H108.32C109.494 78.9999 110.63 78.5871 111.529 77.834L129.687 62.6328C130.946 61.5782 132.537 61.0001 134.18 61H256.99C258.753 61.0001 260.45 61.6652 261.744 62.8623L277.745 77.6699C278.669 78.5249 279.882 78.9999 281.141 79H331.784C333.051 79 334.27 78.5188 335.196 77.6543L352.089 61.8838C353.385 60.6736 355.092 60.0001 356.865 60H376.003C384.287 59.9998 391.003 53.2841 391.003 45V18C391.003 8.61129 383.392 1.00021 374.003 1H6C3.23858 1 1 3.23857 1 6V74C1 76.7614 3.23858 79 6 79Z" fill="#919191" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
        </g>
        <path d="M6 79H108.32C109.494 78.9999 110.63 78.5871 111.529 77.834L129.687 62.6328C130.946 61.5782 132.537 61.0001 134.18 61H256.99C258.753 61.0001 260.45 61.6652 261.744 62.8623L277.745 77.6699C278.669 78.5249 279.882 78.9999 281.141 79H331.784C333.051 79 334.27 78.5188 335.196 77.6543L352.089 61.8838C353.385 60.6736 355.092 60.0001 356.865 60H376.003C384.287 59.9998 391.003 53.2841 391.003 45V18C391.003 8.61129 383.392 1.00021 374.003 1H6C3.23858 1 1 3.23857 1 6V74C1 76.7614 3.23858 79 6 79Z" fill="#E3F4EE" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
        <!-- Slider tab (right edge) -->
        <path d="M354 17H391V45H354V17Z" fill="#B1B1B1"/>
        <path d="M354 2H376.025C376.025 2 382.428 2.5 386.418 7C389.909 10 390.906 17 390.906 17H354V2Z" fill="#E3F4EE"/>
        <path d="M354 59H376.025C376.025 59 381.929 59 386.418 54.5C389.909 51.5 390.713 45 390.713 45H354V59Z" fill="#E3F4EE"/>
        <path d="M354 24H390.906V38H354V24Z" fill="#E3F4EE"/>
        <line x1="354" y1="16.5" x2="390.906" y2="16.5" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
        <line x1="354" y1="24"   x2="390.906" y2="24"   stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
        <line x1="354" y1="38"   x2="390.906" y2="38"   stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
        <line x1="354" y1="44.5" x2="390.906" y2="44.5" stroke="black" stroke-width="3" vector-effect="non-scaling-stroke"/>
      </svg>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import LibraryBottomBar from './LibraryBottomBar.vue'
import FilterBtn1 from './buttons/FilterBtn1.vue'
import FilterBtn2 from './buttons/FilterBtn2.vue'
import LibraryContent from './LibraryContent.vue'
import { useAppState } from '../composables/useAppState'
import { useCardScanner } from '../composables/useCardScanner'
import { useLibraryStore } from '../composables/useLibraryStore'

const { currentUser } = useAppState()
const { viewCard } = useCardScanner()
const { selectedSetId, clearSetDetail } = useLibraryStore()

function onSelectCard(card) {
  viewCard(card.cardId, card.image)
  closePanel()
}

const emit = defineEmits(['owned', 'unowned'])

const panelMode     = ref('library')   // 'library' | 'scans' | 'sets'
const panelTitle    = computed(() => {
  if (panelMode.value === 'scans') return 'Scans'
  if (panelMode.value === 'sets')  return selectedSetId.value ? 'Set' : 'Sets'
  return 'Library'
})
const filterLabel1  = computed(() => panelMode.value === 'scans' ? 'Known'   : 'Owned')
const filterLabel2  = computed(() => panelMode.value === 'scans' ? 'Unknown' : 'Unowned')

// Hide the Owned/Unowned buttons in the sets grid (they're irrelevant there);
// keep them when drilled into a specific set.
const showFilters = computed(() =>
  panelMode.value !== 'sets' || !!selectedSetId.value,
)

function setMode(mode) {
  panelMode.value = mode
  activeFilter.value = null   // reset filter selection on mode switch
  if (mode !== 'sets') clearSetDetail()
}
const panelRef      = ref(null)
const isDragging    = ref(false)
const isOpen        = ref(false)
const bottomVisible = ref(false)
const offset        = ref(0)
const activeFilter  = ref(null)   // 'owned' | 'unowned' | null

let bottomTimer = null

// The slider tab starts at x=354 in the 392-wide viewBox → 90.3% from left
const TAB_RATIO = 354 / 392

function getClosedOffset() {
  if (!panelRef.value) return 0
  return -panelRef.value.offsetWidth * TAB_RATIO
}

onMounted(() => {
  offset.value = getClosedOffset()
})

// ── Drag state ──
let dragStartX    = 0
let dragStartOffset = 0
let maxDelta      = 0
let lastVX        = 0
let lastX         = 0
let lastT         = 0

function onPointerDown(e) {
  if (!currentUser.value) return
  isDragging.value = true
  dragStartX      = e.clientX
  dragStartOffset = offset.value
  maxDelta        = 0
  lastVX          = 0
  lastX           = e.clientX
  lastT           = e.timeStamp

  window.addEventListener('pointermove', onPointerMove)
  window.addEventListener('pointerup',   onPointerUp)
}

function onPointerMove(e) {
  const delta = e.clientX - dragStartX
  maxDelta = Math.max(maxDelta, Math.abs(delta))

  // track velocity (px/ms)
  const dt = e.timeStamp - lastT
  if (dt > 0) lastVX = (e.clientX - lastX) / dt
  lastX = e.clientX
  lastT = e.timeStamp

  const closed = getClosedOffset()
  offset.value = Math.min(0, Math.max(closed, dragStartOffset + delta))
}

function onPointerUp() {
  isDragging.value = false
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup',   onPointerUp)

  // Tap (no real movement) → toggle
  if (maxDelta < 6) {
    isOpen.value ? closePanel() : openPanel()
    return
  }

  // Snap by velocity (>0.4 px/ms) or midpoint
  const closed   = getClosedOffset()
  const midpoint = closed / 2

  if (lastVX > 0.4 || offset.value > midpoint) {
    openPanel()
  } else {
    closePanel()
  }
}

function openPanel() {
  isOpen.value = true
  offset.value = 0
  // trigger bottom bar after slide-in completes
  clearTimeout(bottomTimer)
  bottomTimer = setTimeout(() => { bottomVisible.value = true }, 300)
}

function closePanel() {
  isOpen.value        = false
  bottomVisible.value = false
  clearTimeout(bottomTimer)
  offset.value = getClosedOffset()
}

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('pointerup',   onPointerUp)
  clearTimeout(bottomTimer)
})
</script>

<style scoped>
.library-panel {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 50;
  pointer-events: none;         /* panel itself doesn't block the UI underneath */
  display: flex;
  flex-direction: column;
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94), filter 2s ease;
}

.library-panel.dragging {
  transition: none;             /* follow finger in real time while dragging */
}

/* Transparent blocker — eats all clicks while panel is open */
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: all;
  z-index: 0;
  background: #17171779;
}

/* Center screen */
.library-screen {
  position: absolute;
  height: 100%;
  width: 80%;
  left: 50%;
  transform: translateX(-50%) scaleY(0);
  transform-origin: top center;
  border: 3px solid black;
  background-color: #101F13;
  z-index: 1;
  pointer-events: none;
  transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.library-screen.visible {
  transform: translateX(-50%) scaleY(1);
  pointer-events: all;
}

/* Filter button group — just below the panel bar */
.filter-group {
  position: absolute;
  top: 8.4%;
  left: 49%;
  width: 60%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: row;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
  z-index: 2;
}

.filter-group.visible {
  opacity: 1;
  pointer-events: all;
}

/* Bar itself is not interactive — only the drag handle inside it is */
.panel-bar {
  pointer-events: none;
  flex-shrink: 0;
  user-select: none;
  position: relative;
  z-index: 2;
}

/* Covers only the slider tab: x=354–392 out of 392-wide viewBox (~9.7% from right) */
.drag-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 9.7%;
  height: 100%;
  pointer-events: all;
  cursor: grab;
  -webkit-tap-highlight-color: transparent;
}

.drag-handle:active {
  cursor: grabbing;
}

.bar-svg {
  display: block;
  width: 100%;
  height: 86px;
}

.panel-title {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -60%);
  font-family: 'Jaro', sans-serif;
  font-size: 48px;
  color: #FFD624;
  -webkit-text-stroke: 2px #005B98;
  pointer-events: none;
  white-space: nowrap;
  z-index: 1;
}

</style>
