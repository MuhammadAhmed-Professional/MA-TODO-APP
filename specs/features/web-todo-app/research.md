# Research: Phase II Full-Stack Web Application

**Feature**: 004-phase-2-web-app
**Date**: 2025-12-06
**Purpose**: Resolve technical unknowns and establish best practices for Phase II implementation

## Overview

This document consolidates research findings for implementing a full-stack todo application with Next.js 16+, FastAPI, Neon PostgreSQL, and Better Auth. All decisions are based on current best practices, official documentation, and industry standards.

---

## 1. Better Auth Integration Strategy

### Decision
Use Better Auth as the authentication provider with custom JWT validation in FastAPI backend.

### Rationale
- **Better Auth Advantages**:
  - Built for Next.js with native App Router support
  - Handles complex auth flows (signup, login, logout, password reset)
  - Provides social OAuth providers if needed later
  - Automatic CSRF protection
  - Session management with refresh tokens

- **Backend Integration**:
  - Better Auth issues JWT tokens
  - Store tokens in HttpOnly cookies (prevents XSS)
  - FastAPI validates JWT signature with shared secret
  - Backend extracts user ID from token claims for authorization

### Alternatives Considered
- **NextAuth.js**: Popular but Better Auth has better TypeScript support and simpler API
- **Custom Auth**: More control but significantly more implementation time and security risks
- **Firebase Auth**: Third-party dependency, vendor lock-in, not aligned with hackathon requirements

### Implementation Pattern
```typescript
// Frontend (Better Auth setup)
import { createAuth } from "better-auth/react";
export const auth = createAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  cookiePrefix: "tda_",
});

// Backend (FastAPI JWT validation)
from jose import JWTError, jwt
def verify_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload  # Contains user_id, email, exp
```

---

## 2. Database Schema Design with SQLModel

### Decision
Use SQLModel for unified database schema and API validation with UUIDs for primary keys.

### Rationale
- **SQLModel Benefits**:
  - Single source of truth: same model for DB schema + API validation
  - Type-safe: full Python type hints and IDE support
  - Pydantic integration: automatic validation and serialization
  - SQLAlchemy under the hood: mature ORM with migration support (Alembic)

- **UUID vs Auto-Increment**:
  - UUIDs provide globally unique identifiers (no collisions)
  - Better for distributed systems and API security (non-sequential)
  - Prevents ID enumeration attacks

### Schema Design Principles
- **Normalization**: 3NF (users and tasks in separate tables)
- **Timestamps**: `created_at` and `updated_at` on all tables
- **Foreign Keys**: `user_id` in tasks table with ON DELETE CASCADE
- **Indexes**: Create index on `tasks.user_id` for fast user-task queries
- **Constraints**: NOT NULL on required fields, UNIQUE on email

### Implementation Pattern
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    description: str | None = Field(default=None, max_length=2000)
    is_complete: bool = Field(default=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## 3. Next.js 16 App Router Best Practices

### Decision
Use React Server Components (RSC) by default, with Client Components only for interactivity.

### Rationale
- **Performance**: RSC render on server, reducing JavaScript bundle size
- **Data Fetching**: Server Components can directly query database/API (no waterfall requests)
- **SEO**: Fully rendered HTML improves search engine indexing
- **Streaming**: Suspense boundaries enable progressive rendering

### App Router Patterns
- **Route Groups**: `(auth)/` for public routes, `(dashboard)/` for protected routes
- **Layouts**: Shared layouts with `layout.tsx` for consistent UI (header, sidebar)
- **Loading States**: `loading.tsx` for skeleton screens during data fetching
- **Error Boundaries**: `error.tsx` for graceful error handling
- **Metadata**: Dynamic metadata with `generateMetadata()` for SEO

### Client vs Server Components
- **Server Components** (default):
  - Task list page (data fetching)
  - Task detail page (data fetching)
  - Landing page (static content)

- **Client Components** (use `"use client"`):
  - Forms (LoginForm, SignupForm, TaskForm)
  - Interactive buttons (mark complete, delete with confirmation)
  - Modal dialogs
  - Real-time updates (if added later)

### Implementation Pattern
```typescript
// Server Component (default)
export default async function TasksPage() {
  const tasks = await fetchTasks();  // Server-side fetch
  return <TaskList tasks={tasks} />;
}

// Client Component (for interactivity)
"use client";
export function TaskForm() {
  const [title, setTitle] = useState("");
  return <form onSubmit={handleSubmit}>...</form>;
}
```

---

## 4. API Design and OpenAPI Documentation

### Decision
Follow RESTful conventions with FastAPI auto-generated OpenAPI 3.0 documentation.

### Rationale
- **RESTful Standards**:
  - Clear HTTP methods: GET (read), POST (create), PUT/PATCH (update), DELETE (delete)
  - Resource-based URLs: `/api/tasks`, `/api/tasks/{task_id}`
  - Idempotency: GET, PUT, DELETE are idempotent
  - Status codes: 200 (success), 201 (created), 204 (no content), 400 (validation), 401 (auth), 403 (forbidden), 404 (not found), 500 (server error)

- **OpenAPI Benefits**:
  - Auto-generated from FastAPI code (no manual documentation)
  - Interactive Swagger UI at `/docs`
  - Type-safe client generation (if needed)
  - Contract testing against spec

### API Endpoint Structure
```
Authentication:
- POST   /api/auth/signup      - Create new user account
- POST   /api/auth/login       - Authenticate and issue JWT
- POST   /api/auth/logout      - Invalidate session (clear cookie)

Tasks (all require authentication):
- GET    /api/tasks            - List all tasks for authenticated user
- POST   /api/tasks            - Create new task
- GET    /api/tasks/{task_id}  - Get single task (with ownership check)
- PUT    /api/tasks/{task_id}  - Update task (with ownership check)
- DELETE /api/tasks/{task_id}  - Delete task (with ownership check)
- PATCH  /api/tasks/{task_id}/complete - Toggle completion status

Health Check:
- GET    /api/health           - Server health status (no auth)

Documentation:
- GET    /docs                 - Swagger UI (interactive API docs)
- GET    /openapi.json         - OpenAPI 3.0 specification
```

### Request/Response Patterns
```python
# Request Model (Pydantic)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)

# Response Model (from SQLModel)
class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    is_complete: bool
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
```

---

## 5. Testing Strategy and Tools

### Decision
Implement three-tier testing pyramid: unit (70%), integration (20%), E2E (10%).

### Rationale
- **Unit Tests**: Fast, isolated, test individual functions/components
- **Integration Tests**: Verify API endpoints with test database
- **E2E Tests**: Validate critical user flows end-to-end

### Testing Tools
- **Backend**:
  - `pytest`: Test runner with fixtures and parametrization
  - `FastAPI TestClient`: HTTP client for API testing
  - `SQLite in-memory`: Fast unit test database
  - `pytest-cov`: Code coverage reporting

- **Frontend**:
  - `vitest`: Fast Vite-powered test runner
  - `React Testing Library`: Component testing (user-centric)
  - `@testing-library/user-event`: Simulate user interactions
  - `msw` (Mock Service Worker): Mock API responses

- **E2E**:
  - `Playwright`: Cross-browser E2E testing
  - `@playwright/test`: Test runner with parallel execution
  - Headless mode for CI/CD, headed mode for debugging

### Test Coverage Goals
- **Critical Paths** (90% coverage):
  - Authentication (signup, login, logout)
  - Task CRUD operations
  - Authorization (user-task ownership)

- **Standard Paths** (80% coverage):
  - Form validation
  - Error handling
  - UI components

### Implementation Pattern
```python
# Backend Integration Test (pytest)
def test_create_task_authenticated(client, auth_token):
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        cookies={"auth_token": auth_token}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

```typescript
// Frontend Unit Test (vitest)
test("TaskForm validates required title", async () => {
  render(<TaskForm />);
  const submitButton = screen.getByRole("button", { name: /save/i });
  await userEvent.click(submitButton);
  expect(screen.getByText(/title is required/i)).toBeInTheDocument();
});
```

```typescript
// E2E Test (Playwright)
test("user can create and complete task", async ({ page }) => {
  await page.goto("/login");
  await page.fill("[name=email]", "test@example.com");
  await page.fill("[name=password]", "password123");
  await page.click("button[type=submit]");
  await page.waitForURL("/dashboard");

  await page.click("text=Add Task");
  await page.fill("[name=title]", "New Task");
  await page.click("button:has-text('Save')");
  await expect(page.locator("text=New Task")).toBeVisible();

  await page.click("[aria-label='Mark complete']");
  await expect(page.locator("text=New Task")).toHaveClass(/line-through/);
});
```

---

## 6. Deployment Strategy

### Decision
Use platform-optimized hosting: Vercel (frontend), Railway/Render (backend), Neon (database).

### Rationale
- **Vercel**:
  - Built for Next.js (edge functions, ISR, streaming SSR)
  - Global CDN for static assets
  - Automatic HTTPS and custom domains
  - Git-based deployment (push to deploy)
  - Environment variables management
  - Free tier sufficient for hackathon

- **Railway/Render** (Backend):
  - Native Python 3.13 support
  - Automatic deployments from Git
  - Environment variable management
  - PostgreSQL connection support
  - Health check monitoring
  - Free tier or low-cost plans

- **Neon** (Database):
  - Serverless PostgreSQL (auto-scaling)
  - Instant branching for test environments
  - Connection pooling built-in
  - Generous free tier (3 GB storage, 1 compute hour)
  - Automatic backups

### Deployment Workflow
1. **Development**: Local development with SQLite (backend) and dev database (Neon branch)
2. **Staging**: Deploy to staging environments (preview deployments on Vercel, staging branch on Railway)
3. **Production**: Main branch deployments with environment-specific configs

### Environment Variables
```env
# Backend (.env)
DATABASE_URL=postgresql://user:pass@neon-host/db
JWT_SECRET=<256-bit-random-string>
CORS_ORIGINS=https://your-frontend.vercel.app

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-frontend.vercel.app
```

---

## 7. Performance Optimization Strategies

### Decision
Implement caching, lazy loading, and database query optimization from the start.

### Rationale
Success criteria require <200ms API latency and <2s page loads.

### Optimization Techniques
- **Database**:
  - Index on `tasks.user_id` for fast user-task queries
  - Use `select(Task).where(Task.user_id == user_id)` (optimized queries)
  - Connection pooling via Neon (reuse connections)
  - Avoid N+1 queries (use `selectinload()` for relationships if added)

- **Backend API**:
  - FastAPI async endpoints for I/O operations
  - Pydantic model validation (minimal overhead)
  - Response caching for read-heavy endpoints (if needed)
  - Compression middleware (gzip) for large responses

- **Frontend**:
  - React Server Components (reduce client-side JavaScript)
  - Dynamic imports for heavy components (`next/dynamic`)
  - Image optimization (`next/image`)
  - Route prefetching (Next.js automatic)
  - Tailwind CSS JIT mode (minimal CSS bundle)

### Monitoring
- Lighthouse audits for frontend performance
- FastAPI built-in timing headers for API latency
- Neon query insights for slow database queries

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| **Authentication** | Better Auth + JWT in HttpOnly cookies | Native Next.js support, secure, stateless |
| **Database ORM** | SQLModel with UUIDs | Type-safe, unified models, globally unique IDs |
| **Frontend Pattern** | React Server Components default | Performance, SEO, reduced bundle size |
| **API Design** | RESTful with OpenAPI auto-docs | Industry standard, self-documenting |
| **Testing** | Pytest (backend), Vitest (frontend), Playwright (E2E) | Comprehensive coverage, fast, reliable |
| **Deployment** | Vercel + Railway/Render + Neon | Platform-optimized, cost-effective, scalable |
| **Performance** | Indexing, async, caching, lazy loading | Meet <200ms API, <2s page load targets |

---

## Next Steps

1. Create `data-model.md` with detailed SQLModel schemas
2. Generate `contracts/` with OpenAPI specification and API documentation
3. Write `quickstart.md` with development setup instructions
4. Update agent context with Phase II technology stack
5. Proceed to `/sp.tasks` for task breakdown
