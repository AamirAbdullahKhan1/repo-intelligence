import React, { createContext, useContext, useState, useEffect } from 'react'
import { api, ApiClientError } from '../services/api'
import type { ArchitectureModel, RepositoryInventory } from '../types'

interface AnalysisContextType {
  inventory: RepositoryInventory | null
  architecture: ArchitectureModel | null
  isAnalyzing: boolean
  error: string | null
  analyzeGithub: (url: string) => Promise<void>
  analyzeZip: (file: File) => Promise<void>
  clearAnalysis: () => void
}

const AnalysisContext = createContext<AnalysisContextType | null>(null)

const STORAGE_KEY_INV = 'repo_intelligence_inventory'
const STORAGE_KEY_ARCH = 'repo_intelligence_architecture'

export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [inventory, setInventory] = useState<RepositoryInventory | null>(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY_INV)
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  const [architecture, setArchitecture] = useState<ArchitectureModel | null>(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY_ARCH)
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    try {
      if (inventory) {
        sessionStorage.setItem(STORAGE_KEY_INV, JSON.stringify(inventory))
      } else {
        sessionStorage.removeItem(STORAGE_KEY_INV)
      }
    } catch {}
  }, [inventory])

  useEffect(() => {
    try {
      if (architecture) {
        sessionStorage.setItem(STORAGE_KEY_ARCH, JSON.stringify(architecture))
      } else {
        sessionStorage.removeItem(STORAGE_KEY_ARCH)
      }
    } catch {}
  }, [architecture])

  async function analyzeGithub(url: string) {
    setIsAnalyzing(true)
    setError(null)
    try {
      const res = await api.analyzeGithub(url)
      setInventory(res.inventory)
      setArchitecture(res.architecture)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message)
      } else {
        setError('Failed to analyze repository. Check your connection to the server.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function analyzeZip(file: File) {
    setIsAnalyzing(true)
    setError(null)
    try {
      const res = await api.analyzeZip(file)
      setInventory(res.inventory)
      setArchitecture(res.architecture)
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message)
      } else {
        setError('Failed to analyze uploaded archive. Check your connection to the server.')
      }
    } finally {
      setIsAnalyzing(false)
    }
  }

  function clearAnalysis() {
    setInventory(null)
    setArchitecture(null)
    setError(null)
    sessionStorage.removeItem(STORAGE_KEY_INV)
    sessionStorage.removeItem(STORAGE_KEY_ARCH)
  }

  return (
    <AnalysisContext.Provider
      value={{
        inventory,
        architecture,
        isAnalyzing,
        error,
        analyzeGithub,
        analyzeZip,
        clearAnalysis,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  )
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext)
  if (!ctx) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return ctx
}
