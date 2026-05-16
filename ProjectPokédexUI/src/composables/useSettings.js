import { ref, watch } from 'vue'
import { CLAUDE_MODEL_IDS, DEFAULT_CLAUDE_MODEL } from '../lib/claude.js'
import { GEMINI_MODEL_IDS, DEFAULT_GEMINI_MODEL } from '../lib/gemini.js'

const STORAGE_KEY = 'pokedex.settings'

const PROVIDERS = ['claude', 'gemini']

function modelsForProvider(p) {
  return p === 'gemini' ? GEMINI_MODEL_IDS : CLAUDE_MODEL_IDS
}

function defaultModelForProvider(p) {
  return p === 'gemini' ? DEFAULT_GEMINI_MODEL : DEFAULT_CLAUDE_MODEL
}

// If we have an old stored model but no stored provider, infer the provider
// from the model ID prefix so users who were on Gemini land on Gemini.
function inferProvider(modelId) {
  if (typeof modelId === 'string' && modelId.startsWith('gemini-')) return 'gemini'
  return 'claude'
}

const defaults = {
  autoSpeakAnswers:     false,
  autoSpeakBio:         false,
  rate:                 1.05,
  pitch:                1.15,
  voiceURI:             '',
  provider:             'claude',
  model:                DEFAULT_CLAUDE_MODEL,
  onboardingDismissed:  false,
}

function load() {
  if (typeof localStorage === 'undefined') return { ...defaults }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaults }
    return { ...defaults, ...JSON.parse(raw) }
  } catch {
    return { ...defaults }
  }
}

const stored = load()

// Resolve provider: explicit value if present, else infer from stored model.
const resolvedProvider = PROVIDERS.includes(stored.provider)
  ? stored.provider
  : inferProvider(stored.model)

// Resolve model: must be valid for the resolved provider, else fall back.
const allowedIds = modelsForProvider(resolvedProvider)
const resolvedModel = allowedIds.has(stored.model)
  ? stored.model
  : defaultModelForProvider(resolvedProvider)

const autoSpeakAnswers = ref(stored.autoSpeakAnswers)
const autoSpeakBio     = ref(stored.autoSpeakBio)
const rate             = ref(stored.rate)
const pitch            = ref(stored.pitch)
const voiceURI         = ref(stored.voiceURI)
const provider         = ref(resolvedProvider)
const model            = ref(resolvedModel)
const onboardingDismissed = ref(stored.onboardingDismissed)

// When the user switches providers, snap the model to that provider's default
// if the current one doesn't belong to it.
watch(provider, (newProvider) => {
  if (!modelsForProvider(newProvider).has(model.value)) {
    model.value = defaultModelForProvider(newProvider)
  }
})

const voices = ref([])

function refreshVoices() {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) return
  voices.value = window.speechSynthesis.getVoices() ?? []
}

if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  refreshVoices()
  window.speechSynthesis.addEventListener('voiceschanged', refreshVoices)
}

watch(
  [autoSpeakAnswers, autoSpeakBio, rate, pitch, voiceURI, provider, model, onboardingDismissed],
  () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        autoSpeakAnswers:    autoSpeakAnswers.value,
        autoSpeakBio:        autoSpeakBio.value,
        rate:                rate.value,
        pitch:               pitch.value,
        voiceURI:            voiceURI.value,
        provider:            provider.value,
        model:               model.value,
        onboardingDismissed: onboardingDismissed.value,
      }))
    } catch (err) {
      console.error('[settings] persist', err)
    }
  },
)

export function useSettings() {
  return {
    autoSpeakAnswers, autoSpeakBio, rate, pitch, voiceURI, voices,
    provider, model,
    onboardingDismissed,
  }
}
