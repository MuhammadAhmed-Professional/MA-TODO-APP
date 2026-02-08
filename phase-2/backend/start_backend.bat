@echo off
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Phase II Backend - Starting FastAPI Server        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
echo 📁 Backend directory: %CD%
echo.

echo Step 1: Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.13+
    pause
    exit /b 1
)
echo ✅ Python found
echo.

echo Step 2: Installing/updating dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo Step 3: Starting FastAPI server...
echo.
echo 📍 API Docs:   http://localhost:8000/docs
echo 📍 Health:     http://localhost:8000/health
echo 📍 Press CTRL+C to stop
echo.
echo ════════════════════════════════════════════════════════════════

uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
