# Dapr Configuration

This directory contains Dapr component configurations for event publishing and state management.

## Components

### Pub/Sub (Event Publishing)

#### Kafka (Production)
- **File**: `components/pubsub-kafka.yaml`
- **Component Name**: `kafka-pubsub`
- **Usage**: Primary pub/sub component for production deployments
- **Topics**:
  - `task-events`: Task lifecycle events (created, updated, completed, deleted)
  - `reminders`: Reminder notification events
  - `audit-logs`: Audit log events

#### Redis (Local Development)
- **File**: `components/pubsub-redis.yaml`
- **Component Name**: `redis-pubsub`
- **Usage**: Fallback for local development when Kafka is not available

## Environment Variables

Configure these in your `.env` file:

```env
# Dapr Configuration
DAPR_HTTP_PORT=3500
EVENT_PUBLISHING_ENABLED=true

# Kafka Configuration (for pubsub-kafka.yaml)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis Configuration (for pubsub-redis.yaml, optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Running with Dapr

### Development (Local)

1. Start Kafka (or Redis for local dev):
```bash
# Using Docker Compose
docker-compose up -d kafka redis

# Or individual services
docker run -d -p 9092:9092 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  confluentinc/cp-kafka:latest
```

2. Start the backend with Dapr:
```bash
# From phase-2/backend directory
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ./dapr/components \
  -- uv run uvicorn src.main:app --reload
```

### Production (Kubernetes)

Deploy with Dapr sidecar:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/config: "production"
    spec:
      containers:
      - name: backend
        image: your-registry/todo-backend:latest
        env:
        - name: EVENT_PUBLISHING_ENABLED
          value: "true"
        - name: DAPR_HTTP_PORT
          value: "3500"
```

## Topics

### task-events
Task lifecycle events published when tasks are created, updated, completed, or deleted.

**Event Types**:
- `task.created`: Published when a new task is created
- `task.updated`: Published when a task is updated (any field change)
- `task.completed`: Published when a task is marked as complete
- `task.deleted`: Published when a task is deleted

**Event Schema** (TaskEvent):
```json
{
  "event_type": "task.created",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Write comprehensive README",
    "is_complete": false,
    "priority": 2,
    "due_date": "2025-12-31T23:59:59Z",
    "user_id": "450e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-01-31T12:00:00Z",
    "updated_at": "2025-01-31T12:00:00Z"
  },
  "user_id": "450e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-31T12:00:00Z",
  "metadata": {}
}
```

**Consumers**:
- RecurringTaskConsumer: Spawns next recurring task instance when parent is completed
- AuditLogConsumer: Logs all task operations for compliance

### reminders
Reminder notification events published when a reminder is due.

**Event Schema** (ReminderEvent):
```json
{
  "reminder_id": "650e8400-e29b-41d4-a716-446655440002",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_title": "Submit quarterly report",
  "user_id": "450e8400-e29b-41d4-a716-446655440000",
  "remind_at": "2025-01-31T09:00:00Z",
  "notification_type": "email",
  "timestamp": "2025-01-31T09:00:00Z",
  "metadata": {}
}
```

**Consumers**:
- NotificationService: Delivers notifications via email, push, or in-app

### audit-logs
Audit log events for compliance and debugging.

**Event Schema** (AuditLogEvent):
```json
{
  "event_type": "audit.task.created",
  "resource_type": "task",
  "resource_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "450e8400-e29b-41d4-a716-446655440000",
  "action": "created",
  "timestamp": "2025-01-31T12:00:00Z",
  "changes": {
    "before": null,
    "after": {
      "title": "Complete project documentation"
    }
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

**Consumers**:
- AuditLogConsumer: Stores audit logs in database for compliance reporting

## Monitoring

### Check Dapr Sidecar Health
```bash
curl http://localhost:3500/v1.0/healthz
```

### List Published Events (Dapr Logs)
```bash
dapr logs --app-id todo-backend
```

### Monitor Kafka Topics
```bash
# List topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Consume events from task-events topic
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

## Troubleshooting

### Events Not Published

1. Check if Dapr is running:
```bash
curl http://localhost:3500/v1.0/healthz
```

2. Verify event publishing is enabled:
```bash
grep EVENT_PUBLISHING_ENABLED .env
# Should be: EVENT_PUBLISHING_ENABLED=true
```

3. Check Kafka is accessible:
```bash
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

4. Review Dapr logs for errors:
```bash
dapr logs --app-id todo-backend --level error
```

### Event Publishing Disabled

To temporarily disable event publishing (graceful degradation):
```env
EVENT_PUBLISHING_ENABLED=false
```

This allows the API to function normally without attempting to publish events.

## References

- [Dapr Pub/Sub Overview](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Dapr Kafka Binding](https://docs.dapr.io/operations/components/setup-pubsub/supported-pubsub/setup-kafka/)
- [Event-Driven Architecture Pattern](https://docs.dapr.io/patterns/event-driven/)
