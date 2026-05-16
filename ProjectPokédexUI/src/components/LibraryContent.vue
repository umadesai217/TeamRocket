<template>
  <div class="library-content">

    <!----LIBRARY MODE ---->
    <template v-if="mode === 'library'">
      <!-- Sticky toolbar: stats line + search/sort/group -->
      <div class="toolbar">
        <div class="stats">
          <span class="stat"><b>{{ stats.owned }}</b> OWNED</span>
          <span class="stat-sep">·</span>
          <span class="stat"><b>{{ stats.unowned }}</b> UNOWNED</span>
          <span class="stat-sep">·</span>
          <span class="stat value"><b>${{ formattedValue }}</b></span>
        </div>
        <div class="controls">
          <input
            class="search"
            v-model="searchQuery"
            type="text"
            placeholder="Search…"
            spellcheck="false"
          />
          <select class="sort" v-model="sortKey">
            <option value="date">Recent</option>
            <option value="name">Name</option>
            <option value="set">Set</option>
            <option value="value">Value</option>
          </select>
          <button
            class="group-btn"
            :class="{ on: groupBySet }"
            @click="groupBySet = !groupBySet"
            :title="groupBySet ? 'Ungroup' : 'Group by set'"
          >⊞</button>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="!totalDisplayed" class="empty">
        <span v-if="!stats.owned && !stats.unowned">No cards in your Library yet.</span>
        <span v-else-if="searchQuery.trim()">No matches for "{{ searchQuery }}".</span>
        <span v-else>No cards in this view.</span>
      </div>

      <!-- Grouped or flat rendering -->
      <template v-for="group in groups" :key="group.setName ?? '_flat'">
        <div v-if="group.setName" class="set-header">
          <span class="set-name">{{ group.setName }}</span>
          <span class="set-count">{{ group.cards.length }}</span>
        </div>
        <div class="card-grid">
          <div
            v-for="card in group.cards"
            :key="card.id"
            class="card-item"
            :class="[card.tag ?? 'undiscovered', { clickable: card.tag !== null }]"
            @click="card.tag !== null && emit('select-card', card)"
          >
            <template v-if="card.tag === null">
              <div class="card-silhouette">
                <span class="question-mark">?</span>
              </div>
            </template>
            <template v-else>
              <img :src="card.image" :alt="card.name" class="card-img" draggable="false" />
              <span v-if="card.price && sortKey === 'value'" class="price-tag">
                ${{ card.price.toFixed(2) }}
              </span>
            </template>
          </div>
        </div>
      </template>
    </template>

    <!----SETS MODE---->
    <template v-else-if="mode === 'sets'">
      <!-- Set grid (no selection) -->
      <template v-if="!selectedSetId">
        <div v-if="!setsList.length" class="empty">Loading sets…</div>
        <div v-else class="sets-grid">
          <div
            v-for="set in setsList"
            :key="set.id"
            class="set-tile"
            :class="{ complete: set.owned >= set.total && set.total > 0 }"
            @click="openSet(set.id)"
          >
            <div class="set-logo-wrap">
              <img
                :src="`/sets/${set.id}.png`"
                :alt="set.name"
                class="set-logo"
                draggable="false"
                @error="onLogoError"
              />
              <div class="set-logo-fallback">{{ set.name }}</div>
            </div>
            <div class="set-tile-name">{{ set.name }}</div>
            <div class="set-progress">
              <div
                class="set-progress-fill"
                :style="{ width: pct(set.owned, set.total) + '%' }"
              />
            </div>
            <div class="set-tile-count">
              <span class="owned">{{ set.owned }}</span>
              <span class="of">/ {{ set.total }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- Set detail (drilled into a specific set) -->
      <template v-else>
        <div class="set-detail-header">
          <button class="back-btn" @click="clearSetDetail">‹ Back</button>
          <div class="set-detail-title">
            <span class="set-detail-name">{{ currentSetMeta?.name ?? 'Set' }}</span>
            <span class="set-detail-count">
              {{ currentSetMeta?.owned ?? 0 }} / {{ currentSetMeta?.total ?? setDetailCards.length }}
            </span>
          </div>
        </div>

        <div v-if="!filteredSetCards.length" class="empty">No cards here.</div>
        <div v-else class="card-grid">
          <div
            v-for="card in filteredSetCards"
            :key="card.cardId"
            class="card-item"
            :class="[card.tag ?? 'undiscovered', { clickable: card.tag !== null }]"
            @click="card.tag !== null && emit('select-card', card)"
          >
            <template v-if="card.tag === null">
              <div class="card-silhouette">
                <span class="question-mark">?</span>
              </div>
            </template>
            <template v-else>
              <img :src="card.image" :alt="card.name" class="card-img" draggable="false" />
            </template>
          </div>
        </div>
      </template>
    </template>

    <!----SCANS MODE---->
    <template v-else>
      <div class="scan-grid">
        <div
          v-for="scan in displayedScans"
          :key="scan.id"
          class="scan-item"
          :class="scan.tag"
        >
          <img :src="scan.image" :alt="scan.name" class="scan-img" draggable="false" />
          <span class="scan-label">{{ scan.name }}</span>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useLibraryStore } from '../composables/useLibraryStore.js'

const props = defineProps({
  mode: {
    type: String,
    default: 'library',   // 'library' | 'scans'
  },
  activeFilter: {
    type: String,
    default: null,        // 'owned' | 'unowned' | null
  },
})

const emit = defineEmits(['select-card'])

const {
  stats,
  searchQuery, sortKey, groupBySet,
  groupedCards, filteredScans,
  setsList, selectedSetId, setDetailCards,
  loadSetDetail, clearSetDetail,
} = useLibraryStore()

const groups = computed(() => groupedCards(props.activeFilter))
const displayedScans = computed(() => filteredScans(props.activeFilter))

// ── Sets helpers ────────────────────────────────────────────────────────
function pct(owned, total) {
  if (!total) return 0
  return Math.min(100, Math.round((owned / total) * 100))
}

async function openSet(setId) {
  await loadSetDetail(setId)
}

function onLogoError(e) {
  // Hide the broken image; the text fallback underneath shows through.
  e.target.style.visibility = 'hidden'
}

const currentSetMeta = computed(() =>
  setsList.value.find(s => s.id === selectedSetId.value) ?? null,
)

const filteredSetCards = computed(() => {
  if (!props.activeFilter) return setDetailCards.value
  // In set detail, 'owned'/'unowned' filter applies; null (undiscovered) is hidden.
  return setDetailCards.value.filter(c => c.tag === props.activeFilter)
})

const totalDisplayed = computed(() =>
  groups.value.reduce((sum, g) => sum + g.cards.length, 0),
)

const formattedValue = computed(() => {
  const v = stats.value.value
  if (v >= 1000) return v.toLocaleString('en-US', { maximumFractionDigits: 0 })
  return v.toFixed(2)
})
</script>

<style scoped>
/* ── Scroll container ──────────────────────────────────────────────────── */
.library-content {
  position: absolute;
  top: 132px;
  bottom: 108px;
  left: 0;
  right: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 10px 12px;
  box-sizing: border-box;
  -webkit-overflow-scrolling: touch;

  scrollbar-width: thin;
  scrollbar-color: #2FABD0 transparent;
}
.library-content::-webkit-scrollbar { width: 4px; }
.library-content::-webkit-scrollbar-thumb { background: #2FABD0; border-radius: 2px; }

/* ── Sticky toolbar ────────────────────────────────────────────────────── */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 5;
  background: #101F13;
  padding: 8px 0 6px;
  border-bottom: 1px solid rgba(127, 217, 194, 0.25);
  margin-bottom: 8px;
}

.stats {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 6px;
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.7);
  letter-spacing: 1px;
  margin-bottom: 6px;
}
.stats b {
  color: #FFD624;
  font-weight: 400;
}
.stat.value b { color: #7FD9C2; }
.stat-sep { color: rgba(127, 217, 194, 0.5); }

.controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search {
  flex: 1 1 auto;
  min-width: 0;
  height: 22px;
  background: #084236;
  border: 1px solid rgba(127, 217, 194, 0.45);
  border-radius: 3px;
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #E3F4EE;
  padding: 0 6px;
  outline: none;
  caret-color: #FFD624;
  -webkit-tap-highlight-color: transparent;
}
.search::placeholder { color: rgba(227, 244, 238, 0.4); }
.search:focus { border-color: #FFD624; }

.sort {
  height: 22px;
  background: #084236;
  border: 1px solid rgba(127, 217, 194, 0.45);
  border-radius: 3px;
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: #E3F4EE;
  padding: 0 2px;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.group-btn {
  width: 24px;
  height: 22px;
  background: transparent;
  border: 1px solid rgba(127, 217, 194, 0.45);
  border-radius: 3px;
  color: rgba(227, 244, 238, 0.55);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}
.group-btn.on {
  color: #1a1a1a;
  background: #FFD624;
  border-color: #FFD624;
}

/* ── Empty state ───────────────────────────────────────────────────────── */
.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 12px;
  font-family: 'Jura', sans-serif;
  font-size: 12px;
  color: rgba(227, 244, 238, 0.55);
  text-align: center;
}

/* ── Set headers (when grouped) ────────────────────────────────────────── */
.set-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin: 12px 2px 6px;
  padding-bottom: 4px;
  border-bottom: 1px solid rgba(127, 217, 194, 0.25);
}
.set-name {
  font-family: 'Iceland', sans-serif;
  font-size: 14px;
  color: #FFD624;
  letter-spacing: 1px;
}
.set-count {
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  color: rgba(227, 244, 238, 0.55);
}

/* ── Card grid ─────────────────────────────────────────────────────────── */
.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 10px;
}

.card-item {
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 5 / 7;
  position: relative;
}

.card-item.clickable {
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease;
}
.card-item.clickable:active {
  filter: brightness(0.7);
  transform: scale(0.96);
}

.card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 8px;
  transition: filter 0.2s ease;
}

.card-item.owned .card-img   { filter: none; }
.card-item.unowned .card-img { filter: grayscale(1); }

.card-silhouette {
  width: 100%;
  height: 100%;
  background: #0a0a0a;
  border-radius: 8px;
  border: 2px solid #222;
  display: flex;
  align-items: center;
  justify-content: center;
}
.question-mark {
  font-family: 'Jura', sans-serif;
  font-size: 52px;
  color: #FFD624;
  -webkit-text-stroke: 2px #333;
  user-select: none;
}

/* Price tag on Value-sort */
.price-tag {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.72);
  color: #7FD9C2;
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  letter-spacing: 0.5px;
  text-align: center;
  padding: 1px 0;
  pointer-events: none;
}

/* ── Sets grid ─────────────────────────────────────────────────────────── */
.sets-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding-top: 12px;
}

.set-tile {
  background: #084236;
  border: 1.5px solid rgba(127, 217, 194, 0.45);
  border-radius: 6px;
  padding: 8px 8px 6px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.08s ease, transform 0.08s ease, border-color 0.15s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.set-tile:active {
  filter: brightness(0.8);
  transform: scale(0.97);
}
.set-tile.complete {
  border-color: #FFD624;
}

.set-logo-wrap {
  position: relative;
  width: 100%;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.set-logo {
  position: relative;
  z-index: 1;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.6));
}

/* Fallback text — sits beneath the image; shows through if image fails. */
.set-logo-fallback {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Iceland', sans-serif;
  font-size: 13px;
  text-align: center;
  color: rgba(255, 214, 36, 0.7);
  padding: 0 4px;
  z-index: 0;
}

.set-tile-name {
  font-family: 'Jura', sans-serif;
  font-size: 10px;
  color: #E3F4EE;
  text-align: center;
  line-height: 1.2;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 24px;
}

.set-progress {
  width: 100%;
  height: 4px;
  background: rgba(0, 0, 0, 0.45);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 3px;
}
.set-progress-fill {
  height: 100%;
  background: #7FD9C2;
  transition: width 0.3s ease;
}
.set-tile.complete .set-progress-fill { background: #FFD624; }

.set-tile-count {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.6);
}
.set-tile-count .owned {
  color: #FFD624;
  margin-right: 2px;
}

/* ── Set detail header ─────────────────────────────────────────────────── */
.set-detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0 10px;
  border-bottom: 1px solid rgba(127, 217, 194, 0.25);
  margin-bottom: 10px;
  position: sticky;
  top: 0;
  background: #101F13;
  z-index: 5;
}
.back-btn {
  background: transparent;
  border: 1px solid rgba(127, 217, 194, 0.55);
  border-radius: 3px;
  color: #7FD9C2;
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  letter-spacing: 1px;
  padding: 3px 9px;
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}
.back-btn:active { filter: brightness(0.6); }
.set-detail-title {
  flex: 1 1 auto;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}
.set-detail-name {
  font-family: 'Iceland', sans-serif;
  font-size: 15px;
  color: #FFD624;
  letter-spacing: 1px;
}
.set-detail-count {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.7);
}

/*--- Scan grid ---*/
.scan-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 10px;
  padding-top: 12px;
}

.scan-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 5 / 7;
}
.scan-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: 8px;
}
.scan-item.known   { box-shadow: none; }
.scan-item.unknown { outline: 2px solid #e03030; outline-offset: -2px; }

.scan-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.65);
  color: white;
  font-family: 'Jura', sans-serif;
  font-size: 14px;
  text-align: center;
  padding: 3px 0;
  pointer-events: none;
}
</style>
