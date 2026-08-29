# start_grant_agent.ps1
#
# Local launcher for the Grant Agent (branch grant-sector-g1-production).
#
#   powershell -ExecutionPolicy Bypass -File start_grant_agent.ps1             API on :8000
#   powershell -ExecutionPolicy Bypass -File start_grant_agent.ps1 -Web        API + Next.js UI on :3000
#   powershell -ExecutionPolicy Bypass -File start_grant_agent.ps1 -Stop       stop processes this launcher started
#   powershell -ExecutionPolicy Bypass -File start_grant_agent.ps1 -Status     show what is running
#
# Uses the repo-local Python venv (.venv). No scheduled tasks, no Windows
# services, no Startup-folder shortcuts. Singleton is enforced with repo-local
# PID files (var/*.pid), per AGENTS.md.

[CmdletBinding()]
param(
    [switch]$Web,
    [switch]$Stop,
    [switch]$Status,
    [int]$ApiPort = 8000,
    [int]$WebPort = 3000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$Python        = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$ApiPidFile    = Join-Path $RepoRoot "var\g1-api.pid"
$WebPidFile    = Join-Path $RepoRoot "var\g1-web.pid"
$ApiOut        = Join-Path $RepoRoot "var\g1-api.out.log"
$ApiErr        = Join-Path $RepoRoot "var\g1-api.err.log"
$WebOut        = Join-Path $RepoRoot "var\g1-web.out.log"
$WebErr        = Join-Path $RepoRoot "var\g1-web.err.log"

function Read-Pid([string]$file) {
    if (Test-Path $file) {
        $c = (Get-Content $file -Raw).Trim()
        if ($c -match '^\d+$') { return [int]$c }
    }
    return $null
}

function Is-Running([string]$file) {
    $p = Read-Pid $file
    if ($p -and (Get-Process -Id $p -ErrorAction SilentlyContinue)) { return $true }
    if ($p) { Remove-Item $file -Force -ErrorAction SilentlyContinue }
    return $false
}

function Save-Pid([string]$file, [int]$value) {
    $dir = Split-Path -Parent $file
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Set-Content -Path $file -Value "$value" -NoNewline -Encoding ascii
}

function Stop-From-Pid([string]$file) {
    $p = Read-Pid $file
    if ($p) {
        $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Stopping pid $p ($($proc.ProcessName))..."
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 400
        }
        Remove-Item $file -Force -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path $Python)) {
    Write-Host "Python venv not found at: $Python" -ForegroundColor Red
    Write-Host "Create it first:"
    Write-Host "  uv venv .venv --python 3.12"
    Write-Host "  uv pip install --python .venv/Scripts/python.exe fastapi uvicorn pydantic requests reportlab python-multipart pyyaml"
    Write-Host "  (plus pytest for tests), and 'npm install' in apps/web for the UI."
    exit 1
}

if ($Status) {
    $apiRun = Is-Running $ApiPidFile
    $webRun = Is-Running $WebPidFile
    Write-Host "=== Grant Agent status (branch grant-sector-g1-production) ==="
    if ($apiRun) { Write-Host "  API  RUNNING  http://127.0.0.1:$ApiPort  (pid $(Read-Pid $ApiPidFile))" }
    else         { Write-Host "  API  stopped" }
    if ($webRun) { Write-Host "  Web  RUNNING  http://127.0.0.1:$WebPort  (pid $(Read-Pid $WebPidFile))" }
    else         { Write-Host "  Web  stopped" }
    if (-not [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable("OPENROUTER_API_KEY"))) {
        Write-Host "  Live model: OPENROUTER_API_KEY present -> AUTO/MANUAL produce enabled"
    } else {
        Write-Host "  Live model: no OPENROUTER_API_KEY -> AUTO produce fails closed (503); deterministic dev lane works"
    }
    exit 0
}

if ($Stop) {
    Write-Host "Stopping Grant Agent..."
    Stop-From-Pid $ApiPidFile
    Stop-From-Pid $WebPidFile
    Write-Host "Done."
    exit 0
}

# Export variables from '.env' (if present) to the API process.
$EnvFile = Join-Path $RepoRoot ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -match '^[A-Za-z_][A-Za-z0-9_]*=') {
            $parts = $line -split '=', 2
            $name = $parts[0].Trim()
            $value = $parts[1].Trim().Trim('"').Trim("'")
            if ($value -ne '') { Set-Item -Path "env:$name" -Value $value }
        }
    }
}

# --- API ---
if (Is-Running $ApiPidFile) {
    Write-Host "API already running (pid $(Read-Pid $ApiPidFile)) -> http://127.0.0.1:$ApiPort"
} else {
    Write-Host "Starting Grant Agent API -> http://127.0.0.1:$ApiPort ..."
    $apiArgs = @("-m", "uvicorn", "apps.api.main:app", "--port", "$ApiPort", "--host", "127.0.0.1")
    $apiProc = Start-Process -FilePath $Python -ArgumentList $apiArgs -WorkingDirectory $RepoRoot `
        -WindowStyle Hidden -RedirectStandardOutput $ApiOut -RedirectStandardError $ApiErr -PassThru
    Save-Pid $ApiPidFile $apiProc.Id
    $ready = $false
    for ($i = 0; $i -lt 25; $i++) {
        Start-Sleep -Milliseconds 400
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$ApiPort/openapi.json" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch { }
    }
    if ($ready) { Write-Host "  API ready (pid $($apiProc.Id)). Docs: http://127.0.0.1:$ApiPort/docs" }
    else {
        Write-Warning "API did not become ready. Last log lines:"
        Get-Content $ApiOut -Tail 20 -ErrorAction SilentlyContinue
        Get-Content $ApiErr -Tail 20 -ErrorAction SilentlyContinue
    }
}

# --- Web ---
if ($Web) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Warning "node not found; skipping Next.js UI. The API is still up."
        exit 0
    }
    $webDir = Join-Path $RepoRoot "apps\web"
    if (-not (Test-Path (Join-Path $webDir "node_modules"))) {
        Write-Host "Installing web dependencies (npm install)..."
        Push-Location $webDir
        npm install --no-fund --no-audit | Out-Null
        Pop-Location
    }
    if (Is-Running $WebPidFile) {
        Write-Host "Web already running (pid $(Read-Pid $WebPidFile)) -> http://127.0.0.1:$WebPort"
    } else {
        Write-Host "Starting Next.js UI -> http://127.0.0.1:$WebPort ..."
        $env:API_URL = "http://127.0.0.1:$ApiPort"
        $webProc = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev", "--", "-p", "$WebPort") `
            -WorkingDirectory $webDir -WindowStyle Hidden -RedirectStandardOutput $WebOut -RedirectStandardError $WebErr -PassThru
        Save-Pid $WebPidFile $webProc.Id
        Write-Host "  Web starting (pid $($webProc.Id)). UI: http://127.0.0.1:$WebPort"
    }
}

Write-Host ""
Write-Host "Grant Agent is up. Submission is DISABLED."
Write-Host "  API : http://127.0.0.1:$ApiPort"
Write-Host "  Use mode=DETERMINISTIC for dev output; AUTO/MANUAL require OPENROUTER_API_KEY."