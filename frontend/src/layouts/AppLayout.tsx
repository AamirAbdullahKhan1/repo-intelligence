import { Outlet } from 'react-router-dom'
import { Sidebar } from '../components/Sidebar'
import { useHealth } from '../hooks/useHealth'

export function AppLayout() {
  const health = useHealth()

  return (
    <div className="flex h-screen overflow-hidden bg-surface-900">
      <Sidebar backendStatus={health.status} />
      <main className="flex-1 overflow-y-auto">
        <Outlet context={health} />
      </main>
    </div>
  )
}
