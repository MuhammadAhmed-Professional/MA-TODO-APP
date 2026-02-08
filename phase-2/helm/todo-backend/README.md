# todo-backend Helm Chart

Helm chart for deploying the Phase II Todo App FastAPI Backend with Dapr sidecar support.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Dapr 1.12+ (if Dapr sidecar is enabled)
- PostgreSQL database (external or in-cluster)

## Installation

### Default Installation

```bash
helm install todo-backend ./todo-backend
```

### Custom Values

Create a `custom-values.yaml` file:

```yaml
# Image configuration
image:
  registry: ghcr.io
  repository: your-org/todo-backend
  tag: "v1.0.0"

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.todo-app.example.com
      paths:
        - path: /
          pathType: Prefix

# Secret configuration (use existing secrets)
secret:
  create: false

# Reference existing secrets
envFromSecret:
  DATABASE_URL:
    secretName: todo-backend-secret
    key: database-url
  OPENAI_API_KEY:
    secretName: todo-backend-secret
    key: openai-api-key
  JWT_SECRET:
    secretName: todo-backend-secret
    key: jwt-secret

# Enable autoscaling
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
```

Install with custom values:

```bash
helm install todo-backend ./todo-backend -f custom-values.yaml
```

## Configuration

The following table lists the configurable parameters of the todo-backend chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.registry` | Image registry | `docker.io` |
| `image.repository` | Image repository | `todo-backend` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `nameOverride` | Override chart name | `""` |
| `fullnameOverride` | Override full deployment name | `""` |
| `app.port` | Application container port | `8000` |
| `app.environment` | Application environment | `production` |
| `app.logLevel` | Application log level | `INFO` |
| `dapr.enabled` | Enable Dapr sidecar | `true` |
| `dapr.appId` | Dapr application ID | `todo-backend` |
| `dapr.appPort` | Dapr application port | `8000` |
| `dapr.appProtocol` | Dapr protocol | `http` |
| `dapr.enableMetrics` | Enable Dapr metrics | `true` |
| `dapr.metricsPort` | Dapr metrics port | `9090` |
| `serviceAccount.create` | Create service account | `true` |
| `serviceAccount.name` | Service account name | `""` |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts` | Ingress hosts | `[]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `autoscaling.enabled` | Enable HPA | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `5` |
| `podDisruptionBudget.enabled` | Enable PDB | `false` |
| `podDisruptionBudget.minAvailable` | Minimum available pods | `1` |
| `envFromConfigMap` | Load env from ConfigMap | `true` |
| `secret.create` | create secret | `true` |
| `secret.DATABASE_URL` | Database connection string | `postgresql://...` |
| `secret.OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `secret.JWT_SECRET` | JWT signing secret | `change-me` |

## Required Secrets

The backend requires the following environment variables:

1. **DATABASE_URL**: PostgreSQL connection string
   ```
   postgresql://user:password@host:5432/dbname?sslmode=require
   ```

2. **OPENAI_API_KEY**: OpenAI API key for AI agent functionality
   ```
   sk-your-openai-key-here
   ```

3. **JWT_SECRET**: Secret for JWT token signing
   ```
   # Generate with: openssl rand -hex 32
   ```

### Creating the Secret

```bash
kubectl create secret generic todo-backend-secret \
  --from-literal=database-url='postgresql://user:password@host:5432/todo?sslmode=require' \
  --from-literal=openai-api-key='sk-your-openai-key-here' \
  --from-literal=jwt-secret='your-256-bit-random-secret' \
  -n default
```

## Dapr Configuration

The chart includes Dapr sidecar annotations by default. To configure Dapr:

```yaml
dapr:
  enabled: true
  appId: "todo-backend"
  appPort: 8000
  appProtocol: http
  enableMetrics: true
  metricsPort: 9090
  config: todo-backend-config  # Reference existing Dapr configuration
```

## Upgrading

```bash
helm upgrade todo-backend ./todo-backend -f custom-values.yaml
```

## Uninstalling

```bash
helm uninstall todo-backend
```

## Troubleshooting

### Check pod status

```bash
kubectl get pods -l app.kubernetes.io/name=todo-backend
```

### View logs

```bash
kubectl logs -l app.kubernetes.io/name=todo-backend --all-containers=true
```

### Port forward to test locally

```bash
kubectl port-forward svc/todo-backend 8000:8000
```

Then access:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Development

To test changes locally:

```bash
helm install todo-backend ./todo-backend --dry-run --debug
```

To package the chart:

```bash
helm package ./todo-backend
```
