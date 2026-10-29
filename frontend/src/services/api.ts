/**
 * Typed API client for the Repo Intelligence backend.
 * All requests are proxied through Vite to http://localhost:8000.
 */

import type {
  AnalysisResponse,
  CapabilitiesResponse,
  HealthResponse,
} from '../types'

const BASE = '/api/v1'

export class ApiClientError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    let code = 'request_failed'
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      code = body.error ?? code
      detail = body.detail ?? detail
    } catch {
      // ignore JSON parse errors for error responses
    }
    throw new ApiClientError(response.status, code, detail)
  }

  return response.json() as Promise<T>
}

export const api = {
  health: (): Promise<HealthResponse> => request<HealthResponse>('/health'),
  capabilities: (): Promise<CapabilitiesResponse> =>
    request<CapabilitiesResponse>('/capabilities'),

  analyzeGithub: (url: string): Promise<AnalysisResponse> =>
    request<AnalysisResponse>('/analyze/github', {
      method: 'POST',
      body: JSON.stringify({ url }),
    }),

  analyzeZip: async (file: File): Promise<AnalysisResponse> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${BASE}/analyze/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      let code = 'upload_failed'
      let detail = `HTTP ${response.status}`
      try {
        const body = await response.json()
        code = body.error ?? code
        detail = body.detail ?? detail
      } catch {
        // ignore
      }
      throw new ApiClientError(response.status, code, detail)
    }

    return response.json() as Promise<AnalysisResponse>
  },
}
