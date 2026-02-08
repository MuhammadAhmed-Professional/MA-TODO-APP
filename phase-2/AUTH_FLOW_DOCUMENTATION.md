# Authentication Flow Documentation

## Overview

This document explains how authentication works in the Phase II Todo App using Better Auth.

## Architecture

```
Frontend (Next.js on Vercel port 3000)
    ↓ HTTP POST /api/auth/signup
Backend (FastAPI on Railway port 8000)
    ↓ HTTP POST to auth-server/auth/sign-up
Auth Server (Better Auth on Railway port 3001)
    ↓ Better Auth SDK handles authentication
Neon PostgreSQL Database
    - user table (Better Auth managed)
    - session table (Better Auth managed)
```

## Component Responsibilities

### 1. Frontend (Next.js)
- **Role**: User interface and client-side logic
- **Responsibilities**:
  - Collect user input (email, name, password)
  - Call backend API endpoints
  - Store JWT tokens (httpOnly cookies)
  - Handle authentication state

**Signup Request**:
```typescript
// Frontend makes request to backend
const response = await fetch('http://localhost:8000/api/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    name: 'User Name',
    password: 'SecurePass123!'
  })
});
```

### 2. Backend (FastAPI)
- **Role**: Business logic orchestrator and API gateway
- **Responsibilities**:
  - Proxy authentication requests to auth-server
  - Validate JWT tokens from auth-server
  - Handle task CRUD operations (authorized)
  - Manage CORS and security

**Backend Proxies to Auth Server**:
```python
# phase-2/backend/src/api/routes/auth.py
import httpx

AUTH_SERVER_URL = "https://auth-server-production-cd0e.up.railway.app"

@router.post("/signup")
async def signup(user_data: UserCreate):
    """
    Proxy signup request to Better Auth server
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVER_URL}/auth/sign-up",
            json={
                "email": user_data.email,
                "name": user_data.name,
                "password": user_data.password
            }
        )
        return response.json()
```

### 3. Auth Server (Better Auth)
- **Role**: Authentication authority using Better Auth SDK
- **Responsibilities**:
  - Hash passwords (bcrypt)
  - Generate JWT tokens
  - Manage sessions
  - Create/validate users in database
  - Set httpOnly cookies

**Better Auth Endpoints**:
- `POST /auth/sign-up` - Create account
- `POST /auth/sign-in/email` - Login
- `POST /auth/sign-out` - Logout
- `GET /auth/get-session` - Current user

**Better Auth Configuration** (`phase-2/auth-server/src/auth.ts`):
```typescript
export const auth = betterAuth({
  appName: "Phase II Todo Application",
  baseURL: process.env.BETTER_AUTH_URL,
  secret: process.env.BETTER_AUTH_SECRET,  // JWT secret

  database: new Pool({
    connectionString: process.env.DATABASE_URL
  }),

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 6,
    requireEmailVerification: false,
    autoSignIn: true
  },

  session: {
    expiresIn: 60 * 15,  // 15 minutes
    updateAge: 60 * 5
  }
});
```

### 4. Database (Neon PostgreSQL)
- **Role**: Persistent storage
- **Tables**:
  - `user` - User accounts (managed by Better Auth)
    - id (UUID)
    - email (unique)
    - name
    - email_verified (boolean)
    - image (nullable)
    - created_at
    - updated_at
  - `session` - Active sessions (managed by Better Auth)
    - id (UUID)
    - expires_at (timestamp)
    - token (text)
    - user_id (foreign key)
  - `todo` - User tasks (managed by backend)
    - id (UUID)
    - user_id (foreign key)
    - title
    - completed
    - created_at
    - updated_at

## Complete Signup Flow (Step-by-Step)

### Step 1: User submits signup form
```
User fills form:
  - Email: user@example.com
  - Name: John Doe
  - Password: SecurePass123!

Frontend validates input (client-side)
```

### Step 2: Frontend → Backend
```http
POST http://localhost:8000/api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!"
}
```

### Step 3: Backend → Auth Server
```http
POST https://auth-server-production-cd0e.up.railway.app/auth/sign-up
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePass123!"
}
```

### Step 4: Auth Server processes with Better Auth
```
1. Better Auth validates input
2. Checks if email already exists in database
3. Hashes password with bcrypt
4. Creates user in Neon PostgreSQL 'user' table
5. Generates JWT token with secret
6. Creates session in 'session' table
7. Sets httpOnly cookie with JWT
```

### Step 5: Auth Server → Backend
```http
HTTP 200 OK
Set-Cookie: better-auth.session_token=<JWT>; HttpOnly; Secure; SameSite=Lax
Content-Type: application/json

{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "image": null,
    "createdAt": "2025-12-21T12:00:00Z",
    "updatedAt": "2025-12-21T12:00:00Z"
  },
  "session": {
    "token": "<JWT>",
    "expiresAt": "2025-12-21T12:15:00Z"
  }
}
```

### Step 6: Backend → Frontend
```http
HTTP 200 OK
Set-Cookie: better-auth.session_token=<JWT>; HttpOnly; Secure; SameSite=Lax
Content-Type: application/json

{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "message": "Signup successful"
}
```

### Step 7: Frontend updates UI
```
- Store session state in React context/state
- Redirect to dashboard
- Show welcome message
- Cookie is automatically included in future requests
```

## Login Flow (Similar to Signup)

### Login Request
```http
POST /auth/sign-in/email
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Better Auth validates:
1. Find user by email in database
2. Compare password hash with bcrypt
3. If valid, generate JWT and create session
4. Return user data + session token

## Protected Endpoints

### Backend validates JWT for protected routes
```python
# phase-2/backend/src/auth/dependencies.py
from jose import jwt, JWTError

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Validate JWT token from auth-server
    CRITICAL: JWT_SECRET must match BETTER_AUTH_SECRET
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,  # Must match Better Auth secret
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Protected task endpoints
```python
@router.get("/tasks")
async def get_tasks(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get all tasks for authenticated user"""
    tasks = db.exec(
        select(Task).where(Task.user_id == current_user)
    ).all()
    return tasks
```

## Environment Variables

### Auth Server (.env)
```env
DATABASE_URL=postgresql://...?sslmode=require&channel_binding=require
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
BETTER_AUTH_URL=https://auth-server-production-cd0e.up.railway.app
PORT=3001
NODE_ENV=production
CORS_ORIGINS=http://localhost:3000,https://frontend-six-coral-90.vercel.app
```

### Backend (.env)
```env
DATABASE_URL=postgresql://...?sslmode=require&channel_binding=require
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
JWT_ALGORITHM=HS256
AUTH_SERVER_URL=https://auth-server-production-cd0e.up.railway.app
CORS_ORIGINS=http://localhost:3000,https://frontend-six-coral-90.vercel.app
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production:
NEXT_PUBLIC_API_URL=https://backend-production.up.railway.app
```

## Security Considerations

1. **JWT Secret Matching**: `JWT_SECRET` (backend) MUST equal `BETTER_AUTH_SECRET` (auth-server)
2. **HTTPS Only**: Use HTTPS in production for secure cookie transmission
3. **HttpOnly Cookies**: Prevents XSS attacks from accessing tokens
4. **SameSite=Lax**: Prevents CSRF attacks
5. **Password Hashing**: bcrypt with 10 rounds (Better Auth default)
6. **Database Connection**: SSL mode required for Neon PostgreSQL

## Troubleshooting

### Issue: "Failed to initialize database adapter"
- **Cause**: DATABASE_URL missing or incorrect in auth-server
- **Fix**: Ensure DATABASE_URL includes `?sslmode=require&channel_binding=require`

### Issue: "Invalid token" when calling protected endpoints
- **Cause**: JWT_SECRET mismatch between backend and auth-server
- **Fix**: Verify both use the same secret value

### Issue: CORS errors
- **Cause**: Origin not whitelisted
- **Fix**: Add frontend URL to CORS_ORIGINS in both backend and auth-server

### Issue: User can signup but can't create tasks
- **Cause**: JWT not being sent or validated correctly
- **Fix**: Check cookie is being set and sent in requests, verify token validation logic

## Next Steps

1. ✅ Update local .env files with correct DATABASE_URL
2. ⏳ Set Railway environment variables (manual)
3. ⏳ Update backend to proxy auth requests to auth-server
4. ⏳ Test signup flow end-to-end
5. ⏳ Deploy backend to Railway
6. ⏳ Test production deployment

## Useful Commands

```bash
# Check auth-server logs
railway logs --service ac8b8441-def7-49e9-af64-47dd171ae1c2

# Test auth-server health
curl https://auth-server-production-cd0e.up.railway.app/health

# Test signup endpoint
curl -X POST https://auth-server-production-cd0e.up.railway.app/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"password123"}'

# Test backend health (once deployed)
curl https://backend-production.up.railway.app/health

# Check database tables
psql $DATABASE_URL -c "\dt"
```
