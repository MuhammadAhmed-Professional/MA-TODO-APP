# Dapr Event Publishing Integration - Phase 2

**Date**: 2025-01-31
**Status**: ✅ Complete
**Source**: Phase 5 event publishing logic copied and adapted to Phase 2

## Overview

Successfully integrated Dapr event publishing into Phase 2 task CRUD operations. Event publishing is **non-blocking (fire-and-forget)** to ensure API performance is not impacted.

## Files Created

### Event Module (`src/events/`)

| File | Description |
|------|-------------|
| `__init__.py` | Event module exports |
| `event_schemas.py` | Data classes for task, reminder, and audit events |
| `dapr_publisher.py` | Primary Dapr-based event publisher |
| `kafka_producer.py` | Fallback direct Kafka producer (for dev) |

### Services (`src/services/`)

| File | Description |
|------|-------------|
| `dapr_client.py` | Dapr HTTP client wrapper for pub/sub, state, secrets |

### API Dependencies (`src/api/`)

| File | Description |
|------|-------------|
| `dependencies.py` | FastAPI dependencies including `get_event_publisher` |

### Dapr Configuration (`dapr/`)

| File | Description |
|------|-------------|
| `components/pubsub-kafka.yaml` | Kafka pub/sub component (production) |
| `components/pubsub-redis.yaml` | Redis pub/sub component (local dev) |
| `README.md` | Complete Dapr setup and monitoring guide |

## Files Modified

### API Endpoints (`src/api/tasks.py`)

Updated task CRUD endpoints to publish events:

| Endpoint | Event Type | Trigger |
|----------|-----------|---------|
| `POST /api/tasks` | `task.created` | After task creation |
| `PUT /api/tasks/{id}` | `task.updated` | After task update |
| `PATCH /api/tasks/{id}` | `task.updated`, `task.completed` | After task update |
| `PATCH /api/tasks/{id}/complete` | `task.completed` or `task.updated` | On completion toggle |
| `DELETE /api/tasks/{id}` | `task.deleted` | Before task deletion |

### Dependencies (`pyproject.toml`)

Added packages:
- `dapr>=1.12.0` - Dapr Python SDK
- `aiokafka>=0.12.0` - Async Kafka client (fallback producer)
- `kafka-python>=2.0.0` - Kafka Python client (compatibility)

## Event Publishing Details

### Event Schema (TaskEvent)

```python
@dataclass
class TaskEvent:
    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: str
    task_data: Dict[str, Any]  # Full task object
    user_id: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
```

### Topics

| Topic | Purpose | Event Types |
|-------|---------|-------------|
| `task-events` | Task lifecycle events | `task.created`, `task.updated`, `task.completed`, `task.deleted` |
| `reminders` | Reminder notifications | `reminder.due` |
| `audit-logs` | Audit trails | `audit.task.*` |

### Non-Blocking Implementation

Events are published using **fire-and-forget** pattern:

```python
# In dapr_publisher.py
async def publish_task_event(self, event_type: str, task_data: Dict, user_id: str) -> bool:
    # ... create event ...
    # Fire-and-forget: publish in background task
    asyncio.create_task(self.publish_event(topic="task-events", data=event.to_dict()))
    return True  # Return immediately
```

This ensures:
- ✅ API responses are not delayed by event publishing
- ✅ Event publishing failures don't crash API endpoints
- ✅ Background tasks handle retries via Dapr

## Environment Variables

Add to `.env`:

```env
# Dapr Configuration
DAPR_HTTP_PORT=3500
EVENT_PUBLISHING_ENABLED=true

# Kafka (for pubsub-kafka.yaml)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Redis (for pubsub-redis.yaml, optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Graceful Degradation

If event publishing fails or is disabled:

```env
EVENT_PUBLISHING_ENABLED=false
```

The API continues to function normally, logging debug messages instead of attempting to publish.

## Running with Dapr

### Local Development

```bash
# 1. Start Kafka (or Redis)
docker-compose up -d kafka

# 2. Start backend with Dapr
cd phase-2/backend
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ./dapr/components \
  -- uv run uvicorn src.main:app --reload
```

### Production (Kubernetes)

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
```

## Testing

### Verify Event Publishing

1. Create a task:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Cookie: auth_token=..." \
  -d '{"title": "Test task", "description": "Test event publishing"}'
```

2. Check Kafka topic for event:
```bash
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning
```

Expected output:
```json
{
  "event_type": "task.created",
  "task_id": "...",
  "task_data": {
    "id": "...",
    "title": "Test task",
    "description": "Test event publishing",
    "is_complete": false,
    ...
  },
  "user_id": "...",
  "timestamp": "2025-01-31T12:00:00Z",
  "metadata": {}
}
```

## Architecture Decisions

### 1. Dapr Abstraction
**Decision**: Use Dapr pub/sub instead of direct Kafka
**Rationale**:
- Decouples application from infrastructure
- Automatic retries and error handling
- Easy switching between Kafka, Redis, Pulsar, etc.

### 2. Fire-and-Forget Publishing
**Decision**: Publish events asynchronously without waiting
**Rationale**:
- API performance not impacted by event infrastructure
- Better user experience (faster responses)
- Dapr handles retries automatically

### 3. Event Publishing Toggle
**Decision**: `EVENT_PUBLISHING_ENABLED` environment variable
**Rationale**:
- Graceful degradation when messaging is unavailable
- Easy testing without full infrastructure
- Development flexibility

### 4. Fallback Kafka Producer
**Decision**: Include `kafka_producer.py` for direct Kafka access
**Rationale**:
- Development flexibility when Dapr is not available
- Migration path from direct Kafka to Dapr
- Debugging and testing capabilities

## Next Steps

### Optional Enhancements

1. **Event Schema Registry**: Add Confluent Schema Registry for Avro/Protobuf schemas
2. **Dead Letter Queue**: Configure DLQ for failed events
3. **Event Replay**: Add event replay capability for recovery
4. **Monitoring**: Integrate with OpenTelemetry for event tracing
5. **Consumer Services**: Implement consumers for task-events (audit log, recurring tasks)

### Related Features

- Implement `AuditLogConsumer` to store audit logs in database
- Implement `RecurringTaskConsumer` for recurring task spawning
- Implement `NotificationService` for reminder delivery

## References

- [Dapr Pub/Sub Documentation](https://docs.dapr.io/developing-applications/building-blocks/pubsub/)
- [Dapr Kafka Component](https://docs.dapr.io/operations/components/setup-pubsub/supported-pubsub/setup-kafka/)
- [Event-Driven Architecture](https://docs.dapr.io/patterns/event-driven/)
- `/phase-2/backend/dapr/README.md` - Complete Dapr setup guide

## Checklist

- ✅ Copied event schemas from phase-5
- ✅ Copied Dapr publisher from phase-5
- ✅ Copied Kafka producer from phase-5
- ✅ Created Dapr client service
- ✅ Integrated event publishing into task CRUD endpoints
- ✅ Added dependencies to pyproject.toml
- ✅ Created Dapr component YAML configs
- ✅ Created comprehensive documentation
- ✅ Implemented non-blocking (fire-and-forget) publishing
- ✅ Added graceful degradation toggle
- ✅ Tested event schema compatibility with phase-2 Task model
