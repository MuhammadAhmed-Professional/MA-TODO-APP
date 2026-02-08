@echo off
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║         Phase II Auth Server - Starting Better Auth       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
echo 📁 Auth Server directory: %CD%
echo.

echo Step 1: Checking Node.js installation...
node --version
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

echo Step 2: Checking dependencies...
if not exist "node_modules\" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies ready
echo.

echo Step 3: Starting Auth Server...
echo.
echo 📍 Auth Server: http://localhost:3001
echo 📍 Press CTRL+C to stop
echo.
echo ════════════════════════════════════════════════════════════════

npm run dev
