# Resolve-only is assumed done (`uv lock`). This script scans before install.
# Usage: pwsh scripts/verify_deps.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "uv.lock")) {
    Write-Error "uv.lock not found. Run: uv lock --python 3.11"
}

$trivy = Get-Command trivy -ErrorAction SilentlyContinue
if (-not $trivy) {
    $wingetTrivy = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter trivy.exe -Recurse -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
    if ($wingetTrivy) {
        $trivyPath = $wingetTrivy
    } else {
        Write-Error "trivy not found. Install with: winget install --id AquaSecurity.Trivy -e"
    }
} else {
    $trivyPath = $trivy.Source
}

Write-Host "Scanning with: $trivyPath"
& $trivyPath fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL --exit-code 1 .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Trivy found HIGH/CRITICAL issues (or scan failed). Do not uv sync until reviewed."
}

Write-Host "Trivy clean (no HIGH/CRITICAL). Safe to run: uv sync --extra dev"
