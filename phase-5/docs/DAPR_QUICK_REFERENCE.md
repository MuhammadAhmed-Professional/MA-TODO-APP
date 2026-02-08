# Dapr Quick Reference Guide

## Common Dapr Operations

### Publishing Events

```python
from src.events.dapr_publisher import get_event_publisher

# Get publisher
publisher = await get_event_publisher()

# Publish task event
await publisher.publish_task_event(
    event_type="task.created",
    task_data={"id": "123", "title": "My Task"},
    user_id="user-123"
)

# Publish custom event
await publisher.publish_event(
    topic="custom-events",
    data={"key": "value"}
)
```

### State Management

```python
from src.services.state_service import get_state_service

# Get state service
state_service = await get_state_service()

# Cache task
await state_service.cache_task(
    task_id="task-123",
    task_data={"title": "My Task"},
    ttl=3600  # 1 hour
)

# Get cached task
cached = await state_service.get_cached_task("task-123")

# Invalidate cache
await state_service.invalidate_task_cache("task-123")

# Rate limiting
allowed = await state_service.check_rate_limit(
    key=f"api_limit:user-123",
    limit=100,
    window_seconds=3600
)
```

### Service Invocation

```python
from src.services.dapr_client import get_dapr_client

# Get client
dapr_client = await get_dapr_client()

# Call service
response = await dapr_client.invoke_service(
    app_id="notification-service",
    method="api/notify",
    http_verb="POST",
    data={"task_id": "123"}
)
```

### Conversation State

```python
from src.services.conversation_state import get_conversation_service

# Get service
conv_service = await get_conversation_service()

# Create conversation
context = await conv_service.create_conversation(user_id="user-123")

# Add message
await conv_service.add_message(
    conversation_id=context.conversation_id,
    role="user",
    content="Create a task for tomorrow"
)

# Get messages
messages = await conv_service.get_messages(context.conversation_id)
```

## Dapr HTTP API (via curl)

### Publish Event

```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type":"task.created","task_id":"123","task_data":{"title":"Test"},"user_id":"user-123","timestamp":"2024-01-01T00:00:00Z"}'
```

### Get State

```bash
curl http://localhost:3500/v1.0/state/postgres-statestore/task:123
```

### Save State

```bash
curl -X POST http://localhost:3500/v1.0/state/postgres-statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"task:123","value":{"title":"My Task"},"metadata":{"ttlInSeconds":"3600"}}]'
```

### Delete State

```bash
curl -X DELETE http://localhost:3500/v1.0/state/postgres-statestore/task:123
```

### Invoke Service

```bash
# POST
curl -X POST http://localhost:3500/v1.0/invoke/notification-service/method/api/notify \
  -H "Content-Type: application/json" \
  -d '{"task_id":"123"}'

# GET
curl http://localhost:3500/v1.0/invoke/todo-backend/method/api/tasks/123
```

### Get Secret

```bash
curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/sendgrid-secret
```

### Health Check

```bash
# Dapr sidecar health
curl http://localhost:3500/v1.0/healthz

# Application subscriptions
curl http://localhost:8000/dapr/subscribe
```

## Dapr CLI Commands

### Local Development

```bash
# Initialize Dapr
dapr init

# Run application with Dapr
dapr run --app-id my-app --app-port 8000 -- python main.py

# List running Dapr apps
dapr list

# View Dapr logs
dapr logs --app-id my-app

# Stop Dapr app
dapr stop --app-id my-app
```

### Kubernetes

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Check Dapr version
dapr --version

# Uninstall Dapr from Kubernetes
dapr uninstall -k
```

## Configuration Files

### Dapr Config (`dapr/config.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: dapr-config
  namespace: todo-app
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v2/spans"
  metric:
    enabled: true
  features:
    - name: ServiceInvocation
      enabled: true
    - name: Pubsub
      enabled: true
    - name: State
      enabled: true
```

### Pub/Sub Component (`dapr/components/pubsub-kafka.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "kafka-kafka-bootstrap.todo-app.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-backend-group"
```

### State Store Component (`dapr/components/statestore-postgres.yaml`)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: postgres-statestore
  namespace: todo-app
spec:
  type: state.postgresql
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-credentials
        key: connectionString
```

## Kubernetes Annotations

### Enable Dapr Sidecar

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "my-app"
  dapr.io/app-port: "8000"
  dapr.io/app-protocol: "http"
  dapr.io/log-level: "info"
  dapr.io/config: "dapr-config"
```

### Resource Limits

```yaml
annotations:
  dapr.io/sidecar-cpu-limit: "300m"
  dapr.io/sidecar-memory-limit: "256Mi"
  dapr.io/sidecar-cpu-request: "100m"
  dapr.io/sidecar-memory-request: "128Mi"
```

### Enable mTLS

```yaml
annotations:
  dapr.io/enable-mtls: "true"
```

## Environment Variables

```bash
# Dapr Ports
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# App Configuration
APP_ID=todo-backend
APP_PORT=8000

# Dapr Configuration
DAPR_CONFIG=dapr-config
DAPR_COMPONENTS_PATH=./dapr/components
```

## Subscription Examples

### Python (FastAPI)

```python
from fastapi import Request

@app.get("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "kafka-pubsub",
        "topic": "task-events",
        "route": "/events/task"
    }]

@app.post("/events/task")
async def handle_task_event(request: Request):
    body = await request.json()
    # Extract data from CloudEvents envelope
    data = body.get("data", body)
    # Process event
    return {"status": "success"}
```

### Node.js (Express)

```javascript
app.get('/dapr/subscribe', (req, res) => {
  res.json([{
    pubsubname: 'kafka-pubsub',
    topic: 'task-events',
    route: '/events/task'
  }]);
});

app.post('/events/task', (req, res) => {
  const data = req.body.data || req.body;
  // Process event
  res.json({ status: 'success' });
});
```

## Resiliency Patterns

### Retry

```yaml
# dapr/components/resiliency.yaml
policies:
  retries:
    DefaultRetryPolicy:
      policy: constant
      duration: 1s
      maxRetries: 3
```

### Circuit Breaker

```yaml
circuitBreakers:
  DefaultCircuitBreakerPolicy:
    maxRequests: 1
    timeout: 30s
    trip: consecutiveFailures > 5
```

### Timeout

```yaml
timeouts:
  DefaultTimeoutPolicy:
    timeout: 30s
```

## Metrics

### View Metrics

```bash
# Dapr sidecar metrics
curl http://localhost:9090/metrics

# Key metrics to watch
dapr_http_server_request_count_total
dapr_http_client_request_count_total
dapr_component_pubsub_publish_success_total
dapr_runtime_actor_invocation_total
```

### Prometheus Scrape Config

```yaml
scrape_configs:
  - job_name: 'dapr'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names: ['todo-app']
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enable_metrics]
        action: keep
        regex: "true"
      - source_labels: [__meta_kubernetes_pod_container_port_number]
        action: keep
        regex: "9090"
```

## Troubleshooting

### Dapr Sidecar Not Starting

```bash
# Check Dapr installation
dapr status

# Check logs
journalctl -u dapr-sidebar -f

# Reinstall
dapr uninstall
dapr init
```

### Events Not Received

```bash
# Check subscriptions
curl http://localhost:8000/dapr/subscribe

# Check Dapr logs
dapr logs --app-id my-app | grep subscribe

# Test publish
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{"test":"data"}'
```

### State Operations Failing

```bash
# Check component
kubectl get component postgres-statestore -n todo-app -o yaml

# Test connection
kubectl exec -it <pod> -c backend -- nc -zv postgres 5432

# Check secret
kubectl get secret postgres-credentials -n todo-app -o yaml
```

## Performance Tuning

### Increase Throughput

```yaml
# Pub/sub component
metadata:
  - name: maxMessageBytes
    value: "1024000"  # 1MB
  - name: consumeRetryInterval
    value: "200ms"
```

### Reduce Latency

```yaml
# Timeout policies
timeouts:
  FastTimeoutPolicy:
    timeout: 5s

# Circuit breaker
circuitBreakers:
  LowLatencyPolicy:
    maxRequests: 10
    timeout: 5s
```

### Memory Optimization

```yaml
annotations:
  dapr.io/sidecar-memory-limit: "128Mi"
  dapr.io/sidecar-memory-request: "64Mi"
```

## Security

### Enable mTLS

```yaml
# dapr/config.yaml
spec:
  mtls:
    enabled: true
    workloadCertTTL: 24h
```

### Access Control

```yaml
accessControl:
  policies:
    - appId: todo-frontend
      defaultAction: allow
      trustDomain: "public"
      operations:
        - name: "/api/*"
          httpVerb: ["GET", "POST"]
          action: allow
```

### Secret Store

```yaml
# dapr/components/secret-store.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
```

## Best Practices

1. **Use State Store for Caching**: Cache frequently accessed data with TTL
2. **Implement Idempotent Handlers**: Handle duplicate events gracefully
3. **Set Appropriate Timeouts**: Balance between responsiveness and reliability
4. **Monitor Circuit Breakers**: Alert on frequent trips
5. **Use Structured Logging**: Include trace IDs in logs
6. **Test Failure Scenarios**: Verify retry and circuit breaker behavior
7. **Secure Secrets**: Use Dapr secret store, never environment variables
8. **Label Namespaces**: Enable Dapr injection at namespace level
9. **Resource Limits**: Set CPU/memory limits for Dapr sidecars
10. **Health Checks**: Implement both liveness and readiness probes

## Resources

- [Dapr Documentation](https://docs.dapr.io)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Dapr Samples](https://github.com/dapr/samples)
- [Dapr Discord](https://discord.gg/dapr)
