import { useCallback, useEffect, useState } from 'react'
import { api } from '../services/api'
import type { BackendStatus, HealthResponse } from '../types'

interface UseHealthResult {
  status: BackendStatus
  data: HealthResponse | null
  error: string | null
  refetch: () => void
}

export function useHealth(): UseHealthResult {
  const [status, setStatus] = useState<BackendStatus>('checking')
  const [data, setData] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const check = useCallback(async () => {
    setStatus('checking')
    setError(null)
    try {
      const result = await api.health()
      setData(result)
      setStatus('connected')
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to reach the backend. Ensure the API server is running.'
      setError(message)
      setStatus('error')
      setData(null)
    }
  }, [])

  useEffect(() => {
    check()
  }, [check])

  return { status, data, error, refetch: check }
}
