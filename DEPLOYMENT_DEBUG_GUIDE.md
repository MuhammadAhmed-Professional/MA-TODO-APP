# Railway Deployment Debug Guide

**Issue**: Backend session validation not working despite code fixes
**Root Cause**: Railway may not have deployed latest commits

---

## Confirmed Facts ✅

1. **Auth Server Exists and Works**
   ```bash
   $ curl https://auth-server-production-8251.up.railway.app/health
   {"status":"healthy","timestamp":"2025-12-27T20:42:44.524Z","service":"better-auth-server","version":"1.0.0"}
   ```

2. **Login Works Through Backend**
   ```bash
   $ curl -X POST https://tda-backend-production.up.railway.app/api/auth/sign-in/email
   Response: 200 OK with token
   ```
   → This proves AUTH_SERVER_URL is configured correctly!

3. **Session Validation Fails**
   ```bash
   $ curl https://tda-backend-production.up.railway.app/api/auth/get-session \
     -H "Authorization: Bearer TOKEN"
   Response: 401 "Invalid authentication token"
   ```
   → This error comes from JWT decoding (OLD CODE), not session validation (NEW CODE)

---

## Latest Commits (Not Deployed?)

```bash
27465d5 - debug: add logging to Better Auth session validation
9cc6aa2 - fix: validate Better Auth session tokens by calling auth server
65cbd0a - debug: add AUTH_SERVER_URL to health endpoint
```

**Expected**: Health endpoint should return `{"status": "healthy", "auth_server_url": "...", "commit": "27465d5"}`
**Actual**: Returns only `{"status": "healthy"}`

**Conclusion**: Railway is running OLD code!

---

## Railway Project Structure

Based on the code, you should have:

**Option A: Single Service with Multiple Ports**
```
Railway Project: tda-production
└── Service: tda-backend-auth (combined)
    ├── Port 8000: FastAPI backend
    └── Port 3001: Better Auth server
```

**Option B: Separate Services**
```
Railway Project: tda-production
├── Service: tda-backend
│   └── Port 8000: FastAPI
└── Service: auth-server
    └── Port 3001: Better Auth
```

---

## Action Steps to Debug

### Step 1: Check Railway Dashboard

Go to: https://railway.app/project/1a580b9d-e43b-4faf-a523-b3454b9d3bf1

**Check Services Tab**:
- How many services are listed?
- Which GitHub repo/branch is each connected to?
- What is the root directory for each service?

**For Backend Service**:
- Settings → Source
- Is it pointing to `phase-2/backend/`?
- Is it watching the `main` branch?
- What is the latest deployment?

### Step 2: Check Environment Variables

**Backend Service → Variables**:
Look for:
- `AUTH_SERVER_URL` - Should be `https://auth-server-production-8251.up.railway.app`
- `DATABASE_URL` - Should be Neon PostgreSQL connection string
- `JWT_SECRET` - Should match `BETTER_AUTH_SECRET` in auth server

### Step 3: Force Redeploy

If environment variables are correct but code is old:

**Option A: Trigger Redeploy**
1. Go to backend service
2. Click "Deployments" tab
3. Find latest deployment
4. Click "Redeploy"

**Option B: Empty Commit**
```bash
cd phase-2/backend
git commit --allow-empty -m "force rebuild"
git push
```

### Step 4: Check Build Logs

1. Go to backend service → Deployments
2. Click latest deployment
3. Check "Build Logs" tab
4. Look for errors or warnings

---

## Quick Test Commands

After redeployment, test these in order:

### Test 1: Health Endpoint (Verify Deployment)
```bash
curl https://tda-backend-production.up.railway.app/health
```

**Expected (if deployed)**:
```json
{
  "status": "healthy",
  "auth_server_url": "https://auth-server-production-8251.up.railway.app",
  "commit": "65cbd0a"
}
```

**Actual (current)**:
```json
{
  "status": "healthy"
}
```

### Test 2: Login (Verify Auth Server Connection)
```bash
curl -X POST https://tda-backend-production.up.railway.app/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"ta234567801@gmail.com","password":"talal12345"}'
```

**Expected**: 200 OK with token
**Status**: ✅ WORKS (auth server connection OK)

### Test 3: Session Validation (Verify Session Code)
```bash
# First login to get a token
TOKEN=$(curl -s -X POST https://tda-backend-production.up.railway.app/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email":"ta234567801@gmail.com","password":"talal12345"}' | jq -r '.token')

# Then validate session
curl https://tda-backend-production.up.railway.app/api/auth/get-session \
  -H "Authorization: Bearer $TOKEN"
```

**Expected (after fix deploys)**: 200 OK with user data
**Actual (current)**: 401 "Invalid authentication token"

---

## If Redeployment Works

Once the new code is deployed, you should see in Railway logs:
```
🔍 Validating token with Better Auth server: https://auth-server-production-8251.up.railway.app
🔑 Token: nsKbZ0D4hYsbzgyy...
📡 Auth server response status: 200
```

Then session validation will work and the todo app will be fully functional!

---

## Current Status

✅ **Fixed Locally**: Commits 9cc6aa2, 27465d5, 65cbd0a
✅ **Pushed to GitHub**: main branch updated
❌ **Not Deployed on Railway**: Still running old code
⏳ **Awaiting**: Railway deployment or manual redeploy

---

## Next Actions

1. Open Railway dashboard
2. Check which commits are deployed
3. Manually trigger redeploy if needed
4. Test with commands above
5. Report back what you see

