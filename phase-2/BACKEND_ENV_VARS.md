# Backend Environment Variables Configuration

## Required Variables for Railway Deployment

Configure these in Railway dashboard for the backend service (`ma-todo-app-production`):

```env
# Database Connection
DATABASE_URL=postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Auth Server URL (Better Auth)
AUTH_SERVER_URL=https://auth-server-production-cd0e.up.railway.app

# JWT Secret (MUST match BETTER_AUTH_SECRET in auth-server)
JWT_SECRET=cbdca7cd62ff75aa5d8460c94dd5dc5ed3a1366629a701576e5a80df207b4801

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://frontend-six-coral-90.vercel.app

# Environment
ENVIRONMENT=production
```

## Steps to Configure via Railway Dashboard:

1. Go to: https://railway.app/project/1a580b9d-e43b-4faf-a523-b3454b9d3bf1
2. Find the backend service (should be named similar to "tda" or "backend")
3. Click "Variables" tab
4. Add each of the above variables
5. Railway will automatically redeploy after variable changes

## Testing After Configuration:

```bash
# Test health endpoint
curl https://backend-production-9a40.up.railway.app/health

# Test signup endpoint
curl -X POST https://backend-production-9a40.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test pass123"}'
```

## Expected Results:

- Health check: `{"status":"healthy"}`
- Signup: Should proxy to auth-server and return user data with session token
