# This script will properly set up the backend venv and run the app

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         Phase II Backend - Complete Fix Setup              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$backendDir = Get-Location
Write-Host "📁 Backend directory: $backendDir" -ForegroundColor Yellow

# Step 1: Clear environment variables
Write-Host ""
Write-Host "Step 1: Clearing environment variables..." -ForegroundColor Cyan
$env:VIRTUAL_ENV = ""
$env:PYTHONHOME = ""
$env:PYTHONPATH = ""
Write-Host "✅ Cleared" -ForegroundColor Green

# Step 2: Check Python installation
Write-Host ""
Write-Host "Step 2: Checking Python installation..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Step 3: Delete old .venv if it exists
Write-Host ""
Write-Host "Step 3: Cleaning old venv..." -ForegroundColor Cyan
if (Test-Path ".\.venv") {
    Remove-Item -Recurse -Force .\.venv -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "✅ Old venv removed" -ForegroundColor Green
} else {
    Write-Host "✅ No old venv found" -ForegroundColor Green
}

# Step 4: Create fresh Python venv (NOT UV sync)
Write-Host ""
Write-Host "Step 4: Creating fresh Python venv..." -ForegroundColor Cyan
python -m venv .\.venv
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Venv created successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create venv" -ForegroundColor Red
    exit 1
}

# Step 5: Activate venv
Write-Host ""
Write-Host "Step 5: Activating venv..." -ForegroundColor Cyan
& ".\\.venv\\Scripts\\Activate.ps1"
Write-Host "✅ Venv activated" -ForegroundColor Green
Write-Host "   (You should see (.venv) in the prompt)" -ForegroundColor Yellow

# Step 6: Upgrade pip
Write-Host ""
Write-Host "Step 6: Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip -q
Write-Host "✅ Pip upgraded" -ForegroundColor Green

# Step 7: Install dependencies from pyproject.toml
Write-Host ""
Write-Host "Step 7: Installing project dependencies..." -ForegroundColor Cyan
pip install -q -e .
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 8: Verify uvicorn is installed
Write-Host ""
Write-Host "Step 8: Verifying installations..." -ForegroundColor Cyan
python -c "import uvicorn; print(f'✅ uvicorn {uvicorn.__version__} installed')" -ForegroundColor Green
python -c "import fastapi; print(f'✅ fastapi {fastapi.__version__} installed')" -ForegroundColor Green
python -c "import sqlmodel; print(f'✅ sqlmodel installed')" -ForegroundColor Green

# Step 9: Start the application
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            Starting FastAPI Backend...                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 API Docs:   http://localhost:8000/docs" -ForegroundColor Green
Write-Host "📍 Health:     http://localhost:8000/health" -ForegroundColor Green
Write-Host "📍 Press CTRL+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
