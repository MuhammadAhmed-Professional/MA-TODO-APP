# todo-frontend Helm Chart

Helm chart for deploying the Phase II Todo App Next.js Frontend to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (optional)

## Installing the Chart

To install the chart with the release name `todo-frontend`:

```bash
helm install todo-frontend ./todo-frontend
```

## Uninstalling the Chart

To uninstall/delete the `todo-frontend` deployment:

```bash
helm uninstall todo-frontend
```

## Configuration

The following table lists the configurable parameters of the todo-frontend chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `todo-frontend` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `image.tag` | Image tag | `latest` |
| `nameOverride` | String to partially override fullname | `""` |
| `fullnameOverride` | String to fully override fullname | `""` |
| `serviceAccount.create` | Create service account | `true` |
| `serviceAccount.annotations` | Service account annotations | `{}` |
| `serviceAccount.name` | Service account name | `""` |
| `podAnnotations` | Pod annotations | `{}` |
| `podSecurityContext` | Pod security context | See values.yaml |
| `securityContext` | Container security context | See values.yaml |
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `3000` |
| `service.targetPort` | Service target port | `3000` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.annotations` | Ingress annotations | See values.yaml |
| `ingress.hosts` | Ingress hosts | See values.yaml |
| `ingress.tls` | Ingress TLS configuration | See values.yaml |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `256Mi` |
| `autoscaling.enabled` | Enable HPA | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `5` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU % | `70` |
| `autoscaling.targetMemoryUtilizationPercentage` | Target Memory % | `80` |
| `replicaCount` | Replica count (no HPA) | `1` |
| `env.NEXT_PUBLIC_API_URL` | Backend API URL | `http://todo-backend:8000` |
| `env.NEXT_PUBLIC_ENVIRONMENT` | Environment | `production` |
| `envFrom` | Additional envFrom sources | `[]` |
| `nodeSelector` | Node selector | `{}` |
| `tolerations` | Tolerations | `[]` |
| `affinity` | Affinity rules | `{}` |
| `dapr.enabled` | Enable Dapr sidecar | `false` |
| `dapr.appId` | Dapr app ID | `todo-frontend` |
| `dapr.appPort` | Dapr app port | `3000` |
| `dapr.protocols` | Dapr protocol | `http` |

### Example: Custom Values

Create a `custom-values.yaml` file:

```yaml
image:
  repository: myregistry/todo-frontend
  tag: v1.0.0

ingress:
  hosts:
    - host: todo.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-tls
      hosts:
        - todo.example.com

env:
  NEXT_PUBLIC_API_URL: https://api.example.com
  NEXT_PUBLIC_ENVIRONMENT: production
```

Install with custom values:

```bash
helm install todo-frontend ./todo-frontend -f custom-values.yaml
```

## Dapr Integration

To enable Dapr sidecar for service invocation:

```bash
helm install todo-frontend ./todo-frontend --set dapr.enabled=true
```

## Production Deployment

For production deployment with proper resource limits and HPA:

```bash
helm install todo-frontend ./todo-frontend \
  --set image.tag=v1.0.0 \
  --set ingress.hosts[0].host=todo.example.com \
  --set env.NEXT_PUBLIC_API_URL=https://api.example.com \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

## Upgrading

To upgrade the deployment:

```bash
helm upgrade todo-frontend ./todo-frontend
```

## Rolling Back

To rollback to a previous release:

```bash
helm rollback todo-frontend [REVISION]
```

## Troubleshooting

Get all resources for the release:

```bash
helm get all todo-frontend
```

Check pod status:

```bash
kubectl get pods -l app.kubernetes.io/name=todo-frontend
```

View logs:

```bash
kubectl logs -l app.kubernetes.io/name=todo-frontend --tail=100 -f
```

Port forward for local testing:

```bash
kubectl port-forward svc/todo-frontend 3000:3000
```

Then visit http://localhost:3000
