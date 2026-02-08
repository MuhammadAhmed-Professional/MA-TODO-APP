@echo off
REM ============================================================================
REM Start All Phase II Services (Windows)
REM ============================================================================
REM
REM This script starts all three services in separate windows:
REM 1. Auth Server (Better Auth) - Port 3001
REM 2. Backend API (FastAPI) - Port 8000
REM 3. Frontend (Next.js) - Port 3000
REM
REM Prerequisites:
REM - Node.js 20+ installed (for auth server and frontend)
REM - Python 3.13+ with UV installed (for backend)
REM - Dependencies installed in each service
REM
REM Usage:
REM   start-all-services.bat
REM
REM To stop all services:
REM   Press Ctrl+C in each window
REM
REM ============================================================================

echo.
echo ============================================================================
echo  Starting Phase II Todo Application Services
echo ============================================================================
echo.
echo  This will open 3 terminal windows:
echo  1. Auth Server (Better Auth)    - http://localhost:3001
echo  2. Backend API (FastAPI)        - http://localhost:8000
echo  3. Frontend (Next.js)           - http://localhost:3000
echo.
echo  Press Ctrl+C in each window to stop the services
echo ============================================================================
echo.
pause

REM Get the current directory
set PHASE2_DIR=%~dp0
cd /d "%PHASE2_DIR%"

REM Check if directories exist
if not exist "auth-server" (
    echo ERROR: auth-server directory not found!
    echo Please run this script from the phase-2 directory
    pause
    exit /b 1
)

if not exist "backend" (
    echo ERROR: backend directory not found!
    echo Please run this script from the phase-2 directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ERROR: frontend directory not found!
    echo Please run this script from the phase-2 directory
    pause
    exit /b 1
)

echo [1/3] Starting Auth Server (Better Auth)...
start "Auth Server - Port 3001" cmd /k "cd /d %PHASE2_DIR%auth-server && npm run dev"
timeout /t 2 /nobreak >nul

echo [2/3] Starting Backend API (FastAPI)...
start "Backend API - Port 8000" cmd /k "cd /d %PHASE2_DIR%backend && uv run uvicorn src.main:app --reload --port 8000"
timeout /t 2 /nobreak >nul

echo [3/3] Starting Frontend (Next.js)...
start "Frontend - Port 3000" cmd /k "cd /d %PHASE2_DIR%frontend && npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================================
echo  All services started successfully!
echo ============================================================================
echo.
echo  Service URLs:
echo  - Auth Server:  http://localhost:3001/health
echo  - Backend API:  http://localhost:8000/docs
echo  - Frontend:     http://localhost:3000
echo.
echo  To verify services are running:
echo  1. Open browser to http://localhost:3000
echo  2. Check each service health endpoint
echo.
echo  To stop services:
echo  - Press Ctrl+C in each terminal window
echo  - Or close the terminal windows
echo.
echo ============================================================================
echo.

REM Wait a bit for services to start
timeout /t 5 /nobreak >nul

REM Open browser to frontend
echo Opening frontend in default browser...
start http://localhost:3000

echo.
echo Press any key to exit this window (services will continue running)...
pause >nul
