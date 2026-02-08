# Phase II Todo App - Production Integration Guide

**Date**: 2025-12-19
**Status**: Ready for Deployment Integration

---

## Production URLs

| Service | URL | Platform |
|---------|-----|----------|
| **Frontend** | https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app/ | Vercel |
| **Backend API** | https://talal-s-tda-production.up.railway.app/ | Railway |
| **Auth Server** | https://auth-server-production-8251.up.railway.app | Railway |
| **Database** | Neon PostgreSQL (pooler connection) | Neon |

---

## Production JWT Secret

**CRITICAL**: All three services MUST use this EXACT secret for token compatibility.

```
cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
```

**Generated with**: `openssl rand -hex 32` on 2025-12-19

---

## 1. Auth Server - Railway Environment Variables

**Service**: `auth-server` (Service ID: `ac8b8441-def7-49e9-af64-47dd171ae1c2`)

Navigate to Railway dashboard → `auth-server` service → Variables tab and **UPDATE** these variables:

```env
# PostgreSQL Database (shared with backend)
DATABASE_URL=postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require

# Auth Server Configuration
BETTER_AUTH_URL=https://auth-server-production-8251.up.railway.app
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801

# CORS - Allow production frontend
CORS_ORIGINS=http://localhost:3000,https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app

# Server Configuration
PORT=3001
NODE_ENV=production
```

**Changes from current config**:
- ✅ `BETTER_AUTH_URL`: Already correct
- ✅ `DATABASE_URL`: Already correct
- ⚠️ **UPDATE** `BETTER_AUTH_SECRET`: Replace dev secret with production secret
- ⚠️ **UPDATE** `CORS_ORIGINS`: Add production frontend URL

---

## 2. Backend API - Railway Environment Variables

**Service**: Backend service (find the service that serves https://talal-s-tda-production.up.railway.app/)

Navigate to Railway dashboard → Backend service → Variables tab and **ADD/UPDATE** these variables:

```env
# PostgreSQL Database (MUST MATCH auth server)
DATABASE_URL=postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# JWT Authentication (MUST MATCH auth server)
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Allow production frontend and auth server
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://auth-server-production-8251.up.railway.app,https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app

# Environment
ENVIRONMENT=production
```

**Changes from current config**:
- ✅ `DATABASE_URL`: Already correct
- ⚠️ **UPDATE** `JWT_SECRET`: Replace dev secret with production secret
- ⚠️ **UPDATE** `CORS_ORIGINS`: Add production frontend URL
- ℹ️ `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`: Add if missing

---

## 3. Frontend - Vercel Environment Variables

**Project**: `talal-s-tda` or similar (https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app/)

Navigate to Vercel dashboard → Project Settings → Environment Variables tab and **ADD/UPDATE** these variables:

### Production Environment Variables

```env
# Backend API URL (Railway backend)
NEXT_PUBLIC_API_URL=https://talal-s-tda-production.up.railway.app

# Auth Server URL (Railway auth server)
NEXT_PUBLIC_AUTH_URL=https://auth-server-production-8251.up.railway.app

# App Configuration
NEXT_PUBLIC_APP_NAME="Phase II Todo"
NEXT_PUBLIC_ENVIRONMENT=production

# JWT Secret (MUST MATCH auth server and backend)
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
```

**Important**:
- Set these variables for **Production** environment in Vercel
- After updating, trigger a new deployment for changes to take effect
- The local `.env.local` file has already been updated with these values

---

## 4. Local Development Environment Variables

### Frontend (`phase-2/frontend/.env.local`)

**Status**: ✅ Already updated with production values

```env
NEXT_PUBLIC_AUTH_URL=https://auth-server-production-8251.up.railway.app
NEXT_PUBLIC_API_URL=https://talal-s-tda-production.up.railway.app
NEXT_PUBLIC_APP_NAME="Phase II Todo"
NEXT_PUBLIC_ENVIRONMENT=production
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
```

### Backend (`phase-2/backend/.env`)

**Status**: ⚠️ Needs manual update

Update `JWT_SECRET` in `phase-2/backend/.env`:

```env
# Current (dev):
JWT_SECRET=dev-secret-replace-in-production-openssl-rand-hex-32

# Update to (production):
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
```

Update `CORS_ORIGINS` to include production frontend:

```env
# Current:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://auth-server-production-8251.up.railway.app

# Update to:
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://auth-server-production-8251.up.railway.app,https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app
```

### Auth Server (`phase-2/auth-server/.env`)

**Status**: ⚠️ Needs manual update

Update `BETTER_AUTH_SECRET` and `CORS_ORIGINS` in `phase-2/auth-server/.env`:

```env
# Current (dev):
BETTER_AUTH_SECRET=dev-secret-replace-in-production-openssl-rand-hex-32
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Update to (production):
BETTER_AUTH_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
CORS_ORIGINS=http://localhost:3000,https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app
```

---

## 5. Deployment Steps

### Step 1: Update Railway Services

1. **Auth Server** (ac8b8441-def7-49e9-af64-47dd171ae1c2):
   - Go to Railway dashboard → auth-server → Variables
   - Update `BETTER_AUTH_SECRET` → `cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801`
   - Update `CORS_ORIGINS` → `http://localhost:3000,https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app`
   - Service will automatically redeploy

2. **Backend Service**:
   - Go to Railway dashboard → Backend service → Variables
   - Update `JWT_SECRET` → `cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801`
   - Update `CORS_ORIGINS` → Add `https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app`
   - Service will automatically redeploy

### Step 2: Update Vercel Frontend

1. Go to Vercel dashboard → Project → Settings → Environment Variables
2. Update/Add the following for **Production** environment:
   - `NEXT_PUBLIC_API_URL` → `https://talal-s-tda-production.up.railway.app`
   - `NEXT_PUBLIC_AUTH_URL` → `https://auth-server-production-8251.up.railway.app`
   - `BETTER_AUTH_SECRET` → `cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801`
   - `NEXT_PUBLIC_ENVIRONMENT` → `production`
3. Trigger a new deployment (Deployments tab → Redeploy)

### Step 3: Verify Integration

After all services are redeployed, test the integration:

1. **Auth Server Health Check**:
   ```bash
   curl https://auth-server-production-8251.up.railway.app/health
   # Expected: {"status":"healthy","timestamp":"...","service":"better-auth-server","version":"1.0.0"}
   ```

2. **Backend Health Check**:
   ```bash
   curl https://talal-s-tda-production.up.railway.app/health
   # Expected: {"status":"healthy"} or similar
   ```

3. **Frontend**:
   - Open https://frontend-k235s8ble-talal-ahmeds-projects.vercel.app/
   - Try to sign up / log in
   - Create a task
   - Verify CORS is working (no CORS errors in browser console)

---

## 6. Security Checklist

- ✅ Production JWT secret is cryptographically secure (256-bit)
- ⚠️ Ensure JWT secret is NOT committed to git (only in Railway/Vercel dashboards)
- ✅ All services use the SAME JWT secret
- ✅ CORS is configured to allow only trusted origins
- ✅ Database connection uses SSL (`sslmode=require`)
- ⚠️ Verify HTTPS is enforced on all production services
- ⚠️ Set `HttpOnly` and `Secure` flags on auth cookies

---

## 7. Troubleshooting

### Issue: "Invalid token" or "Not authenticated" errors

**Cause**: JWT secret mismatch between services
**Solution**: Verify all three services use the EXACT same `JWT_SECRET` / `BETTER_AUTH_SECRET`

### Issue: CORS errors in browser console

**Cause**: Frontend origin not in backend/auth CORS_ORIGINS
**Solution**: Ensure `CORS_ORIGINS` includes the exact frontend URL (no trailing slash)

### Issue: Database connection errors

**Cause**: DATABASE_URL mismatch or incorrect connection string
**Solution**: Verify both auth-server and backend use the SAME Neon PostgreSQL URL

### Issue: Auth server crashes after deployment

**Cause**: Missing or incorrect environment variables
**Solution**:
1. Check Railway logs: `railway logs --service ac8b8441-def7-49e9-af64-47dd171ae1c2`
2. Verify all required env vars are set in Railway dashboard
3. Check that `DATABASE_URL` is correct and accessible

---

## 8. Rollback Plan

If production integration fails:

1. **Revert Railway Environment Variables**:
   - Auth server: Use previous `BETTER_AUTH_SECRET` value
   - Backend: Use previous `JWT_SECRET` value
   - Services will auto-redeploy with old config

2. **Revert Vercel Environment Variables**:
   - Set `NEXT_PUBLIC_API_URL` back to localhost or previous value
   - Redeploy frontend

3. **Check Logs**:
   - Railway: `railway logs --service <service-id>`
   - Vercel: Check deployment logs in Vercel dashboard

---

## 9. Next Steps

After successful integration:

1. **Test End-to-End Flows**:
   - User signup
   - User login
   - Create task
   - Update task
   - Delete task
   - Logout

2. **Monitor Performance**:
   - Check Railway metrics (CPU, memory, response times)
   - Monitor Vercel deployment analytics
   - Check Neon database connection pool usage

3. **Enable Production Features**:
   - Set up email verification (if needed)
   - Configure password reset flow
   - Add rate limiting to auth endpoints
   - Set up monitoring/alerting (Sentry, LogRocket, etc.)

4. **Documentation**:
   - Update README with production URLs
   - Document API endpoints
   - Create user guide

---

## Contact & Support

- **Railway Dashboard**: https://railway.app/project/1a580b9d-e43b-4faf-a523-b3454b9d3bf1
- **Vercel Dashboard**: https://vercel.com/talal-ahmeds-projects
- **Neon Dashboard**: https://console.neon.tech

For issues, check:
- Railway logs: `railway logs --service <service-id>`
- Vercel deployment logs
- Browser console (for frontend errors)
- Network tab (for API request/response details)

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-19
**Author**: Claude Code Assistant
