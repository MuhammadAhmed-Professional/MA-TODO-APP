# Railway Deployment Checklist for Backend Service

**Service Name**: `imaginative-strength`
**URL**: https://talal-s-tda-production.up.railway.app
**Database**: Neon PostgreSQL (Serverless)

---

## Issues Fixed (2025-12-20)

### 1. Table Name Mismatch (CRITICAL)
- **Problem**: Migration created `users` table but SQLModel expected `user` table
- **Fix**: Updated migration `ea3540bc87e7` to create `user` table (singular)
- **Files Changed**:
  - `src/db/migrations/versions/ea3540bc87e7_add_users_table_with_authentication_.py`
  - `src/db/migrations/versions/ba7aa1f810b4_add_tasks_table.py` (foreign key reference)

### 2. Migration Files Not in Docker Image
- **Problem**: `.dockerignore` excluded test files, potentially blocking migrations
- **Fix**: Added explicit exception for migration files in `.dockerignore`
- **Files Changed**:
  - `.dockerignore` - Added `!src/db/migrations/versions/*.py`
  - `Dockerfile` - Added validation check for migrations directory

### 3. Better Auth Schema Compatibility
- **Problem**: Migration didn't include Better Auth required fields
- **Fix**: Added `emailVerified`, `image`, `createdAt`, `updatedAt` with camelCase preservation
- **Files Changed**:
  - `src/db/migrations/versions/ea3540bc87e7_add_users_table_with_authentication_.py`

---

## Pre-Deployment Verification (Local)

Before deploying to Railway, verify these locally:

### Step 1: Test Migrations Locally

```bash
cd phase-2/backend

# Set DATABASE_URL to Neon PostgreSQL
export DATABASE_URL="postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Run migrations (this will apply to production Neon DB!)
uv run alembic upgrade head

# Verify migrations applied
uv run alembic current

# Expected output:
# 003_add_conversation_tables (head)
```

**IMPORTANT**: This will apply migrations to your PRODUCTION Neon database. Only do this if you're ready to deploy.

### Step 2: Test Docker Build Locally

```bash
cd phase-2/backend

# Build Docker image
docker build -t backend-test .

# Verify migrations are in the image
docker run --rm backend-test ls -la /app/src/db/migrations/versions/

# Expected output: 4 migration files
# ea3540bc87e7_add_users_table_with_authentication_.py
# ba7aa1f810b4_add_tasks_table.py
# 7582d33c41bc_add_performance_indexes_to_tasks_table.py
# 003_add_conversation_tables.py
```

### Step 3: Test Full Startup Locally

```bash
# Run container with Neon DATABASE_URL
docker run --rm \
  -e DATABASE_URL="postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require" \
  -e JWT_SECRET="cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801" \
  -e CORS_ORIGINS="http://localhost:3000" \
  -e ENVIRONMENT="production" \
  -e PORT="8000" \
  -p 8000:8000 \
  backend-test \
  sh -c 'alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000'

# Test health endpoint in another terminal
curl http://localhost:8000/health

# Expected: {"status":"healthy","timestamp":"..."}
```

---

## Railway Dashboard Deployment Steps

### Step 1: Verify Environment Variables

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Select project: **Talal's TDA**
3. Select service: **imaginative-strength**
4. Click **Variables** tab
5. Verify these variables exist with **EXACT** values:

```env
DATABASE_URL=postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://auth-server-production-8251.up.railway.app,https://talal-s-tda.vercel.app
ENVIRONMENT=production
```

**CRITICAL**: Ensure `DATABASE_URL` points to **Neon PostgreSQL**, NOT Railway's internal Postgres!

### Step 2: Commit and Push Changes

```bash
# From project root (phase-1/)
git add phase-2/backend/

# Check what will be committed
git status

# Commit with descriptive message
git commit -m "Fix Railway deployment: correct table names and ensure migrations are included"

# Push to trigger Railway deployment
git push origin main
```

### Step 3: Monitor Railway Deployment

1. Go to **Deployments** tab in Railway dashboard
2. Click on the latest deployment (should start automatically after push)
3. Click **View Logs** to monitor deployment progress

### Step 4: Check Migration Logs

Look for these log entries in deployment logs:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> ea3540bc87e7, Add users table with authentication fields
INFO  [alembic.runtime.migration] Running upgrade ea3540bc87e7 -> ba7aa1f810b4, Add tasks table
INFO  [alembic.runtime.migration] Running upgrade ba7aa1f810b4 -> 7582d33c41bc, Add performance indexes to tasks table
INFO  [alembic.runtime.migration] Running upgrade 7582d33c41bc -> 003_add_conversation_tables, Add conversations and messages tables for Phase III chatbot
```

**If migrations already applied**:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 003_add_conversation_tables, (already at head)
```

### Step 5: Verify Application Started

Look for uvicorn startup logs:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 6: Test Deployed Endpoint

```bash
# Test health endpoint
curl https://talal-s-tda-production.up.railway.app/health

# Expected response:
# {"status":"healthy","timestamp":"2025-12-20T..."}

# Test API docs
curl https://talal-s-tda-production.up.railway.app/docs
# Should return HTML for Swagger UI
```

---

## Troubleshooting Guide

### Error: "relation 'user' does not exist"

**Cause**: Migrations didn't run or failed
**Solution**:

1. Check deployment logs for migration errors
2. Verify `DATABASE_URL` in Railway variables
3. Try manual migration:
   - Click **"Deploy"** button again (redeploy)
   - If still failing, check migration files are in image:
     ```bash
     # In Railway logs, look for Dockerfile RUN command output
     # Should show: src/db/migrations/versions exists
     ```

### Error: "relation 'users' does not exist"

**Cause**: Old migration still creating `users` table instead of `user`
**Solution**:

1. Verify you pushed the updated migration file
2. Check git commit includes the migration changes:
   ```bash
   git log --oneline -1
   git show HEAD:phase-2/backend/src/db/migrations/versions/ea3540bc87e7_add_users_table_with_authentication_.py | grep "op.create_table"
   # Should show: op.create_table('user',
   ```

### Error: "Migration files missing"

**Cause**: Docker build failed validation check
**Solution**:

1. Check `.dockerignore` doesn't exclude migrations
2. Verify `!src/db/migrations/versions/*.py` is in `.dockerignore`
3. Rebuild Docker image locally to test

### Error: "Invalid JWT token" or CORS errors

**Cause**: Environment variables not set correctly
**Solution**:

1. Go to Railway Variables tab
2. Verify `JWT_SECRET` matches exactly (no extra spaces)
3. Verify `CORS_ORIGINS` includes your frontend URL
4. Click **"Redeploy"** after changing variables

### Deployment Succeeds but App Crashes

**Cause**: Database connection or startup error
**Solution**:

1. Check Railway logs for Python exceptions
2. Common issues:
   - `DATABASE_URL` malformed (check for special characters in password)
   - Port conflict (Railway sets `$PORT` env var automatically)
   - Missing dependencies (check `pyproject.toml`)

---

## Rollback Procedure

If deployment fails and you need to rollback:

### Option 1: Rollback via Railway Dashboard

1. Go to **Deployments** tab
2. Find the last successful deployment
3. Click **"..."** menu → **"Redeploy"**

### Option 2: Rollback Migrations (Database)

If migrations broke the database:

```bash
# Connect to Neon PostgreSQL
export DATABASE_URL="postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade ea3540bc87e7

# Rollback all migrations (DANGER!)
uv run alembic downgrade base
```

**WARNING**: Rollback will **delete data** in those tables!

---

## Post-Deployment Verification

### Checklist

- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at `/docs`
- [ ] Database tables exist (check Neon console)
- [ ] User registration works (test `/api/auth/signup`)
- [ ] JWT authentication works (test protected endpoints)
- [ ] CORS allows frontend requests
- [ ] No errors in Railway logs for 5 minutes

### Test User Registration

```bash
# Create test user
curl -X POST https://talal-s-tda-production.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "SecurePassword123!"
  }'

# Expected: 201 Created with user object
```

### Verify Database Schema

1. Go to Neon Console: https://console.neon.tech/
2. Select your database: `neondb`
3. Click **SQL Editor**
4. Run these queries:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Expected tables:
-- user, tasks, conversations, messages, alembic_version

-- Check user table schema
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user';

-- Expected columns:
-- id, email, name, hashed_password, emailVerified, image, createdAt, updatedAt

-- Check migration version
SELECT version_num FROM alembic_version;

-- Expected: 003_add_conversation_tables
```

---

## Environment Variables Reference

### Required for All Environments

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | Neon PostgreSQL connection string |
| `JWT_SECRET` | 64-char hex string | Secret key for JWT signing (generate with `openssl rand -hex 32`) |
| `CORS_ORIGINS` | `https://app.example.com` | Comma-separated allowed origins |
| `ENVIRONMENT` | `production` | Environment name (development/staging/production) |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | HTTP port (Railway sets this automatically) |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | JWT token expiration (minutes) |

---

## Additional Resources

- **Railway Docs**: https://docs.railway.app/
- **Neon Docs**: https://neon.tech/docs/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## Support Checklist

If you're still experiencing issues after following this guide:

1. **Collect Logs**:
   - Railway deployment logs (last 100 lines)
   - Neon database query logs (if available)
   - Local test results (migration output, curl responses)

2. **Verify Configuration**:
   - Screenshot of Railway environment variables
   - Output of `git log --oneline -5` (recent commits)
   - Output of `alembic current` (current migration version)

3. **Test Locally**:
   - Can you connect to Neon DB locally?
   - Do migrations run successfully locally?
   - Does Docker image build without errors?

4. **Check External Services**:
   - Is Neon database accessible? (check status page)
   - Is Railway experiencing outages? (check status page)
   - Is your auth-server service running?

---

**Last Updated**: 2025-12-20
**Version**: 1.0
**Maintainer**: Claude Code Agent
