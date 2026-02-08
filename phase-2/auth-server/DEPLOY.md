# Railway Deployment Guide - Better Auth Server

This guide provides step-by-step instructions for deploying the Better Auth server to Railway with PostgreSQL.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway
- Railway CLI installed (optional)

## Current Deployment Status

**Project**: auth-server  
**Project ID**: `1a580b9d-e43b-4faf-a523-b3454b9d3bf1`  
**Service ID**: `ac8b8441-def7-49e9-af64-47dd171ae1c2`  
**Environment**: production  
**Railway URL**: https://auth-server-production-8251.up.railway.app

## Deployment Steps

### Step 1: Access Railway Dashboard

1. Visit: https://railway.app/project/1a580b9d-e43b-4faf-a523-b3454b9d3bf1
2. You should see two services:
   - `auth-server` (Node.js service)
   - `Postgres` (PostgreSQL database)

### Step 2: Configure Environment Variables

Click on the **auth-server** service, then navigate to the **Variables** tab.

#### Required Variables:

Add the following environment variables:

```bash
# Database Connection (Reference to Postgres service)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Auth Server Base URL (Your Railway domain)
BETTER_AUTH_URL=https://auth-server-production-8251.up.railway.app

# CORS Origins (Comma-separated list of allowed origins)
CORS_ORIGINS=http://localhost:3000,https://auth-server-production-8251.up.railway.app

# Auth Secret (Already set - verify it exists)
BETTER_AUTH_SECRET=<your-secret-key>
```

#### Variable Details:

- **DATABASE_URL**: Use `${{Postgres.DATABASE_URL}}` to reference the PostgreSQL service. Railway will automatically resolve this to the correct connection string.
- **BETTER_AUTH_URL**: Replace with your actual Railway domain (check the service's "Settings" tab for the domain).
- **CORS_ORIGINS**: Add all allowed origins. Include localhost for local testing and your frontend domain.
- **BETTER_AUTH_SECRET**: Should already be set. If not, generate a new one: `openssl rand -base64 32`

### Step 3: Verify Database Service

1. Click on the **Postgres** service
2. Verify it's running and has a `DATABASE_URL` variable
3. Note the connection details if needed for debugging

### Step 4: Trigger Deployment

After setting the environment variables:

1. Railway will automatically trigger a new deployment
2. Watch the deployment logs in the **Deployments** tab
3. The build process takes approximately 1-2 minutes

### Step 5: Verify Deployment

Once deployed, verify the service is healthy:

#### Check Health Endpoints:

```bash
# Primary health check
curl https://auth-server-production-8251.up.railway.app/health

# Railway health check
curl https://auth-server-production-8251.up.railway.app/api/auth/health
```

Both should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-18T...",
  "service": "better-auth-server",
  "version": "1.0.0"
}
```

#### Test Authentication Endpoints:

```bash
# Get session (should return null for unauthenticated users)
curl https://auth-server-production-8251.up.railway.app/auth/get-session

# Sign up (test account creation)
curl -X POST https://auth-server-production-8251.up.railway.app/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### Step 6: Monitor Logs

Monitor the deployment logs for any errors:

```bash
# Using Railway CLI
railway logs --service ac8b8441-def7-49e9-af64-47dd171ae1c2

# Or use the Railway dashboard "Logs" tab
```

## Troubleshooting

### Issue: Healthcheck Failing

**Symptoms**: Deployment shows "Healthcheck failed" or "service unavailable"

**Solutions**:
1. Verify all environment variables are set correctly
2. Check that `DATABASE_URL` references the Postgres service: `${{Postgres.DATABASE_URL}}`
3. Ensure the Postgres service is running
4. Check logs for database connection errors

### Issue: Database Connection Error

**Symptoms**: Logs show "Failed to initialize database adapter" or connection errors

**Solutions**:
1. Verify `DATABASE_URL` is set to `${{Postgres.DATABASE_URL}}`
2. Check Postgres service status
3. Verify the Postgres service is in the same project and environment

### Issue: CORS Errors

**Symptoms**: Frontend can't connect, CORS policy errors in browser console

**Solutions**:
1. Add your frontend domain to `CORS_ORIGINS`
2. Ensure `CORS_ORIGINS` includes both `http://localhost:3000` and your production frontend URL
3. Format: `http://localhost:3000,https://your-frontend.up.railway.app` (no spaces)

### Issue: Authentication Not Working

**Symptoms**: Sign up/login returns errors or tokens not valid

**Solutions**:
1. Verify `BETTER_AUTH_SECRET` matches between auth-server and your backend
2. Ensure `BETTER_AUTH_URL` is set to the correct Railway domain
3. Check that cookies are being sent (credentials: 'include' in frontend fetch)

## Database Migrations

Better Auth handles database migrations automatically on startup. The tables will be created when the service first connects to the database.

To manually trigger migrations (if needed):

```bash
# Using Railway CLI
railway run npm run migrate
```

## Updating the Deployment

To deploy changes:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

2. **Railway auto-deploys** from the main branch

3. **Monitor deployment** in the Railway dashboard

## Rolling Back

If a deployment fails:

1. Go to the **Deployments** tab
2. Find a previous successful deployment
3. Click the "..." menu
4. Select "Redeploy"

## Environment-Specific Configuration

### Production

Current configuration is for production. No changes needed.

### Staging (Optional)

To create a staging environment:

1. Create a new environment in Railway
2. Clone the production environment variables
3. Update `BETTER_AUTH_URL` and `CORS_ORIGINS` for staging URLs
4. Deploy to the staging environment

## Security Checklist

- [ ] `BETTER_AUTH_SECRET` is a strong, random value (32+ characters)
- [ ] `BETTER_AUTH_SECRET` matches between auth-server and backend
- [ ] `CORS_ORIGINS` only includes trusted domains
- [ ] Database uses SSL/TLS connections (enabled by default on Railway)
- [ ] Environment variables are stored in Railway (not in code)
- [ ] `.env` files are in `.gitignore`

## API Endpoints

Once deployed, your Better Auth server provides:

- `GET /health` - Health check
- `GET /api/auth/health` - Railway health check
- `POST /auth/sign-up` - Create account
- `POST /auth/sign-in/email` - Login with email
- `POST /auth/sign-out` - Logout
- `GET /auth/get-session` - Get current session

## Support

For issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Review the `.env.example` file for configuration reference
4. Check Better Auth documentation: https://better-auth.com

## Next Steps

After successful deployment:

1. Update your frontend to use the Railway URL
2. Test all authentication flows
3. Set up monitoring and alerts
4. Configure custom domain (optional)
5. Set up backup strategy for database

---

Last Updated: 2025-12-18  
Deployment Platform: Railway  
Database: PostgreSQL (Neon Serverless)  
Runtime: Node.js 20
