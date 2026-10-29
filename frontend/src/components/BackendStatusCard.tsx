import { useOutletContext } from 'react-router-dom'
import { ServerCrash, Server, Loader2, RefreshCw } from 'lucide-react'
import type { BackendStatus, HealthResponse } from '../types'

interface HealthContext {
  status: BackendStatus
  data: HealthResponse | null
  error: string | null
  refetch: () => void
}

export function BackendStatusCard() {
  const { status, data, error, refetch } = useOutletContext<HealthContext>()

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          {status === 'checking' && (
            <Loader2 className="w-5 h-5 text-gray-400 animate-spin flex-shrink-0" />
          )}
          {status === 'connected' && (
            <Server className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          )}
          {status === 'error' && (
            <ServerCrash className="w-5 h-5 text-red-400 flex-shrink-0" />
          )}
          <div>
            <p className="text-sm font-medium text-gray-200">
              {status === 'checking' && 'Connecting to API…'}
              {status === 'connected' && 'Backend API'}
              {status === 'error' && 'Backend API Unavailable'}
            </p>
            {status === 'connected' && data && (
              <p className="text-xs text-gray-500 mt-0.5">
                {data.service} · v{data.version} · {data.environment}
              </p>
            )}
            {status === 'error' && (
              <p className="text-xs text-red-400/80 mt-0.5">{error}</p>
            )}
          </div>
        </div>
        {(status === 'connected' || status === 'error') && (
          <button
            onClick={refetch}
            className="btn-secondary text-xs py-1 px-2"
            aria-label="Retry backend connection"
          >
            <RefreshCw className="w-3 h-3" aria-hidden="true" />
            Retry
          </button>
        )}
      </div>
    </div>
  )
}
