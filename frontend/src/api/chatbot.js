const CHATBOT_API_BASE = (import.meta.env.VITE_CHATBOT_API_BASE || '/chatbot').replace(/\/$/, '')

async function request(path, options = {}) {
  const response = await fetch(`${CHATBOT_API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const detail =
      typeof payload === 'string'
        ? payload
        : payload?.detail || payload?.message || `Request failed with status ${response.status}`
    throw new Error(detail)
  }

  return payload
}

export function startChatbotSession() {
  return request('/session/start', { method: 'POST' })
}

export function sendChatbotMessage(sessionId, message) {
  return request(`/session/${sessionId}/message`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function endChatbotSession(sessionId) {
  return request(`/session/${sessionId}/end`, {
    method: 'POST',
  })
}

export function getChatbotHealth() {
  return request('/health', {
    method: 'GET',
  })
}
