# Phase V: Cloud-Native Deployment & Advanced Features

**Status**: ✅ Complete (100%)

---

## Overview

Phase V extends the Todo application with advanced task features and cloud-native architecture using Dapr, Kafka, and event-driven microservices.

---

## Advanced Features

### Task Management
- **Recurring Tasks** - Daily, weekly, monthly, custom cron (croniter)
- **Due Dates & Reminders** - Schedule reminders with in-app, email, push notifications
- **Priorities** - LOW, MEDIUM, HIGH, URGENT with enum validation
- **Categories/Tags** - User-defined categories with hex color coding
- **Search & Filter** - Full-text keyword search, filter by priority/category/status/date range
- **Sort** - By due_date, priority, created_at, updated_at, title (asc/desc)

### Event-Driven Architecture (Dapr + Kafka)
- **3 Kafka Topics**: task-events, reminders, audit-logs
- **Dapr Pub/Sub** - Publish/subscribe via Dapr sidecar (no direct Kafka client)
- **Dapr State Store** - PostgreSQL-backed caching and notification state
- **Dapr Bindings** - 3 cron jobs (reminder checker, recurring processor, daily cleanup)
- **Dapr Secrets** - Kubernetes secret store integration
- **Dapr Service Invocation** - Inter-service HTTP calls via Dapr

### Microservices
- **Notification Service** (port 8001) - Processes reminders, delivers in-app/email/push
- **Recurring Task Service** (port 8002) - Spawns new task instances on schedule

### Resiliency
- Retry policies (constant, exponential, aggressive, conservative)
- Timeout policies (5s fast, 30s default, 120s long, 300s extended)
- Circuit breaker policies (3-10 failure thresholds)

### CI/CD
- GitHub Actions: lint, test, build Docker images, deploy to staging
- Multi-stage Docker builds for all services
- Codecov integration for coverage reporting

---

## Architecture

```
                    ┌─────────────┐
                    │   Frontend  │
                    │  (Next.js)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Backend   │◄──── Dapr Sidecar
                    │  (FastAPI)  │         │
                    └──────┬──────┘         │
                           │          ┌─────▼─────┐
                    ┌──────▼──────┐   │   Kafka   │
                    │    Neon     │   │  Pub/Sub  │
                    │ PostgreSQL  │   └─────┬─────┘
                    └─────────────┘         │
                                    ┌───────┴────────┐
                              ┌─────▼──────┐  ┌──────▼─────────┐
                              │Notification│  │Recurring Task  │
                              │  Service   │  │   Service      │
                              └────────────┘  └────────────────┘
```

---

## Directory Structure

```
phase-5/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── advanced_tasks.py       # Search, filter, sort, categories, recurring, reminders
│   │   │   └── dapr_subscriptions.py   # Event handlers for Dapr pub/sub
│   │   ├── events/
│   │   │   ├── event_schemas.py        # TaskEvent, ReminderEvent, AuditLogEvent
│   │   │   └── dapr_publisher.py       # Publish events via Dapr sidecar
│   │   ├── models/
│   │   │   ├── task.py                 # Extended task with priority, due_date
│   │   │   └── advanced_task.py        # RecurringTask, TaskReminder, TaskCategory
│   │   └── services/
│   │       ├── search_service.py       # Full-text search, multi-filter, sort
│   │       ├── reminder_service.py     # Reminder scheduling & Dapr pub/sub
│   │       ├── recurring_task_service.py # Cron-based recurring tasks
│   │       └── dapr_client.py          # Dapr HTTP API wrapper
│   └── migrations/
│       └── 002_advanced_features.py    # Schema for Phase V tables
├── dapr/
│   ├── config.yaml                     # Tracing, metrics, CORS, access control
│   └── components/
│       ├── pubsub-kafka.yaml           # Kafka pub/sub component
│       ├── statestore-postgres.yaml    # PostgreSQL state store
│       ├── bindings-cron.yaml          # 3 cron job bindings
│       ├── secret-store.yaml           # Kubernetes secrets
│       └── resiliency.yaml             # Retry, timeout, circuit breaker
├── services/
│   ├── notification-service/
│   │   ├── main.py                     # Standalone service
│   │   ├── main_dapr.py               # Dapr-integrated service
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── recurring-task-service/
│       ├── main.py                     # Standalone service
│       ├── main_dapr.py               # Dapr-integrated service
│       ├── Dockerfile
│       └── requirements.txt
├── k8s/cloud/                          # Production K8s manifests
│   ├── namespace.yaml
│   ├── backend-deployment.yaml         # 3 replicas, Dapr sidecar
│   ├── frontend-deployment.yaml
│   ├── notification-service-deployment.yaml
│   ├── recurring-task-service-deployment.yaml
│   ├── services.yaml
│   ├── ingress.yaml                    # TLS + cert-manager
│   ├── hpa.yaml                        # Horizontal Pod Autoscaler
│   └── kafka-strimzi.yaml              # Strimzi Kafka operator
├── .github/workflows/
│   ├── ci.yml                          # Lint, test, build, deploy
│   └── deploy.yml                      # Production deployment
└── docs/                               # Architecture documentation
    ├── CLOUD_DEPLOYMENT_GUIDE.md
    ├── DAPR_ARCHITECTURE.md
    └── DAPR_INTEGRATION_EXAMPLE.md
```

---

## Running Locally

### Prerequisites
- Dapr CLI installed (`dapr init`)
- Kafka running (or use Redis pub/sub for local dev)
- Neon PostgreSQL database

### Start Backend with Dapr
```bash
cd phase-5/backend
dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 \
  --resources-path ../dapr/components -- uvicorn src.main:app --port 8000
```

### Start Notification Service
```bash
cd phase-5/services/notification-service
dapr run --app-id notification-service --app-port 8001 --dapr-http-port 3501 \
  --resources-path ../../dapr/components -- uvicorn main_dapr:app --port 8001
```

### Start Recurring Task Service
```bash
cd phase-5/services/recurring-task-service
dapr run --app-id recurring-task-service --app-port 8002 --dapr-http-port 3502 \
  --resources-path ../../dapr/components -- uvicorn main_dapr:app --port 8002
```

---

## Cloud Deployment

For production deployment on AKS, GKE, or Oracle Cloud, see `docs/CLOUD_DEPLOYMENT_GUIDE.md`.

Key steps:
1. Deploy Strimzi Kafka operator (`k8s/cloud/kafka-strimzi.yaml`)
2. Install Dapr on cluster (`dapr init -k`)
3. Apply Dapr components (`dapr/components/`)
4. Deploy services (`k8s/cloud/`)
5. Configure ingress with TLS (`k8s/cloud/ingress.yaml`)
