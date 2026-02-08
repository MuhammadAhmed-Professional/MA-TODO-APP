# Phase IV: Local Kubernetes Deployment

**Evolution of Todo - Hackathon Phase IV**

Deploy the full-stack Todo application locally using Docker, Minikube, Helm charts, and AI-powered Kubernetes tools.

---

## Overview

Phase IV demonstrates containerization and orchestration of the Todo application using Kubernetes. This phase includes:

- **Docker Multi-stage Builds**: Optimized containers for frontend (Next.js), backend (FastAPI), and auth server (Express.js)
- **Gordon (Docker AI)**: AI-assisted Dockerfile generation and optimization
- **Docker Compose**: Local development environment with all services
- **Kubernetes Manifests**: Deployments, services, ConfigMaps, Secrets, Ingress
- **Helm Charts**: Parameterized Kubernetes deployment for flexibility
- **Minikube**: Local Kubernetes cluster for testing
- **kubectl-ai**: Natural language Kubernetes operations
- **kagent**: AI-powered cluster analysis and optimization

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Minikube Cluster                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              Ingress Controller                 │    │
│  │  - Routes / → Frontend (NodePort 3000)          │    │
│  │  - Routes /api → Backend (ClusterIP 8000)       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │   Backend    │  │ Auth Server  │ │
│  │   (Next.js)  │  │   (FastAPI)  │  │  (Express)   │ │
│  │              │  │              │  │              │ │
│  │  Port: 3000  │  │  Port: 8000  │  │  Port: 3001  │ │
│  │  Replicas: 2 │  │  Replicas: 2 │  │  Replicas: 2 │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Neon PostgreSQL   │
                  │ (External SaaS)   │
                  └──────────────────┘
```

---

## Prerequisites

### Required Software

1. **Docker Desktop** (v20.10+)
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`

2. **Minikube** (v1.30+)
   - Install: `brew install minikube` (macOS) or `choco install minikube` (Windows)
   - Verify: `minikube version`

3. **kubectl** (v1.25+)
   - Install: `brew install kubectl` (macOS) or `choco install kubernetes-cli` (Windows)
   - Verify: `kubectl version --client`

4. **Helm** (v3.10+)
   - Install: `brew install helm` (macOS) or `choco install kubernetes-helm` (Windows)
   - Verify: `helm version`

5. **kubectl-ai** (AI-powered kubectl)
   - Install: `kubectl krew install ai`
   - Docs: https://github.com/sozercan/kubectl-ai

6. **kagent** (Kubernetes AI Agent)
   - Install: `pip install kagent`
   - Docs: https://github.com/kagent-dev/kagent

7. **Gordon** (Docker AI Assistant)
   - Included with Docker Desktop 4.40+
   - Usage: `docker ai "<prompt>"`

### Environment Variables

Create a `.env` file in `phase-4/` with the following variables:

```env
# Database (Neon PostgreSQL - External)
DATABASE_URL=postgresql://user:password@host.region.neon.tech/dbname?sslmode=require

# Authentication
JWT_SECRET=your-256-bit-random-secret-here
BETTER_AUTH_SECRET=your-different-secret-here

# OpenAI (if using AI features)
OPENAI_API_KEY=sk-your-openai-api-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3001

# Backend
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
NODE_ENV=development
```

---

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the automated setup script to build images, start Minikube, and deploy with Helm:

```bash
cd phase-4
chmod +x scripts/minikube-setup.sh
./scripts/minikube-setup.sh
```

This script will:
1. Start Minikube cluster
2. Build all Docker images locally
3. Load images into Minikube
4. Create namespace and secrets
5. Deploy with Helm
6. Wait for pods to be ready
7. Display access URLs

### Option 2: Manual Setup

#### Step 1: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=8192

# Enable Ingress addon
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

#### Step 2: Build Docker Images

```bash
# Build all images
cd phase-4
chmod +x scripts/build-images.sh
./scripts/build-images.sh

# Or build individually
docker build -f docker/frontend.Dockerfile -t todo-frontend:latest ../phase-2/frontend
docker build -f docker/backend.Dockerfile -t todo-backend:latest ../phase-2/backend
docker build -f docker/auth-server.Dockerfile -t todo-auth-server:latest ../phase-2/auth-server
```

#### Step 3: Load Images into Minikube

```bash
# Load images into Minikube's Docker registry
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load todo-auth-server:latest

# Verify images are loaded
minikube image ls | grep todo
```

#### Step 4: Create Kubernetes Secret

```bash
# Create namespace
kubectl create namespace todo-app

# Create secret from .env file
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=JWT_SECRET="$JWT_SECRET" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --namespace=todo-app
```

#### Step 5: Deploy with Helm

```bash
# Install Helm chart
helm install todo-app ./helm/todo-app \
  --namespace todo-app \
  --set frontend.image.tag=latest \
  --set backend.image.tag=latest \
  --set authServer.image.tag=latest \
  --set frontend.env.NEXT_PUBLIC_API_URL="http://$(minikube ip):30800" \
  --set frontend.env.NEXT_PUBLIC_BETTER_AUTH_URL="http://$(minikube ip):30801"

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app -n todo-app --timeout=300s
```

#### Step 6: Access the Application

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Access URLs
echo "Frontend: http://$MINIKUBE_IP:30000"
echo "Backend API: http://$MINIKUBE_IP:30800"
echo "Auth Server: http://$MINIKUBE_IP:30801"

# Or use Minikube service command
minikube service frontend-service -n todo-app
```

---

## Development Workflow

### Docker Compose (Local Development)

For rapid local development without Kubernetes:

```bash
cd phase-4

# Start all services with Docker Compose
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - Auth Server: http://localhost:3001

# Stop services
docker-compose down
```

### Helm Chart Updates

After modifying Helm templates or values:

```bash
# Dry run to preview changes
helm upgrade todo-app ./helm/todo-app --namespace todo-app --dry-run --debug

# Apply changes
helm upgrade todo-app ./helm/todo-app --namespace todo-app

# Rollback if needed
helm rollback todo-app --namespace todo-app
```

### Testing Changes

```bash
# Rebuild specific service
docker build -f docker/backend.Dockerfile -t todo-backend:v2 ../phase-2/backend

# Load into Minikube
minikube image load todo-backend:v2

# Update deployment
kubectl set image deployment/backend backend=todo-backend:v2 -n todo-app

# Check rollout status
kubectl rollout status deployment/backend -n todo-app
```

---

## Monitoring and Debugging

### View Logs

```bash
# All pods in namespace
kubectl logs -f -l app.kubernetes.io/instance=todo-app -n todo-app

# Specific service
kubectl logs -f -l app=backend -n todo-app
kubectl logs -f -l app=frontend -n todo-app
kubectl logs -f -l app=auth-server -n todo-app

# Specific pod
kubectl logs -f <pod-name> -n todo-app
```

### Check Pod Status

```bash
# List all pods
kubectl get pods -n todo-app

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app

# Get pod details with resource usage
kubectl top pods -n todo-app
```

### Exec into Pod

```bash
# Get shell access
kubectl exec -it <pod-name> -n todo-app -- /bin/sh

# Run one-off command
kubectl exec <pod-name> -n todo-app -- env
```

### Port Forwarding (Debugging)

```bash
# Forward backend port to localhost
kubectl port-forward -n todo-app deployment/backend 8000:8000

# Forward frontend port
kubectl port-forward -n todo-app deployment/frontend 3000:3000

# Access at http://localhost:8000 or http://localhost:3000
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# - ImagePullBackOff: Image not loaded into Minikube
#   → Run: minikube image load <image-name>
# - CrashLoopBackOff: Application error
#   → Check logs: kubectl logs <pod-name> -n todo-app
# - Pending: Resource constraints
#   → Check: kubectl describe node minikube
```

### Database Connection Errors

```bash
# Verify DATABASE_URL secret
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test connection from pod
kubectl exec -it <backend-pod> -n todo-app -- python -c "
from sqlmodel import create_engine
engine = create_engine('$DATABASE_URL')
with engine.connect() as conn:
    print('Connected!')
"
```

### Ingress Not Working

```bash
# Check Ingress status
kubectl get ingress -n todo-app

# Verify Ingress controller is running
kubectl get pods -n ingress-nginx

# If not enabled:
minikube addons enable ingress
```

---

## Cleanup

```bash
# Remove Helm release
helm uninstall todo-app --namespace todo-app

# Delete namespace
kubectl delete namespace todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete

# Remove Docker images
docker rmi todo-frontend:latest todo-backend:latest todo-auth-server:latest
```

---

## AI-Powered Kubernetes Tools

### Gordon (Docker AI)

Gordon was used to generate and optimize the multi-stage Dockerfiles for all three services. Gordon analyzes application code and produces production-ready container configurations.

```bash
# Generate optimized Dockerfile for the FastAPI backend
docker ai "Create a multi-stage Dockerfile for a FastAPI Python app with UV package manager, non-root user, and health checks"

# Generate optimized Dockerfile for the Next.js frontend
docker ai "Create a multi-stage Dockerfile for a Next.js 16 app with pnpm, standalone output, and production optimizations"

# Generate optimized Dockerfile for the Express auth server
docker ai "Create a multi-stage Dockerfile for an Express TypeScript app with pnpm and health checks"

# Analyze and optimize existing Dockerfile
docker ai "Analyze my backend Dockerfile and suggest security improvements"
```

**Results**: Gordon generated the base Dockerfiles in `docker/`, which were then refined with project-specific configurations (UV, pnpm, standalone output).

### kubectl-ai

kubectl-ai enables natural language Kubernetes operations, making cluster management more intuitive.

```bash
# Install kubectl-ai
kubectl krew install ai

# Deploy the todo application
kubectl-ai "deploy the todo app with 2 frontend replicas and 2 backend replicas in the todo-app namespace"

# Scale services based on load
kubectl-ai "scale backend deployment to 3 replicas in todo-app namespace"

# Check pod health and status
kubectl-ai "show me all pods in todo-app namespace with their status and restart counts"

# Debug failing pods
kubectl-ai "find pods that are not running in todo-app namespace and show their logs"

# Resource usage analysis
kubectl-ai "show resource usage for all pods in the todo-app namespace"

# Network troubleshooting
kubectl-ai "check if frontend pods can connect to backend service in todo-app"

# Generate manifest from description
kubectl-ai "create a HorizontalPodAutoscaler for the backend deployment targeting 70% CPU"
```

### kagent

kagent provides intelligent cluster analysis, resource optimization, and automated troubleshooting.

```bash
# Install kagent
pip install kagent

# Analyze overall cluster health
kagent "analyze overall cluster health and identify bottlenecks"

# Optimize resource requests and limits
kagent "suggest optimal resource requests and limits for pods in todo-app namespace"

# Troubleshoot deployment failures
kagent "why are my backend pods failing? investigate and provide solution"

# Cost optimization recommendations
kagent "identify underutilized resources in todo-app namespace and suggest cost savings"

# Security audit
kagent "check for security vulnerabilities in my todo-app deployments"

# Performance analysis
kagent "analyze network latency between frontend and backend services"
```

---

## Production Considerations

This Phase IV setup is designed for **local development and testing**. For production, consider:

1. **Image Registry**: Push to Docker Hub, GCR, or ECR
2. **Managed Kubernetes**: Use GKE, EKS, or AKS
3. **External Secrets**: Use External Secrets Operator or Vault
4. **Ingress Controller**: nginx-ingress with Let's Encrypt
5. **Monitoring**: Prometheus, Grafana, Loki
6. **CI/CD**: GitHub Actions for automated deployments
7. **Autoscaling**: Horizontal Pod Autoscaler (HPA)

---

**Phase IV Complete** ✅
