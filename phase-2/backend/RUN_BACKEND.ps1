# PowerShell Script to Run Backend with Correct venv
# This script fixes the venv path issue

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Phase II Backend Startup Script" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clear environment variable
Write-Host "🔧 Clearing old VIRTUAL_ENV variable..." -ForegroundColor Yellow
$env:VIRTUAL_ENV = ""
Write-Host "✅ Cleared" -ForegroundColor Green
Write-Host ""

# Step 2: Get current directory
$currentDir = Get-Location
Write-Host "📁 Current directory: $currentDir" -ForegroundColor Cyan
Write-Host ""

# Step 3: Check if we're in backend directory
if (-not (Test-Path ".\src\main.py")) {
    Write-Host "❌ ERROR: Not in backend directory!" -ForegroundColor Red
    Write-Host "Please run this script from: E:\Hackathons-Panaversity\Hackathon-ii\MA-TODO\phase-2\backend" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Confirmed: In backend directory" -ForegroundColor Green
Write-Host ""

# Step 4: Activate backend venv
Write-Host "🔄 Activating backend virtual environment..." -ForegroundColor Yellow
& ".\\.venv\\Scripts\\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Step 5: Verify venv
Write-Host "🔍 Verifying virtual environment setup..." -ForegroundColor Yellow
$pythonPath = (python -c "import sys; print(sys.executable)")
Write-Host "✅ Python interpreter: $pythonPath" -ForegroundColor Green
Write-Host ""

# Step 6: Run uvicorn
Write-Host "🚀 Starting FastAPI backend..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

uv run uvicorn src.main:app --reload

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Backend stopped" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
