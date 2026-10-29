import { useState, useRef, type ChangeEvent, type FormEvent } from 'react'
import { Github, Upload, FolderOpen, Search, AlertCircle, Loader2 } from 'lucide-react'
import type { InputMode } from '../types'

const GITHUB_URL_RE =
  /^https?:\/\/(www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/.*)?$/

function isValidGitHubUrl(url: string): boolean {
  return GITHUB_URL_RE.test(url.trim())
}

interface RepoInputPanelProps {
  isAnalyzing: boolean
  onAnalyzeGithub: (url: string) => Promise<void>
  onAnalyzeZip: (file: File) => Promise<void>
  errorMessage?: string | null
}

export function RepoInputPanel({
  isAnalyzing,
  onAnalyzeGithub,
  onAnalyzeZip,
  errorMessage,
}: RepoInputPanelProps) {
  const [mode, setMode] = useState<InputMode>('github')
  const [githubUrl, setGithubUrl] = useState('')
  const [zipFile, setZipFile] = useState<File | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleUrlChange(e: ChangeEvent<HTMLInputElement>) {
    setGithubUrl(e.target.value)
    setValidationError(null)
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    setValidationError(null)
    if (file) {
      if (!file.name.toLowerCase().endsWith('.zip')) {
        setValidationError('Only .zip archives are accepted.')
        setZipFile(null)
        return
      }
      if (file.size > 52_428_800) {
        setValidationError('File exceeds the 50 MiB size limit.')
        setZipFile(null)
        return
      }
      setZipFile(file)
    } else {
      setZipFile(null)
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (isAnalyzing) return

    if (mode === 'github') {
      if (!githubUrl.trim()) {
        setValidationError('Please enter a GitHub repository URL.')
        return
      }
      if (!isValidGitHubUrl(githubUrl)) {
        setValidationError(
          'Enter a valid GitHub URL, e.g. https://github.com/owner/repo'
        )
        return
      }
      await onAnalyzeGithub(githubUrl.trim())
    } else {
      if (!zipFile) {
        setValidationError('Please select a ZIP archive to upload.')
        return
      }
      await onAnalyzeZip(zipFile)
    }
  }

  const activeError = validationError || errorMessage

  return (
    <div className="card">
      <h2 className="text-base font-semibold text-gray-100 mb-4">
        Analyse a Repository
      </h2>

      {/* Mode Toggle */}
      <div
        className="flex rounded-lg bg-surface-700 p-1 mb-5 w-fit"
        role="tablist"
        aria-label="Input method"
      >
        <button
          type="button"
          role="tab"
          disabled={isAnalyzing}
          aria-selected={mode === 'github'}
          onClick={() => {
            setMode('github')
            setValidationError(null)
          }}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === 'github'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Github className="w-4 h-4" aria-hidden="true" />
          GitHub URL
        </button>
        <button
          type="button"
          role="tab"
          disabled={isAnalyzing}
          aria-selected={mode === 'zip'}
          onClick={() => {
            setMode('zip')
            setValidationError(null)
          }}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            mode === 'zip'
              ? 'bg-surface-500 text-gray-100 shadow-sm'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <Upload className="w-4 h-4" aria-hidden="true" />
          ZIP Archive
        </button>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        {mode === 'github' ? (
          <div className="space-y-3">
            <div>
              <label
                htmlFor="github-url"
                className="block text-xs font-medium text-gray-400 mb-1.5"
              >
                GitHub Repository URL
              </label>
              <input
                id="github-url"
                type="url"
                disabled={isAnalyzing}
                className="input-base"
                placeholder="https://github.com/owner/repository"
                value={githubUrl}
                onChange={handleUrlChange}
                aria-invalid={!!activeError}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">
                ZIP Archive
              </label>
              <div
                className={`border-2 border-dashed rounded-lg p-5 text-center cursor-pointer transition-colors ${
                  isAnalyzing ? 'opacity-50 pointer-events-none' : ''
                } ${
                  zipFile
                    ? 'border-brand-500 bg-brand-500/5'
                    : 'border-surface-500 hover:border-brand-600 hover:bg-surface-700/50'
                }`}
                onClick={() => !isAnalyzing && fileInputRef.current?.click()}
                onKeyDown={(e) => e.key === 'Enter' && !isAnalyzing && fileInputRef.current?.click()}
                tabIndex={0}
                role="button"
                aria-label="Select ZIP file"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".zip"
                  disabled={isAnalyzing}
                  className="sr-only"
                  onChange={handleFileChange}
                  aria-label="ZIP archive file input"
                />
                {zipFile ? (
                  <div className="flex items-center justify-center gap-2 text-brand-400">
                    <FolderOpen className="w-5 h-5" aria-hidden="true" />
                    <span className="text-sm font-medium truncate max-w-xs">
                      {zipFile.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({(zipFile.size / 1024 / 1024).toFixed(1)} MiB)
                    </span>
                  </div>
                ) : (
                  <div className="text-gray-500">
                    <Upload className="w-6 h-6 mx-auto mb-2 text-gray-600" aria-hidden="true" />
                    <p className="text-sm">Click to select a ZIP archive</p>
                    <p className="text-xs mt-1">Max 50 MiB · .zip only</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeError && (
          <p className="mt-2.5 flex items-center gap-1.5 text-xs text-red-400" role="alert">
            <AlertCircle className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
            {activeError}
          </p>
        )}

        <button
          type="submit"
          disabled={isAnalyzing}
          className="btn-primary mt-4 w-full justify-center"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              Analyzing Repository Structure…
            </>
          ) : (
            <>
              <Search className="w-4 h-4" aria-hidden="true" />
              Analyse Repository
            </>
          )}
        </button>
      </form>
    </div>
  )
}
