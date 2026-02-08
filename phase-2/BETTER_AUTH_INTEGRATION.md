# Better Auth Integration Summary

## Architecture Overview

The authentication system uses a **3-tier architecture**:

```
Frontend (Next.js)  →  Backend (FastAPI)  →  Auth Server (Better Auth)
Port 3000               Port 8000              Port 3001
```

### Why This Architecture?

1. **Separation of Concerns**: Authentication logic is isolated in the Better Auth server
2. **Backend Control**: FastAPI can validate tokens and add business logic
3. **Security**: JWT secrets are managed server-side only
4. **Flexibility**: Can swap auth providers without changing frontend code

## Components Implemented

### 1. Frontend (Next.js 16)

**Location**: `phase-2/frontend/`

**Key Files**:
- `src/lib/auth.ts` - Better Auth client (configured to use FastAPI backend as proxy)
- `src/lib/api.ts` - API client with auth cookie handling
- `src/types/user.ts` - User type definitions (match backend)
- `src/types/task.ts` - Task type definitions (match backend)
- `middleware.ts` - Route protection (dashboard requires auth)
- `src/app/login/page.tsx` - Login form
- `src/app/signup/page.tsx` - Signup form
- `src/app/dashboard/page.tsx` - Protected dashboard page

**Architecture Decision**:
```typescript
// ✅ CORRECT: Frontend → FastAPI Backend
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL, // http://localhost:8000
});

// ❌ WRONG: Frontend → Better Auth directly
// baseURL: process.env.NEXT_PUBLIC_AUTH_URL, // http://localhost:3001
```

**Why**: The FastAPI backend acts as a proxy, allowing it to:
- Add rate limiting (already implemented with slowapi)
- Log authentication events
- Validate JWT tokens for protected endpoints
- Add custom logic before/after auth operations

### 2. Backend (FastAPI)

**Location**: `phase-2/backend/`

**Key Files**:
- `src/api/auth.py` - Auth proxy endpoints
  - POST `/api/auth/signup` → Better Auth POST `/api/auth/sign-up`
  - POST `/api/auth/login` → Better Auth POST `/api/auth/sign-in/email`
  - POST `/api/auth/logout` → Clears auth_token cookie
  - GET `/api/auth/me` → Better Auth GET `/api/auth/get-session`
- `src/auth/dependencies.py` - JWT validation for protected routes
- `src/models/user.py` - User model (SQLModel, matches database schema)

**Cookie Handling**:
```python
# Backend sets auth_token cookie from Better Auth response
response.set_cookie(
    key="auth_token",
    value=jwt_token,  # From Better Auth session.token
    httponly=True,
    secure=True,
    samesite="lax",
    max_age=15 * 60,  # 15 minutes
)
```

### 3. Auth Server (Better Auth)

**Location**: `phase-2/auth-server/`

**Key Files**:
- `src/auth.ts` - Better Auth configuration
- `src/server.ts` - Express server with Better Auth handlers
- `src/db.ts` - PostgreSQL connection pool

**Configuration**:
```typescript
export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!, // MUST match backend JWT_SECRET
  database: new Pool({ connectionString: process.env.DATABASE_URL }),
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 6,
    autoSignIn: true,
  },
  session: {
    expiresIn: 60 * 15, // 15 minutes
  },
});
```

## Request Flow Examples

### Signup Flow

```
1. User fills signup form (frontend/src/app/signup/page.tsx)
   → POST { name, email, password }

2. Frontend calls Better Auth client (frontend/src/lib/auth.ts)
   → signUp({ name, email, password })

3. Better Auth client sends to FastAPI backend
   → POST http://localhost:8000/api/auth/signup

4. FastAPI proxies to Better Auth server (backend/src/api/auth.py)
   → POST http://localhost:3001/api/auth/sign-up

5. Better Auth server:
   - Hashes password with bcrypt
   - Creates user in PostgreSQL (users table)
   - Generates JWT token
   → Returns { user, session: { token, expiresAt } }

6. FastAPI backend:
   - Receives response from Better Auth
   - Extracts JWT token from session.token
   - Sets auth_token cookie
   → Returns user data to frontend

7. Frontend:
   - Receives user data
   - auth_token cookie automatically stored by browser
   → Redirects to /dashboard
```

### Login Flow

```
1. User enters credentials (frontend/src/app/login/page.tsx)
   → POST { email, password }

2. Frontend → FastAPI
   → POST http://localhost:8000/api/auth/login

3. FastAPI → Better Auth
   → POST http://localhost:3001/api/auth/sign-in/email

4. Better Auth:
   - Verifies password against bcrypt hash
   - Generates JWT token
   → Returns { user, session: { token, expiresAt } }

5. FastAPI:
   - Sets auth_token cookie
   → Returns user data

6. Frontend:
   - Stores auth_token cookie
   → Redirects to /dashboard
```

### Protected API Request Flow

```
1. User visits /dashboard (frontend/src/app/dashboard/page.tsx)

2. Middleware checks for auth_token cookie (frontend/middleware.ts)
   - If missing → Redirect to /login
   - If present → Allow access

3. Dashboard component calls getCurrentUser() (frontend/src/lib/auth.ts)
   → GET http://localhost:8000/api/auth/me

4. FastAPI receives request with auth_token cookie
   - Calls get_current_user dependency (backend/src/auth/dependencies.py)
   - Validates JWT token (checks signature with JWT_SECRET)
   - Decodes user_id from token payload
   - Fetches user from database
   → Returns user data

5. Frontend displays user information
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

**CRITICAL**: `BETTER_AUTH_SECRET` (auth-server) MUST match `JWT_SECRET` (backend) for token validation to work.

## Database Schema

Better Auth creates these tables in PostgreSQL:

```sql
-- User table
CREATE TABLE "user" (
  id TEXT PRIMARY KEY,           -- UUID
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  emailVerified BOOLEAN DEFAULT FALSE,
  image TEXT,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session table
CREATE TABLE "session" (
  id TEXT PRIMARY KEY,
  userId TEXT NOT NULL REFERENCES "user"(id),
  expiresAt TIMESTAMP NOT NULL,
  ipAddress TEXT,
  userAgent TEXT,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Account table (for OAuth providers, future)
CREATE TABLE "account" (
  id TEXT PRIMARY KEY,
  userId TEXT NOT NULL REFERENCES "user"(id),
  accountId TEXT NOT NULL,
  providerId TEXT NOT NULL,
  accessToken TEXT,
  refreshToken TEXT,
  expiresAt TIMESTAMP,
  createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Features

1. **Password Hashing**: bcrypt (handled by Better Auth)
2. **JWT Tokens**: HS256 signed with shared secret
3. **HttpOnly Cookies**: Prevents XSS attacks
4. **Secure Cookies**: HTTPS only in production
5. **SameSite Cookies**: CSRF protection (lax mode)
6. **Rate Limiting**: 5 login attempts per minute (backend)
7. **Token Expiry**: 15 minutes (configurable)

## Testing the Integration

### Local Development

1. **Start Auth Server**:
```bash
cd phase-2/auth-server
npm install
npm run dev  # Port 3001
```

2. **Start Backend**:
```bash
cd phase-2/backend
uv sync
uv run uvicorn src.main:app --reload  # Port 8000
```

3. **Start Frontend**:
```bash
cd phase-2/frontend
npm install --legacy-peer-deps
npm run dev  # Port 3000
```

4. **Test Flow**:
   - Visit http://localhost:3000
   - Click "Sign Up"
   - Create account → Should redirect to /dashboard
   - Sign out → Should redirect to /
   - Sign in with same credentials → Should work

### Production Deployment

**Auth Server**: Railway (https://auth-server-production-8251.up.railway.app)
**Backend**: Railway (https://talal-s-tda-production.up.railway.app)
**Frontend**: Vercel (https://talal-s-tda.vercel.app)

**Environment Variables**:
- Frontend `NEXT_PUBLIC_API_URL` → Backend Railway URL
- Backend `AUTH_SERVER_URL` → Auth Server Railway URL
- Both backend and auth-server use same `DATABASE_URL` and `JWT_SECRET`

## Known Issues & Solutions

### Issue 1: Vitest Peer Dependency Conflict
**Error**: Better Auth 1.4.7 requires vitest@^4.0.15, but we have vitest@3.2.4

**Solution**: Install with `--legacy-peer-deps`:
```bash
npm install --legacy-peer-deps
```

**Future Fix**: Upgrade to vitest 4.x when stable

### Issue 2: CORS Errors in Development
**Symptom**: Frontend can't connect to backend

**Solution**: Ensure `CORS_ORIGINS` in backend includes `http://localhost:3000`

### Issue 3: 401 Unauthorized on Protected Routes
**Symptom**: Dashboard redirects to login even after signup/login

**Causes**:
1. JWT_SECRET mismatch between backend and auth-server
2. Cookie not being set (check browser DevTools → Application → Cookies)
3. Cookie SameSite issues (use "lax" for cross-origin in dev)

**Solution**: Verify environment variables and check browser console for errors

## Next Steps

- [ ] Implement task CRUD endpoints (backend)
- [ ] Create task management UI (frontend)
- [ ] Add password reset flow
- [ ] Add email verification (optional)
- [ ] Add OAuth providers (Google, GitHub)
- [ ] Implement refresh tokens (longer sessions)
- [ ] Add user profile editing
- [ ] Add user avatar upload
- [ ] Implement admin panel
- [ ] Add audit logging (who did what when)

## References

- **Better Auth Docs**: https://better-auth.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs
- **Backend Auth Code**: `phase-2/backend/src/api/auth.py`
- **Frontend Auth Code**: `phase-2/frontend/src/lib/auth.ts`
- **Auth Server Code**: `phase-2/auth-server/src/auth.ts`
