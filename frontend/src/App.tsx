import { Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { Dashboard } from './pages/Dashboard'
import { Architecture } from './pages/Architecture'
import { Workflows } from './pages/Workflows'
import { ThreatModel } from './pages/ThreatModel'
import { Reports } from './pages/Reports'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/overview" replace />} />
        <Route path="/overview" element={<Dashboard />} />
        <Route path="/architecture" element={<Architecture />} />
        <Route path="/workflows" element={<Workflows />} />
        <Route path="/threat-model" element={<ThreatModel />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
    </Routes>
  )
}
