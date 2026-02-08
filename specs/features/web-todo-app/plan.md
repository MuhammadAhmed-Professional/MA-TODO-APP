# Implementation Plan: Phase II Full-Stack Web Application

**Branch**: `004-phase-2-web-app` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-phase-2-web-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a complete full-stack web application for todo task management with user authentication, CRUD operations, responsive UI, and comprehensive API documentation. The application follows a clean architecture with Next.js 16+ frontend (App Router, React Server Components), FastAPI backend (SQLModel ORM), and Neon Serverless PostgreSQL database. Authentication uses Better Auth with JWT tokens stored in HttpOnly cookies for stateless, secure session management. The system implements all 5 CRUD operations (create, read, update, delete, mark complete) with proper authorization ensuring users can only access their own tasks. Testing strategy includes unit tests (vitest for frontend, pytest for backend), integration tests for API endpoints, and E2E tests with Playwright for critical user flows. Deployment targets Vercel for frontend, Railway/Render for backend, with Neon handling database hosting.

## Technical Context

**Language/Version**:
- **Backend**: Python 3.13+ (FastAPI 0.110+, SQLModel, Pydantic v2)
- **Frontend**: TypeScript 5+ in strict mode (Next.js 16+ with App Router, React 19+)

**Primary Dependencies**:
- **Backend**: FastAPI (REST API), SQLModel (ORM), Alembic (migrations), Better Auth SDK (auth provider integration), python-jose or PyJWT (JWT), bcrypt/argon2 (password hashing), httpx (testing)
- **Frontend**: Next.js 16+ (framework), React 19+ (UI), Tailwind CSS 4+ (styling), shadcn/ui (component library), Better Auth client (auth integration), React Hook Form (forms), Zod (validation)
- **Dev Tools**: UV (Python package manager), pnpm (Node.js package manager), ESLint + Prettier (linting), ruff (Python linting), Vitest + React Testing Library (frontend tests), pytest (backend tests), Playwright (E2E tests)

**Storage**:
- **Database**: Neon Serverless PostgreSQL (production and staging)
- **Test Database**: SQLite in-memory for backend unit tests, Neon test instance for integration tests
- **Session Storage**: HttpOnly cookies (client-side, secure)

**Testing**:
- **Unit**: pytest (backend), vitest + React Testing Library (frontend)
- **Integration**: pytest with FastAPI TestClient (API endpoints), Neon test database (database operations)
- **E2E**: Playwright (critical user flows: signup, login, CRUD operations)
- **Coverage Target**: 80% overall (90% for auth and CRUD critical paths)

**Target Platform**:
- **Frontend**: Web browsers (Chrome, Firefox, Safari, Edge latest versions), responsive for mobile (320px+), tablet (768px+), desktop (1024px+)
- **Backend**: Linux server environment (Railway/Render with Python 3.13 runtime)
- **Database**: Neon Serverless PostgreSQL (cloud-hosted, serverless pooling)

**Project Type**: Web application (full-stack monorepo with frontend/ and backend/ directories)

**Performance Goals**:
- **API Latency**: <200ms p95 for all endpoints
- **Page Load**: First Contentful Paint <1.5s, Time to Interactive <3s
- **Task Creation**: <3s from save click to list update
- **Signup Flow**: <60s from landing to authenticated dashboard
- **Concurrent Users**: 500 users without degradation

**Constraints**:
- **API Response Time**: <200ms p95 latency
- **Database Connections**: Neon serverless pooling (auto-scaling)
- **Authentication**: JWT token expiration 15 minutes, refresh tokens 7 days
- **Security**: WCAG 2.1 AA compliance, zero high/critical vulnerabilities (CVSS 7.0+)
- **Browser Support**: Latest Chrome, Firefox, Safari, Edge (no IE support)

**Scale/Scope**:
- **Initial Users**: 500 concurrent users
- **Database**: ~100K tasks, ~10K users (expected first year)
- **API Endpoints**: ~15 endpoints (auth + CRUD + docs)
- **Frontend Pages**: ~8 pages (landing, signup, login, dashboard, task list, task detail, profile, settings)
- **Component Count**: ~30-40 React components
- **Test Count**: ~150 unit tests, ~30 integration tests, ~10 E2E tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development
- **Status**: PASS
- **Evidence**: Comprehensive specification created at `specs/004-phase-2-web-app/spec.md` with 5 user stories, 25 functional requirements, 15 success criteria
- **Compliance**: All features specified before implementation, organized by type (features, API, database, UI)

### ✅ II. Clean Code & Multi-Language Standards
- **Status**: PASS
- **Python Standards**: FastAPI with type hints (Pydantic/SQLModel), PEP 8 via ruff, docstrings for public APIs
- **TypeScript Standards**: Strict mode enabled, ESLint + Prettier, React Server Components default, PascalCase components
- **File Limits**: Backend max 300 lines, frontend components max 200 lines (extract if longer)

### ✅ III. Test-First Development (TDD)
- **Status**: PASS
- **Testing Pyramid**: 70% unit (pytest, vitest), 20% integration (FastAPI TestClient), 10% E2E (Playwright)
- **Coverage Target**: 80% overall, 90% for critical paths (auth, CRUD)
- **Test Database**: SQLite in-memory for unit tests, Neon test instance for integration tests

### ✅ IV. Database-First Design
- **Status**: PASS
- **ORM**: SQLModel for Python (combines SQLAlchemy + Pydantic)
- **Migrations**: Alembic for schema version control
- **Database**: Neon Serverless PostgreSQL with connection pooling
- **Schema**: User and Task entities with proper relationships, UUIDs for primary keys, timestamps

### ✅ V. Multi-Interface Excellence
- **Status**: PASS
- **Phase I CLI**: Preserved in `src/todo_app/` (always accessible for demo)
- **Phase II Web UI**: Next.js responsive design (mobile 320px+, tablet 768px+, desktop 1024px+)
- **Accessibility**: WCAG 2.1 AA compliance, keyboard navigation, screen reader support

### ✅ VI. Modern Technology Stack
- **Status**: PASS
- **Backend**: FastAPI 0.110+, Python 3.13+, SQLModel, Pydantic v2, UV package manager
- **Frontend**: Next.js 16+ (App Router), React 19+, TypeScript 5+ strict, Tailwind CSS 4+, pnpm
- **Auth**: Better Auth with JWT tokens in HttpOnly cookies
- **Testing**: Vitest, React Testing Library, Playwright, pytest

### ✅ VII. Monorepo Organization
- **Status**: PASS
- **Structure**: Phase I in `src/todo_app/`, Phase II in `frontend/` and `backend/` directories
- **Independence**: Each phase runs independently (CLI, frontend dev server, backend API)
- **Shared Specs**: `/specs` organized by type (features/, api/, database/, ui/)

### ✅ VIII. Full-Stack Architecture Patterns
- **Status**: PASS
- **Frontend Architecture**: `frontend/src/` with app/ (routes), components/, lib/ (utilities), types/
- **Backend Architecture**: `backend/src/` with api/ (routes), models/ (SQLModel), services/ (business logic), auth/, db/
- **Communication**: RESTful HTTP with JSON, JWT in HttpOnly cookies, structured error responses

### ✅ IX. API Security & Authentication
- **Status**: PASS
- **Authentication Flow**: Better Auth issues JWT → HttpOnly cookies → FastAPI validates with shared secret
- **JWT Standards**: HS256/RS256, 15min expiration, user_id/email claims
- **Security**: Rate limiting (5 attempts/min), CORS whitelist, security headers, input validation with Pydantic
- **Protected Endpoints**: All CRUD operations require authentication, user-task ownership enforced

### ✅ X. Database-First Design Workflow
- **Status**: PASS
- **Workflow**: Spec → SQLModel model → Alembic migration → Test → Apply
- **Schema Design**: 3NF normalization, UUIDs for PKs, created_at/updated_at timestamps, JSONB for metadata
- **Transactions**: Multi-table operations wrapped in transactions, optimistic locking for concurrent updates

### ✅ XI. Subagent Coordination & Parallel Execution
- **Status**: PASS (to be used during implementation)
- **Planned Patterns**:
  - Feature Swarm: Parallel subagents for backend API + frontend UI + integration tests
  - Sequential Pipeline: Database migration → Model → API → Frontend types
  - Specialist Agents: database-architect, api-designer, ui-builder, test-engineer
- **Context7 MCP**: Query for latest library docs (Next.js 16+, FastAPI 0.110+, Better Auth)

### ✅ XII. Reusable Intelligence via Skills
- **Status**: PASS (skills to be created during implementation)
- **Planned Skills**:
  - Database: create-sqlmodel-model, generate-migration, seed-test-data
  - API: create-fastapi-endpoint, add-jwt-auth, write-api-tests
  - Frontend: create-next-page, create-form-component, add-auth-guard
  - Testing: generate-unit-tests, generate-e2e-test, setup-test-db

### Summary
**Overall Status**: ✅ **PASS** - All 12 constitution principles satisfied

**No Violations**: All constitution requirements met without exceptions

**Proceed to Phase 0**: Approved for research and detailed design

## Project Structure

### Documentation (this feature)

```text
specs/004-phase-2-web-app/
├── spec.md              # Feature specification (created by /sp.specify)
├── plan.md              # This file (implementation plan from /sp.plan)
├── research.md          # Phase 0 research (will be created by /sp.plan)
├── data-model.md        # Phase 1 data models (will be created by /sp.plan)
├── quickstart.md        # Phase 1 development guide (will be created by /sp.plan)
├── contracts/           # Phase 1 API contracts (will be created by /sp.plan)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   ├── auth.md          # Authentication API documentation
│   └── tasks.md         # Task CRUD API documentation
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification quality checklist (created)
└── tasks.md             # Phase 2 implementation tasks (/sp.tasks - NOT created by /sp.plan)
```

### Source Code (repository root - Web Application)

```text
phase-1/                         # Monorepo root
├── backend/                     # FastAPI backend (NEW for Phase II)
│   ├── src/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── api/                 # API route handlers (thin controllers)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Signup, login, logout endpoints
│   │   │   └── tasks.py         # Task CRUD endpoints
│   │   ├── models/              # SQLModel database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User model (SQLModel + Pydantic)
│   │   │   └── task.py          # Task model (SQLModel + Pydantic)
│   │   ├── services/            # Business logic (fat services)
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Authentication logic
│   │   │   └── task_service.py  # Task operations, validation
│   │   ├── auth/                # Authentication utilities
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py           # JWT creation, validation
│   │   │   └── dependencies.py  # FastAPI auth dependencies
│   │   ├── db/                  # Database connection and migrations
│   │   │   ├── __init__.py
│   │   │   ├── session.py       # SQLModel session management
│   │   │   └── migrations/      # Alembic migration scripts
│   │   │       └── versions/    # Timestamped migrations
│   │   └── config.py            # Configuration (env vars, settings)
│   ├── tests/                   # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures (test DB, client)
│   │   ├── unit/                # Unit tests
│   │   │   ├── test_models.py
│   │   │   ├── test_services.py
│   │   │   └── test_auth.py
│   │   └── integration/         # Integration tests
│   │       ├── test_auth_api.py
│   │       └── test_tasks_api.py
│   ├── pyproject.toml           # UV project config (dependencies)
│   ├── .env.example             # Example environment variables
│   └── CLAUDE.md                # Backend-specific Claude instructions
│
├── frontend/                    # Next.js frontend (NEW for Phase II)
│   ├── src/
│   │   ├── app/                 # Next.js App Router (routes + layouts)
│   │   │   ├── layout.tsx       # Root layout (providers, auth)
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── (auth)/          # Auth route group
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── signup/
│   │   │   │       └── page.tsx
│   │   │   └── (dashboard)/     # Protected route group
│   │   │       ├── layout.tsx   # Dashboard layout (sidebar)
│   │   │       ├── dashboard/
│   │   │       │   └── page.tsx
│   │   │       └── tasks/
│   │   │           ├── page.tsx        # Task list
│   │   │           └── [id]/
│   │   │               └── page.tsx    # Task detail
│   │   ├── components/          # React components
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── auth/            # Auth-related components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── SignupForm.tsx
│   │   │   ├── tasks/           # Task components
│   │   │   │   ├── TaskList.tsx
│   │   │   │   ├── TaskCard.tsx
│   │   │   │   ├── TaskForm.tsx
│   │   │   │   └── TaskFilters.tsx
│   │   │   └── layout/          # Layout components
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── Footer.tsx
│   │   ├── lib/                 # Utilities and API clients
│   │   │   ├── api.ts           # Fetch wrapper with auth headers
│   │   │   ├── auth.ts          # Client-side auth utilities
│   │   │   └── utils.ts         # General utilities
│   │   └── types/               # TypeScript type definitions
│   │       ├── user.ts          # User types (matching backend)
│   │       ├── task.ts          # Task types (matching backend)
│   │       └── api.ts           # API response types
│   ├── public/                  # Static assets
│   │   ├── favicon.ico
│   │   └── images/
│   ├── tests/                   # Frontend tests
│   │   ├── unit/                # Component unit tests
│   │   │   ├── TaskCard.test.tsx
│   │   │   └── TaskForm.test.tsx
│   │   └── e2e/                 # Playwright E2E tests
│   │       ├── auth.spec.ts
│   │       └── tasks.spec.ts
│   ├── package.json             # pnpm dependencies
│   ├── tsconfig.json            # TypeScript config (strict mode)
│   ├── tailwind.config.ts       # Tailwind configuration
│   ├── next.config.js           # Next.js configuration
│   ├── .env.local.example       # Example environment variables
│   └── CLAUDE.md                # Frontend-specific Claude instructions
│
├── src/todo_app/                # Phase I: CLI (PRESERVED)
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   ├── operations.py
│   ├── ui.py
│   └── banner.py
│
├── tests/                       # Phase I: CLI tests (PRESERVED)
│   ├── test_models.py
│   ├── test_storage.py
│   ├── test_operations.py
│   ├── test_ui.py
│   ├── test_integration.py
│   └── test_banner.py
│
├── specs/                       # Specifications (organized by type)
│   ├── 001-console-todo-app/
│   ├── 002-cli-banner/
│   ├── 003-project-readme/
│   └── 004-phase-2-web-app/    # This feature
│
├── .specify/                    # Spec-Kit Plus config (global)
│   ├── memory/
│   │   └── constitution.md      # v2.0.0 (governs all phases)
│   ├── templates/
│   └── scripts/
│
├── .claude/                     # Claude Code config (global)
│   ├── agents/                  # Subagent definitions
│   └── skills/                  # Reusable intelligence
│
├── history/                     # Global history
│   ├── prompts/                 # PHR records
│   └── adr/                     # Architecture Decision Records
│
├── README.md                    # Project overview (all phases)
├── CLAUDE.md                    # Root Claude Code instructions
└── pyproject.toml               # Phase I Python dependencies
```

**Structure Decision**:
Selected **Web Application** structure with frontend/ and backend/ directories to support Phase II full-stack requirements. Phase I CLI (`src/todo_app/`) is preserved for independent operation and demo recording. This monorepo structure enables:
- Phase independence (each runs separately)
- Shared specifications and documentation
- Clean separation of concerns (frontend, backend, database)
- Easy navigation for subagents working on different layers

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - Constitution Check passed all 12 principles without exceptions.

No complexity tracking required.
