param(
    [switch]$BuildFrontend
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($BuildFrontend) {
    Push-Location "$Root\app\frontend"
    npm install
    npm run build
    Pop-Location
}

Push-Location "$Root\app\backend"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt

if (Test-Path "$Root\.env") {
    Get-Content "$Root\.env" | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

Write-Host "Starting Flux Chat at http://localhost:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
