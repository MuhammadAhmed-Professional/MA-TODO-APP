#!/bin/bash

# Build Docker Images for Todo Application
# This script builds all three Docker images for the Todo application

set -e  # Exit on error

echo "🏗️  Building Docker images for Todo Application"
echo "=============================================="

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Build Frontend Image
echo "🔨 Building Frontend (Next.js) image..."
docker build \
  -f "$PROJECT_ROOT/phase-4/docker/frontend.Dockerfile" \
  -t todo-frontend:latest \
  "$PROJECT_ROOT/phase-2/frontend"

if [ $? -eq 0 ]; then
  echo "✅ Frontend image built successfully"
else
  echo "❌ Failed to build frontend image"
  exit 1
fi

echo ""

# Build Backend Image
echo "🔨 Building Backend (FastAPI) image..."
docker build \
  -f "$PROJECT_ROOT/phase-4/docker/backend.Dockerfile" \
  -t todo-backend:latest \
  "$PROJECT_ROOT/phase-2/backend"

if [ $? -eq 0 ]; then
  echo "✅ Backend image built successfully"
else
  echo "❌ Failed to build backend image"
  exit 1
fi

echo ""

# Build Auth Server Image
echo "🔨 Building Auth Server (Express.js) image..."
docker build \
  -f "$PROJECT_ROOT/phase-4/docker/auth-server.Dockerfile" \
  -t todo-auth-server:latest \
  "$PROJECT_ROOT/phase-2/auth-server"

if [ $? -eq 0 ]; then
  echo "✅ Auth server image built successfully"
else
  echo "❌ Failed to build auth server image"
  exit 1
fi

echo ""
echo "=============================================="
echo "✅ All images built successfully!"
echo ""
echo "📦 Built images:"
docker images | grep -E "todo-frontend|todo-backend|todo-auth-server" | head -3
echo ""
echo "Next steps:"
echo "  1. Load images into Minikube: minikube image load <image-name>"
echo "  2. Or deploy with Docker Compose: docker-compose up"
echo "  3. Or run automated setup: ./scripts/minikube-setup.sh"
