# Dapr Architecture Documentation

## System Overview

Phase V of the Todo Application implements a microservices architecture with Dapr providing the distributed systems primitives. The architecture decouples services through event-driven communication and provides resilience through automatic retries and circuit breaking.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Kubernetes Cluster                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        Frontend Layer                           │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │           todo-frontend (Next.js 16)                     │   │   │
│  │  │  - App Router                                            │   │   │
│  │  │  - React Server Components                               │   │   │
│  │  │  - shadcn/ui Components                                  │   │   │
│  │  └───────────────────────┬──────────────────────────────────┘   │   │
│  └──────────────────────────┼──────────────────────────────────────┘   │
│                             │ HTTP/REST                                 │
│  ┌──────────────────────────▼──────────────────────────────────────┐   │
│  │                     API Gateway / Ingress                       │   │
│  │  - Nginx Ingress Controller                                    │   │
│  │  - TLS Termination                                             │   │
│  │  - Path-based Routing                                          │   │
│  └──────────────────────────┬──────────────────────────────────────┘   │
│                             │                                           │
│         ┌───────────────────┼───────────────────┐                     │
│         │                   │                   │                     │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐              │
│  │todo-backend │    │notification │    │  recurring  │              │
│  │   (FastAPI) │    │  -service   │    │    -task    │              │
│  │             │    │  (FastAPI)  │    │  -service   │              │
│  │ ┌─────────┐ │    │             │    │  (FastAPI)  │              │
│  │ │ Business│ │    │ ┌─────────┐ │    │             │              │
│  │ │  Logic  │ │    │ │  Event  │ │    │ ┌─────────┐ │              │
│  │ └────┬────┘ │    │ │Handlers │ │    │ │Process  │ │              │
│  │      │      │    │ └────┬────┘ │    │ │  Logic  │ │              │
│  │ ┌────▼────┐ │    │      │      │    │ └────┬────┘ │              │
│  │ │  Dapr   │ │    │ ┌────▼────┐ │    │      │      │              │
│  │ │ Sidecar │ │    │ │  Dapr   │ │    │ ┌────▼────┐ │              │
│  │ └────┬────┘ │    │ │ Sidecar │ │    │ │  Dapr   │ │              │
│  └──────┼──────┘    │ └────┬────┘ │    │ │ Sidecar │ │              │
│         │           └──────┼──────┘    │ └────┬────┘ │              │
│         └──────────────────┼───────────────┼──────┘                │
│                             │               │                        │
│         ┌───────────────────┼───────────────┼────────────────┐     │
│         │                   │               │                │     │
│  ┌──────▼──────┐    ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼─────┐│
│  │   Kafka    │    │ PostgreSQL  │  │   Kubernetes│  │   Cron    ││
│  │  (Strimzi) │    │ State Store │  │   Secrets  │  │  Bindings ││
│  └─────────────┘    └─────────────┘  └────────────┘  └───────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Dapr Building Blocks

### 1. Service Invocation

**Purpose**: Direct service-to-service communication with automatic retries and circuit breaking.

**Architecture**:
```
┌─────────────────┐     ┌─────────────────┐
│  Service A      │     │  Service B      │
│                 │     │                 │
│  ┌───────────┐  │     │  ┌───────────┐  │
│  │  App Code │  │     │  │  App Code │  │
│  └─────┬─────┘  │     │  └─────▲─────┘  │
│        │ invoke  │     │        │        │
│  ┌─────▼─────┐  │     │  ┌─────┴─────┐  │
│  │  Dapr    │◄─┼─────┼──┤   Dapr    │  │
│  │ Sidecar  │  │     │  │  Sidecar  │  │
│  └──────────┘  │     │  └──────────┘  │
└─────────────────┘     └─────────────────┘
```

**Flow**:
1. Service A's Dapr sidecar receives invoke call
2. Sidecar resolves service B location (via Kubernetes service discovery)
3. Sidecar applies resiliency policies (retry, timeout, circuit breaker)
4. Sidecar calls service B's Dapr sidecar
5. Service B's sidecar forwards to app code
6. Response flows back through the same path

**Configuration**:
- Resiliency: Defined in `dapr/components/resiliency.yaml`
- Access Control: Defined in `dapr/config.yaml`
- Timeout: 30s default, configurable per service

### 2. Pub/Sub (Publish-Subscribe)

**Purpose**: Decoupled, asynchronous event communication between services.

**Architecture**:
```
┌─────────────┐                    ┌─────────────┐
│   Publisher │                    │  Subscriber │
│             │                    │             │
│ ┌─────────┐ │                    │ ┌─────────┐ │
│ │   App   │ │                    │ │   App   │ │
│ └────┬────┘ │                    │ └────▲────┘ │
│      │      │                    │      │      │
│ ┌────▼────┐ │                    │ ┌────┴────┐ │
│ │  Dapr   │ │                    │ │  Dapr   │ │
│ │ Sidecar │ │                    │ │ Sidecar │ │
│ └────┬────┘ │                    │ └────▲────┘ │
└─────┼───────┘                    │      │      │
      │ publish                   └──────┼──────┘
      │                                 │ subscribe
      ▼                                 │
 ┌──────────────────────────────────────┴──────┐
 │              Kafka Cluster                  │
 │  - topic: task-events                       │
 │  - topic: reminders                         │
 │  - topic: audit-logs                        │
 └─────────────────────────────────────────────┘
```

**Event Flow**:
1. Publisher app publishes event to Dapr sidecar
2. Dapr sidecar sends event to Kafka topic
3. Kafka delivers to all consumer groups
4. Each consumer group has one consumer receive the message
5. Dapr sidecar calls subscriber's route with CloudEvents envelope
6. Subscriber returns 200 to acknowledge (commit offset)

**Topics**:
- `task-events`: Task lifecycle (created, updated, completed, deleted)
- `reminders`: Due reminder notifications
- `audit-logs`: Audit trail for compliance

### 3. State Management

**Purpose**: Distributed caching and state storage with pluggable backends.

**Architecture**:
```
┌─────────────────┐
│   Application   │
│                 │
│ ┌─────────────┐ │
│ │ State Store │ │
│ │   Client    │ │
│ └──────┬──────┘ │
│        │        │
│ ┌──────▼──────┐ │
│ │  Dapr       │ │
│ │  Sidecar    │ │
│ └──────┬──────┘ │
└─────────┼────────┘
          │
          ▼
┌─────────────────────────────────┐
│      State Store Component      │
│  - Type: state.postgresql       │
│  - Table: dapr_state            │
│  - Metadata: dapr_metadata      │
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│      PostgreSQL Database        │
│  - Host: postgres.todo-app.svc  │
│  - Port: 5432                   │
│  - Database: tododb             │
└─────────────────────────────────┘
```

**State Operations**:
- **Get**: Retrieve value by key
- **Set**: Save value with optional TTL and ETag
- **Delete**: Remove value
- **Bulk**: Operations on multiple keys

**Use Cases**:
- Task data caching (reduce DB queries)
- Conversation state (AI chat history)
- Rate limiting counters
- User session data

**Data Model**:
```sql
-- Dapr state table (auto-created)
CREATE TABLE dapr_state (
    key VARCHAR PRIMARY KEY,
    value JSONB NOT NULL,
    is_binary BOOLEAN DEFAULT FALSE,
    expiration_time TIMESTAMP
);

-- Dapr metadata table
CREATE TABLE dapr_metadata (
    key VARCHAR PRIMARY KEY,
    etag VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Secrets Management

**Purpose**: Secure secret retrieval without environment variables or code exposure.

**Architecture**:
```
┌─────────────────┐
│   Application   │
│                 │
│ ┌─────────────┐ │
│ │Secret Client│ │
│ └──────┬──────┘ │
│        │        │
│ ┌──────▼──────┐ │
│ │  Dapr       │ │
│ │  Sidecar    │ │
│ └──────┬──────┘ │
└─────────┼────────┘
          │
          ▼
┌─────────────────────────────────┐
│   Kubernetes Secret Store       │
│  - Type: secretstores.kubernetes│
│  - Namespace: todo-app          │
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│  Kubernetes Secrets (etcd)      │
│  - sendgrid-secret              │
│  - jwt-secret                   │
│  - postgres-credentials         │
└─────────────────────────────────┘
```

**Secret Access Flow**:
1. Application requests secret from Dapr sidecar
2. Dapr sidecar authenticates with Kubernetes API server
3. Retrieves secret from namespace (service account permissions)
4. Returns secret value to application
5. Application uses secret (never logs or exposes)

### 5. Bindings (Cron Jobs)

**Purpose**: Trigger periodic tasks without external cron services.

**Architecture**:
```
┌─────────────────────────────────┐
│  Dapr Cron Binding Component    │
│  - Type: bindings.cron          │
│  - Schedule: */1 * * * *        │
└──────────────┬──────────────────┘
               │
               │ trigger (every minute)
               ▼
┌─────────────────────────────────┐
│   Application Endpoint          │
│  POST /api/jobs/check-reminders │
│  - Queries DB for due reminders │
│  - Publishes events to Kafka    │
└─────────────────────────────────┘
```

**Configured Bindings**:
- `reminder-checker-cron`: Every minute
- `recurring-task-cron`: Every hour
- `daily-cleanup-cron`: Daily at 2 AM UTC

## Service Communication Patterns

### Synchronous Communication (Service Invocation)

**Use Case**: Request/response where immediate response needed.

**Example**: Backend queries recurring-task service for configuration.

```python
# todo-backend
response = await dapr_client.invoke_service(
    app_id="recurring-task-service",
    method="api/recurring/123",
    http_verb="GET"
)

# recurring-task-service
@app.get("/api/recurring/{task_id}")
async def get_recurring(task_id: str):
    return await get_recurring_config(task_id)
```

**Pattern**: Query, Command, Validation

### Asynchronous Communication (Pub/Sub)

**Use Case**: Fire-and-forget events, fan-out notifications.

**Example**: Task completion triggers notification and audit logging.

```python
# todo-backend (publisher)
await publisher.publish_task_event(
    event_type="task.completed",
    task_data={...},
    user_id="user-123"
)

# notification-service (subscriber)
@app.post("/task-events")
async def handle_task_event(request: Request):
    event = await request.json()
    if event["event_type"] == "task.completed":
        await send_notification(event)
    return {"status": "success"}

# audit-service (subscriber)
@app.post("/task-events")
async def handle_task_event(request: Request):
    event = await request.json()
    await audit_log.log(event)
    return {"status": "success"}
```

**Pattern**: Event, Notification, Async Processing

### Caching (State Store)

**Use Case**: Reduce database load, improve response times.

**Example**: Cache frequently accessed tasks.

```python
# Get task (with cache)
cached_task = await state_service.get_cached_task(task_id)
if cached_task:
    return cached_task

# Cache miss - query DB
task = await db.get_task(task_id)
await state_service.cache_task(task_id, task, ttl=3600)
return task

# Invalidate cache on update
await update_task(task_id, updates)
await state_service.invalidate_task_cache(task_id)
```

**Pattern**: Cache-Aside, Write-Through

## Data Flow Examples

### Example 1: Task Creation with Notification

```
User → Frontend → Backend → Database
 │                │          │
 │                ├→ Dapr Pub/Sub → Kafka
 │                │                   │
 │                │                   ├→ Notification Service → Email
 │                │                   │
 │                │                   └→ Audit Service → Audit Log
 │                │
 └─────────────────◄ Response ◄───────┘
```

**Steps**:
1. User creates task via UI
2. Frontend calls backend API
3. Backend saves to PostgreSQL
4. Backend publishes `task.created` event via Dapr
5. Notification service receives event, sends email
6. Audit service receives event, logs to audit DB
7. Backend returns response to frontend
8. Frontend shows task to user

### Example 2: Recurring Task Processing

```
Kafka → Recurring Task Service → Dapr Invoke → Backend → Database
                                   │                      │
                                   └──────────────┬────────┘
                                                  │
                                          Dapr Pub/Sub → Kafka
                                                  │
                                              Notification Service
```

**Steps**:
1. User completes recurring task
2. Backend publishes `task.completed` event
3. Recurring task service receives event
4. Service invokes backend via Dapr to:
   - Check if task is recurring
   - Create new task instance
   - Update next due date
5. Backend publishes `task.created` event for new task
6. Notification service sends reminder for new task

### Example 3: Reminder Processing with State

```
Cron Binding → Notification Service
                           │
                           ├→ Query Backend for Due Reminders
                           │          │
                           │          └→ Database
                           │
                           ├→ Check Dapr State (deduplication)
                           │
                           ├→ Send Notification
                           │
                           └→ Update Dapr State (tracking)
```

**Steps**:
1. Dapr cron triggers every minute
2. Notification service queries backend for due reminders
3. Service checks Dapr state for processing status
4. Sends notification (email/push/in-app)
5. Updates state to prevent duplicates

## Resiliency Patterns

### Retry Policy

```yaml
policies:
  retries:
    DefaultRetryPolicy:
      policy: constant
      duration: 1s
      maxRetries: 3
```

**Behavior**:
- Attempt 1: Immediate
- Failure: Wait 1s
- Attempt 2: Wait 1s
- Attempt 3: Wait 1s
- Final failure: Return error to application

### Circuit Breaker

```yaml
circuitBreakers:
  DefaultCircuitBreakerPolicy:
    maxRequests: 1
    timeout: 30s
    trip: consecutiveFailures > 5
```

**States**:
- **Closed**: Normal operation, requests pass through
- **Open**: 5 consecutive failures, requests fail immediately
- **Half-Open**: After timeout, allow one request to test

### Timeout Policy

```yaml
timeouts:
  DefaultTimeoutPolicy:
    timeout: 30s
```

**Behavior**:
- Request starts
- 30 second timer starts
- If no response within 30s, request cancelled
- Circuit breaker records failure

## Security Model

### mTLS (Mutual TLS)

All Dapr sidecar-to-sidecar communication encrypted with mTLS:

```yaml
# Enabled by default in Dapr
spec:
  mtls:
    enabled: true
    workloadCertTTL: 24h
```

### Service Access Control

Restrict which services can invoke which endpoints:

```yaml
accessControl:
  policies:
    - appId: todo-frontend
      operations:
        - name: "/api/*"
          httpVerb: ["GET", "POST", "PUT", "DELETE"]
          action: allow
```

### Secret Management

Secrets stored in Kubernetes, accessed via Dapr:

```bash
# Create secret
kubectl create secret generic sendgrid-secret \
  --from-literal=api-key=YOUR_KEY \
  -n todo-app

# Access via Dapr
curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/sendgrid-secret
```

## Scalability

### Horizontal Scaling

All services stateless (state in Dapr/DB), can scale horizontally:

```bash
# Scale backend to 5 replicas
kubectl scale deployment todo-backend --replicas=5 -n todo-app
```

**Consumer Groups**:
- Each service has unique consumer group
- Kafka partitions messages across group members
- Dapr handles partition assignment

### Load Balancing

Kubernetes Service provides load balancing:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
    - port: 80
      targetPort: 8000
```

Dapr sidecars use Kubernetes service discovery for service invocation.

## Monitoring and Observability

### Metrics Collection

```
Dapr Sidecar → Prometheus → Grafana
     │
     └→ /metrics endpoint (port 9090)
```

**Key Metrics**:
- Request rate, latency, error rate
- Circuit breaker state
- Pub/sub publish/consume rates
- State store operations

### Distributed Tracing

```
Service A → Dapr → Zipkin
     │              │
     └──────────────┘
        Trace Context
```

**Trace Flow**:
1. Service A generates trace ID
2. Dapr injects trace context into requests
3. All downstream services propagate context
4. Zipkin receives spans from all services
5. View full request trace in Zipkin UI

### Logging

```bash
# Application logs
kubectl logs -n todo-app <pod> -c backend

# Dapr sidecar logs
kubectl logs -n todo-app <pod> -c daprd
```

**Structured Logging** (JSON):
```json
{
  "level": "info",
  "msg": "Published event to task-events",
  "app_id": "todo-backend",
  "timestamp": "2024-01-01T00:00:00Z",
  "trace_id": "abc-123",
  "span_id": "def-456"
}
```

## Deployment Architecture

### Development

```
Local Machine
  ├── Docker Compose
  │   ├── Kafka
  │   └── PostgreSQL
  └── Dapr
      ├── todo-backend (dapr run)
      ├── notification-service (dapr run)
      └── recurring-task-service (dapr run)
```

### Production

```
Kubernetes Cluster (EKS/GKE/AKS)
  ├── Namespace: todo-app
  │   ├── Deployment: todo-frontend
  │   ├── Deployment: todo-backend
  │   ├── Deployment: notification-service
  │   ├── Deployment: recurring-task-service
  │   ├── StatefulSet: Kafka (Strimzi)
  │   └── StatefulSet: PostgreSQL (CloudSQL/RDS)
  └── Namespace: dapr-system
      ├── Deployment: dapr-sentry
      ├── Deployment: dapr-placement
      ├── Deployment: dapr-sidecar-injector
      └── Service: dapr-api
```

## Best Practices

### 1. Idempotent Event Handlers
```python
@app.post("/task-events")
async def handle_event(request: Request):
    event = await request.json()

    # Check if already processed
    if await was_processed(event["id"]):
        return {"status": "already_processed"}

    # Process event
    await process_event(event)

    # Mark as processed
    await mark_processed(event["id"])

    return {"status": "success"}
```

### 2. Graceful Shutdown
```python
@app.on_event("shutdown")
async def shutdown():
    # Close Dapr client
    await dapr_client.aclose()

    # Commit Kafka offsets
    await consumer.commit()

    # Close database connections
    await db.close()
```

### 3. Health Checks
```python
@app.get("/health/ready")
async def readiness():
    # Check Dapr connection
    dapr_healthy = await check_dapr()

    # Check database connection
    db_healthy = await check_db()

    return {
        "status": "ready" if all([dapr_healthy, db_healthy]) else "not_ready",
        "dapr": dapr_healthy,
        "db": db_healthy
    }
```

### 4. Resource Limits
```yaml
resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### 5. Liveness/Readiness Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

## References

- [Dapr Architecture](https://docs.dapr.io/concepts/)
- [Dapr Building Blocks](https://docs.dapr.io/developing-applications/building-blocks/)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)
- [Dapr Security](https://docs.dapr.io/operations/security/)
- [Dapr Observability](https://docs.dapr.io/operations/observability/)
