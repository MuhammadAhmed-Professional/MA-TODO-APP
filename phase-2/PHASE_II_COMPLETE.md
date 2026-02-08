# Phase II: Full-Stack Web Application - COMPLETE ✅

## Overview

Phase II transforms the console todo app into a modern, multi-user full-stack web application with persistent storage and Better Auth authentication.

## Technology Stack

| Layer          | Technology                                |
| :------------- | :---------------------------------------- |
| Frontend       | Next.js 16+ (App Router), React 19        |
| Backend        | FastAPI 0.110+, Python 3.13+              |
| ORM            | SQLModel (SQLAlchemy + Pydantic)          |
| Database       | Neon Serverless PostgreSQL                |
| Authentication | Better Auth with JWT tokens (HS256)       |
| Styling        | Tailwind CSS 4+                           |
| Dev Tools      | Claude Code, Spec-Kit Plus                |

## Implemented Features (Basic Level)

✅ **1. Add Task** - Create new todo items with title and optional description
✅ **2. Delete Task** - Remove tasks from the list
✅ **3. Update Task** - Modify existing task details (toggle completion)
✅ **4. View Task List** - Display all tasks with filtering (all/pending/completed)
✅ **5. Mark as Complete** - Toggle task completion status

## Authentication Features

✅ **User Signup** - Better Auth email/password registration
✅ **User Login** - Better Auth email/password authentication
✅ **JWT Tokens** - HS256 signed tokens in HttpOnly cookies
✅ **Protected Routes** - Middleware-based route protection
✅ **User Isolation** - Each user only sees their own tasks
✅ **Session Management** - 15-minute access token expiry

## Architecture

### Frontend → Backend → Auth Server Flow

```
Frontend (Next.js)  →  Backend (FastAPI)  →  Auth Server (Better Auth)
Port 3000               Port 8000              Port 3001

User Action             Proxy/Business Logic    Authentication
↓                       ↓                       ↓
React Components  →     API Endpoints     →     Better Auth Handlers
HttpOnly Cookies  ←     JWT Validation    ←     JWT Generation
```

### Directory Structure

```
phase-2/
├── frontend/                      # Next.js 16 App
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── login/page.tsx     # Login form
│   │   │   ├── signup/page.tsx    # Signup form
│   │   │   └── dashboard/page.tsx # Task management (protected)
│   │   ├── components/
│   │   │   └── tasks/
│   │   │       ├── TaskForm.tsx   # Create/edit task form
│   │   │       ├── TaskCard.tsx   # Individual task display
│   │   │       ├── TaskList.tsx   # Task list container
│   │   │       └── EmptyState.tsx # No tasks placeholder
│   │   ├── lib/
│   │   │   ├── auth.ts            # Better Auth client (proxies to FastAPI)
│   │   │   └── api.ts             # API client with auth cookies
│   │   └── types/
│   │       ├── user.ts            # User type definitions
│   │       └── task.ts            # Task type definitions
│   ├── middleware.ts              # Route protection
│   └── package.json
│
├── backend/                       # FastAPI Server
│   ├── src/
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── api/
│   │   │   ├── auth.py            # Auth proxy endpoints
│   │   │   └── tasks.py           # Task CRUD endpoints
│   │   ├── models/
│   │   │   ├── user.py            # User SQLModel
│   │   │   └── task.py            # Task SQLModel
│   │   ├── services/
│   │   │   ├── auth_service.py    # Auth business logic
│   │   │   └── task_service.py    # Task business logic
│   │   ├── auth/
│   │   │   ├── jwt.py             # JWT creation/validation
│   │   │   └── dependencies.py    # FastAPI auth dependencies
│   │   └── db/
│   │       ├── session.py         # Database session management
│   │       └── migrations/        # Alembic migrations
│   └── pyproject.toml
│
└── auth-server/                   # Better Auth Server
    ├── src/
    │   ├── auth.ts                # Better Auth configuration
    │   ├── server.ts              # Express server
    │   └── db.ts                  # PostgreSQL connection
    └── package.json
```

## API Endpoints

### Authentication Endpoints (Backend Proxy)

| Method | Endpoint              | Description                               |
| :----- | :-------------------- | :---------------------------------------- |
| POST   | /api/auth/signup      | Create account (proxies to Better Auth)   |
| POST   | /api/auth/login       | Login (proxies to Better Auth)            |
| POST   | /api/auth/logout      | Logout (clears auth_token cookie)         |
| GET    | /api/auth/me          | Get current user (JWT validation)         |

### Task Endpoints (Protected with JWT)

| Method | Endpoint                   | Description              |
| :----- | :------------------------- | :----------------------- |
| GET    | /api/tasks                 | List all user's tasks    |
| POST   | /api/tasks                 | Create new task          |
| GET    | /api/tasks/{id}            | Get task by ID           |
| PUT    | /api/tasks/{id}            | Update task              |
| DELETE | /api/tasks/{id}            | Delete task              |
| PATCH  | /api/tasks/{id}/complete   | Toggle completion status |

## Database Schema

### Users Table (Better Auth)

| Column         | Type     | Description              |
| :------------- | :------- | :----------------------- |
| id             | UUID     | Primary key              |
| email          | STRING   | Unique, indexed          |
| name           | STRING   | User's display name      |
| emailVerified  | BOOLEAN  | Email verification flag  |
| createdAt      | DATETIME | Account creation time    |
| updatedAt      | DATETIME | Last update time         |

### Tasks Table

| Column       | Type     | Description                     |
| :----------- | :------- | :------------------------------ |
| id           | UUID     | Primary key                     |
| title        | STRING   | Task title (1-200 chars)        |
| description  | STRING   | Task description (max 2000)     |
| is_complete  | BOOLEAN  | Completion status (default: false) |
| user_id      | UUID     | Foreign key to users.id (indexed) |
| created_at   | DATETIME | Creation timestamp              |
| updated_at   | DATETIME | Last update timestamp           |

**Indexes:**
- `user_id` (fast task lookup by user)
- `is_complete` (fast filtering by status)

## Security Features

### Authentication Security

✅ **Password Hashing** - bcrypt (handled by Better Auth)
✅ **JWT Tokens** - HS256 signed with shared secret
✅ **HttpOnly Cookies** - Prevents XSS attacks
✅ **Secure Cookies** - HTTPS only in production
✅ **SameSite Cookies** - CSRF protection (lax mode)
✅ **Rate Limiting** - 5 login attempts per minute (backend)
✅ **Token Expiry** - 15 minutes (configurable)

### Input Validation

✅ **Pydantic Validation** - Automatic request validation
✅ **XSS Prevention** - HTML tags stripped from user input
✅ **SQL Injection Prevention** - SQLModel parameterized queries
✅ **CORS Configuration** - Whitelist frontend origins only

### Authorization

✅ **Ownership Checks** - Users can only access their own tasks
✅ **JWT Validation** - Every protected endpoint validates token
✅ **User Isolation** - Database queries filtered by user_id

## User Flow

### 1. Signup Flow

```
1. User fills signup form (name, email, password)
   → POST /api/auth/signup

2. Backend proxies to Better Auth
   → POST http://localhost:3001/api/auth/sign-up

3. Better Auth:
   - Hashes password with bcrypt
   - Creates user in PostgreSQL
   - Generates JWT token
   → Returns { user, session: { token } }

4. Backend:
   - Extracts JWT from session.token
   - Sets auth_token HttpOnly cookie
   → Returns user data

5. Frontend:
   - Stores cookie automatically
   → Redirects to /dashboard
```

### 2. Login Flow

```
1. User enters credentials
   → POST /api/auth/login

2. Backend proxies to Better Auth
   → POST http://localhost:3001/api/auth/sign-in/email

3. Better Auth:
   - Verifies password against hash
   - Generates JWT token
   → Returns { user, session: { token } }

4. Backend:
   - Sets auth_token cookie
   → Returns user data

5. Frontend:
   → Redirects to /dashboard
```

### 3. Task Management Flow

```
1. User visits /dashboard
   - Middleware checks auth_token cookie
   - If missing → Redirect to /login
   - If present → Allow access

2. Dashboard loads tasks
   → GET /api/tasks (with auth_token cookie)

3. Backend:
   - Validates JWT token
   - Extracts user_id from token
   - Queries tasks WHERE user_id = <current_user>
   → Returns filtered tasks

4. User creates task
   → POST /api/tasks { title, description }

5. Backend:
   - Validates JWT
   - Creates task with user_id from token
   → Returns created task

6. Frontend:
   - Adds new task to state
   - Displays in task list
```

## Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
```

### Backend (.env)

```env
DATABASE_URL=postgresql://neondb_owner:...@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
AUTH_SERVER_URL=http://localhost:3001
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
CORS_ORIGINS=http://localhost:3000,https://talal-s-tda.vercel.app
ENVIRONMENT=production
```

### Auth Server (.env)

```env
DATABASE_URL=postgresql://neondb_owner:...@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
BETTER_AUTH_URL=http://localhost:3001
NODE_ENV=development
PORT=3001
```

**CRITICAL**: `BETTER_AUTH_SECRET` (auth-server) MUST match `JWT_SECRET` (backend).

## Running Locally

### Prerequisites

- Node.js 20+
- Python 3.13+
- PostgreSQL (Neon account)
- UV (Python package manager)
- pnpm (Node package manager)

### 1. Start Auth Server (Port 3001)

```bash
cd phase-2/auth-server
npm install
npm run dev
```

### 2. Start Backend (Port 8000)

```bash
cd phase-2/backend
uv sync
uv run uvicorn src.main:app --reload
```

### 3. Start Frontend (Port 3000)

```bash
cd phase-2/frontend
npm install --legacy-peer-deps
npm run dev
```

### 4. Test the Application

1. Visit http://localhost:3000
2. Click "Sign Up" → Create account
3. Redirected to /dashboard
4. Click "+ Add New Task"
5. Fill form → Submit
6. Task appears in list
7. Click checkbox → Mark complete
8. Click delete icon → Remove task
9. Use filter tabs (All/Pending/Completed)
10. Sign out → Redirected to home page

## Deployment Instructions

### Frontend (Vercel)

```bash
cd phase-2/frontend

# Build test
npm run build

# Deploy to Vercel
vercel --prod

# Configure environment variables in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://talal-s-tda-production.up.railway.app
```

### Backend (Railway)

```bash
cd phase-2/backend

# Deploy via Railway CLI or GitHub integration
railway up

# Configure environment variables in Railway dashboard:
# DATABASE_URL=<neon-connection-string>
# AUTH_SERVER_URL=https://auth-server-production-8251.up.railway.app
# JWT_SECRET=<same-as-auth-server>
# CORS_ORIGINS=https://talal-s-tda.vercel.app
# ENVIRONMENT=production
```

### Auth Server (Railway)

```bash
cd phase-2/auth-server

# Deploy via Railway CLI
railway up

# Configure environment variables:
# DATABASE_URL=<neon-connection-string>
# BETTER_AUTH_SECRET=<same-as-backend-jwt-secret>
# BETTER_AUTH_URL=https://auth-server-production-8251.up.railway.app
# NODE_ENV=production
# PORT=3001
```

## Testing Checklist

- [ ] User can sign up with email/password
- [ ] User can log in with credentials
- [ ] User is redirected to dashboard after login
- [ ] Unauthenticated users are redirected to login
- [ ] User can create a new task
- [ ] Task appears in "All" and "Pending" tabs
- [ ] User can mark task as complete
- [ ] Completed task moves to "Completed" tab
- [ ] User can toggle task back to incomplete
- [ ] User can delete a task
- [ ] Deleted task is removed from list
- [ ] Empty state shows when no tasks exist
- [ ] Stats (Total/Pending/Completed) update correctly
- [ ] User can sign out
- [ ] Signed out user cannot access dashboard
- [ ] Different users see only their own tasks
- [ ] Form validation prevents empty titles
- [ ] Form validation enforces character limits

## Phase II Achievements

✅ **Full-Stack Architecture** - Separated frontend, backend, and auth concerns
✅ **Better Auth Integration** - Production-ready authentication with JWT
✅ **User Isolation** - Multi-user support with ownership verification
✅ **Persistent Storage** - PostgreSQL with Neon Serverless
✅ **Type Safety** - TypeScript (frontend) + Pydantic/SQLModel (backend)
✅ **Responsive UI** - Tailwind CSS with dark mode support
✅ **Security** - HttpOnly cookies, CORS, rate limiting, input validation
✅ **Scalability** - Stateless JWT, connection pooling, indexed queries
✅ **Developer Experience** - Claude Code, Spec-Kit Plus, hot reload

## Next: Phase III (AI Chatbot)

Phase III will add conversational AI interface using:
- OpenAI Agents SDK
- Official MCP SDK
- Stateless chat endpoint
- Conversation history (database-persisted)
- Natural language task management

Stay tuned! 🚀
