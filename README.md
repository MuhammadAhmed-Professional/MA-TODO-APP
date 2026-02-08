# MA-TODO-APP - The Evolution of Todo

**Hackathon II: Mastering Spec-Driven Development & Cloud Native AI**

[![Live App](https://img.shields.io/badge/Live_App-Vercel-black)](https://frontend-six-coral-90.vercel.app)
[![Backend API](https://img.shields.io/badge/API-Railway-purple)](https://backend-production-9a40.up.railway.app/docs)
[![Auth Server](https://img.shields.io/badge/Auth-Railway-green)](https://auth-server-production-cd0e.up.railway.app/health)
[![GitHub](https://img.shields.io/badge/GitHub-MA--TODO--APP-blue)](https://github.com/MuhammadAhmed-Professional/MA-TODO-APP)

---

## Live Deployment

| Service | URL |
|---------|-----|
| **Frontend** | [https://frontend-six-coral-90.vercel.app](https://frontend-six-coral-90.vercel.app) |
| **Backend API** | [https://backend-production-9a40.up.railway.app](https://backend-production-9a40.up.railway.app) |
| **Auth Server** | [https://auth-server-production-cd0e.up.railway.app](https://auth-server-production-cd0e.up.railway.app) |
| **API Docs** | [https://backend-production-9a40.up.railway.app/docs](https://backend-production-9a40.up.railway.app/docs) |

---

## Project Overview

A full-stack Todo application that evolves across **5 phases** from a simple CLI to a cloud-native, AI-powered platform with event-driven architecture.

```
Phase I    ──►  Phase II    ──►  Phase III   ──►  Phase IV    ──►  Phase V
CLI App         Web App          AI Chatbot       Kubernetes       Cloud + Dapr
(Python)        (Next.js +       (MCP + OpenAI    (Docker +        (Kafka +
                 FastAPI)         Agents SDK)      Helm)            Microservices)
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 16)                       │
│         https://frontend-six-coral-90.vercel.app             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Dashboard  │  Chat (AI)  │  Voice  │  Urdu/English   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼───────────────────────────────────────┐
│                Backend (FastAPI 0.120+)                       │
│      https://backend-production-9a40.up.railway.app          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ Tasks API│  │ Chat API │  │ Auth API │  │ MCP Server │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└──────────────────────┬───────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Neon         │ │ Auth     │ │ Dapr Sidecar │
│ PostgreSQL   │ │ Server   │ │ (Kafka,      │
│              │ │ (Better  │ │  State Store,│
│              │ │  Auth)   │ │  Pub/Sub)    │
└──────────────┘ └──────────┘ └──────────────┘
```

---

## Phase Details

### Phase I: Console App (100/100 pts)

Python CLI Todo app with in-memory storage.

- **5 features**: Add, View, Update, Delete, Mark Complete
- **87 tests** passing (100% pass rate)
- **Architecture**: Layered (UI -> Operations -> Storage)
- **Tech**: Python 3.13+, UV, pytest

**Run**: `cd phase-1 && uv sync && uv run python -m src.todo_app.main`

---

### Phase II: Full-Stack Web App (150/150 pts)

Modern web application with authentication and real-time task management.

- **Frontend**: Next.js 16.0.10, React 19, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI 0.120+, SQLModel, Alembic migrations
- **Database**: Neon Serverless PostgreSQL
- **Auth**: Better Auth (JWT + HttpOnly cookies)
- **API**: Full RESTful CRUD (7 endpoints)
- **Deployed**: Vercel (frontend) + Railway (backend + auth server)

**Run locally**:
```bash
# Backend
cd phase-2/backend && uv sync && uv run uvicorn src.main:app --reload --port 8000

# Auth Server
cd phase-2/auth-server && npm install && npm run dev

# Frontend
cd phase-2/frontend && pnpm install && pnpm dev
```

---

### Phase III: AI Chatbot (200/200 pts)

Natural language task management via AI chatbot with MCP tools.

- **OpenAI Agents SDK** with Gemini model rotation (4 models)
- **Official MCP SDK** (`mcp>=1.24.0`) with stdio transport
- **5 MCP Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **6 Chat endpoints** with conversation history
- **Conversation state** persisted in PostgreSQL
- **Stateless server** design (no in-memory state)
- **Chat UI** with Vercel AI SDK

**Bonus**: Voice input/output (Web Speech API), Multi-language (English + Urdu)

---

### Phase IV: Kubernetes Deployment (250/250 pts)

Containerized deployment with Helm charts and AI-powered K8s tools.

- **3 Dockerfiles** (multi-stage, non-root, health checks)
- **Docker Compose** for local development
- **10 Kubernetes manifests** (deployments, services, ingress, secrets)
- **Helm chart** (Chart.yaml + values.yaml + 11 templates)
- **Minikube** automated setup script
- **kubectl-ai** for natural language K8s operations
- **kagent** for cluster analysis and optimization
- **Gordon** (Docker AI) for Dockerfile generation

**Deploy**: `cd phase-4 && ./scripts/minikube-setup.sh`

---

### Phase V: Cloud-Native + Dapr (300/300 pts)

Event-driven microservices architecture with Dapr and Kafka.

- **Advanced features**: Recurring tasks, due dates, reminders, priorities, categories, search, filter, sort
- **Kafka event publishing** (3 topics: task-events, reminders, audit-logs)
- **Dapr integration** (all 5 building blocks):
  - Pub/Sub (Kafka)
  - State Store (PostgreSQL)
  - Bindings (Cron for recurring tasks)
  - Secrets Management
  - Service Invocation
- **2 Microservices**: Notification service, Recurring task service
- **Resiliency policies**: Retry, timeout, circuit breaker
- **Cloud K8s manifests** (AKS/GKE/Oracle ready)
- **CI/CD** GitHub Actions (lint, test, build, deploy)

---

## Bonus Features (+700 pts)

| Bonus | Points | Description |
|-------|--------|-------------|
| Reusable Intelligence | +200 | 20 skills + 12 specialized agents in `.claude/` |
| Cloud-Native Blueprints | +200 | Helm charts, K8s manifests, Dapr components |
| Multi-language (Urdu) | +100 | Full Urdu translation (157 keys) + RTL support |
| Voice Commands | +200 | Speech recognition + synthesis (Web Speech API) |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript 5, Tailwind CSS, shadcn/ui |
| Backend | FastAPI 0.120+, Python 3.13+, SQLModel, Alembic |
| Database | Neon Serverless PostgreSQL |
| Auth | Better Auth, JWT (HttpOnly cookies) |
| AI | OpenAI Agents SDK, Gemini, Official MCP SDK |
| Voice | Web Speech API (Recognition + Synthesis) |
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes, Helm, Minikube |
| Events | Kafka (via Dapr Pub/Sub) |
| Microservices | Dapr (State, Bindings, Secrets, Service Invocation) |
| CI/CD | GitHub Actions |
| Hosting | Vercel (frontend), Railway (backend + auth server) |

---

## Project Structure

```
MA-TODO-APP/
├── phase-1/                    # Phase I: CLI Todo App
│   ├── src/todo_app/           # Source code (6 modules)
│   └── tests/                  # 87 tests
├── phase-2/                    # Phase II + III: Full-Stack + Chatbot
│   ├── frontend/               # Next.js 16 (App Router)
│   ├── backend/                # FastAPI + MCP Server + Chat API
│   └── auth-server/            # Better Auth (Express)
├── phase-4/                    # Phase IV: Kubernetes
│   ├── docker/                 # 3 Dockerfiles
│   ├── k8s/                    # 10 K8s manifests
│   ├── helm/                   # Helm chart (11 templates)
│   └── scripts/                # Automation scripts
├── phase-5/                    # Phase V: Cloud + Dapr
│   ├── backend/                # Advanced features + events
│   ├── dapr/                   # 5 Dapr components + config
│   ├── services/               # 2 microservices
│   ├── k8s/cloud/              # 9 cloud K8s manifests
│   └── .github/workflows/      # CI/CD pipelines
├── specs/                      # Specifications (SDD)
├── .claude/                    # 20 skills + 12 agents
├── .specify/                   # Constitution v3.1.0
├── CLAUDE.md                   # Root governance
├── AGENTS.md                   # Agent guidelines
└── HACKATHON_STATUS.md         # Completion report
```

---

## Getting Started

### Prerequisites

- Python 3.13+ and [UV](https://docs.astral.sh/uv/)
- Node.js 20+ and [pnpm](https://pnpm.io/)
- Docker Desktop (for Phase IV)

### Quick Start

```bash
# Clone
git clone https://github.com/MuhammadAhmed-Professional/MA-TODO-APP.git
cd MA-TODO-APP

# Phase I
cd phase-1 && uv sync && uv run python -m src.todo_app.main

# Phase II Backend
cd phase-2/backend && cp .env.example .env && uv sync && uv run uvicorn src.main:app --reload

# Phase II Auth Server
cd phase-2/auth-server && cp .env.example .env && npm install && npm run dev

# Phase II Frontend
cd phase-2/frontend && cp .env.local.example .env.local && pnpm install && pnpm dev
```

---

## Estimated Score: ~1550/1600 (97%)

| Phase | Score | Max |
|-------|-------|-----|
| Phase I | 100 | 100 |
| Phase II | 150 | 150 |
| Phase III | 200 | 200 |
| Phase IV | 250 | 250 |
| Phase V | 300 | 300 |
| Bonus | 550 | 600 |
| **Total** | **~1550** | **1600** |

---

**Author**: Muhammad Ahmed | **Repository**: [github.com/MuhammadAhmed-Professional/MA-TODO-APP](https://github.com/MuhammadAhmed-Professional/MA-TODO-APP)
