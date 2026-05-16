<template>
  <div class="screen">

    <span v-if="!cardTrade" class="placeholder">TRADE VIEWER</span>

    <div v-else class="scroll">

      <h1 class="card-name">{{ scannedCard?.name }}</h1>
      <div class="divider" />

      <div class="section-header">PRICES</div>
      <div class="price-row">
        <span class="price-lbl">Low</span>
        <span class="price-val">${{ fmt(cardTrade.price_low) }}</span>
      </div>
      <div class="price-row">
        <span class="price-lbl">Mid</span>
        <span class="price-val">${{ fmt(cardTrade.price_mid) }}</span>
      </div>
      <div class="price-row">
        <span class="price-lbl">High</span>
        <span class="price-val">${{ fmt(cardTrade.price_high) }}</span>
      </div>
      <div class="price-row market">
        <span class="price-lbl">Market</span>
        <span class="price-val market-val">${{ fmt(cardTrade.price_market) }}</span>
      </div>

      <template v-if="cardTrade.url">
        <div class="divider" />
        <a class="tcg-link" :href="cardTrade.url" target="_blank" rel="noopener">
          View on TCGPlayer ↗
        </a>
      </template>

      <template v-if="cardTrade.created_at || cardTrade.last_updated">
        <div class="divider" />
        <div class="timestamp" v-if="cardTrade.created_at">
          <span class="ts-lbl">Established</span>
          <span class="ts-val">{{ fmtDate(cardTrade.created_at) }}</span>
        </div>
        <div class="timestamp" v-if="cardTrade.last_updated">
          <span class="ts-lbl">Updated</span>
          <span class="ts-val">{{ fmtDate(cardTrade.last_updated) }}</span>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { useAppState } from '../../composables/useAppState'
const { cardTrade, scannedCard } = useAppState()

function fmt(val) {
  if (val == null) return '—'
  return Number(val).toFixed(2)
}

function fmtDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}
</script>

<style scoped>
.screen {
  width: 100%;
  height: 100%;
  background-color: #0a1a0a;
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

.section-header {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  color: #2FABD0;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(47, 171, 208, 0.4);
  padding-bottom: 2px;
  margin-top: 4px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 3px 0;
}

.price-row.market {
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  margin-top: 3px;
  padding-top: 6px;
}

.price-lbl {
  font-family: 'Iceland', sans-serif;
  font-size: 13px;
  color: rgba(214, 244, 255, 0.65);
}

.price-val {
  font-family: 'Jura', sans-serif;
  font-size: 14px;
  color: #ffffff;
}

.market-val {
  font-size: 18px;
  color: #FFD624;
}

.tcg-link {
  font-family: 'Iceland', sans-serif;
  font-size: 12px;
  color: #2FABD0;
  text-decoration: none;
  letter-spacing: 0.5px;
  align-self: flex-start;
  transition: opacity 0.1s ease;
}
.tcg-link:active { opacity: 0.5; }

.timestamp {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.ts-lbl {
  font-family: 'Iceland', sans-serif;
  font-size: 11px;
  color: rgba(214, 244, 255, 0.5);
}

.ts-val {
  font-family: 'Jura', sans-serif;
  font-size: 11px;
  color: rgba(227, 244, 238, 0.8);
}
</style>
