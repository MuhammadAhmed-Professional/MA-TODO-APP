# Railway Deployment Guide - Auth Server

## Prerequisites
- GitHub repository with auth-server code pushed to `main` branch ✅
- Railway account (free tier available at https://railway.app)
- Neon PostgreSQL database connection string

## Deployment Steps

### 1. Create New Railway Project

1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authenticate with GitHub if prompted
5. Select repository: `Talal/Hackathons-Panaversity` (or your repo name)
6. Select branch: `main`

### 2. Configure Service Settings

Once the project is created:

1. Click on the service card
2. Go to **"Settings"** tab
3. Configure the following:

#### Root Directory
```
phase-2/auth-server
```
**IMPORTANT**: No leading slash!

#### Build Settings
- **Builder**: Dockerfile
- **Dockerfile Path**: `Dockerfile` (default, should auto-detect)

### 3. Add Environment Variables

Go to **"Variables"** tab and add the following:

#### Required Variables

**DATABASE_URL**
```
postgresql://neondb_owner:your-password@ep-your-instance.us-east-2.aws.neon.tech/neondb?sslmode=require
```
Replace with your actual Neon connection string from the backend `.env` file.

**BETTER_AUTH_SECRET**
```
ajRphFFR4XJ5aIM1q2PRtjq31pTTnWKeYjzmBk0e50g=
```

**BETTER_AUTH_URL**
```
https://${{RAILWAY_PUBLIC_DOMAIN}}
```
**IMPORTANT**: Use this Railway variable reference - it will auto-populate with your deployed URL.

**CORS_ORIGINS**
```
https://talal-s-tda.vercel.app
```
This is your deployed Vercel frontend URL.

**PORT**
```
3001
```

**NODE_ENV**
```
production
```

### 4. Deploy

1. Railway will automatically start building and deploying
2. Monitor the **"Deployments"** tab for build progress
3. Check **"Build Logs"** if any errors occur

### 5. Get Deployed URL

1. Once deployment succeeds (green checkmark)
2. Go to **"Settings"** tab
3. Under **"Networking"** section, click **"Generate Domain"**
4. Copy the generated URL (e.g., `https://auth-server-production-xxxx.up.railway.app`)

### 6. Verify Deployment

Test the health endpoint:
```bash
curl https://your-auth-server-url.up.railway.app/api/auth/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-18T..."
}
```

## Next Steps After Deployment

### Update Frontend Environment Variables

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Update `NEXT_PUBLIC_AUTH_URL`:
   ```
   NEXT_PUBLIC_AUTH_URL=https://your-auth-server-url.up.railway.app
   ```
4. Redeploy the frontend for changes to take effect

### Test Authentication Flow

1. Visit your Vercel frontend: https://talal-s-tda.vercel.app
2. Click **"Sign Up"**
3. Create a new account
4. Verify you're redirected to the dashboard
5. Test **"Sign Out"** and **"Sign In"**

## Troubleshooting

### Build Fails with "Dockerfile not found"
- Verify **Root Directory** is set to `phase-2/auth-server` (no leading slash)
- Check that Dockerfile exists in the repository

### Health Check Fails
- Check **Deploy Logs** for startup errors
- Verify `PORT` environment variable is set to `3001`
- Ensure database connection string is correct

### CORS Errors in Frontend
- Verify `CORS_ORIGINS` includes your exact Vercel URL
- Check that auth server URL in Vercel matches Railway deployment
- Ensure `credentials: 'include'` is set in frontend fetch requests

### Database Connection Errors
- Verify Neon database is active (not paused)
- Check DATABASE_URL format includes `?sslmode=require`
- Ensure Neon allows connections from Railway IPs (should be default)

## Configuration Files Reference

### Dockerfile
Located at: `phase-2/auth-server/Dockerfile`
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3001
CMD ["npm", "start"]
```

### railway.json
Located at: `phase-2/auth-server/railway.json`
- Health check endpoint: `/api/auth/health`
- Restart policy: ON_FAILURE with max 10 retries

### railway.toml (Root)
Located at: `/railway.toml`
- Defines multi-service deployment structure
- Auth-server source: `phase-2/auth-server`

## Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Test database connectivity separately
4. Review Neon database logs for connection issues
5. Check Railway community forums: https://help.railway.app

## Environment Variables Summary

| Variable | Value | Notes |
|----------|-------|-------|
| DATABASE_URL | `postgresql://...` | From Neon dashboard |
| BETTER_AUTH_SECRET | `ajRphFFR4XJ5aIM1q2PRtjq31pTTnWKeYjzmBk0e50g=` | Pre-generated |
| BETTER_AUTH_URL | `https://${{RAILWAY_PUBLIC_DOMAIN}}` | Auto-populated |
| CORS_ORIGINS | `https://talal-s-tda.vercel.app` | Vercel frontend |
| PORT | `3001` | Must match Dockerfile |
| NODE_ENV | `production` | Standard |
