<template>
  <div class="screen">

    <span v-if="!cardMeta" class="placeholder">META VIEWER</span>

    <div v-else class="scroll">

      <h1 class="card-name">{{ cardMeta.card_name }}</h1>
      <div class="divider" />

      <!-- Supertype / subtypes / HP -->
      <div class="row-spread">
        <span class="chip">{{ cardMeta.supertype }}</span>
        <span class="chip" v-for="s in cardMeta.subtypes" :key="s">{{ s }}</span>
        <span class="chip hp" v-if="cardMeta.hp">HP {{ cardMeta.hp }}</span>
      </div>

      <!-- Types -->
      <div class="row" v-if="cardMeta.pokemon_types.length">
        <span class="lbl">Type</span>
        <span class="val">{{ cardMeta.pokemon_types.join(' · ') }}</span>
      </div>

      <!-- Number -->
      <div class="row" v-if="cardMeta.number">
        <span class="lbl">Number</span>
        <span class="val">{{ cardMeta.number }}</span>
      </div>

      <!-- Weakness / Resistance / Retreat -->
      <div class="row-spread mid-row" v-if="cardMeta.weakness || cardMeta.resistance || cardMeta.retreat_cost.length">
        <div class="stat-block" v-if="cardMeta.weakness">
          <span class="stat-lbl">WK</span>
          <span class="stat-val">{{ cardMeta.weakness }}</span>
        </div>
        <div class="stat-block" v-if="cardMeta.resistance">
          <span class="stat-lbl">RS</span>
          <span class="stat-val">{{ cardMeta.resistance }}</span>
        </div>
        <div class="stat-block" v-if="cardMeta.retreat_cost.length">
          <span class="stat-lbl">RT</span>
          <span class="stat-val">{{ cardMeta.retreat_cost.length }}</span>
        </div>
      </div>

      <!-- Attacks -->
      <template v-if="cardMeta.attacks.length">
        <div class="section-header">ATTACKS</div>
        <div class="attack" v-for="atk in cardMeta.attacks" :key="atk.id">
          <div class="atk-top">
            <span class="atk-name">{{ atk.name }}</span>
            <span class="atk-damage">{{ atk.damage || '—' }}</span>
          </div>
          <div class="atk-meta" v-if="atk.type?.length || atk.cost.length">
            <span v-if="atk.type?.length">{{ atk.type.join(', ') }}</span>
            <span v-if="atk.cost.length">· {{ atk.cost.join(', ') }}</span>
          </div>
          <p class="atk-desc" v-if="atk.description">{{ atk.description }}</p>
        </div>
      </template>

      <!-- Set -->
      <template v-if="cardMeta.set">
        <div class="section-header">SET</div>
        <div class="row">
          <span class="lbl">Name</span>
          <span class="val">{{ cardMeta.set.name }}</span>
        </div>
        <div class="row">
          <span class="lbl">Series</span>
          <span class="val">{{ cardMeta.set.series }}</span>
        </div>
        <div class="row">
          <span class="lbl">Prints</span>
          <span class="val">{{ cardMeta.set.printed_total }} / {{ cardMeta.set.total }}</span>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { useAppState } from '../../composables/useAppState'
const { cardMeta } = useAppState()
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #1a1a0a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.placeholder {
  font-family: 'Iceland', sans-serif;
  font-size: 18px;
  color: #E3F4EE;
  opacity: 0.4;
  letter-spacing: 2px;
}

.scroll {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 12px 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 6px;
  scrollbar-width: thin;
  scrollbar-color: #2FABD0 transparent;
}
.scroll::-webkit-scrollbar { width: 3px; }
.scroll::-webkit-scrollbar-thumb { background: #2FABD0; border-radius: 2px; }

.card-name {
  font-family: 'Jaro', sans-serif;
  font-size: 22px;
  font-weight: 400;
  color: #FFD624;
  -webkit-text-stroke: 0.4px #005B98;
  margin: 0;
  text-align: center;
}

.divider {
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  margin: 2px 0;
}

.row-spread {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}

.chip {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.35);
  border-radius: 2px;
  padding: 1px 6px;
  white-space: nowrap;
}

.chip.hp {
  color: #ff8080;
  border-color: rgba(255, 128, 128, 0.5);
  background: rgba(255, 128, 128, 0.1);
}

.row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.lbl {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(214, 244, 255, 0.6);
  flex-shrink: 0;
  width: 48px;
}

.val {
  font-family: 'Jura', sans-serif;
  font-size: 12px;
  color: #ffffff;
  flex: 1;
  min-width: 0;
}

.mid-row { margin: 2px 0; }

.stat-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 36px;
}

.stat-lbl {
  font-family: 'Iceland', sans-serif;
  font-size: 10px;
  color: rgba(214, 244, 255, 0.55);
}

.stat-val {
  font-family: 'Jura', sans-serif;
  font-size: 12px;
  color: #ffffff;
  text-align: center;
}

.section-header {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  color: #2FABD0;
  letter-spacing: 2px;
  margin-top: 6px;
  border-bottom: 1px solid rgba(47, 171, 208, 0.4);
  padding-bottom: 2px;
}

.attack {
  padding: 5px 0 3px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.atk-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.atk-name {
  font-family: 'Jura', sans-serif;
  font-size: 13px;
  color: #FFD624;
}

.atk-damage {
  font-family: 'Iceland', sans-serif;
  font-size: 15px;
  color: #ff8080;
  flex-shrink: 0;
}

.atk-meta {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(214, 244, 255, 0.65);
  display: flex;
  gap: 4px;
}

.atk-desc {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.85);
  margin: 0;
  line-height: 1.4;
}
</style>
