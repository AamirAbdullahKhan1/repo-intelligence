import { useState, useRef, type ChangeEvent, type FormEvent } from 'react'
import { Github, Upload, FolderOpen, Search, AlertCircle, Info } from 'lucide-react'
import type { InputMode } from '../types'

const GITHUB_URL_RE =
  /^https?:\/\/(www\.)?github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\/.*)?$/

function isValidGitHubUrl(url: string): boolean {
  return GITHUB_URL_RE.test(url.trim())
}

export function RepoInputPanel() {
  const [mode, setMode] = useState<InputMode>('github')
  const [githubUrl, setGithubUrl] = useState('')
  const [zipFile, setZipFile] = useState<File | null>(null)
  const [urlError, setUrlError] = useState<string | null>(null)
  const [zipError, setZipError] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleUrlChange(e: ChangeEvent<HTMLInputElement>) {
    setGithubUrl(e.target.value)
    setUrlError(null)
    setSubmitted(false)
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    setZipError(null)
    setSubmitted(false)
    if (file) {
      if (!file.name.endsWith('.zip')) {
        setZipError('Only .zip archives are accepted.')
        setZipFile(null)
        return
      }
      if (file.size > 52_428_800) {
        setZipError('File exceeds the 50 MiB size limit.')
        setZipFile(null)
        return
      }
      setZipFile(file)
    } else {
      setZipFile(null)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()

    if (mode === 'github') {
      if (!githubUrl.trim()) {
        setUrlError('Please enter a GitHub repository URL.')
        return
      }
      if (!isValidGitHubUrl(githubUrl)) {
        setUrlError(
          'Enter a valid GitHub URL, e.g. https://github.com/owner/repo'
        )
        return
      }
    } else {
      if (!zipFile) {
        setZipError('Please select a ZIP archive to upload.')
        return
      }
    }

    setSubmitted(true)
  }

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
          aria-selected={mode === 'github'}
          onClick={() => {
            setMode('github')
            setSubmitted(false)
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
          aria-selected={mode === 'zip'}
          onClick={() => {
            setMode('zip')
            setSubmitted(false)
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
                className="input-base"
                placeholder="https://github.com/owner/repository"
                value={githubUrl}
                onChange={handleUrlChange}
                aria-describedby={urlError ? 'url-error' : undefined}
                aria-invalid={!!urlError}
              />
              {urlError && (
                <p id="url-error" className="mt-1.5 flex items-center gap-1.5 text-xs text-red-400" role="alert">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
                  {urlError}
                </p>
              )}
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
                  zipFile
                    ? 'border-brand-500 bg-brand-500/5'
                    : 'border-surface-500 hover:border-brand-600 hover:bg-surface-700/50'
                }`}
                onClick={() => fileInputRef.current?.click()}
                onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
                tabIndex={0}
                role="button"
                aria-label="Select ZIP file"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".zip"
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
              {zipError && (
                <p className="mt-1.5 flex items-center gap-1.5 text-xs text-red-400" role="alert">
                  <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />
                  {zipError}
                </p>
              )}
            </div>
          </div>
        )}

        <button type="submit" className="btn-primary mt-4 w-full justify-center">
          <Search className="w-4 h-4" aria-hidden="true" />
          Analyse Repository
        </button>

        {submitted && (
          <div className="mt-3 flex items-start gap-2 p-3 bg-brand-500/10 border border-brand-500/30 rounded-lg text-xs text-brand-300" role="status">
            <Info className="w-4 h-4 flex-shrink-0 mt-0.5" aria-hidden="true" />
            <span>
              <strong>Repository analysis will be enabled in Milestone 2.</strong>{' '}
              The input has been validated. The analysis engine — repository cloning,
              code inventory, and architecture extraction — is planned for the next
              development iteration.
            </span>
          </div>
        )}
      </form>
    </div>
  )
}
