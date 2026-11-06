$ErrorActionPreference = 'Stop'
$evaluationFolder = $PSScriptRoot
if (-not (Test-Path -LiteralPath (Join-Path $evaluationFolder '.env'))) {
    Copy-Item -LiteralPath (Join-Path $evaluationFolder '.env.example') -Destination (Join-Path $evaluationFolder '.env')
}
$labPort = if ($env:BRD_PORT) { $env:BRD_PORT } else { '8766' }
foreach ($line in Get-Content -LiteralPath (Join-Path $evaluationFolder '.env')) {
    if (-not $env:BRD_PORT -and $line -match '^BRD_PORT=(\d+)\s*$') { $labPort = $Matches[1] }
}
try {
    $connection = Invoke-RestMethod -Uri "http://127.0.0.1:$labPort/api/config" -TimeoutSec 2
    if ($connection.skills -contains 'repository-analysis') {
        Write-Host "BRD lab is already running at http://127.0.0.1:$labPort"
        Start-Process "http://127.0.0.1:$labPort"
        exit 0
    }
} catch { }
$projectFolder = Split-Path (Split-Path $evaluationFolder -Parent) -Parent
$pythonCandidates = @(
    (Join-Path $projectFolder 'backend\.venv\Scripts\python.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe')
)
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) { $pythonCandidates += $pythonCommand.Source }
$pythonExecutable = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $pythonExecutable) {
    throw 'Python was not found. Run server.py with your Python 3.10 or newer executable.'
}
Write-Host "Project: $projectFolder"
Write-Host "Python: $pythonExecutable"
Write-Host 'Starting BRD lab. Keep this window open. Press Ctrl+C to stop.'
& $pythonExecutable -u (Join-Path $evaluationFolder 'server.py') --open
if ($LASTEXITCODE -ne 0) { throw "BRD lab exited with code $LASTEXITCODE" }
