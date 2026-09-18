const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

async function request(path, options) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

export const startAnalysis = (url) =>
  request('/api/analyses', { method: 'POST', body: JSON.stringify({ url }) })

export const getAnalysis = (id, accessToken) =>
  request(`/api/analyses/${id}`, {
    headers: { 'X-Analysis-Token': accessToken },
  })

export const listAnalyses = () => request('/api/analyses?limit=10')

export const getChecks = () => request('/api/checks')
