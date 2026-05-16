// Translates raw API / network errors into short, in-character messages
// safe to display in the Rotom LCD. Always logs the actual error to the
// console so the developer can still see what went wrong.

function statusOf(err) {
  return (
    err?.status ??
    err?.response?.status ??
    err?.cause?.status ??
    null
  )
}

function messageOf(err) {
  // Anthropic SDK errors expose .error.message; Gemini SDK errors expose .message
  // directly; native errors expose .message.
  return String(
    err?.error?.message ??
    err?.message ??
    err ??
    '',
  ).toLowerCase()
}

export function friendlyRotomError(err, tag = '[Rotom]') {
  // Always preserve the real error for the developer.
  console.error(tag, err)

  const status = statusOf(err)
  const msg    = messageOf(err)

  // Billing / credit balance — Anthropic returns 400 with this in the message.
  if (msg.includes('credit balance') || msg.includes('billing')) {
    return 'Rotom is out of power. (Top up API credits to continue.)'
  }

  // Quota exhausted — Gemini's free tier and Anthropic's rate limits both land here.
  if (status === 429 || msg.includes('quota') || msg.includes('rate limit') || msg.includes('rate-limit')) {
    return 'Rotom is busy. Try again in a moment.'
  }

  // Auth / permission failures.
  if (
    status === 401 || status === 403 ||
    msg.includes('api key') || msg.includes('api_key') ||
    msg.includes('unauthorized') || msg.includes('permission') ||
    msg.includes('authentication')
  ) {
    return 'Pokédex authorization failed.'
  }

  // Bad request — usually our fault (wrong model, malformed payload).
  if (status === 400 || msg.includes('invalid')) {
    return 'Rotom misunderstood the request.'
  }

  // Server-side errors.
  if (status && status >= 500) {
    return 'Pokédex servers are offline. Try again later.'
  }

  // Network / fetch failures.
  if (
    msg.includes('network') ||
    msg.includes('failed to fetch') ||
    msg.includes('fetch failed') ||
    msg.includes('connection')
  ) {
    return 'Lost connection to the Pokédex network.'
  }

  // Aborted by the user / page unload.
  if (msg.includes('abort')) {
    return ''
  }

  return 'Rotom encountered an error. Try again.'
}
