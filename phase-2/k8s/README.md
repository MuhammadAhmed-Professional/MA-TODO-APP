# Kubernetes Manifests for Todo Application

This directory contains Kubernetes deployment manifests for the Phase 2 Todo Application with Dapr sidecar integration.

## Prerequisites

### 1. Kubernetes Cluster

- **Minikube** (for local development):
  ```bash
  minikube start --cpus=4 --memory=8192 --driver=docker
  minikube addons enable ingress
  minikube addons enable metrics-server
  ```

- **Kind** (alternative for local):
  ```bash
  kind create cluster --config kind-config.yaml
  ```

### 2. Dapr Installation

```bash
# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

# Initialize Dapr in Kubernetes
dapr init --kubernetes --wait
# Or for local Minikube with registry:
dapr init --kubernetes --image-registry docker.io/daprio --wait
```

Verify Dapr installation:
```bash
dapr status -k
```

### 3. Kafka (Optional - for pub/sub)

```bash
# Using Strimzi
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Create a Kafka cluster
kubectl apply -f -n kafka -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
spec:
  kafka:
    replicas: 1
    storage:
      type: jbod
      volumes:
      - id: 0
        type: persistent-claim
        size: 100Gi
        deleteClaim: false
  zookeeper:
    replicas: 1
    storage:
      type: persistent-claim
      size: 100Gi
        deleteClaim: false
EOF
```

## Quick Start

### 1. Build and Push Images

```bash
# Build backend image
docker build -t todo-backend:latest phase-2/backend/

# Build frontend image
docker build -t todo-frontend:latest phase-2/frontend/

# For Minikube, load images directly
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### 2. Create Secrets

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Create secret
kubectl create secret generic todo-app-secrets \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=database-url="postgresql://todo_user:password@postgres:5432/todo_db?sslmode=disable" \
  --from-literal=openai-api-key="sk-..." \
  -n todo-app
```

### 3. Apply Manifests

```bash
# Apply all manifests
kubectl apply -f phase-2/k8s/

# Or apply individually:
kubectl apply -f phase-2/k8s/namespace.yaml
kubectl apply -f phase-2/k8s/configmaps.yaml
kubectl apply -f phase-2/k8s/secrets.yaml
kubectl apply -f phase-2/k8s/dapr-config.yaml
kubectl apply -f phase-2/k8s/backend-deployment.yaml
kubectl apply -f phase-2/k8s/backend-service.yaml
kubectl apply -f phase-2/k8s/frontend-deployment.yaml
kubectl apply -f phase-2/k8s/frontend-service.yaml
kubectl apply -f phase-2/k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check Dapr sidecars
kubectl get pods -n todo-app -o custom-columns=NAME:.metadata.name,DAPR:.spec.containers[1].name

# Check ingress
kubectl get ingress -n todo-app
```

### 5. Access the Application

**With Minikube:**
```bash
# Get the Minikube IP
minikube ip

# Option 1: Use port forwarding
kubectl port-forward -n todo-app svc/frontend 3000:80

# Option 2: Enable ingress and use tunnel
minikube tunnel
# Then access via http://todo-app.local (add to /etc/hosts)
```

**With Ingress:**
```bash
# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Access the app
open http://todo-app.local
```

## Manifest Files

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `todo-app` namespace |
| `backend-deployment.yaml` | FastAPI deployment with Dapr sidecar |
| `backend-service.yaml` | ClusterIP service for backend API |
| `frontend-deployment.yaml` | Next.js deployment |
| `frontend-service.yaml` | ClusterIP service for frontend |
| `ingress.yaml` | NGINX ingress routing rules |
| `dapr-config.yaml` | Dapr configuration (pub/sub, state store) |
| `secrets.yaml` | Placeholder secrets (MUST update for production) |
| `configmaps.yaml` | Non-sensitive configuration |

## Dapr Integration

### Service Invocation

Call backend from frontend via Dapr:

```python
# Backend (Python/FastAPI)
from dapr import DaprClient

with DaprClient() as dapr:
    response = dapr.invoke_method(
        'todo-backend',
        '/api/tasks',
        data='{"title": "New Task"}',
        http_verb='POST'
    )
```

### Pub/Sub Messaging

```python
# Publish event
dapr.publish_event(
    pubsub_name='todo-pubsub',
    topic_name='task-events',
    data=json.dumps({"event": "task_created", "task_id": "123"})
)
```

## Scaling

```bash
# Scale backend
kubectl scale deployment/backend -n todo-app --replicas=3

# Scale frontend
kubectl scale deployment/frontend -n todo-app --replicas=2

# Horizontal Pod Autoscaler
kubectl autoscale deployment/backend -n todo-app --cpu-percent=70 --min=2 --max=10
kubectl autoscale deployment/frontend -n todo-app --cpu-percent=70 --min=2 --max=5
```

## Monitoring

```bash
# View logs
kubectl logs -n todo-app deployment/backend -f
kubectl logs -n todo-app deployment/frontend -f

# View Dapr sidecar logs
kubectl logs -n todo-app deployment/backend -c daprd -f

# Check resource usage
kubectl top pods -n todo-app
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod -n todo-app <pod-name>
kubectl logs -n todo-app <pod-name> --previous
```

### Dapr sidecar issues
```bash
# Check Dapr logs
kubectl logs -n todo-app <pod-name> -c daprd

# Restart Dapr
kubectl delete pod -n todo-app <pod-name>
```

### Ingress not working
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress rules
kubectl describe ingress -n todo-app
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace todo-app

# Or delete individual resources
kubectl delete -f phase-2/k8s/
```

## Production Considerations

1. **Secrets Management**: Use Sealed Secrets, External Secrets Operator, or cloud secret management
2. **TLS**: Enable TLS on ingress and configure certificates
3. **Resource Limits**: Adjust limits based on actual usage
4. **HPA**: Configure Horizontal Pod Autoscaler for production traffic
5. **PDB**: Add Pod Disruption Budgets for high availability
6. **Monitoring**: Add Prometheus, Grafana, and distributed tracing
7. **Logging**: Add centralized logging (ELK, Loki)

## Related Documentation

- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Strimzi Kafka Operator](https://strimzi.io/)
