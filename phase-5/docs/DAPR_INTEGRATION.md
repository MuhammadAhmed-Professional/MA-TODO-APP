# Dapr Integration Guide

## Overview

Phase V of the Todo Application uses [Dapr (Distributed Application Runtime)](https://dapr.io) for microservice orchestration. Dapr provides building blocks for distributed systems including pub/sub, state management, service invocation, and secrets management.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                      │
│                                                               │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │   todo-backend   │        │ todo-frontend    │          │
│  │   (FastAPI)      │        │   (Next.js)      │          │
│  │                  │        │                  │          │
│  │  ┌────────────┐  │        │                  │          │
│  │  │  Business  │  │        │                  │          │
│  │  │   Logic    │  │        │                  │          │
│  │  └─────┬──────┘  │        │                  │          │
│  │        │         │        │                  │          │
│  │  ┌─────▼──────┐  │        │                  │          │
│  │  │  Dapr      │  │        │                  │          │
│  │  │  Sidecar   │  │        │                  │          │
│  │  └─────┬──────┘  │        │                  │          │
│  └────────┼─────────┘        └──────────────────┘          │
│           │                                                   │
│           ├──────────────┬──────────────┬─────────────┐     │
│           ▼              ▼              ▼             ▼     │
│  ┌─────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────┐│
│  │    Kafka    │ │  PostgreSQL  │ │  Kubernetes │ │ Dapr ││
│  │   (Strimzi) │ │  (Neon/Cloud)│ │   Secrets   │ │State ││
│  └─────────────┘ └──────────────┘ └────────────┘ └──────┘│
│                                                           │
│  ┌──────────────────────┐  ┌──────────────────────────┐  │
│  │ notification-service │  │ recurring-task-service   │  │
│  │       (FastAPI)      │  │       (FastAPI)          │  │
│  │                      │  │                          │  │
│  │  ┌────────────────┐  │  │  ┌────────────────────┐ │  │
│  │  │   Dapr Pub/Sub │  │  │  │   Dapr Invoke      │ │  │
│  │  │   Subscribers  │  │  │  │   Service Calls     │ │  │
│  │  └────────────────┘  │  │  └────────────────────┘ │  │
│  └──────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Dapr Building Blocks Used

### 1. Pub/Sub (Publish/Subscribe)

**Component**: `kafka-pubsub` (type: pubsub.kafka)

**Topics**:
- `task-events` - Task lifecycle events (created, updated, completed, deleted)
- `reminders` - Reminder notification events
- `audit-logs` - Audit log events

**Publishing Events**:
```python
from src.events.dapr_publisher import get_event_publisher

publisher = await get_event_publisher()

# Publish task event
await publisher.publish_task_event(
    event_type="task.completed",
    task_data={"id": "123", "title": "My Task", ...},
    user_id="user-123"
)
```

**Subscribing to Events**:
```python
from fastapi import Request

@app.post("/task-events")
async def handle_task_event(request: Request):
    # Dapr sends CloudEvents envelope
    body = await request.json()
    event_data = body.get("data", body)

    # Process event
    logger.info(f"Received event: {event_data}")

    # Return 200 to acknowledge
    return {"status": "success"}
```

**Subscription Discovery**:
```python
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
```

### 2. State Management

**Component**: `postgres-statestore` (type: state.postgresql)

**Usage Patterns**:

**Caching Task Data**:
```python
from src.services.state_service import get_state_service

state_service = await get_state_service()

# Cache task data
await state_service.cache_task(
    task_id="task-123",
    task_data={"id": "123", "title": "My Task", ...},
    ttl=3600  # 1 hour
)

# Retrieve cached task
cached_task = await state_service.get_cached_task("task-123")
```

**Conversation State**:
```python
from src.services.conversation_state import get_conversation_service

conv_service = await get_conversation_service()

# Create conversation
context = await conv_service.create_conversation(user_id="user-123")

# Add message
await conv_service.add_message(
    conversation_id=context.conversation_id,
    role="user",
    content="Create a task for tomorrow"
)
```

**Rate Limiting**:
```python
# Check rate limit (60 requests per minute)
allowed = await state_service.check_rate_limit(
    key=f"rate_limit:user:{user_id}",
    limit=60,
    window_seconds=60
)

if not allowed:
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### 3. Service Invocation

**Usage**: Replace direct HTTP calls with Dapr service invocation for automatic retries, circuit breaking, and service discovery.

```python
from src.services.dapr_client import get_dapr_client

dapr_client = await get_dapr_client()

# Call another service
response = await dapr_client.invoke_service(
    app_id="recurring-task-service",
    method="api/tasks/created",
    http_verb="POST",
    data={"task_id": "123", "user_id": "user-123"}
)
```

**Benefits**:
- Automatic retries (configurable)
- Circuit breaking (prevents cascading failures)
- Service discovery (no hardcoded URLs)
- Observability (built-in tracing)

### 4. Secrets Management

**Component**: `kubernetes-secrets` (type: secretstores.kubernetes)

**Usage**: Access secrets without exposing them in environment variables.

```python
dapr_client = await get_dapr_client()

# Get secret from Kubernetes secret store
secret = await dapr_client.get_secret(
    store_name="kubernetes-secrets",
    key="sendgrid-secret"
)

api_key = secret.get("api-key")
```

**Creating Kubernetes Secrets**:
```bash
kubectl create secret generic sendgrid-secret \
  --from-literal=api-key=YOUR_SENDGRID_API_KEY \
  -n todo-app
```

### 5. Bindings (Cron Jobs)

**Component**: `bindings.cron`

**Usage**: Trigger periodic tasks without external cron services.

```python
@app.post("/api/jobs/check-reminders")
async def check_reminders_job(request: Request):
    """Called every minute by Dapr cron binding"""
    # Check for due reminders
    due_reminders = await get_due_reminders()

    # Send notifications
    for reminder in due_reminders:
        await send_notification(reminder)

    return {"status": "success"}
```

**Cron Bindings Configured**:
- `reminder-checker-cron`: Every minute (`*/1 * * * *`)
- `recurring-task-cron`: Every hour (`0 * * * *`)
- `daily-cleanup-cron`: Daily at 2 AM (`0 2 * * *`)

## Resiliency Policies

Dapr provides automatic retry, timeout, and circuit breaker policies configured in `dapr/components/resiliency.yaml`.

**Default Retry Policy**:
- Constant backoff: 1 second
- Max retries: 3
- Backoff coefficient: 1.5

**Circuit Breaker**:
- Opens after 5 consecutive failures
- Timeout: 30 seconds
- Threshold: 50% failure rate

**Applying Policies**:
```yaml
# Applied automatically based on configuration
targets:
  apps:
    todo-backend:
      retry: DefaultRetryPolicy
      timeout: DefaultTimeoutPolicy
      circuitBreaker: DefaultCircuitBreakerPolicy
```

## Local Development

### Prerequisites

1. **Dapr CLI**:
   ```bash
   # Install Dapr CLI
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

   # Initialize Dapr
   dapr init
   ```

2. **Kubernetes (for minikube/kind)**:
   ```bash
   # Install Dapr on Kubernetes
   dapr init -k
   ```

3. **Dependencies**:
   - Kafka (local or Strimzi in Kubernetes)
   - PostgreSQL (local or Neon cloud)

### Running Services with Dapr

**Backend**:
```bash
# Run backend with Dapr sidecar
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --config ../dapr/config.yaml \
  --components-path ../dapr/components \
  -- uvicorn src.main:app
```

**Notification Service**:
```bash
dapr run \
  --app-id notification-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --config ../dapr/config.yaml \
  -- python main.py
```

**Recurring Task Service**:
```bash
dapr run \
  --app-id recurring-task-service \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --config ../dapr/config.yaml \
  -- python main.py
```

### Testing Dapr Endpoints

**Publish Event**:
```bash
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.created",
    "task_id": "123",
    "task_data": {"title": "Test Task"},
    "user_id": "user-123",
    "timestamp": "2024-01-01T00:00:00Z"
  }'
```

**Get State**:
```bash
curl http://localhost:3500/v1.0/state/postgres-statestore/task:123
```

**Save State**:
```bash
curl -X POST http://localhost:3500/v1.0/state/postgres-statestore \
  -H "Content-Type: application/json" \
  -d '[
    {
      "key": "task:123",
      "value": {"title": "Test Task", "completed": false}
    }
  ]'
```

**Invoke Service**:
```bash
curl -X POST http://localhost:3500/v1.0/invoke/notification-service/method/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "123",
    "user_id": "user-123"
  }'
```

**Get Secret**:
```bash
curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/sendgrid-secret
```

## Kubernetes Deployment

### Namespace Setup

```bash
# Create namespace
kubectl create namespace todo-app

# Label namespace for Dapr injection
kubectl label namespace todo-app dapr.io/inject=enabled
```

### Deploy Services

Services are automatically deployed with Dapr sidecars due to annotations in deployment files:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-backend"
  dapr.io/app-port: "8000"
  dapr.io/config: "dapr-config"
```

**Apply Kubernetes manifests**:
```bash
kubectl apply -f k8s/cloud/namespace.yaml
kubectl apply -f k8s/cloud/services.yaml
kubectl apply -f k8s/cloud/backend-deployment.yaml
kubectl apply -f k8s/cloud/notification-service-deployment.yaml
kubectl apply -f k8s/cloud/recurring-task-service-deployment.yaml
```

**Apply Dapr components**:
```bash
kubectl apply -f dapr/components/
```

### Verify Dapr Sidecar

```bash
# Check Dapr sidecar is injected
kubectl get pods -n todo-app

# View Dapr logs
kubectl logs -n todo-app <pod-name> -c daprd

# Check Dapr health
kubectl exec -n todo-app <pod-name> -c daprd -- curl localhost:3500/v1.0/healthz
```

## Observability

### Metrics

Dapr exposes Prometheus metrics on port `9090`:

```bash
kubectl port-forward -n todo-app <pod-name> 9090:9090
curl http://localhost:9090/metrics
```

**Key Metrics**:
- `dapr_http_server_request_count` - Number of HTTP requests
- `dapr_http_client_request_count` - Number of client requests
- `dapr_runtime_actor_invocation_count` - Actor invocations
- `dapr_component_pubsub_publish_success_count` - Pub/sub success

### Tracing

Dapr sends traces to Zipkin (configured in `dapr/config.yaml`):

```yaml
tracing:
  samplingRate: "1"
  zipkin:
    endpointAddress: "http://zipkin.observability.svc.cluster.local:9411/api/v2/spans"
```

View traces in Zipkin UI:
```bash
kubectl port-forward -n observability svc/zipkin 9411:9411
```

### Logging

Dapr logs are available via Kubernetes:

```bash
# View Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd --tail=100 -f

# View application logs
kubectl logs -n todo-app <pod-name> -c backend --tail=100 -f
```

## Troubleshooting

### Dapr Sidecar Not Starting

**Symptoms**: Pod stuck in `Init` or `CrashLoopBackOff`

**Solutions**:
1. Check Dapr installation: `kubectl get pods -n dapr-system`
2. Verify namespace has injection enabled: `kubectl describe namespace todo-app`
3. Check Dapr logs: `kubectl logs -n todo-app <pod-name> -c daprd`

### Pub/Sub Messages Not Delivered

**Symptoms**: Events published but not received

**Solutions**:
1. Verify subscription endpoint: `curl http://localhost:8000/dapr/subscribe`
2. Check topic subscription in logs
3. Verify Kafka connectivity: `kubectl exec -it <pod-name> -c backend -- nc -zv kafka-kafka-bootstrap 9092`
4. Check Dapr pub/sub health: `curl http://localhost:3500/v1.0/healthz`

### State Store Errors

**Symptoms**: State operations fail

**Solutions**:
1. Verify PostgreSQL connection string in secret
2. Check database exists and tables created
3. Test state store: `curl http://localhost:3500/v1.0/state/postgres-statestore/test-key`

### Service Invocation Failing

**Symptoms**: Service-to-service calls timeout

**Solutions**:
1. Verify target service is running: `kubectl get pods -n todo-app`
2. Check service name matches app-id
3. Check Dapr sidecar logs for target service
4. Test direct HTTP call to bypass Dapr for diagnosis

## Best Practices

### 1. Use State Store for Caching
- Cache frequently accessed data (tasks, user preferences)
- Set appropriate TTL values
- Invalidate cache on updates

### 2. Leverage Resiliency Policies
- Configure retries for transient failures
- Use circuit breakers to prevent cascading failures
- Set appropriate timeouts

### 3. Structure Events Properly
- Include event type and timestamp
- Use CloudEvents format (Dapr adds this automatically)
- Make events idempotent (handle duplicates)

### 4. Monitor Dapr Metrics
- Track request latency and error rates
- Monitor circuit breaker state
- Alert on abnormal patterns

### 5. Security
- Use Dapr secret store (no secrets in env vars)
- Enable mTLS for service-to-service communication
- Restrict service invocation with access control policies

## Migration Path

### From Direct Kafka to Dapr Pub/Sub

**Before**:
```python
from aiokafka import AIOKafkaProducer

producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
await producer.send("task-events", value=event_data)
```

**After**:
```python
from src.events.dapr_publisher import get_event_publisher

publisher = await get_event_publisher()
await publisher.publish_task_event(
    event_type="task.created",
    task_data=task_data,
    user_id=user_id
)
```

### From Direct HTTP to Dapr Invoke

**Before**:
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://notification-service:8001/api/notify",
        json={"task_id": "123"}
    )
```

**After**:
```python
dapr_client = await get_dapr_client()
response = await dapr_client.invoke_service(
    app_id="notification-service",
    method="api/notify",
    data={"task_id": "123"}
)
```

## References

- [Dapr Documentation](https://docs.dapr.io)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Dapr Pub/Sub](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Dapr State Management](https://docs.dapr.io/developing-applications/building-blocks/state-management/)
- [Dapr Service Invocation](https://docs.dapr.io/developing-applications/building-blocks/service-invocation/)
