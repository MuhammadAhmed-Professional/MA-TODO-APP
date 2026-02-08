# Quickstart Guide: Phase II Full-Stack Web Application

**Feature**: 004-phase-2-web-app
**Last Updated**: 2025-12-06
**Purpose**: Get the Phase II full-stack todo application running locally in <10 minutes

---

## Prerequisites

Ensure you have the following installed before starting:

- **Python 3.13+** (check with `python --version` or `python3 --version`)
- **UV** (Python package manager) - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Node.js 20+** (check with `node --version`) - Recommended: Use `nvm` or download from [nodejs.org](https://nodejs.org/)
- **pnpm** (Node package manager) - Install: `npm install -g pnpm`
- **Git** (for cloning and version control)
- **PostgreSQL client** (optional, for local database inspection) - Install: `brew install postgresql` (macOS) or `apt-get install postgresql-client` (Linux)

---

## Environment Setup

### 1. Clone Repository (if not already done)

```bash
git clone <repository-url>
cd phase-1
git checkout 004-phase-2-web-app
```

### 2. Set Up Backend (FastAPI)

#### Install Dependencies

```bash
cd backend
uv sync  # Creates virtual environment and installs all dependencies
```

#### Configure Environment Variables

```bash
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```env
# Database (Neon Serverless PostgreSQL)
DATABASE_URL=postgresql://user:password@host.region.neon.tech/dbname?sslmode=require

# Authentication
JWT_SECRET=your-256-bit-random-secret-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (whitelist frontend origins)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development  # development | staging | production
```

**Generate JWT Secret**:
```bash
openssl rand -hex 32
```

#### Set Up Database

**Option A: Neon Serverless (Recommended for Development)**

1. Sign up at [neon.tech](https://neon.tech) (free tier available)
2. Create a new project: "phase-1-dev"
3. Copy the connection string from the Neon dashboard
4. Paste into `DATABASE_URL` in `.env`

**Option B: Local PostgreSQL (Alternative)**

```bash
# Start PostgreSQL locally
brew services start postgresql  # macOS
sudo service postgresql start   # Linux

# Create database
createdb phase1_dev

# Update .env with local connection string
DATABASE_URL=postgresql://localhost/phase1_dev
```

#### Run Database Migrations

```bash
# Initialize Alembic (first time only)
uv run alembic init backend/src/db/migrations

# Generate initial migration
uv run alembic revision --autogenerate -m "Initial schema: users and tasks"

# Apply migrations
uv run alembic upgrade head
```

#### Start Backend Server

```bash
# Development server with auto-reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### Verify Backend Health

```bash
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","database":"connected"}
```

---

### 3. Set Up Frontend (Next.js)

#### Install Dependencies

```bash
cd ../frontend  # From backend/ directory
pnpm install
```

#### Configure Environment Variables

```bash
cp .env.local.example .env.local
```

Edit `frontend/.env.local`:

```env
# API Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-different-secret-here  # Generate with: openssl rand -hex 32

# Environment
NEXT_PUBLIC_ENVIRONMENT=development
```

**Note**: `BETTER_AUTH_SECRET` should be different from `JWT_SECRET` in the backend.

#### Start Frontend Development Server

```bash
pnpm dev
```

Frontend will be available at:
- **App**: http://localhost:3000
- **Landing Page**: http://localhost:3000/
- **Login**: http://localhost:3000/login
- **Signup**: http://localhost:3000/signup
- **Dashboard**: http://localhost:3000/dashboard (requires authentication)

#### Verify Frontend

Open http://localhost:3000 in your browser. You should see the landing page with "Sign Up" and "Login" buttons.

---

## Running the Full Stack

### Terminal 1: Backend

```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
pnpm dev
```

### Test the Stack

1. **Open Frontend**: http://localhost:3000
2. **Sign Up**: Create a new account at http://localhost:3000/signup
3. **Verify Backend**: Check Swagger UI at http://localhost:8000/docs to see the authentication cookie set
4. **Create Task**: In the dashboard, add a new todo task
5. **Verify Database**: Check Neon dashboard or use `psql` to query tasks table

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/integration/test_auth_api.py

# Run unit tests only
uv run pytest tests/unit/

# Run integration tests only
uv run pytest tests/integration/
```

### Frontend Tests

```bash
cd frontend

# Run unit tests (vitest)
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage

# Run E2E tests (Playwright)
pnpm test:e2e

# Run E2E in headed mode (see browser)
pnpm test:e2e --headed
```

---

## Development Workflow

### 1. Start Development Session

```bash
# Terminal 1: Backend
cd backend && uv run uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend && pnpm dev

# Terminal 3: Watch tests
cd backend && uv run pytest --watch  # or cd frontend && pnpm test:watch
```

### 2. Making Changes

**Backend Changes**:
- Edit files in `backend/src/`
- Server auto-reloads on save (FastAPI `--reload` flag)
- API docs update automatically at http://localhost:8000/docs

**Frontend Changes**:
- Edit files in `frontend/src/`
- Browser auto-refreshes on save (Next.js Fast Refresh)
- Check console for any errors

**Database Changes**:
1. Modify SQLModel models in `backend/src/models/`
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review migration in `backend/src/db/migrations/versions/`
4. Apply migration: `uv run alembic upgrade head`

### 3. Verify Changes

- **Backend**: Check Swagger UI at http://localhost:8000/docs
- **Frontend**: Test in browser at http://localhost:3000
- **Tests**: Run `pytest` (backend) or `pnpm test` (frontend)

---

## Common Issues and Solutions

### Issue: Database Connection Error

**Symptoms**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon project is running (not paused)
3. Test connection: `psql $DATABASE_URL -c "SELECT 1"`
4. For Neon: Ensure `?sslmode=require` is in connection string

### Issue: CORS Error in Browser

**Symptoms**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solutions**:
1. Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
2. Restart backend server after changing `.env`
3. Check browser console for exact origin being blocked

### Issue: Authentication Cookie Not Set

**Symptoms**: Login succeeds but user redirects back to login page

**Solutions**:
1. Check `HttpOnly` cookie in browser DevTools → Application → Cookies
2. Verify `JWT_SECRET` in `backend/.env` is set
3. Ensure backend and frontend are on same domain (localhost) or CORS is configured
4. Check backend logs for JWT validation errors

### Issue: Frontend Can't Reach Backend

**Symptoms**: `Failed to fetch` or network errors in browser console

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local` is `http://localhost:8000`
3. Restart frontend dev server after changing `.env.local`

### Issue: Alembic Migration Conflicts

**Symptoms**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solutions**:
```bash
# Check current revision
uv run alembic current

# View migration history
uv run alembic history

# Downgrade to specific revision
uv run alembic downgrade <revision>

# Upgrade to latest
uv run alembic upgrade head
```

---

## Database Management

### Inspect Database (Neon Dashboard)

1. Go to [Neon Dashboard](https://console.neon.tech)
2. Select your project
3. Click "Tables" tab to view `user` and `task` tables
4. Click "SQL Editor" to run queries

### Inspect Database (psql CLI)

```bash
# Connect to database
psql $DATABASE_URL

# List tables
\dt

# View users
SELECT id, email, name, created_at FROM "user";

# View tasks
SELECT id, title, is_complete, user_id, created_at FROM task;

# Exit
\q
```

### Reset Database

**Warning**: This will delete ALL data.

```bash
# Downgrade all migrations
uv run alembic downgrade base

# Re-apply migrations
uv run alembic upgrade head
```

### Seed Test Data

```bash
# Run seed script (create this in backend/scripts/seed.py)
uv run python -m scripts.seed
```

Example seed script:
```python
# backend/scripts/seed.py
from src.db.session import get_session
from src.models.user import User
from src.models.task import Task
from src.auth.jwt import hash_password
import uuid

with get_session() as session:
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123")
    )
    session.add(user)
    session.commit()

    task = Task(
        id=uuid.uuid4(),
        title="Sample Task",
        description="This is a test task",
        is_complete=False,
        user_id=user.id
    )
    session.add(task)
    session.commit()
    print(f"Created user: {user.email} with 1 task")
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string (Neon or local) |
| `JWT_SECRET` | Yes | - | 256-bit secret for JWT signing (use `openssl rand -hex 32`) |
| `JWT_ALGORITHM` | No | `HS256` | JWT signing algorithm (HS256 or RS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `15` | Access token expiration time |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Refresh token expiration time |
| `CORS_ORIGINS` | Yes | - | Comma-separated list of allowed origins |
| `ENVIRONMENT` | No | `development` | Environment name (development/staging/production) |

### Frontend (.env.local)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | - | Backend API base URL (http://localhost:8000) |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Yes | - | Frontend URL for auth redirects (http://localhost:3000) |
| `BETTER_AUTH_SECRET` | Yes | - | Secret for Better Auth (different from JWT_SECRET) |
| `NEXT_PUBLIC_ENVIRONMENT` | No | `development` | Environment name for frontend |

---

## Next Steps

After getting the stack running:

1. **Explore API Docs**: Visit http://localhost:8000/docs to see all available endpoints
2. **Test User Flows**:
   - Sign up a new user
   - Create, edit, complete, and delete tasks
   - Log out and log back in
3. **Run Tests**: Ensure all unit and integration tests pass
4. **Read Architecture Docs**:
   - [Data Model](./data-model.md) - Database schema details
   - [API Contracts](./contracts/) - Complete API specifications
   - [Research](./research.md) - Architecture decisions and rationale
5. **Check Constitution**: Review `.specify/memory/constitution.md` for coding standards

---

## Performance Benchmarks

Expected performance for local development:

- **Backend API Latency**: <50ms p95 (local database)
- **Frontend Page Load**: <1s (Next.js dev mode with Fast Refresh)
- **Task Creation**: <1s from save click to list update
- **Database Queries**: <10ms for single-task lookup, <50ms for user task list

**Note**: Production performance will differ based on deployment environment (Vercel, Railway, Neon).

---

## Troubleshooting Logs

### Backend Logs

```bash
# Watch backend logs in real-time
cd backend
uv run uvicorn src.main:app --reload --log-level debug
```

Logs include:
- HTTP requests (method, path, status code)
- Database queries (with SQLAlchemy logging enabled)
- Authentication events (login, token validation)
- Errors with stack traces

### Frontend Logs

```bash
# Watch frontend logs
cd frontend
pnpm dev
```

Logs include:
- Page compilation status
- API fetch requests
- React component errors
- Browser console errors (check browser DevTools)

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Better Auth Documentation**: https://better-auth.com/
- **Neon Documentation**: https://neon.tech/docs
- **Alembic Documentation**: https://alembic.sqlalchemy.org/

For project-specific questions, see:
- [Specification](./spec.md) - Feature requirements
- [Implementation Plan](./plan.md) - Technical architecture
- [Constitution](./.specify/memory/constitution.md) - Coding standards
