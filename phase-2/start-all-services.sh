#!/bin/bash

# ============================================================================
# Start All Phase II Services (Linux/Mac)
# ============================================================================
#
# This script starts all three services in the background:
# 1. Auth Server (Better Auth) - Port 3001
# 2. Backend API (FastAPI) - Port 8000
# 3. Frontend (Next.js) - Port 3000
#
# Prerequisites:
# - Node.js 20+ installed (for auth server and frontend)
# - Python 3.13+ with UV installed (for backend)
# - Dependencies installed in each service
#
# Usage:
#   chmod +x start-all-services.sh
#   ./start-all-services.sh
#
# To stop all services:
#   Press Ctrl+C in this terminal
#
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    print_warning "Killing process on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
}

# Cleanup function for Ctrl+C
cleanup() {
    echo ""
    print_warning "Shutting down all services..."
    kill $AUTH_PID $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    print_success "All services stopped"
    exit 0
}

# Set trap for Ctrl+C
trap cleanup SIGINT SIGTERM

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Print banner
echo ""
echo "============================================================================"
echo " Starting Phase II Todo Application Services"
echo "============================================================================"
echo ""
echo " This will start 3 background processes:"
echo " 1. Auth Server (Better Auth)    - http://localhost:3001"
echo " 2. Backend API (FastAPI)        - http://localhost:8000"
echo " 3. Frontend (Next.js)           - http://localhost:3000"
echo ""
echo " Press Ctrl+C to stop all services"
echo "============================================================================"
echo ""

# Check if directories exist
if [ ! -d "auth-server" ]; then
    print_error "auth-server directory not found!"
    print_error "Please run this script from the phase-2 directory"
    exit 1
fi

if [ ! -d "backend" ]; then
    print_error "backend directory not found!"
    print_error "Please run this script from the phase-2 directory"
    exit 1
fi

if [ ! -d "frontend" ]; then
    print_error "frontend directory not found!"
    print_error "Please run this script from the phase-2 directory"
    exit 1
fi

# Check and kill processes on required ports if needed
for port in 3001 8000 3000; do
    if ! check_port $port; then
        print_warning "Port $port is already in use"
        read -p "Kill existing process on port $port? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_port $port
        else
            print_error "Cannot start services - port $port is in use"
            exit 1
        fi
    fi
done

# Create log directory
mkdir -p logs

# Start Auth Server
print_info "[1/3] Starting Auth Server (Better Auth)..."
cd auth-server
npm run dev > ../logs/auth-server.log 2>&1 &
AUTH_PID=$!
cd ..
sleep 2

if ps -p $AUTH_PID > /dev/null; then
    print_success "Auth Server started (PID: $AUTH_PID)"
else
    print_error "Auth Server failed to start"
    cat logs/auth-server.log
    exit 1
fi

# Start Backend API
print_info "[2/3] Starting Backend API (FastAPI)..."
cd backend
uv run uvicorn src.main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 2

if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend API started (PID: $BACKEND_PID)"
else
    print_error "Backend API failed to start"
    cat logs/backend.log
    exit 1
fi

# Start Frontend
print_info "[3/3] Starting Frontend (Next.js)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 3

if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend started (PID: $FRONTEND_PID)"
else
    print_error "Frontend failed to start"
    cat logs/frontend.log
    exit 1
fi

echo ""
echo "============================================================================"
echo " All services started successfully!"
echo "============================================================================"
echo ""
echo " Service URLs:"
echo " - Auth Server:  http://localhost:3001/health"
echo " - Backend API:  http://localhost:8000/docs"
echo " - Frontend:     http://localhost:3000"
echo ""
echo " Process IDs:"
echo " - Auth Server:  $AUTH_PID"
echo " - Backend API:  $BACKEND_PID"
echo " - Frontend:     $FRONTEND_PID"
echo ""
echo " Logs are available in:"
echo " - logs/auth-server.log"
echo " - logs/backend.log"
echo " - logs/frontend.log"
echo ""
echo " To view logs in real-time:"
echo " - tail -f logs/auth-server.log"
echo " - tail -f logs/backend.log"
echo " - tail -f logs/frontend.log"
echo ""
echo " Press Ctrl+C to stop all services"
echo "============================================================================"
echo ""

# Wait for processes
wait
