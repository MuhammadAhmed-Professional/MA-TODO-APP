#!/bin/bash

# Backend startup script for Linux/Mac
# Usage: ./START_BACKEND.sh

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Phase II Backend - Complete Startup                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get current directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Backend directory: $BACKEND_DIR"
echo ""

# Step 1: Verify Python installation
echo "Step 1: Checking Python installation..."
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ Found: $PYTHON_VERSION"
echo ""

# Step 2: Check if .venv exists
echo "Step 2: Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv sync --no-cache
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi
echo ""

# Step 3: Verify dependencies
echo "Step 3: Verifying installations..."
uv run python -c "import uvicorn; print(f'✅ uvicorn installed')" 2>/dev/null
uv run python -c "import fastapi; print(f'✅ fastapi installed')" 2>/dev/null
uv run python -c "import sqlmodel; print(f'✅ sqlmodel installed')" 2>/dev/null
echo ""

# Step 4: Start the application
echo "╔════════════════════════════════════════════════════════════╗"
echo "║            Starting FastAPI Backend...                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📍 API Docs:   http://localhost:8000/docs"
echo "📍 Health:     http://localhost:8000/health"
echo "📍 Press CTRL+C to stop"
echo ""

uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
