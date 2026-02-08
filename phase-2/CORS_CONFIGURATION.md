# CORS Configuration Guide

**Last Updated**: 2025-12-20
**Purpose**: Ensure all services can communicate across origins

---

## Overview

CORS (Cross-Origin Resource Sharing) is required because:
- Frontend (localhost:3000) calls Auth Server (localhost:3001 or Railway)
- Frontend (localhost:3000) calls Backend API (localhost:8000 or Railway)
- All services need to share cookies (credentials)

---

## Current CORS Setup

### Auth Server (Better Auth)
**File**: `phase-2/auth-server/src/server.ts`

```typescript
const CORS_ORIGINS = process.env.CORS_ORIGINS?.split(",") || [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
];

app.use(
  cors({
    origin: CORS_ORIGINS,
    credentials: true, // Required for cookies
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);
```

**Environment Variable** (`.env`):
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**For Production** (Railway):
```env
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app
```

**Status**: ✓ Configured correctly

---

### Backend API (FastAPI)
**File**: `phase-2/backend/src/main.py`

```python
# CORS Configuration from environment variables
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Environment Variable** (`.env`):
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://auth-server-production-8251.up.railway.app
```

**For Production** (Railway):
```env
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app,https://auth-server-production-8251.up.railway.app
```

**Status**: ✓ Configured correctly

---

### Frontend (Next.js)
**No CORS configuration needed** - Frontend makes requests, doesn't receive them.

**Important**: Frontend fetch requests **must** include `credentials: "include"`

**File**: `phase-2/frontend/src/lib/api.ts`
```typescript
const response = await fetch(url, {
  credentials: "include", // ✓ Includes cookies
  // ...
});
```

**File**: `phase-2/frontend/src/lib/auth.ts`
```typescript
export const authClient = createAuthClient({
  fetchOptions: {
    credentials: "include", // ✓ Includes cookies
  },
});
```

**Status**: ✓ Configured correctly

---

## Testing CORS

### 1. Test Auth Server CORS

**Preflight Request** (OPTIONS):
```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  http://localhost:3001/auth/sign-in/email
```

**Expected Response Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

**Actual POST Request**:
```bash
curl -X POST \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -v \
  http://localhost:3001/auth/sign-in/email
```

**Expected Response Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Set-Cookie: auth_token=...; HttpOnly; Secure; SameSite=Strict
```

### 2. Test Backend API CORS

**Preflight Request**:
```bash
curl -X OPTIONS \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v \
  http://localhost:8000/api/tasks
```

**Expected Response Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE
```

**Actual GET Request**:
```bash
curl -X GET \
  -H "Origin: http://localhost:3000" \
  -H "Cookie: auth_token=..." \
  -v \
  http://localhost:8000/api/tasks
```

**Expected Response Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

### 3. Browser DevTools Verification

1. Open frontend in browser (http://localhost:3000)
2. Open DevTools (F12)
3. Go to Network tab
4. Perform login action
5. Check request headers:
   ```
   Origin: http://localhost:3000
   Cookie: auth_token=...
   ```
6. Check response headers:
   ```
   Access-Control-Allow-Origin: http://localhost:3000
   Access-Control-Allow-Credentials: true
   Set-Cookie: auth_token=...; HttpOnly
   ```

---

## Common CORS Errors

### Error 1: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Symptom**:
```
Access to fetch at 'http://localhost:3001/auth/sign-in/email' from origin
'http://localhost:3000' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Cause**: Server not configured to allow frontend origin

**Fix**:
1. Check `CORS_ORIGINS` environment variable includes frontend URL
2. Verify server is reading environment variable correctly
3. Restart server after changing `.env`

**Verify**:
```bash
# Check if env var is set
echo $CORS_ORIGINS  # Linux/Mac
echo %CORS_ORIGINS%  # Windows

# Check if server is using it
curl -v http://localhost:3001/health | grep -i cors
```

---

### Error 2: "Credentials flag is 'true', but cookie not sent"

**Symptom**: Login succeeds but subsequent requests return 401 (not authenticated)

**Cause**: Frontend not including `credentials: "include"`

**Fix**:
Check all fetch calls include credentials:
```typescript
// ✓ GOOD
fetch(url, { credentials: "include" })

// ❌ BAD
fetch(url)  // Cookies not sent!
```

**Verify**:
```javascript
// In browser DevTools console
fetch("http://localhost:3001/auth/get-session", {
  credentials: "include"
}).then(r => r.json()).then(console.log)
```

---

### Error 3: "CORS policy: Credentials mode is 'include', but origin is '*'"

**Symptom**:
```
CORS policy: The value of the 'Access-Control-Allow-Origin' header in the
response must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Cause**: Server using wildcard `allow_origins=["*"]` with `allow_credentials=True`

**Fix**:
```python
# ❌ BAD - Cannot use wildcard with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Not allowed with credentials
    allow_credentials=True,
)

# ✓ GOOD - Specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://frontend.com"],
    allow_credentials=True,
)
```

---

### Error 4: "Blocked by CORS: SameSite attribute"

**Symptom**: Cookies not sent in cross-origin requests

**Cause**: Cookie `SameSite` set to `Strict` or `Lax` prevents cross-origin

**Fix**:
```python
# Backend: Set SameSite=None for cross-origin (HTTPS required)
response.set_cookie(
    key="auth_token",
    value=token,
    httponly=True,
    secure=True,  # HTTPS only
    samesite="none",  # Allow cross-origin (requires HTTPS)
)

# For local development (HTTP):
response.set_cookie(
    key="auth_token",
    value=token,
    httponly=True,
    secure=False,  # Allow HTTP locally
    samesite="lax",  # Less strict for local
)
```

**Note**: For production (HTTPS), use `samesite="strict"` for better security.

---

## Production CORS Configuration

### Railway Deployment (Auth Server + Backend)

**Auth Server Environment Variables** (Railway dashboard):
```env
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
BETTER_AUTH_URL=https://auth-server-production-8251.up.railway.app
```

**Backend Environment Variables** (Railway dashboard):
```env
CORS_ORIGINS=https://your-frontend.vercel.app,https://auth-server-production-8251.up.railway.app,http://localhost:3000
```

**Why include localhost**: Allows testing production APIs from local frontend

---

### Vercel Deployment (Frontend)

**Environment Variables** (Vercel dashboard):
```env
NEXT_PUBLIC_AUTH_URL=https://auth-server-production-8251.up.railway.app
NEXT_PUBLIC_API_URL=https://your-backend.up.railway.app
```

**No CORS configuration needed** - Frontend makes requests, doesn't receive them

---

## CORS Checklist

Before deploying:

- [ ] Auth server `.env` has correct `CORS_ORIGINS`
- [ ] Backend `.env` has correct `CORS_ORIGINS` (includes auth server)
- [ ] Frontend uses `credentials: "include"` in all fetch calls
- [ ] Auth server sets `Access-Control-Allow-Credentials: true`
- [ ] Backend sets `Access-Control-Allow-Credentials: true`
- [ ] Cookies have correct `SameSite` attribute
- [ ] Cookies have correct `Secure` attribute (HTTPS in prod)
- [ ] Tested with browser DevTools Network tab
- [ ] Tested with curl commands
- [ ] No wildcard (`*`) in `allow_origins` when using credentials

---

## CORS Security Best Practices

1. **Never use wildcard with credentials**:
   ```python
   # ❌ NEVER DO THIS
   allow_origins=["*"]
   allow_credentials=True
   ```

2. **Specify exact origins**:
   ```env
   CORS_ORIGINS=https://app.example.com,https://www.example.com
   ```

3. **Use environment variables** (don't hardcode origins):
   ```python
   # ✓ GOOD - Read from .env
   CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")
   ```

4. **Validate origin dynamically** (advanced):
   ```python
   def validate_origin(origin: str) -> bool:
       allowed_patterns = [
           r"https://.*\.vercel\.app$",
           r"http://localhost:\d+$"
       ]
       return any(re.match(pattern, origin) for pattern in allowed_patterns)
   ```

5. **Use HTTPS in production**:
   ```python
   # Production cookie settings
   response.set_cookie(
       secure=True,  # HTTPS only
       samesite="strict",  # Prevent CSRF
       httponly=True  # Prevent XSS
   )
   ```

---

## Resources

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [FastAPI CORS Middleware](https://fastapi.tiangolo.com/tutorial/cors/)
- [Express CORS Package](https://expressjs.com/en/resources/middleware/cors.html)
- [SameSite Cookie Attribute](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
- [Better Auth CORS Config](https://better-auth.com/docs/concepts/cors)
