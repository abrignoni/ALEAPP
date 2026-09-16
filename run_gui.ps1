Set-Location $PSScriptRoot
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Starting ALEAPP (Android Logs Events & Protobuf Parser)" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Error "Virtual environment not found at .\.venv\Scripts\python.exe"
    Read-Host "Press Enter to exit..."
    exit 1
}

& ".\.venv\Scripts\python.exe" aleappGUI.py
if ($LASTEXITCODE -ne 0) {
    Write-Warning "ALEAPP GUI exited with code $LASTEXITCODE."
    Read-Host "Press Enter to exit..."
}
