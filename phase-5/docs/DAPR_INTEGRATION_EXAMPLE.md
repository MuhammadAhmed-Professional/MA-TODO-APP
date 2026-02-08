# Dapr Integration Example - Main Backend Application

This example shows how to integrate the new Dapr components into the main backend FastAPI application.

## File: `backend/src/main.py` (Updated with Dapr)

```python
"""
Main FastAPI Application with Dapr Integration

Todo API with Dapr pub/sub, state management, and service invocation.
"""

import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from sqlmodel import Session, select

from src.api.advanced_tasks import router as advanced_tasks_router
from src.api.dapr_subscriptions import router as dapr_router  # NEW: Dapr subscriptions
from src.api.tasks import router as tasks_router
from src.db.session import get_session
from src.events.dapr_publisher import get_event_publisher, shutdown_event_publisher  # NEW: Dapr publisher
from src.models.task import Task, TaskCreate, TaskResponse
from src.services.dapr_client import shutdown_dapr_client  # NEW: Dapr client
from src.services.state_service import get_state_service  # NEW: State service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ================== LIFECYCLE MANAGEMENT ==================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for:
    - Dapr client initialization
    - Event publisher startup
    - State service warmup
    """
    # Startup
    logger.info("Starting Todo API with Dapr integration...")

    # Warm up state service (optional)
    try:
        state_service = await get_state_service()
        logger.info("State service initialized")
    except Exception as e:
        logger.warning(f"State service initialization failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Todo API...")

    # Shutdown Dapr client
    await shutdown_dapr_client()
    logger.info("Dapr client shutdown")

    # Shutdown event publisher
    await shutdown_event_publisher()
    logger.info("Event publisher shutdown")


# Create FastAPI app
app = FastAPI(
    title="Todo API with Dapr",
    description="Task management API with Dapr integration",
    version="5.0.0",
    lifespan=lifespan,
)


# ================== ROUTERS ==================

# Include API routers
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
app.include_router(advanced_tasks_router, prefix="/api/advanced", tags=["advanced"])
app.include_router(dapr_router, tags=["dapr"])  # NEW: Dapr subscription endpoints


# ================== HEALTH ENDPOINTS ==================

@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness probe."""
    return {
        "status": "healthy",
        "service": "todo-backend",
        "version": "5.0.0",
        "dapr_enabled": True
    }


@app.get("/health/ready")
async def readiness():
    """
    Readiness check endpoint for Kubernetes readiness probe.

    Checks database and Dapr sidecar connectivity.
    """
    # Check database connection
    try:
        from src.db.session import engine
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False

    # Check Dapr sidecar
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3500/v1.0/healthz", timeout=2.0)
            dapr_healthy = response.status_code == 200
    except Exception as e:
        logger.warning(f"Dapr health check failed: {e}")
        dapr_healthy = False

    return {
        "status": "ready" if all([db_healthy, dapr_healthy]) else "not_ready",
        "database": db_healthy,
        "dapr": dapr_healthy,
    }


# ================== EXAMPLE: TASK CREATION WITH DAPR ==================

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    user_id: str,
    session: Session = Depends(get_session),
) -> Task:
    """
    Create a new task with Dapr integration.

    This endpoint demonstrates:
    1. Database transaction
    2. Event publishing via Dapr pub/sub
    3. State caching via Dapr state store
    """
    # Create task in database
    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish event via Dapr pub/sub
    try:
        publisher = await get_event_publisher()
        await publisher.publish_task_event(
            event_type="task.created",
            task_data={
                "id": str(db_task.id),
                "title": db_task.title,
                "description": db_task.description,
                "is_complete": db_task.is_complete,
                "created_at": db_task.created_at.isoformat(),
            },
            user_id=user_id,
        )
        logger.info(f"Published task.created event for task {db_task.id}")
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        # Don't fail request if event publishing fails

    # Cache in Dapr state store (optional, for performance)
    try:
        state_service = await get_state_service()
        await state_service.cache_task(
            task_id=str(db_task.id),
            task_data={
                "id": str(db_task.id),
                "title": db_task.title,
                "description": db_task.description,
                "is_complete": db_task.is_complete,
            },
            ttl=3600,  # 1 hour
        )
        logger.debug(f"Cached task {db_task.id} in state store")
    except Exception as e:
        logger.warning(f"Failed to cache task: {e}")

    return db_task


# ================== EXAMPLE: TASK RETRIEVAL WITH CACHE ==================

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str,
    session: Session = Depends(get_session),
) -> Task:
    """
    Get a task by ID with caching.

    This endpoint demonstrates:
    1. Check Dapr state store first (cache)
    2. Fall back to database if cache miss
    3. Update cache on database hit
    """
    # Try cache first
    state_service = await get_state_service()
    cached_task = await state_service.get_cached_task(task_id)

    if cached_task:
        logger.debug(f"Cache hit for task {task_id}")
        # Convert cached dict to Task model
        return Task(
            id=cached_task["id"],
            title=cached_task["title"],
            description=cached_task.get("description"),
            is_complete=cached_task["is_complete"],
            user_id=user_id,  # From context
            created_at=cached_task.get("created_at"),
            updated_at=cached_task.get("updated_at"),
        )

    # Cache miss - query database
    logger.debug(f"Cache miss for task {task_id}, querying database")
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update cache
    await state_service.cache_task(
        task_id=task_id,
        task_data={
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete,
        },
        ttl=3600,
    )

    return task


# ================== EXAMPLE: TASK UPDATE WITH INVALIDATION ==================

@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    updates: dict,
    user_id: str,
    session: Session = Depends(get_session),
) -> Task:
    """
    Update a task with cache invalidation.

    This endpoint demonstrates:
    1. Database update
    2. Cache invalidation
    3. Event publishing for update
    """
    # Get task
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    for field, value in updates.items():
        if hasattr(task, field):
            setattr(task, field, value)

    session.commit()
    session.refresh(task)

    # Invalidate cache
    state_service = await get_state_service()
    await state_service.invalidate_task_cache(task_id)
    logger.debug(f"Invalidated cache for task {task_id}")

    # Publish update event
    publisher = await get_event_publisher()
    await publisher.publish_task_event(
        event_type="task.updated",
        task_data={
            "id": str(task.id),
            "title": task.title,
            "updates": updates,
        },
        user_id=user_id,
    )

    return task


# ================== EXAMPLE: SERVICE INVOCATION ==================

@app.post("/api/tasks/{task_id}/remind")
async def set_reminder(
    task_id: str,
    remind_at: str,
    notification_type: str = "email",
    user_id: str = None,
    session: Session = Depends(get_session),
):
    """
    Set a reminder for a task using service invocation.

    This endpoint demonstrates:
    1. Calling notification service via Dapr
    2. Service-to-service communication with retries
    """
    # Verify task exists
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Call notification service via Dapr service invocation
    from src.services.dapr_client import get_dapr_client

    dapr_client = await get_dapr_client()

    response = await dapr_client.invoke_service(
        app_id="notification-service",
        method="api/reminders/schedule",
        http_verb="POST",
        data={
            "task_id": task_id,
            "task_title": task.title,
            "user_id": user_id,
            "remind_at": remind_at,
            "notification_type": notification_type,
        },
    )

    if response:
        return {
            "status": "scheduled",
            "task_id": task_id,
            "remind_at": remind_at,
            "notification_type": notification_type,
        }
    else:
        raise HTTPException(
            status_code=503,
            detail="Failed to schedule reminder (service unavailable)"
        )


# ================== EXAMPLE: RATE LIMITING ==================

@app.post("/api/tasks/bulk")
async def create_tasks_bulk(
    tasks: List[TaskCreate],
    user_id: str,
    session: Session = Depends(get_session),
) -> dict:
    """
    Create multiple tasks with rate limiting.

    This endpoint demonstrates:
    1. Rate limiting using Dapr state store
    2. Bulk operations
    """
    # Check rate limit (100 tasks per hour per user)
    state_service = await get_state_service()

    allowed = await state_service.check_rate_limit(
        key=f"bulk_create:{user_id}",
        limit=100,
        window_seconds=3600,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded: max 100 bulk tasks per hour"
        )

    # Create tasks
    created_tasks = []
    for task_data in tasks:
        db_task = Task.from_orm(task_data)
        db_task.user_id = user_id
        session.add(db_task)
        created_tasks.append(db_task)

    session.commit()

    # Publish bulk event
    publisher = await get_event_publisher()
    await publisher.publish_event(
        topic="task-events",
        data={
            "event_type": "tasks.bulk_created",
            "task_ids": [str(t.id) for t in created_tasks],
            "user_id": user_id,
            "count": len(created_tasks),
        },
    )

    return {
        "created": len(created_tasks),
        "tasks": [TaskResponse.from_orm(t) for t in created_tasks],
    }


# ================== ROOT ENDPOINTS ==================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Todo API with Dapr",
        "version": "5.0.0",
        "docs": "/docs",
        "health": "/health",
        "dapr_subscriptions": "/dapr/subscribe",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
```

## Configuration Files

### File: `backend/pyproject.toml` (Dependencies)

```toml
[project]
name = "todo-backend"
version = "5.0.0"
description = "Todo API with Dapr integration"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.29.0",
    "sqlmodel>=0.0.18",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "httpx>=0.27.0",  # HTTP client for Dapr API
    "psycopg2-binary>=2.9.9",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.9",
    "croniter>=2.0.0",  # For recurring tasks
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.27.0",
    "ruff>=0.1.0",
]
```

### File: `backend/.env.example`

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tododb

# Dapr Configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
APP_ID=todo-backend

# JWT Secret (in production, use Dapr secret store)
JWT_SECRET=your-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,https://todo-app.example.com

# Logging
LOG_LEVEL=info

# Environment
ENVIRONMENT=development
```

## Kubernetes Deployment

### File: `k8s/cloud/backend-deployment.yaml` (Existing - Already Has Dapr Annotations)

The existing deployment already has Dapr sidecar annotations:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        # Dapr sidecar annotations (ALREADY CONFIGURED)
        dapr.io/enabled: "true"
        dapr.io/app-id: "todo-backend"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/log-level: "info"
        dapr.io/config: "dapr-config"
    spec:
      containers:
        - name: backend
          image: ghcr.io/demolinator/todo-backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-credentials
                  key: connectionString
```

## Testing the Integration

### 1. Start Services Locally

```bash
# Terminal 1: Backend with Dapr
cd phase-5/backend
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --config ../dapr/config.yaml \
  --components-path ../dapr/components \
  -- uvicorn src.main:app

# Terminal 2: Notification Service with Dapr
cd phase-5/services/notification-service
dapr run \
  --app-id notification-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --config ../../dapr/config.yaml \
  -- python main_dapr.py
```

### 2. Test Task Creation

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task with Dapr",
    "description": "Testing Dapr integration",
    "user_id": "user-123"
  }'
```

**Expected Behavior**:
1. Task created in PostgreSQL database
2. Event published to Kafka via Dapr
3. Task cached in Dapr state store
4. Notification service receives event (if subscribed)

### 3. Verify Event Received

Check notification service logs for received event.

### 4. Test Cache

```bash
# First call - cache miss, queries DB
curl http://localhost:8000/api/tasks/{task_id}?user_id=user-123

# Second call - cache hit, returns from state store
curl http://localhost:8000/api/tasks/{task_id}?user_id=user-123
```

### 5. Check Dapr Metrics

```bash
curl http://localhost:3500/v1.0/metrics
```

## Monitoring

### View Dapr Logs

```bash
# Local development
dapr logs --app-id todo-backend

# Kubernetes
kubectl logs -n todo-app <pod-name> -c daprd
```

### Check Health

```bash
# Local
curl http://localhost:8000/health
curl http://localhost:8000/health/ready

# Kubernetes
kubectl exec -n todo-app <pod-name> -c backend -- curl http://localhost:8000/health
```

### Verify Subscriptions

```bash
curl http://localhost:8000/dapr/subscribe
```

Should return:
```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/dapr/task-events"
  }
]
```

## Troubleshooting

### Issue: Events Not Published

**Check**:
1. Dapr sidecar is running: `dapr list`
2. Kafka is accessible: `kubectl get svc -n todo-app kafka-kafka-bootstrap`
3. Pub/sub component exists: `kubectl get component kafka-pubsub -n todo-app`

**Fix**:
```bash
# Restart with verbose logging
dapr run --app-id todo-backend --log-level debug -- uvicorn src.main:app
```

### Issue: Cache Not Working

**Check**:
1. State store component exists: `kubectl get component postgres-statestore -n todo-app`
2. PostgreSQL connection string correct in secret

**Fix**:
```bash
# Test state store directly
curl http://localhost:3500/v1.0/state/postgres-statestore/test-key \
  -X POST \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":{"test":"data"}}]'

# Verify
curl http://localhost:3500/v1.0/state/postgres-statestore/test-key
```

### Issue: Service Invocation Failing

**Check**:
1. Target service is running: `dapr list`
2. Target service app-id matches invocation call
3. Network connectivity between services

**Fix**:
```bash
# Test direct HTTP call to verify service reachable
curl http://localhost:8001/api/notify

# Then test via Dapr
curl -X POST http://localhost:3500/v1.0/invoke/notification-service/method/api/notify \
  -H "Content-Type: application/json" \
  -d '{"task_id":"123"}'
```

## Next Steps

1. **Add End-to-End Tests**: Test complete flows with Dapr
2. **Set Up Distributed Tracing**: Configure Zipkin/Jaeger
3. **Configure Prometheus Metrics**: Set up Grafana dashboards
4. **Add More Dapr Features**: Actors, Workflow, bindings
5. **Production Hardening**: mTLS, access control, secret policies
