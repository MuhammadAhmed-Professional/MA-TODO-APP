@echo off
REM Batch script to run backend with correct venv

echo.
echo ================================================
echo Phase II Backend Startup Script
echo ================================================
echo.

REM Clear old environment variable
echo Clearing old VIRTUAL_ENV variable...
set VIRTUAL_ENV=
echo ✓ Cleared

REM Check if we're in backend directory
if not exist "src\main.py" (
    echo.
    echo ERROR: Not in backend directory!
    echo Please run from: D:\Talal\Work\Hackathons-Panaversity\phase-1\phase-2\backend
    pause
    exit /b 1
)

echo ✓ Confirmed: In backend directory
echo.

REM Activate venv
echo Activating backend virtual environment...
call .\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)
echo ✓ Virtual environment activated
echo.

REM Run uvicorn
echo ================================================
echo Starting FastAPI backend...
echo ================================================
echo.

uv run uvicorn src.main:app --reload

echo.
echo ================================================
echo Backend stopped
echo ================================================
pause
