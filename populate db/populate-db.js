import fetch from 'node-fetch'
// populate-db.js
import { createClient } from '@supabase/supabase-js'

// Supabase credentials (find in Project Settings > API)
const SUPABASE_URL = 'https://xjtcqylndpugjcikdhtz.supabase.co'
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhqdGNxeWxuZHB1Z2pjaWtkaHR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3Njg5NjIsImV4cCI6MjA3NDM0NDk2Mn0.qx8h2ASx_IIC1DP07k-0SRbOq3tFU1T8EhzKWZfx8YU'

// Scrydex credentials (from scrydex.com dashboard)
const SCRYDEX_API_KEY = '3555cc51dfe07b894851ab192b356d01308e5c65213637f4dd83adc92dda1d5d'
const SCRYDEX_TEAM_ID = 'tcgapp'

// Initialize Supabase client
const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// ============================================
// FETCH DATA FROM SCRYDEX
// ============================================

async function fetchAllScrydexCards() {
    try {
        console.log('🔄 Fetching all cards from Scrydex API...')
        
        let allCards = []
        let page = 1
        let hasMorePages = true
        
        while (hasMorePages) {
            console.log(`   Fetching page ${page}...`)
            
            const response = await fetch(
                `https://api.scrydex.com/pokemon/v1/cards?pageSize=250&page=${page}&include=prices`,
                {
                    headers: {
                        'X-Api-Key': SCRYDEX_API_KEY,
                        'X-Team-ID': SCRYDEX_TEAM_ID,
                        'Accept': 'application/json'
                    }
                }
            )
            
            if (!response.ok) {
                throw new Error(`Scrydex API error: ${response.status} ${response.statusText}`)
            }
            
            const data = await response.json()
            const cards = data.data || data.cards || data
            
            if (!cards || cards.length === 0) {
                hasMorePages = false
            } else {
                allCards = allCards.concat(cards)
                console.log(`   Got ${cards.length} cards (total: ${allCards.length})`)
                
                // If we got less than 250 cards, we're on the last page
                if (cards.length < 250) {
                    hasMorePages = false
                } else {
                    page++
                    // Small delay between pages to avoid rate limiting
                    await new Promise(resolve => setTimeout(resolve, 500))
                }
            }
        }
        
        console.log(`✅ Fetched ${allCards.length} total cards from Scrydex\n`)
        return allCards
        
    } catch (error) {
        console.error('❌ Error fetching from Scrydex:', error.message)
        throw error
    }
}

// ============================================
// INSERT CARD INTO SUPABASE
// ============================================

async function insertCardToSupabase(card) {
    try {
        // 1. Insert Set/Expansion
        if (card.expansion) {
            const { error: setError } = await supabase
                .from('sets')
                .upsert({
                    id: card.expansion.id,
                    name: card.expansion.name,
                    series: card.expansion.series || '',
                    printed_total: card.expansion.printed_total || null,
                    total: card.expansion.total || null
                }, { 
                    onConflict: 'id',
                    ignoreDuplicates: false 
                })
            
            if (setError && !setError.message.includes('duplicate')) {
                console.error('⚠️  Set insert error:', setError.message)
            }
        }
        
        // 2. Prepare weakness array
        let weaknessArray = []
        if (card.weaknesses && card.weaknesses.length > 0) {
            weaknessArray = card.weaknesses.map(w => `${w.type} ${w.value}`)
        }
        
        // 3. Prepare resistance array
        let resistanceArray = []
        if (card.resistances && card.resistances.length > 0) {
            resistanceArray = card.resistances.map(r => `${r.type} ${r.value}`)
        }
        
        // 4. Insert Card
        const { data: insertedCard, error: cardError } = await supabase
            .from('cardinfo')
            .insert({
                id: card.id,
                card_name: card.name,
                number: card.number || null,
                hp: card.hp || null,
                supertype: card.supertype || null,
                subtypes: card.subtypes || [],
                pokemon_types: card.types || [],
                weakness: weaknessArray,
                resistance: resistanceArray,
                retreat_cost: card.retreat_cost || card.retreatCost || [],
                set_id: card.expansion?.id || null
            })
            .select()
            .single()
        
        if (cardError) {
            throw new Error(`Card insert failed: ${cardError.message}`)
        }
        
        const cardId = card.id
        
        // 5. Insert TCGPlayer Pricing from variants
        if (card.variants && card.variants.length > 0) {
            for (const variant of card.variants) {
                if (variant.prices && variant.prices.length > 0) {
                    // Get the most recent price (first in array)
                    const latestPrice = variant.prices[0]
                    
                    // Only insert if we have at least one price value
                    if (latestPrice.low || latestPrice.mid || latestPrice.high || latestPrice.market) {
                        await supabase
                            .from('tcgplayer')
                            .insert({
                                card_id: cardId,
                                url: null,
                                price_low: latestPrice.low || null,
                                price_mid: latestPrice.mid || null,
                                price_high: latestPrice.high || null,
                                price_market: latestPrice.market || null,
                                last_updated: latestPrice.updated_at || new Date().toISOString()
                            })
                        break  // Only insert first variant with prices
                    }
                }
            }
        }
        
        // 6. Insert Attacks
        if (card.attacks && card.attacks.length > 0) {
            const attacks = card.attacks.map(a => ({
                card_id: cardId,
                name: a.name,
                description: a.text || '',
                type: ['attack'],
                cost: a.cost || [],
                damage: a.damage || ''
            }))
            
            await supabase.from('attacks').insert(attacks)
        }
        
        // 7. Insert Abilities
        if (card.abilities && card.abilities.length > 0) {
            const abilities = card.abilities.map(a => ({
                card_id: cardId,
                name: a.name,
                description: a.text || '',
                type: ['ability', a.type || 'Pokémon Power'],
                cost: [],
                damage: ''
            }))
            
            await supabase.from('attacks').insert(abilities)
        }
        
        return insertedCard
        
    } catch (error) {
        throw error
    }
}

// ============================================
// MAIN FUNCTION
// ============================================

async function populateDatabase() {
    console.log('🚀 Starting database population...\n')
    
    try {
        // Fetch all cards
        console.log('DEBUG: About to fetch cards...')
        const cards = await fetchAllScrydexCards()
        console.log('DEBUG: Fetch complete!')
        console.log('DEBUG: Cards is array?', Array.isArray(cards))
        console.log('DEBUG: Cards length:', cards?.length)
        
        if (!cards || cards.length === 0) {
            console.log('⚠️  No cards found to import')
            return
        }
        
        console.log(`\n📦 Processing ${cards.length} cards...\n`)
        console.log('DEBUG: Starting card processing loop...')
        
        let successCount = 0
        let errorCount = 0
        let setsFound = new Set()
        let pricesFound = 0
        
        // Process each card
        for (let i = 0; i < cards.length; i++) {
            const card = cards[i]
            const progress = `[${i + 1}/${cards.length}]`
            
            console.log(`DEBUG: Processing card ${i + 1}: ${card?.id}`)
            
            try {
                await insertCardToSupabase(card)
                successCount++
                
                if (card.expansion?.id) {
                    setsFound.add(card.expansion.id)
                }
                
                if (card.variants?.some(v => v.prices?.length > 0)) {
                    pricesFound++
                }
                
                console.log(`✅ ${progress} ${card.id} - ${card.name}`)
            } catch (error) {
                errorCount++
                console.error(`❌ ${progress} ${card.id} - ${card.name} - ${error.message}`)
            }
            
            if (i % 50 === 0 && i > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000))
            }
        }
        
        // Summary
        console.log('\n' + '='.repeat(60))
        console.log('📊 IMPORT SUMMARY')
        console.log('='.repeat(60))
        console.log(`✅ Successfully imported: ${successCount}`)
        console.log(`❌ Failed: ${errorCount}`)
        console.log(`📦 Total processed: ${cards.length}`)
        console.log(`🎴 Unique sets found: ${setsFound.size}`)
        console.log(`💰 Cards with pricing: ${pricesFound}`)
        console.log('='.repeat(60))
        console.log('\n✨ Database population complete!')
        
    } catch (error) {
        console.error('\n❌ Fatal error:', error.message)
        console.error('Stack trace:', error.stack)
        process.exit(1)
    }
}
// Run the script
populateDatabase()
