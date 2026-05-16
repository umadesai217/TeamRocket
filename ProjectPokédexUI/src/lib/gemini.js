import { GoogleGenAI } from '@google/genai'
export { ROTOM_SYSTEM_INSTRUCTION } from './rotomPrompt'

export const gemini = new GoogleGenAI({
  apiKey: import.meta.env.VITE_GEMINI_API_KEY,
})

export const GEMINI_MODELS = [
  { id: 'gemini-2.5-pro',   label: 'Gemini 2.5 Pro (smart)' },
  { id: 'gemini-2.5-flash', label: 'Gemini 2.5 Flash (fast)' },
]

export const GEMINI_MODEL_IDS = new Set(GEMINI_MODELS.map(m => m.id))
export const DEFAULT_GEMINI_MODEL = 'gemini-2.5-flash'
