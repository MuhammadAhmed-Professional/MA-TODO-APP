#!/bin/bash

# Automated Minikube Setup for Todo Application
# This script automates the entire Minikube deployment process

set -e  # Exit on error

echo "🚀 Todo Application - Minikube Automated Setup"
echo "================================================"
echo ""

# Get the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PHASE4_DIR="$PROJECT_ROOT/phase-4"

# Check for required tools
echo "🔍 Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker first."; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo "❌ Minikube is not installed. Please install Minikube first."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is not installed. Please install kubectl first."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "❌ Helm is not installed. Please install Helm first."; exit 1; }

echo "✅ All prerequisites installed"
echo ""

# Load environment variables
if [ -f "$PHASE4_DIR/.env" ]; then
  echo "📋 Loading environment variables from .env file..."
  set -a
  source "$PHASE4_DIR/.env"
  set +a
  echo "✅ Environment variables loaded"
else
  echo "⚠️  No .env file found at $PHASE4_DIR/.env"
  echo "   Using default/placeholder values. You should create a .env file with your secrets."
  echo ""
fi

# Step 1: Start Minikube
echo "=============================================="
echo "📦 Step 1: Starting Minikube cluster..."
echo "=============================================="

if minikube status | grep -q "Running"; then
  echo "✅ Minikube is already running"
else
  echo "🔧 Starting Minikube with 4 CPUs and 8GB memory..."
  minikube start --driver=docker --cpus=4 --memory=8192
  echo "✅ Minikube started successfully"
fi

echo ""

# Step 2: Enable Ingress addon
echo "=============================================="
echo "📦 Step 2: Enabling Ingress addon..."
echo "=============================================="

if minikube addons list | grep -q "ingress.*enabled"; then
  echo "✅ Ingress addon is already enabled"
else
  minikube addons enable ingress
  echo "✅ Ingress addon enabled"
fi

echo ""

# Step 3: Build Docker images
echo "=============================================="
echo "📦 Step 3: Building Docker images..."
echo "=============================================="

chmod +x "$SCRIPT_DIR/build-images.sh"
"$SCRIPT_DIR/build-images.sh"

echo ""

# Step 4: Load images into Minikube
echo "=============================================="
echo "📦 Step 4: Loading images into Minikube..."
echo "=============================================="

echo "📤 Loading todo-frontend:latest..."
minikube image load todo-frontend:latest

echo "📤 Loading todo-backend:latest..."
minikube image load todo-backend:latest

echo "📤 Loading todo-auth-server:latest..."
minikube image load todo-auth-server:latest

echo "✅ All images loaded into Minikube"
echo ""

# Verify images
echo "🔍 Verifying images in Minikube..."
minikube image ls | grep todo || echo "⚠️  Images not found in Minikube"
echo ""

# Step 5: Create namespace
echo "=============================================="
echo "📦 Step 5: Creating Kubernetes namespace..."
echo "=============================================="

if kubectl get namespace todo-app >/dev/null 2>&1; then
  echo "✅ Namespace 'todo-app' already exists"
else
  kubectl create namespace todo-app
  echo "✅ Namespace 'todo-app' created"
fi

echo ""

# Step 6: Create secrets
echo "=============================================="
echo "📦 Step 6: Creating Kubernetes secrets..."
echo "=============================================="

if kubectl get secret todo-secrets -n todo-app >/dev/null 2>&1; then
  echo "⚠️  Secret 'todo-secrets' already exists. Deleting and recreating..."
  kubectl delete secret todo-secrets -n todo-app
fi

# Use environment variables or defaults
DATABASE_URL="${DATABASE_URL:-postgresql://user:password@host.region.neon.tech/dbname?sslmode=require}"
JWT_SECRET="${JWT_SECRET:-your-256-bit-random-secret-here}"
BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET:-your-different-secret-here}"
OPENAI_API_KEY="${OPENAI_API_KEY:-sk-your-openai-api-key}"

kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --namespace=todo-app

echo "✅ Secrets created"
echo ""

# Step 7: Deploy with Helm
echo "=============================================="
echo "📦 Step 7: Deploying with Helm..."
echo "=============================================="

# Get Minikube IP for dynamic URLs
MINIKUBE_IP=$(minikube ip)
echo "🌐 Minikube IP: $MINIKUBE_IP"
echo ""

# Check if Helm release exists
if helm list -n todo-app | grep -q "todo-app"; then
  echo "⚠️  Helm release 'todo-app' already exists. Upgrading..."
  helm upgrade todo-app "$PHASE4_DIR/helm/todo-app" \
    --namespace todo-app \
    --set frontend.image.tag=latest \
    --set backend.image.tag=latest \
    --set authServer.image.tag=latest \
    --set env.frontend.NEXT_PUBLIC_API_URL="http://$MINIKUBE_IP:30800" \
    --set env.frontend.NEXT_PUBLIC_BETTER_AUTH_URL="http://$MINIKUBE_IP:30801"
  echo "✅ Helm release upgraded"
else
  helm install todo-app "$PHASE4_DIR/helm/todo-app" \
    --namespace todo-app \
    --set frontend.image.tag=latest \
    --set backend.image.tag=latest \
    --set authServer.image.tag=latest \
    --set env.frontend.NEXT_PUBLIC_API_URL="http://$MINIKUBE_IP:30800" \
    --set env.frontend.NEXT_PUBLIC_BETTER_AUTH_URL="http://$MINIKUBE_IP:30801"
  echo "✅ Helm release installed"
fi

echo ""

# Step 8: Wait for pods to be ready
echo "=============================================="
echo "📦 Step 8: Waiting for pods to be ready..."
echo "=============================================="

echo "⏳ Waiting for all pods to be ready (timeout: 5 minutes)..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app -n todo-app --timeout=300s || {
  echo "⚠️  Some pods may not be ready yet. Check status with: kubectl get pods -n todo-app"
}

echo ""

# Step 9: Display deployment status
echo "=============================================="
echo "📦 Step 9: Deployment Status"
echo "=============================================="

echo ""
echo "📊 Pods:"
kubectl get pods -n todo-app

echo ""
echo "📊 Services:"
kubectl get services -n todo-app

echo ""
echo "📊 Ingress:"
kubectl get ingress -n todo-app

echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo "=============================================="
echo ""
echo "🌐 Access your application:"
echo "   Frontend:    http://$MINIKUBE_IP:30000"
echo "   Backend API: http://$MINIKUBE_IP:30800"
echo "   Auth Server: http://$MINIKUBE_IP:30801"
echo ""
echo "📊 Useful commands:"
echo "   View pods:        kubectl get pods -n todo-app"
echo "   View logs:        kubectl logs -f -l app=frontend -n todo-app"
echo "   Delete release:   helm uninstall todo-app --namespace todo-app"
echo "   Stop Minikube:    minikube stop"
echo ""
echo "🎉 Happy testing!"
