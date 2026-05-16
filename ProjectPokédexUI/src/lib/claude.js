import Anthropic from '@anthropic-ai/sdk'
export { ROTOM_SYSTEM_INSTRUCTION } from './rotomPrompt'

// The Anthropic SDK refuses to run in the browser by default because the API
// key is exposed in the bundle. For this proof-of-concept that's acceptable —
// same pattern as VITE_SUPABASE_ANON_KEY. For production, swap this for a
// thin server proxy that holds the key.
export const claude = new Anthropic({
  apiKey: import.meta.env.VITE_ANTHROPIC_API_KEY,
  dangerouslyAllowBrowser: true,
})

export const CLAUDE_MODELS = [
  { id: 'claude-opus-4-7',   label: 'Opus 4.7 (smart)' },
  { id: 'claude-sonnet-4-6', label: 'Sonnet 4.6 (balanced)' },
  { id: 'claude-haiku-4-5',  label: 'Haiku 4.5 (fast)' },
]

export const CLAUDE_MODEL_IDS = new Set(CLAUDE_MODELS.map(m => m.id))
export const DEFAULT_CLAUDE_MODEL = 'claude-opus-4-7'
