# AGENTS.md

A guide for AI coding agents working on Talal's TDA (Todo App) - Evolution of Todo project.

This is a **monorepo** with multiple phases, each representing a different architectural evolution of a Todo application. Agents should read this file before making changes to understand the project structure, conventions, and workflows.

---

## Project Overview

**Monorepo Structure**: Phase-wise organization supporting multiple independent applications
- **Phase 1**: ✅ Complete - Python CLI Todo App (in-memory storage)
- **Phase 2**: 🚧 In Progress - Full-stack Web App (FastAPI + Next.js)
- **Phase 3-5**: 🔮 Future phases (microservices, real-time, cloud deployment)

**Key Technologies**:
- **Backend**: FastAPI 0.110+, Python 3.13+, SQLModel, Neon PostgreSQL
- **Frontend**: Next.js 16+, React 19+, TypeScript 5+, Tailwind CSS 4+
- **Package Managers**: UV (Python), pnpm (JavaScript)
- **Testing**: pytest (backend), Vitest + Playwright (frontend)

**Architecture**: Spec-Driven Development (SDD) with Constitution v2.0.0 principles

---

## Monorepo Navigation

### Phase Independence
Each phase runs independently. When working on a specific phase:

1. **Navigate to the phase directory**:
   - Phase 1: `cd phase-1`
   - Phase 2 Backend: `cd phase-2/backend`
   - Phase 2 Frontend: `cd phase-2/frontend`

2. **Read phase-specific documentation**:
   - Phase 2 Backend: `phase-2/backend/CLAUDE.md`
   - Phase 2 Frontend: `phase-2/frontend/CLAUDE.md`

3. **Use phase-specific commands** (see Setup Commands below)

### Directory Structure
```
phase-1/                    # Phase I: CLI Todo App (complete)
├── src/todo_app/           # Source code
├── tests/                  # Test suite (87 tests)
└── pyproject.toml         # UV project config

phase-2/                    # Phase II: Full-Stack Web App
├── backend/                # FastAPI backend
│   ├── src/               # Source code
│   ├── tests/             # pytest tests
│   └── pyproject.toml     # UV dependencies
└── frontend/              # Next.js frontend
    ├── app/               # Next.js App Router
    ├── components/        # React components
    ├── tests/             # Vitest + Playwright tests
    └── package.json       # pnpm dependencies

specs/                      # Specifications (organized by type)
├── features/              # User-facing features
├── api/                   # API contracts
└── database/              # Schema designs

.claude/                    # Claude Code configuration
├── skills/                # Reusable skills
└── agents/                # Subagent definitions
```

---

## Setup Commands

### Phase 1 (CLI Todo App)
```bash
# Navigate to phase-1
cd phase-1

# Install dependencies (UV automatically creates venv)
uv sync

# Run the application
uv run python -m src.todo_app.main

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=src.todo_app --cov-report=html
```

### Phase 2 Backend (FastAPI)
```bash
# Navigate to backend
cd phase-2/backend

# Install dependencies
uv sync

# Set up environment variables (copy from .env.example)
cp .env.example .env
# Edit .env with your DATABASE_URL and JWT_SECRET

# Run database migrations
uv run alembic upgrade head

# Start dev server (with auto-reload)
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Generate new migration (after model changes)
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1
```

### Phase 2 Frontend (Next.js)
```bash
# Navigate to frontend
cd phase-2/frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
pnpm dev

# Build for production
pnpm build

# Run unit tests (Vitest)
pnpm test

# Run unit tests with UI
pnpm test:ui

# Run E2E tests (Playwright)
pnpm test:e2e

# Run E2E tests with UI
pnpm test:e2e:ui

# Lint code
pnpm lint

# Type check
pnpm type-check  # or: npx tsc --noEmit
```

---

## Code Style Guidelines

### Python (Backend)
- **Style**: PEP 8 (enforced via ruff)
- **Type Hints**: Required for all function parameters and return values
- **Line Length**: 88 characters (ruff default)
- **File Size**: Maximum 300 lines per file
- **Function Size**: Maximum 50 lines per function
- **Docstrings**: Required for all public functions, classes, and API endpoints
- **Pattern**: Thin Controllers, Fat Services (business logic in services, not routes)

**Example**:
```python
from typing import List, Optional
from uuid import UUID

async def get_user_tasks(
    user_id: UUID,
    is_complete: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Task]:
    """Get tasks for a user with optional filtering and pagination."""
    # Implementation here
```

### TypeScript (Frontend)
- **Mode**: Strict TypeScript (`strict: true` in tsconfig.json)
- **Style**: ESLint + Prettier (Next.js defaults)
- **Components**: React Server Components by default, Client Components only when needed
- **File Naming**: 
  - Components: `PascalCase.tsx` (e.g., `TaskCard.tsx`)
  - Utilities: `camelCase.ts` (e.g., `api.ts`)
- **File Size**: Maximum 200 lines per component file
- **Pattern**: Server Components for data fetching, Client Components for interactivity

**Example**:
```typescript
// ✅ Server Component (default, no "use client")
export default async function TasksPage() {
  const tasks = await fetchTasks();
  return <TaskList tasks={tasks} />;
}

// ✅ Client Component (for interactivity)
"use client";
export function TaskForm() {
  const [title, setTitle] = useState("");
  // Form handling
}
```

### Shared Standards
- **No `any` types**: Use proper TypeScript types or Python type hints
- **DRY Principle**: Extract reusable logic into utilities
- **Descriptive Names**: Avoid single-letter variables (except loop counters)
- **Error Handling**: Always handle errors explicitly, never silent failures

---

## Testing Instructions

### Backend Tests (pytest)
```bash
cd phase-2/backend

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_task_service.py -v

# Run specific test function
uv run pytest tests/unit/test_task_service.py::test_create_task_success -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run integration tests only
uv run pytest tests/integration/ -v

# Run unit tests only
uv run pytest tests/unit/ -v
```

**Test Structure**:
- `tests/unit/`: Unit tests for services, models, utilities
- `tests/integration/`: Integration tests for API endpoints
- `tests/conftest.py`: Pytest fixtures (test database, client)

**Requirements**:
- All new features MUST have tests before code review
- Coverage target: minimum 80% overall
- Use test database (SQLite in-memory or Neon test instance)
- Mock external dependencies (don't call real APIs)

### Frontend Tests (Vitest + Playwright)
```bash
cd phase-2/frontend

# Run unit tests
pnpm test

# Run unit tests in watch mode
pnpm test --watch

# Run specific test file
pnpm test TaskCard.test.tsx

# Run tests matching pattern
pnpm vitest run -t "TaskCard"

# Run E2E tests
pnpm test:e2e

# Run E2E tests in headed mode (see browser)
pnpm test:e2e:headed

# Run E2E tests with UI
pnpm test:e2e:ui
```

**Test Structure**:
- `tests/unit/`: Component unit tests (Vitest + React Testing Library)
- `tests/e2e/`: End-to-end tests (Playwright)
- `tests/setup.ts`: Test configuration

**Requirements**:
- Test user interactions, not implementation details
- Mock API calls (use MSW or similar)
- E2E tests for critical user flows (signup, login, CRUD)

### Phase 1 Tests
```bash
cd phase-1

# Run all tests (87 tests should pass)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src.todo_app --cov-report=html
```

**Note**: Phase 1 tests are stable and should always pass. Don't modify Phase 1 code unless explicitly requested.

---

## Build and Deployment

### Phase 2 Backend
```bash
cd phase-2/backend

# Production build (FastAPI doesn't need build step, but check dependencies)
uv sync --no-dev

# Run production server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000

# With Gunicorn (production)
uv run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Phase 2 Frontend
```bash
cd phase-2/frontend

# Production build
pnpm build

# Start production server
pnpm start

# Preview production build locally
pnpm build && pnpm start
```

---

## Security Considerations

### Environment Variables
- **NEVER commit** `.env` or `.env.local` files
- Use `.env.example` and `.env.local.example` for documentation
- Required backend variables:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `JWT_SECRET`: 256-bit random secret (generate with `openssl rand -hex 32`)
  - `CORS_ORIGINS`: Comma-separated allowed origins
- Required frontend variables:
  - `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., `http://localhost:8000`)

### Authentication
- JWT tokens stored in **HttpOnly cookies** (prevents XSS)
- Tokens expire after 15 minutes (configurable)
- Rate limiting on login endpoint (5 attempts/minute)
- Passwords hashed with bcrypt (never stored in plaintext)

### API Security
- All task endpoints require authentication (`get_current_user` dependency)
- Ownership checks on all task operations (403 if not owner)
- Input validation via Pydantic (backend) and Zod (frontend)
- CORS configured for specific origins only

### Code Security
- Never expose `hashed_password` in API responses
- Never log sensitive data (passwords, tokens)
- Use parameterized queries (SQLModel handles this)
- Validate and sanitize all user input

---

## Database Management

### Migrations (Alembic)
```bash
cd phase-2/backend

# Generate migration after model changes
uv run alembic revision --autogenerate -m "Add priority field to tasks"

# Review generated migration in src/db/migrations/versions/

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade <revision_id>

# Show migration history
uv run alembic history

# Show current migration
uv run alembic current
```

**Important**: Always review auto-generated migrations before applying. Alembic may not detect all changes correctly.

### Database Schema
- **User Table**: `users` (id, email, name, hashed_password, timestamps)
- **Task Table**: `tasks` (id, title, description, is_complete, user_id FK, timestamps)
- **Indexes**: On `user_id`, `email`, `created_at`, `is_complete` for performance

---

## Common Workflows

### Adding a New Feature
1. **Create specification** in `specs/features/<feature-name>/spec.md`
2. **Create tasks** in `specs/features/<feature-name>/tasks.md`
3. **Implement backend** (if needed):
   - Create SQLModel model in `phase-2/backend/src/models/`
   - Create service in `phase-2/backend/src/services/`
   - Create API endpoint in `phase-2/backend/src/api/`
   - Write tests in `phase-2/backend/tests/`
4. **Implement frontend** (if needed):
   - Create components in `phase-2/frontend/components/`
   - Create pages in `phase-2/frontend/app/`
   - Write tests in `phase-2/frontend/tests/`
5. **Run tests** and ensure all pass
6. **Update documentation** if needed

### Fixing a Bug
1. **Reproduce the bug** (write a failing test if possible)
2. **Fix the code**
3. **Run tests** to ensure fix works and doesn't break anything
4. **Update tests** if needed

### Refactoring
1. **Ensure tests pass** before refactoring
2. **Refactor incrementally** (small changes, test after each)
3. **Run full test suite** after refactoring
4. **Update documentation** if API/interface changes

---

## File Organization Rules

### Backend (FastAPI)
- **Models**: `src/models/` - SQLModel database models + Pydantic schemas
- **Services**: `src/services/` - Business logic (fat services)
- **API**: `src/api/` - Route handlers (thin controllers)
- **Auth**: `src/auth/` - JWT utilities and dependencies
- **DB**: `src/db/` - Database session and migrations
- **Tests**: `tests/unit/` and `tests/integration/`

### Frontend (Next.js)
- **Pages**: `app/` - Next.js App Router pages and layouts
- **Components**: `components/` - React components (organized by feature)
- **Lib**: `lib/` - Utilities and API clients
- **Types**: `types/` - TypeScript type definitions
- **Tests**: `tests/unit/` and `tests/e2e/`

### Specifications
- **Features**: `specs/features/<feature-name>/` - User-facing features
- **APIs**: `specs/api/<endpoint-group>/` - API contracts
- **Database**: `specs/database/<domain>/` - Schema designs
- **UI**: `specs/ui/<component-group>/` - Component specs

---

## Code Quality Checks

### Before Committing
```bash
# Backend
cd phase-2/backend
uv run ruff check src/          # Lint
uv run ruff format src/         # Format
uv run pytest tests/ -v        # Tests

# Frontend
cd phase-2/frontend
pnpm lint                       # Lint
pnpm test                       # Unit tests
pnpm test:e2e                   # E2E tests (optional, can be slow)
```

### Automated Checks
- **Linting**: ruff (Python), ESLint (TypeScript)
- **Formatting**: ruff format (Python), Prettier (TypeScript)
- **Type Checking**: mypy (Python), TypeScript compiler (TypeScript)
- **Tests**: pytest (backend), Vitest + Playwright (frontend)

---

## Subagent Coordination

This project uses **subagent orchestration** for parallel work. When coordinating multiple agents:

1. **Read `IMPLEMENTATION_STRATEGY.md`** for current subagent strategy
2. **Use reusable skills** from `.claude/skills/`:
   - `create-backend-tests`: Generate pytest tests
   - `create-frontend-tests`: Generate Vitest tests
   - `create-e2e-tests`: Generate Playwright tests
   - `make-responsive`: Add Tailwind responsive classes
   - `add-accessibility`: Add WCAG 2.1 AA features
   - `enhance-api-docs`: Add FastAPI docstrings
3. **Follow Constitution v2.0.0** principles (see `.specify/memory/constitution.md`)
4. **Create PHRs** (Prompt History Records) in `history/prompts/` after significant work

---

## Troubleshooting

### Backend Issues
- **Database connection errors**: Check `DATABASE_URL` in `.env`
- **Migration errors**: Review migration file, may need manual fixes
- **Import errors**: Ensure you're in `phase-2/backend` directory, run `uv sync`
- **Port already in use**: Change port with `--port 8001` or kill existing process

### Frontend Issues
- **API connection errors**: Check `NEXT_PUBLIC_API_URL` in `.env.local`
- **Build errors**: Run `pnpm install` to ensure dependencies are installed
- **Type errors**: Run `pnpm type-check` to see all TypeScript errors
- **Port already in use**: Change port in `package.json` scripts or kill existing process

### Test Issues
- **Backend tests failing**: Ensure test database is set up, check `tests/conftest.py`
- **Frontend tests failing**: Ensure API is mocked, check `tests/setup.ts`
- **E2E tests failing**: Ensure backend is running, check `playwright.config.ts`

---

## Additional Resources

- **Project README**: `README.md` - Overview and getting started
- **Constitution**: `.specify/memory/constitution.md` - Core principles
- **Backend Guide**: `phase-2/backend/CLAUDE.md` - Backend-specific guidelines
- **Frontend Guide**: `phase-2/frontend/CLAUDE.md` - Frontend-specific guidelines
- **Implementation Strategy**: `IMPLEMENTATION_STRATEGY.md` - Subagent coordination
- **MVP Report**: `MVP_COMPLETION_REPORT.md` - Current completion status

---

## Quick Reference

| Task | Command |
|------|---------|
| **Phase 1 - Run CLI** | `cd phase-1 && uv run python -m src.todo_app.main` |
| **Phase 1 - Test** | `cd phase-1 && uv run pytest tests/ -v` |
| **Backend - Dev Server** | `cd phase-2/backend && uv run uvicorn src.main:app --reload` |
| **Backend - Test** | `cd phase-2/backend && uv run pytest tests/ -v` |
| **Backend - Migrate** | `cd phase-2/backend && uv run alembic upgrade head` |
| **Frontend - Dev Server** | `cd phase-2/frontend && pnpm dev` |
| **Frontend - Test** | `cd phase-2/frontend && pnpm test` |
| **Frontend - E2E** | `cd phase-2/frontend && pnpm test:e2e` |
| **Frontend - Build** | `cd phase-2/frontend && pnpm build` |

---

**Last Updated**: 2025-12-11
**Constitution Version**: v2.0.0
**Project Status**: Phase 1 Complete, Phase 2 In Progress (82% complete)

