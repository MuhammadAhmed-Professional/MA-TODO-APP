# Backend Railway Deployment Guide

**Last Updated**: 2025-12-28
**Commit**: `9cc6aa2` - "fix: validate Better Auth session tokens by calling auth server instead of JWT decode"

---

## Deployment Status

The backend code with the Better Auth session token validation fix has been committed and pushed to GitHub. Railway will automatically detect and deploy this update.

---

## Automatic Deployment (Recommended)

Railway is configured to automatically deploy when you push to the `main` branch.

### Current Status
- Latest commit: `9cc6aa2c946c4c94330078c7fc6c098a68be6d02`
- Commit message: "fix: validate Better Auth session tokens by calling auth server instead of JWT decode"
- Status: **Pushed to GitHub** - Railway should auto-deploy

### Verify Deployment

1. **Open Railway Dashboard**
   - Go to https://railway.app/
   - Navigate to your backend service

2. **Check Deployment Status**
   - Look for the latest deployment with commit `9cc6aa2`
   - Status should show: Building → Deploying → Active

3. **Monitor Build Logs**
   - Click on the deployment to see real-time logs
   - Watch for:
     - `Building Dockerfile...`
     - `Installing dependencies with uv...`
     - `Running Alembic migrations: alembic upgrade head`
     - `Starting uvicorn server...`
     - `Application startup complete`

4. **Check Health Endpoint**
   ```bash
   curl https://your-backend.railway.app/health
   ```
   Expected response: `{"status":"healthy"}`

---

## Manual Deployment (Alternative)

If automatic deployment doesn't trigger, you can manually redeploy:

### Option 1: Railway Dashboard
1. Open https://railway.app/
2. Navigate to your backend service
3. Click **"Deploy"** or **"Redeploy"**
4. Select commit `9cc6aa2` if not already selected

### Option 2: Railway CLI (if network issues are resolved)
```bash
cd phase-2/backend
railway up
```

### Option 3: Force Git Push (Trigger Rebuild)
```bash
cd phase-1
git commit --allow-empty -m "Trigger Railway redeploy"
git push origin main
```

---

## Environment Variables Checklist

Ensure these are configured in Railway Dashboard under **Variables**:

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Neon PostgreSQL connection string |
| `AUTH_SERVER_URL` | `https://auth-server-production-cd0e.up.railway.app` | Better Auth server URL |
| `JWT_SECRET` | `<match-auth-server>` | Must match auth server's BETTER_AUTH_SECRET |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Frontend URL (comma-separated for multiple) |
| `ENVIRONMENT` | `production` | Environment type |

### Automatic Variables (Set by Railway)
- `PORT` - Automatically set by Railway (don't override)
- `RAILWAY_ENVIRONMENT` - Set to "production"

### Optional Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `LOG_LEVEL` | `info` | Logging level (debug/info/warning/error) |

---

## Deployment Configuration

The backend uses the following configuration files:

### `Dockerfile`
- Base image: `python:3.12-slim`
- Package manager: `uv` (faster than pip)
- Migrations: Auto-run via `alembic upgrade head`
- Server: `uvicorn` with `--host 0.0.0.0 --port $PORT`

### `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "sh -c 'alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port $PORT'",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## What This Fix Does

### Problem
The backend was treating Better Auth session tokens as JWTs and trying to decode them directly. This failed because Better Auth returns opaque session tokens (not JWTs).

### Solution (Commit `9cc6aa2`)
Modified `src/auth/dependencies.py` to:

1. **Extract session token from cookie** (instead of expecting JWT)
2. **Call Better Auth server** at `/api/auth/get-session` with the token
3. **Validate session** by verifying the response from auth server
4. **Extract user ID** from Better Auth's session response
5. **Fetch user from database** using the validated user ID

### Code Changes
**File**: `phase-2/backend/src/auth/dependencies.py`

```python
async def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """Extract current user from Better Auth session token."""

    # Get token from cookie
    token = request.cookies.get("better-auth.session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validate token by calling Better Auth server
    auth_server_url = os.getenv("AUTH_SERVER_URL")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{auth_server_url}/api/auth/get-session",
            cookies={"better-auth.session_token": token}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid session")

    session_data = response.json()
    user_id = session_data["session"]["userId"]

    # Fetch user from database
    user = session.get(User, UUID(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

---

## Verification Steps After Deployment

### 1. Health Check
```bash
curl https://your-backend.railway.app/health
```
Expected: `{"status":"healthy"}`

### 2. Test Authentication Endpoint
```bash
# From frontend application, login should now work
# Check browser DevTools Network tab for:
# - POST /api/auth/login → 200 OK
# - Cookie: better-auth.session_token set
```

### 3. Test Protected Endpoint
```bash
# Try accessing a protected endpoint (e.g., /api/tasks)
# Should return 401 if no session token
# Should return user's tasks if valid session token
```

### 4. Check Railway Logs
In Railway Dashboard, monitor logs for:
```
INFO: Started server process [1]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## Troubleshooting

### Issue: Deployment Stuck in "Building" State
**Solution**: Check build logs for errors. Common issues:
- Missing environment variables (check Railway Variables tab)
- Migration failures (check DATABASE_URL is correct)
- Dockerfile syntax errors (verify Dockerfile builds locally)

### Issue: 401 Unauthorized After Login
**Possible Causes**:
1. AUTH_SERVER_URL not set correctly
2. CORS_ORIGINS doesn't include frontend URL
3. Session cookie not being sent (check cookie domain/SameSite)

**Debug**:
```bash
# Check Railway logs for auth errors
# Look for "Invalid session" or "Not authenticated" messages
```

### Issue: 500 Internal Server Error
**Possible Causes**:
1. Database connection issue (check DATABASE_URL)
2. Missing JWT_SECRET (check Variables)
3. Auth server unreachable (check AUTH_SERVER_URL)

**Debug**:
```bash
# Check Railway logs for Python traceback
# Look for database connection errors or HTTPX request failures
```

### Issue: CORS Errors in Browser
**Solution**: Add frontend URL to `CORS_ORIGINS` in Railway Variables:
```
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-frontend-preview.vercel.app
```

---

## Rollback Procedure

If the deployment causes issues, you can rollback:

### Option 1: Railway Dashboard
1. Go to Deployments tab
2. Find the last working deployment
3. Click **"Redeploy"**

### Option 2: Git Revert
```bash
cd phase-1
git revert 9cc6aa2
git push origin main
```

---

## Next Steps After Deployment

1. **Test Authentication Flow**
   - Sign up a new user
   - Log in
   - Access protected endpoints
   - Log out

2. **Update Frontend Environment Variables**
   - Set `NEXT_PUBLIC_API_URL` to Railway backend URL
   - Redeploy frontend on Vercel

3. **Monitor for Errors**
   - Watch Railway logs for 24 hours
   - Check error tracking (if configured)
   - Monitor response times

4. **Performance Optimization** (if needed)
   - Add database connection pooling
   - Configure HTTP caching
   - Enable compression

---

## Support Resources

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **Better Auth Docs**: https://www.better-auth.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

## Deployment Checklist

- [x] Code committed to Git (commit `9cc6aa2`)
- [x] Code pushed to GitHub
- [ ] Railway deployment started (check dashboard)
- [ ] Build completed successfully
- [ ] Migrations applied
- [ ] Server started
- [ ] Health check passing
- [ ] Environment variables verified
- [ ] Authentication tested
- [ ] CORS configuration verified
- [ ] Frontend can access API

**Status**: Waiting for Railway to auto-deploy commit `9cc6aa2`
