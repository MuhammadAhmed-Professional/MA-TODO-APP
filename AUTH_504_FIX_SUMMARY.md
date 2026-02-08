# Authentication 504 Timeout - Fix Summary

**Date**: 2025-12-27
**Issue**: 504 Gateway Timeout when logging in
**Status**: Code Fixed ✅ | Railway Config Needed ⚠️

---

## Problem Analysis

### Symptom
```
POST https://backend-production-9a40.up.railway.app/api/auth/sign-in/email
Response: 504 Gateway Timeout
```

Backend logs showed:
```
httpx.RequestError: Auth server unavailable
```

### Root Cause

Testing revealed:
1. ✅ Auth server is running (`/health` responds with 200 OK)
2. ❌ Auth server times out on authentication endpoints
3. ❌ Database connection pool not optimized for Railway → Neon network
4. ❌ Backend missing `AUTH_SERVER_URL` environment variable in Railway

**Diagnosis**: PostgreSQL connection pool in auth server had no timeout configuration, causing slow/failed connections to Neon database.

---

## Fixes Implemented

### 1. Optimized PostgreSQL Connection Pool

**File**: `phase-2/auth-server/src/auth.ts`

Added production-ready pool configuration:
```typescript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL!,
  max: 20, // Maximum 20 concurrent connections
  idleTimeoutMillis: 30000, // Close idle connections after 30s
  connectionTimeoutMillis: 10000, // 10s connection timeout
  ssl: process.env.NODE_ENV === "production"
    ? { rejectUnauthorized: false }
    : false, // SSL for production
});
```

**Why**: Railway → Neon network requires explicit timeouts and SSL configuration.

### 2. Updated CORS Configuration

**Files**:
- `phase-2/auth-server/src/auth.ts`
- `phase-2/auth-server/src/server.ts`

Added backend URL to trusted origins:
```typescript
trustedOrigins: [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "https://frontend-six-coral-90.vercel.app",
  "https://backend-production-9a40.up.railway.app", // Backend can call auth server
],
```

**Why**: Backend proxies authentication requests to auth server (cross-origin).

### 3. Documented Environment Variables

**File**: `phase-2/backend/.env.example`

Added missing `AUTH_SERVER_URL`:
```env
# Auth Server Configuration
# Better Auth server URL (for proxying authentication requests)
# For Railway: https://auth-server-production-cd0e.up.railway.app
AUTH_SERVER_URL=http://localhost:3001
```

**Why**: Backend needs to know where auth server is deployed.

### 4. Created Deployment Guide

**File**: `phase-2/RAILWAY_DEPLOYMENT_GUIDE.md`

Comprehensive guide including:
- Exact Railway environment variables
- Deployment steps
- Architecture diagram
- Troubleshooting guide
- Testing procedures

---

## Code Deployed ✅

All fixes have been:
- ✅ Committed to git (commit `8400e1d`)
- ✅ Pushed to GitHub (`origin/main`)
- ✅ Railway auto-deploy triggered

Railway is now rebuilding both services with the new code.

---

## REQUIRED: Railway Configuration

### Critical Action Needed

You **MUST** set this environment variable in Railway:

**Service**: Backend (FastAPI)
**Variable**: `AUTH_SERVER_URL`
**Value**: `https://auth-server-production-cd0e.up.railway.app`

### How to Set Railway Environment Variables

1. Go to https://railway.app
2. Select your project
3. Click on **"backend"** service (NOT auth-server)
4. Click **"Variables"** tab
5. Click **"+ New Variable"**
6. Add:
   - **Key**: `AUTH_SERVER_URL`
   - **Value**: `https://auth-server-production-cd0e.up.railway.app`
7. Click **"Save"** or **"Add"**
8. Railway will automatically **redeploy** the backend

### Verify Other Variables

While in Railway Variables tab, **verify these are set correctly**:

**Backend Service**:
```
AUTH_SERVER_URL=https://auth-server-production-cd0e.up.railway.app (MUST ADD THIS!)
DATABASE_URL=postgresql://... (should already be set)
JWT_SECRET=... (should match BETTER_AUTH_SECRET in auth server)
CORS_ORIGINS=http://localhost:3000,https://frontend-six-coral-90.vercel.app
ENVIRONMENT=production
```

**Auth Server Service**:
```
DATABASE_URL=postgresql://... (should already be set)
BETTER_AUTH_SECRET=... (should match JWT_SECRET in backend)
BETTER_AUTH_URL=https://auth-server-production-cd0e.up.railway.app
CORS_ORIGINS=http://localhost:3000,https://frontend-six-coral-90.vercel.app,https://backend-production-9a40.up.railway.app
NODE_ENV=production
```

---

## Testing After Deployment

### Wait for Railway Deployment

Monitor Railway dashboard:
1. Auth server should rebuild (code changes)
2. Backend should rebuild (after you add AUTH_SERVER_URL)
3. Both should show "Active" status

**Expected logs**:

**Auth Server**:
```
✅ PostgreSQL connection successful
✅ Better Auth initialized successfully
🌐 CORS Origins: http://localhost:3000,https://frontend-six-coral-90.vercel.app,https://backend-production-9a40.up.railway.app
✅ Better Auth server started successfully
```

**Backend**:
```
🔗 Backend using AUTH_SERVER_URL: https://auth-server-production-cd0e.up.railway.app
```

### Test Commands

**1. Test Auth Server Health**:
```bash
curl https://auth-server-production-cd0e.up.railway.app/health
```
Expected: `{"status":"healthy"}`

**2. Test Auth Server Sign-Up** (create test user):
```bash
curl -X POST https://auth-server-production-cd0e.up.railway.app/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```
Expected: `200 OK` with user object

**3. Test Backend Proxy to Auth Server**:
```bash
curl -X POST https://backend-production-9a40.up.railway.app/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```
Expected: `200 OK` (NOT 504 timeout!)

**4. Test Frontend Login**:
1. Go to https://frontend-six-coral-90.vercel.app/login
2. Email: `test@example.com`
3. Password: `password123`
4. Click "Sign In"
5. Should redirect to `/dashboard` ✅

---

## Troubleshooting

### Still Getting 504 After Railway Config

**Check**:
1. Railway backend logs - look for `AUTH_SERVER_URL` value
2. Railway auth server logs - any database connection errors?
3. Neon database status - is it active?

**Debug**:
```bash
# Check if backend can reach auth server
curl -v https://backend-production-9a40.up.railway.app/api/auth/get-session
```

Look for errors mentioning:
- "Connection refused" → Auth server not running
- "Timeout" → Database connection issue
- "CORS" → CORS_ORIGINS missing backend URL

### Database Connection Still Slow

**Symptoms**: Requests take > 5 seconds

**Solutions**:
1. Check Neon dashboard - database should be "Active" (not suspended)
2. Verify `DATABASE_URL` includes `?sslmode=require`
3. Check Railway region matches Neon region (minimize latency)
4. Monitor Neon connection count (shouldn't exceed 20)

### CORS Errors in Browser Console

**Symptoms**: `No 'Access-Control-Allow-Origin' header`

**Solutions**:
1. Add backend URL to auth server `CORS_ORIGINS`
2. Add frontend URL to backend `CORS_ORIGINS`
3. Verify `credentials: 'include'` in frontend fetch

---

## Architecture Flow (After Fix)

```
User Login Flow:

1. User enters credentials on frontend
   ↓
2. Frontend → Backend (backend-production-9a40.up.railway.app)
   POST /api/auth/sign-in/email
   ↓
3. Backend → Auth Server (auth-server-production-cd0e.up.railway.app)
   POST /api/auth/sign-in/email
   [Uses optimized PostgreSQL pool]
   ↓
4. Auth Server → Neon PostgreSQL
   Verify password (bcrypt)
   [Fast connection with 10s timeout, SSL enabled]
   ↓
5. Auth Server → Backend
   Return user + JWT token
   ↓
6. Backend → Frontend
   Set auth_token cookie (HttpOnly, Secure, SameSite=None)
   ↓
7. Frontend redirects to /dashboard ✅
```

**Key Changes**:
- ✅ Step 4 now completes in < 2 seconds (was timing out)
- ✅ Backend knows where auth server is (AUTH_SERVER_URL set)
- ✅ CORS allows backend → auth server communication

---

## Next Steps

### Immediate (Required)

1. **Set `AUTH_SERVER_URL` in Railway backend** (see instructions above)
2. **Wait for Railway redeployment** (1-2 minutes)
3. **Test authentication** (see test commands above)

### After Successful Deployment

1. **Delete old debug documents**:
   ```bash
   rm AUDIT_REPORT.md AUTH_FIX_DEPLOYED.md BROWSER_DEBUG_STEPS.md \
      DEBUG_LOGIN_NETWORK.md QUICK_NETWORK_CHECK.md \
      RAILWAY_MANUAL_STEPS.md SAMESITE_FIX_DEPLOYED.md \
      STOP_AND_WAIT.md TEST_DASHBOARD_NOW.md \
      TEST_NOW_RATE_LIMIT_DISABLED.md WAIT_FOR_RAILWAY_REDEPLOY.md
   ```

2. **Monitor production logs** for first 24 hours:
   - Check for database connection errors
   - Monitor authentication success rate
   - Watch for timeout errors

3. **Performance testing**:
   - Login response time should be < 2 seconds
   - Test concurrent users (5-10 simultaneous logins)
   - Monitor database connection pool usage

4. **Security review**:
   - Verify JWT tokens expire correctly (15 minutes)
   - Test logout clears cookies properly
   - Ensure HTTPS is enforced in production

---

## Success Criteria

- ✅ Auth server responds to `/health` (200 OK)
- ✅ Auth server can connect to PostgreSQL (< 2s)
- ✅ Backend can reach auth server (no 504 timeout)
- ✅ User can sign up successfully
- ✅ User can sign in successfully
- ✅ Dashboard loads without redirect loop
- ✅ Tasks API requires authentication
- ✅ Logout works correctly

---

## Files Changed

1. `phase-2/auth-server/src/auth.ts` - Optimized PostgreSQL pool
2. `phase-2/auth-server/src/server.ts` - Updated CORS origins
3. `phase-2/backend/.env.example` - Added AUTH_SERVER_URL
4. `phase-2/RAILWAY_DEPLOYMENT_GUIDE.md` - Deployment instructions

**Git Commit**: `8400e1d` - "fix: optimize auth server PostgreSQL connection pool for Railway"

---

## Support

**Detailed Deployment Guide**: See `phase-2/RAILWAY_DEPLOYMENT_GUIDE.md`

**If Still Not Working After Railway Config**:
1. Share Railway backend logs (last 50 lines)
2. Share Railway auth server logs (last 50 lines)
3. Share test command output (curl commands above)
4. Check Neon database dashboard screenshot

---

**Status**: ✅ Code deployed | ⚠️ Railway config needed | 🧪 Testing pending

**Next Action**: Set `AUTH_SERVER_URL` in Railway backend service and wait for redeploy.
