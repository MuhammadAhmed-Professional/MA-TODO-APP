@echo off
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║            Phase II - Complete Stack Startup              ║
echo ║    Auth Server (3001) + Backend (8000) + Frontend (3000)  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
set ROOT_DIR=%CD%
echo 📁 Phase 2 directory: %ROOT_DIR%
echo.

echo ════════════════════════════════════════════════════════════════
echo  Pre-flight Checks
echo ════════════════════════════════════════════════════════════════

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.13+
    pause
    exit /b 1
)
echo ✅ Python found

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js found

echo Checking UV installation...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ UV not found. Please install UV package manager
    pause
    exit /b 1
)
echo ✅ UV found

echo.
echo ════════════════════════════════════════════════════════════════
echo  Installing Dependencies (First Time Only)
echo ════════════════════════════════════════════════════════════════

echo Installing backend dependencies...
cd "%ROOT_DIR%\backend"
uv sync --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)
echo ✅ Backend dependencies ready

echo Installing auth server dependencies...
cd "%ROOT_DIR%\auth-server"
if not exist "node_modules\" (
    echo Installing auth server packages...
    npm install --silent
    if %errorlevel% neq 0 (
        echo ❌ Failed to install auth server dependencies
        pause
        exit /b 1
    )
)
echo ✅ Auth server dependencies ready

echo Installing frontend dependencies...
cd "%ROOT_DIR%\frontend"
if not exist "node_modules\" (
    echo Installing frontend packages...
    npm install --legacy-peer-deps --silent
    if %errorlevel% neq 0 (
        echo ❌ Failed to install frontend dependencies
        pause
        exit /b 1
    )
)
echo ✅ Frontend dependencies ready

echo.
echo ════════════════════════════════════════════════════════════════
echo  Starting Services
echo ════════════════════════════════════════════════════════════════
echo.
echo This will open 3 new command windows:
echo   1. Auth Server    - http://localhost:3001
echo   2. Backend API    - http://localhost:8000
echo   3. Frontend App   - http://localhost:3000
echo.
echo Press any key to continue, or Ctrl+C to cancel...
pause >nul

echo Starting Auth Server (Port 3001)...
cd "%ROOT_DIR%\auth-server"
start "Phase2-AuthServer" cmd /c "title Phase2 Auth Server (Port 3001) && npm run dev && pause"
timeout /t 2 >nul

echo Starting Backend API (Port 8000)...
cd "%ROOT_DIR%\backend"
start "Phase2-Backend" cmd /c "title Phase2 Backend API (Port 8000) && uv run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000 && pause"
timeout /t 3 >nul

echo Starting Frontend App (Port 3000)...
cd "%ROOT_DIR%\frontend"
start "Phase2-Frontend" cmd /c "title Phase2 Frontend (Port 3000) && npm run dev && pause"
timeout /t 2 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   🎉 All Services Started!                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Frontend App:    http://localhost:3000
echo 🔧 Backend API:     http://localhost:8000
echo 📖 API Docs:        http://localhost:8000/docs
echo 🔐 Auth Server:     http://localhost:3001
echo.
echo ⏱️  Services may take 30-60 seconds to fully start up.
echo 👀 Check each service window for startup completion.
echo 🛑 To stop: Close each service window or press Ctrl+C in each.
echo.
echo ════════════════════════════════════════════════════════════════
echo  Next Steps:
echo ════════════════════════════════════════════════════════════════
echo 1. Wait for all services to show "ready" status
echo 2. Open http://localhost:3000 in your browser
echo 3. Register a new user account
echo 4. Start creating and managing tasks!
echo.
echo Press any key to exit this window...
pause >nul
