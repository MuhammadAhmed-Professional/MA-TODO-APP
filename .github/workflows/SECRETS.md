# GitHub Secrets Configuration

This document lists all required GitHub repository secrets for the CI/CD pipeline to function correctly.

## How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret listed below

---

## Required Secrets

### Authentication & Deployment

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `VERCEL_TOKEN` | Vercel authentication token for deploying frontend | 1. Go to https://vercel.com/account/tokens<br>2. Create a new token<br>3. Copy and paste as secret |
| `RAILWAY_TOKEN` | Railway authentication token for deploying backend | 1. Go to https://railway.app/account<br>2. Create an API token<br>3. Copy and paste as secret |
| `RAILWAY_PROJECT_ID` | Railway project ID for triggering redeploys | 1. Go to your Railway project<br>2. Copy Project ID from Settings<br>3. Paste as secret |

### Environment Variables

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) | `postgresql://user:password@host.region.neon.tech/dbname?sslmode=require` |
| `OPENAI_API_KEY` | OpenAI API key for AI chatbot features | `sk-proj-...` |
| `NEXT_PUBLIC_API_URL` | Backend API URL (accessible by frontend) | `https://your-backend.railway.app` |
| `FRONTEND_URL` | Deployed frontend URL for health checks | `https://your-app.vercel.app` |
| `BACKEND_URL` | Deployed backend URL for health checks | `https://your-backend.railway.app` |

### Backend Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `JWT_SECRET` | Secret key for JWT token signing | Generate with: `openssl rand -hex 32` |
| `BETTER_AUTH_SECRET` | Secret for Better Auth | Generate with: `openssl rand -hex 32` |

---

## Secret Generation Commands

Use these commands to generate secure random secrets:

```bash
# Generate JWT_SECRET
openssl rand -hex 32

# Generate BETTER_AUTH_SECRET
openssl rand -hex 32

# For DATABASE_URL, use your Neon database URL
# Found in Neon Dashboard > Connection Details > PostgreSQL
```

---

## Vercel Setup

1. **Create Vercel Account**: https://vercel.com/signup
2. **Import Project**: Connect your GitHub repository
3. **Configure Environment Variables** in Vercel Dashboard:
   - `NEXT_PUBLIC_API_URL`: Your backend URL
   - `NEXT_PUBLIC_BETTER_AUTH_URL`: Your frontend URL
4. **Get Token**: Go to https://vercel.com/account/tokens and create a token

---

## Railway Setup

1. **Create Railway Account**: https://railway.app/
2. **New Project**: Select "Deploy from Dockerfile"
3. **Configure Environment Variables** in Railway Dashboard:
   - `DATABASE_URL`: Your Neon PostgreSQL URL
   - `JWT_SECRET`: Your generated JWT secret
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `CORS_ORIGINS`: Your frontend URL
4. **Get Project ID**: From project settings
5. **Get API Token**: From https://railway.app/account

---

## Neon Database Setup

1. **Create Neon Account**: https://neon.tech/signup
2. **Create Database**: Follow the wizard to create a PostgreSQL database
3. **Get Connection String**: From Dashboard > Connection Details
4. **Format**: `postgresql://user:password@host.region.neon.tech/dbname?sslmode=require`

---

## OpenAI API Setup

1. **Create OpenAI Account**: https://platform.openai.com/
2. **Generate API Key**: https://platform.openai.com/api-keys
3. **Copy Key**: Store securely and add to GitHub Secrets

---

## Security Best Practices

- **Never commit secrets** to your repository
- **Use different secrets** for development, staging, and production
- **Rotate secrets regularly** (every 90 days recommended)
- **Use minimum permissions** for API tokens
- **Monitor secret usage** in provider dashboards
- **Enable 2FA** on all provider accounts

---

## Troubleshooting

### Vercel Deployment Fails
- Verify `VERCEL_TOKEN` is valid and not expired
- Check `NEXT_PUBLIC_API_URL` points to correct backend
- Ensure Vercel project is linked to GitHub repository

### Railway Deployment Fails
- Verify `RAILWAY_TOKEN` has project access
- Check `RAILWAY_PROJECT_ID` matches your project
- Ensure `railway.json` exists in backend directory

### Tests Fail in CI
- Verify `DATABASE_URL` is set (can use test database)
- Ensure `OPENAI_API_KEY` is set for backend tests
- Check that all dependencies are installable

### Health Checks Fail
- Verify `FRONTEND_URL` and `BACKEND_URL` are correct
- Ensure deployments completed successfully
- Check application logs for runtime errors

---

## Local Development Setup

For local development, create a `.env.local` file (frontend) and `.env` file (backend):

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_ENVIRONMENT=development
```

### Backend `.env`
```env
DATABASE_URL=postgresql://user:password@localhost:5432/tododb
JWT_SECRET=your-local-secret
OPENAI_API_KEY=your-openai-key
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
```

**IMPORTANT**: Never commit `.env` or `.env.local` files to version control.
