# Phase 2 Deployment Checklist

## Status: Ready for Production Deployment

This checklist ensures all requirements for Phase II hackathon submission are met.

---

## ✅ Pre-Deployment Verification

### Code Quality
- [x] All unused markdown files removed
- [x] Clean project structure
- [x] All services tested locally
- [x] Environment examples created

### Deployment Files Created
- [x] `frontend/vercel.json` - Vercel configuration
- [x] `frontend/.env.example` - Frontend environment template
- [x] `backend/Dockerfile` - Backend containerization
- [x] `backend/railway.json` - Railway configuration
- [x] `backend/.env.example` - Backend environment template
- [x] `auth-server/Dockerfile` - Auth server containerization
- [x] `auth-server/railway.json` - Railway configuration
- [x] `auth-server/.env.example` - Auth server environment template
- [x] `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide

---

## 📋 Deployment Steps

### Step 1: Database Setup (Neon PostgreSQL)

**Account Setup:**
- [ ] Sign up at https://console.neon.tech
- [ ] Create new project: `phase2-todo-db`
- [ ] Select region (closest to users)
- [ ] Copy connection string

**Connection String Format:**
```
postgresql://[user]:[password]@[host]/[dbname]?sslmode=require
```

**Save for later use in:**
- Backend `DATABASE_URL`
- Auth Server `DATABASE_URL` (with `?schema=auth` suffix)

---

### Step 2: Backend Deployment (Railway)

**Prerequisites:**
- [ ] GitHub repository pushed with all changes
- [ ] Neon database connection string ready
- [ ] OpenAI API key ready (for Phase III)

**Deploy via Railway Dashboard:**

1. **Create Account:**
   - [ ] Go to https://railway.app
   - [ ] Sign up with GitHub

2. **Create New Project:**
   - [ ] Click "New Project"
   - [ ] Select "Deploy from GitHub repo"
   - [ ] Choose your repository
   - [ ] Root Directory: `phase-2/backend`

3. **Configure Environment Variables:**
   ```
   DATABASE_URL=postgresql://[neon-connection-string]
   JWT_SECRET=[generate: openssl rand -base64 32]
   CORS_ORIGINS=http://localhost:3000
   OPENAI_API_KEY=sk-[your-key-here]
   ENVIRONMENT=production
   ```

4. **Deploy:**
   - [ ] Railway auto-detects Dockerfile
   - [ ] Wait for build to complete
   - [ ] Copy generated URL (e.g., `https://backend-production-xxxx.up.railway.app`)

5. **Verify Deployment:**
   ```bash
   curl https://[your-backend-url]/health
   # Should return: {"status":"healthy","timestamp":"..."}
   ```

**Backend URL:** `______________________________________`

---

### Step 3: Auth Server Deployment (Railway)

**Deploy via Railway Dashboard:**

1. **Create New Service:**
   - [ ] In same Railway project, click "New"
   - [ ] Select "GitHub Repo"
   - [ ] Choose your repository again
   - [ ] Root Directory: `phase-2/auth-server`

2. **Configure Environment Variables:**
   ```
   PORT=3001
   DATABASE_URL=postgresql://[neon-connection-string]?schema=auth
   JWT_SECRET=[same as backend]
   BETTER_AUTH_SECRET=[generate: openssl rand -base64 32]
   FRONTEND_URL=http://localhost:3000
   ENVIRONMENT=production
   ```

3. **Deploy:**
   - [ ] Wait for build to complete
   - [ ] Copy generated URL (e.g., `https://auth-production-xxxx.up.railway.app`)

4. **Verify Deployment:**
   ```bash
   curl https://[your-auth-url]/api/auth/health
   ```

**Auth Server URL:** `______________________________________`

---

### Step 4: Update CORS Settings

**After deploying frontend (Step 5), come back and update:**

1. **Backend CORS:**
   - [ ] Go to Railway backend service
   - [ ] Update `CORS_ORIGINS` variable
   - [ ] Set to: `https://[your-vercel-app].vercel.app`
   - [ ] Service will auto-redeploy

2. **Auth Server Frontend URL:**
   - [ ] Go to Railway auth-server service
   - [ ] Update `FRONTEND_URL` variable
   - [ ] Set to: `https://[your-vercel-app].vercel.app`
   - [ ] Service will auto-redeploy

---

### Step 5: Frontend Deployment (Vercel)

**Prerequisites:**
- [ ] Backend URL from Step 2
- [ ] Auth Server URL from Step 3

**Deploy via Vercel Dashboard:**

1. **Create Account:**
   - [ ] Go to https://vercel.com
   - [ ] Sign up with GitHub

2. **Import Project:**
   - [ ] Click "Add New" → "Project"
   - [ ] Import your GitHub repository
   - [ ] Root Directory: `phase-2/frontend`
   - [ ] Framework Preset: Next.js (auto-detected)

3. **Configure Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://[your-backend-url].railway.app
   NEXT_PUBLIC_AUTH_URL=https://[your-auth-url].railway.app
   BETTER_AUTH_SECRET=[same as backend and auth-server]
   NEXT_PUBLIC_ENVIRONMENT=production
   ```

4. **Deploy:**
   - [ ] Click "Deploy"
   - [ ] Wait for build to complete (2-3 minutes)
   - [ ] Copy generated URL (e.g., `https://phase2-todo.vercel.app`)

5. **Verify Deployment:**
   - [ ] Open frontend URL in browser
   - [ ] Should see landing page without errors

**Frontend URL:** `______________________________________`

---

### Step 6: Final Configuration Update

**Now that all services are deployed, update URLs:**

1. **Update Backend CORS:**
   - [ ] Railway → Backend Service → Variables
   - [ ] `CORS_ORIGINS` = `https://[your-frontend].vercel.app`

2. **Update Auth Server:**
   - [ ] Railway → Auth Service → Variables
   - [ ] `FRONTEND_URL` = `https://[your-frontend].vercel.app`

3. **Trigger Redeployment:**
   - [ ] Both services will auto-redeploy with new settings

---

## 🧪 Testing Checklist

### Health Checks
- [ ] Backend health endpoint responds: `curl [backend-url]/health`
- [ ] Auth server health endpoint responds: `curl [auth-url]/api/auth/health`
- [ ] Frontend loads without errors

### User Authentication Flow
- [ ] Open frontend URL
- [ ] Click "Sign Up"
- [ ] Create account with email/password
- [ ] Verify redirect to dashboard
- [ ] Logout and login again
- [ ] Verify session persists

### Task Management Flow
- [ ] Login to application
- [ ] Create a new task
- [ ] Verify task appears in list
- [ ] Edit task title
- [ ] Mark task as complete
- [ ] Delete task
- [ ] All operations should work without errors

### API Documentation
- [ ] Visit `[backend-url]/docs`
- [ ] Swagger UI should load
- [ ] Try "Try it out" on `/health` endpoint

### Database Verification
- [ ] Go to Neon Console
- [ ] Check Tables browser
- [ ] Verify `users` table has entries
- [ ] Verify `tasks` table has entries

---

## 📊 Monitoring & Logs

### Railway Logs
```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login
railway login

# View backend logs
railway logs

# View auth server logs
railway logs --service auth-server
```

### Vercel Logs
- [ ] Go to Vercel Dashboard
- [ ] Select your project
- [ ] Click "Deployments" → Latest deployment
- [ ] View "Functions" tab for logs

---

## 📦 Hackathon Submission Requirements

### 1. GitHub Repository
- [x] All source code for Phase II
- [x] `/specs` folder with specifications
- [x] `CLAUDE.md` with instructions
- [x] `README.md` with setup guide
- [x] Clean folder structure
- [x] `.env.example` files for all services

**Repository URL:** `______________________________________`

### 2. Deployed Application Links

**Frontend (Vercel):** `______________________________________`

**Backend API (Railway):** `______________________________________`

**API Docs (Swagger):** `[backend-url]/docs`

### 3. Demo Video (Max 90 seconds)

**Video Script Outline:**
1. (0-10s) Introduction: "Phase II Full-Stack Todo App"
2. (10-20s) Show signup/login flow
3. (20-35s) Create and manage tasks (CRUD)
4. (35-50s) Show API documentation at `/docs`
5. (50-70s) Show database in Neon console
6. (70-85s) Highlight tech stack: Next.js, FastAPI, Neon
7. (85-90s) Call to action: "View source on GitHub"

**Recording Tools:**
- Option 1: Use [NotebookLM](https://notebooklm.google.com) for AI-generated demo
- Option 2: OBS Studio + Screen recording
- Option 3: Loom (free tier)

**Video Requirements:**
- [ ] Under 90 seconds (judges only watch first 90s)
- [ ] Show all Basic Level features working
- [ ] Include GitHub repo link in description
- [ ] Upload to YouTube/Vimeo (unlisted is fine)

**Video URL:** `______________________________________`

### 4. Contact Information
**WhatsApp Number:** `______________________________________`

---

## 🎯 Submission Form

**Submit at:** https://forms.gle/CQsSEGM3GeCrL43c8

**Information to Submit:**
1. ✅ Public GitHub Repo Link
2. ✅ Vercel Frontend URL
3. ✅ Railway Backend URL
4. ✅ Demo Video Link (YouTube/Vimeo)
5. ✅ WhatsApp Number

**Deadline:** Sunday, December 14, 2025 (Phase II Due Date)

---

## ✅ Final Checklist

### Before Submission
- [ ] All services deployed and healthy
- [ ] All 5 Basic Level features working
- [ ] Authentication flow works end-to-end
- [ ] Database contains test data
- [ ] API documentation accessible
- [ ] Demo video recorded and uploaded
- [ ] GitHub repository is public
- [ ] README.md has clear setup instructions

### Bonus Points Opportunities
- [ ] Created reusable Claude Code subagents (+200 points)
- [ ] Implemented cloud-native blueprints (+200 points)
- [ ] Added comprehensive test coverage
- [ ] Added monitoring/logging setup

---

## 🚀 Deployment Status

| Service      | Status | URL                               |
| :----------- | :----- | :-------------------------------- |
| Database     | ⬜      | postgresql://...                  |
| Backend      | ⬜      | https://backend-xxx.railway.app   |
| Auth Server  | ⬜      | https://auth-xxx.railway.app      |
| Frontend     | ⬜      | https://phase2-todo.vercel.app    |
| Demo Video   | ⬜      | https://youtube.com/...           |
| Submission   | ⬜      | Submitted to form                 |

**Legend:** ⬜ Pending | ⏳ In Progress | ✅ Complete | ❌ Failed

---

## 📞 Support Resources

### Official Documentation
- **Neon Docs:** https://neon.tech/docs
- **Railway Docs:** https://docs.railway.app
- **Vercel Docs:** https://vercel.com/docs
- **Next.js Docs:** https://nextjs.org/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com

### Hackathon Resources
- **Hackathon Guide:** [Link provided by organizers]
- **Claude Code Docs:** https://claude.ai/docs
- **Spec-Kit Plus:** https://github.com/panaversity/spec-kit-plus

### Community Support
- **WhatsApp Group:** [If provided]
- **Discord:** [If provided]
- **Zoom Presentations:** Sundays 8:00 PM

---

## 🎓 Learning Outcomes (Phase II)

By completing Phase II deployment, you have learned:

- ✅ Full-stack application architecture
- ✅ Serverless PostgreSQL with Neon
- ✅ Modern authentication with Better Auth + JWT
- ✅ RESTful API design with FastAPI
- ✅ Frontend deployment with Vercel
- ✅ Backend deployment with Railway
- ✅ Environment variable management
- ✅ Docker containerization
- ✅ CI/CD basics (auto-deployment)
- ✅ Database migrations with Alembic

**Next:** Phase III - AI Chatbot with OpenAI Agents SDK and MCP

---

**Last Updated:** 2025-12-17
**Status:** Ready for Deployment ✅
