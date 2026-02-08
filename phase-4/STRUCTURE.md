# Phase IV Directory Structure

```
phase-4/
├── README.md                              # Comprehensive documentation with setup guide
├── STRUCTURE.md                           # This file
│
├── docker/                                # Docker multi-stage builds
│   ├── frontend.Dockerfile                # Next.js 16 (standalone output)
│   ├── backend.Dockerfile                 # FastAPI with UV package manager
│   └── auth-server.Dockerfile             # Express.js TypeScript build
│
├── docker-compose.yml                     # Local development environment (all 3 services)
│
├── k8s/                                   # Raw Kubernetes manifests
│   ├── namespace.yaml                     # Create "todo-app" namespace
│   ├── configmap.yaml                     # Non-secret environment variables
│   ├── secret.yaml                        # Secret template (base64 placeholders)
│   │
│   ├── backend-deployment.yaml            # Backend pods (2 replicas, resource limits)
│   ├── backend-service.yaml               # Backend NodePort service (port 30800)
│   │
│   ├── frontend-deployment.yaml           # Frontend pods (2 replicas)
│   ├── frontend-service.yaml              # Frontend NodePort service (port 30000)
│   │
│   ├── auth-server-deployment.yaml        # Auth server pods (2 replicas)
│   ├── auth-server-service.yaml           # Auth server NodePort service (port 30801)
│   │
│   └── ingress.yaml                       # HTTP routing (/ → frontend, /api → backend)
│
├── helm/                                  # Helm chart for parameterized deployment
│   └── todo-app/
│       ├── Chart.yaml                     # Chart metadata (version 1.0.0)
│       ├── values.yaml                    # Default values (replicas, resources, env vars)
│       │
│       └── templates/
│           ├── _helpers.tpl               # Template helper functions
│           ├── namespace.yaml             # Namespace template
│           ├── configmap.yaml             # ConfigMap template
│           ├── secret.yaml                # Secret template
│           │
│           ├── backend-deployment.yaml    # Backend deployment template
│           ├── backend-service.yaml       # Backend service template
│           │
│           ├── frontend-deployment.yaml   # Frontend deployment template
│           ├── frontend-service.yaml      # Frontend service template
│           │
│           ├── auth-server-deployment.yaml # Auth server deployment template
│           ├── auth-server-service.yaml   # Auth server service template
│           │
│           └── ingress.yaml               # Ingress template
│
└── scripts/                               # Automation scripts
    ├── build-images.sh                    # Build all 3 Docker images
    └── minikube-setup.sh                  # Automated Minikube cluster setup

Total Files: 30
```

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd phase-4
./scripts/minikube-setup.sh
```

### Option 2: Docker Compose (Local Development)
```bash
cd phase-4
docker-compose up --build
```

### Option 3: Manual Kubernetes Deployment
```bash
# Build images
./scripts/build-images.sh

# Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192
minikube addons enable ingress

# Load images
minikube image load todo-frontend:latest
minikube image load todo-backend:latest
minikube image load todo-auth-server:latest

# Deploy with Helm
helm install todo-app ./helm/todo-app --namespace todo-app

# Access application
minikube service frontend-service -n todo-app
```

## Architecture

- **Frontend**: Next.js 16 (port 3000, NodePort 30000)
- **Backend**: FastAPI (port 8000, NodePort 30800)
- **Auth Server**: Express.js (port 3001, NodePort 30801)
- **Database**: Neon PostgreSQL (external SaaS, not containerized)

## Resource Configuration

All deployments include:
- Resource requests and limits (CPU/memory)
- Liveness and readiness probes
- Health checks on `/health` endpoints
- Non-root container users for security
- 2 replicas per service for high availability

## Next Steps

1. Create `.env` file with your secrets (DATABASE_URL, JWT_SECRET, etc.)
2. Run automated setup: `./scripts/minikube-setup.sh`
3. Access frontend at `http://<minikube-ip>:30000`
4. Monitor with `kubectl get pods -n todo-app`
