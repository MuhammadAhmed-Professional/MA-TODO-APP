# Fix 504 Gateway Timeout - Set Railway Environment Variable

## Issue Confirmed with Playwright

I tested your login and confirmed:
- Backend CANNOT reach auth server (504 Gateway Timeout)
- Both services are healthy externally
- Backend is missing AUTH_SERVER_URL environment variable

## CRITICAL FIX - Do This Now:

### Step 1: Open Railway Backend
https://railway.app/project/1a580b9d-e43b-4faf-a523-b3454b9d3bf1/service/ac8b8441-def7-49e9-af64-47dd171ae1c2

### Step 2: Add Environment Variable
1. Click "Variables" tab
2. Click "New Variable"
3. Add:
   - Variable Name: AUTH_SERVER_URL
   - Value: https://auth-server-production-cd0e.up.railway.app
4. Click "Save"

### Step 3: Wait for Redeploy
Railway will auto-redeploy (2-3 minutes)

### Step 4: Test Login
After "Deployed" status, test login in fresh browser!
