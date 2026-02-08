# 🚀 Phase 2 Deployment - Quick Start Guide

**Time Required:** 30-45 minutes  
**Difficulty:** Beginner-Friendly  
**Cost:** $0 (using free tiers)

---

## 📋 What You'll Deploy

A full-stack Todo application with:
- **Frontend:** Next.js on Vercel
- **Backend:** FastAPI on Railway  
- **Auth Server:** Node.js on Railway
- **Database:** PostgreSQL on Neon

---

## ⚡ 5-Step Deployment (Express Path)

### Step 1: Neon Database (5 minutes)

1. Go to https://console.neon.tech
2. Click "Sign Up" (use GitHub for quick signup)
3. Create Project:
   - Name: `phase2-todo-db`
   - Region: Choose closest to you
4. **COPY CONNECTION STRING** (you'll need it 3 times)
   - Format: `postgresql://user:pass@host/dbname`
   - Save it somewhere safe!

✅ **Done!** You have a serverless PostgreSQL database.

---

### Step 2: Deploy Backend (10 minutes)

1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. **Important:** Set Root Directory to `phase-2/backend`
6. Add these environment variables (click "Variables"):

```env
DATABASE_URL=<paste-your-neon-connection-string>
JWT_SECRET=<generate below>
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-placeholder-for-now
ENVIRONMENT=production
```

**Generate JWT_SECRET:**
```bash
# On Linux/Mac:
openssl rand -base64 32

# On Windows (PowerShell):
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))

# Or use online: https://generate-secret.vercel.app/32
```

7. Click "Deploy"
8. Wait 3-5 minutes
9. **COPY THE GENERATED URL** (looks like: `https://backend-production-abc123.up.railway.app`)
10. Test it: Visit `https://your-backend-url/docs` (should see Swagger UI)

✅ **Backend is live!**

---

### Step 3: Deploy Auth Server (10 minutes)

1. In same Railway project, click "New" → "GitHub Repo"
2. Select your repository again
3. **Important:** Set Root Directory to `phase-2/auth-server`
4. Add environment variables:

```env
PORT=3001
DATABASE_URL=<paste-neon-connection-string>?schema=auth
JWT_SECRET=<same-as-backend>
BETTER_AUTH_SECRET=<generate-new-secret>
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=production
```

**Generate BETTER_AUTH_SECRET** (use same method as JWT_SECRET)

5. Click "Deploy"
6. Wait 3-5 minutes
7. **COPY THE GENERATED URL** (looks like: `https://auth-production-xyz789.up.railway.app`)
8. Test it: `curl https://your-auth-url/api/auth/health`

✅ **Auth server is live!**

---

### Step 4: Deploy Frontend (10 minutes)

1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New" → "Project"
4. Import your GitHub repository
5. **Important:** Set Root Directory to `phase-2/frontend`
6. Framework: Next.js (auto-detected)
7. Add environment variables:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_AUTH_URL=https://your-auth-url.railway.app
BETTER_AUTH_SECRET=<same-as-auth-server>
NEXT_PUBLIC_ENVIRONMENT=production
```

8. Click "Deploy"
9. Wait 2-3 minutes
10. **COPY YOUR VERCEL URL** (looks like: `https://phase2-todo-abc123.vercel.app`)

✅ **Frontend is live!**

---

### Step 5: Update CORS (5 minutes)

Now that frontend is deployed, update backend CORS settings:

1. **Go back to Railway**
2. **Select Backend service**
3. Click "Variables"
4. Update `CORS_ORIGINS`:
   ```
   https://your-vercel-app.vercel.app
   ```
5. **Select Auth Server service**
6. Update `FRONTEND_URL`:
   ```
   https://your-vercel-app.vercel.app
   ```
7. Both services will auto-redeploy (wait 2-3 minutes)

✅ **All services connected!**

---

## 🧪 Test Your Deployment

### 1. Open Your App
Visit: `https://your-vercel-app.vercel.app`

### 2. Create Account
1. Click "Sign Up"
2. Enter email: `test@example.com`
3. Enter password: `Test@123456`
4. Should redirect to dashboard

### 3. Test Task Management
1. Click "Add Task"
2. Title: "Deploy Phase 2"
3. Description: "Complete hackathon submission"
4. Click Save
5. Task should appear in list
6. Try: Edit, Complete, Delete

### 4. Verify API
Visit: `https://your-backend-url.railway.app/docs`
- Should see interactive Swagger UI

✅ **Everything works!**

---

## 📹 Record Demo Video (10 minutes)

### Option 1: Use NotebookLM (AI-Generated)
1. Go to https://notebooklm.google.com
2. Upload your README.md
3. Click "Generate Audio Overview"
4. Download and use as voiceover
5. Record screen showing app features
6. Combine with video editor

### Option 2: Screen Recording
1. **Windows:** Use Xbox Game Bar (Win + G)
2. **Mac:** QuickTime Player → New Screen Recording
3. **Linux:** OBS Studio (free)

**What to Record (90 seconds):**
```
0:00-0:10  Show landing page, introduce app
0:10-0:20  Sign up / Login flow
0:20-0:40  Create, edit, complete tasks
0:40-0:55  Show API docs (Swagger UI)
0:55-1:15  Show database in Neon console
1:15-1:25  Highlight tech stack
1:25-1:30  Show GitHub repo, end screen
```

### Upload Options
- YouTube (unlisted): Free, easy sharing
- Vimeo: Professional look
- Google Drive: Simple, direct link

---

## 📝 Submit to Hackathon

**Form:** https://forms.gle/CQsSEGM3GeCrL43c8

**You'll Need:**
1. ✅ GitHub Repo URL (public)
2. ✅ Vercel Frontend URL
3. ✅ Railway Backend URL (optional but recommended)
4. ✅ Demo Video URL
5. ✅ WhatsApp Number

**Deadline:** Sunday, December 14, 2025

---

## 🆘 Troubleshooting

### "Database connection failed"
- Check Neon database is not paused (free tier auto-pauses after 7 days inactive)
- Verify connection string has `?sslmode=require`
- Check Railway logs: `railway logs`

### "CORS error" in browser console
- Verify `CORS_ORIGINS` in backend matches your Vercel URL exactly
- No trailing slash in URL
- Wait for Railway to redeploy after changing variables

### "Authentication not working"
- Verify `JWT_SECRET` is the same in backend and auth server
- Check `BETTER_AUTH_SECRET` is set in all 3 services
- Clear browser cookies and try again

### "Frontend not loading"
- Check Vercel deployment logs
- Verify all environment variables are set
- Try rebuilding: Vercel Dashboard → Deployments → "..." → "Redeploy"

---

## 💰 Cost Breakdown

| Service       | Free Tier                | What You Get              |
| :------------ | :----------------------- | :------------------------ |
| **Neon**      | 1 project free forever   | 3GB storage, 0.5GB RAM    |
| **Railway**   | $5 credit/month (resets) | ~500 hours/month          |
| **Vercel**    | Unlimited hobby projects | 100GB bandwidth/month     |
| **Total**     | **$0/month**             | Perfect for hackathon! 🎉 |

---

## 🎯 Success Checklist

Before submitting:
- [ ] All 3 services deployed and healthy
- [ ] Can sign up and login
- [ ] Can create, edit, delete tasks
- [ ] API docs accessible at `/docs`
- [ ] Demo video under 90 seconds
- [ ] GitHub repo is public
- [ ] Form submitted before deadline

---

## 📚 What You Learned

- ✅ Deploying to 3 different cloud platforms
- ✅ Managing environment variables in production
- ✅ CORS configuration
- ✅ Database connection pooling
- ✅ JWT authentication flow
- ✅ CI/CD basics (auto-deployment from git)
- ✅ Monitoring and debugging production apps

**Next Phase:** Phase III - AI Chatbot (Due: Dec 21, 2025)

---

## 🎉 Congratulations!

You've successfully deployed a full-stack application to production!

**Share your achievement:**
- Tweet your demo with #Panaversity
- Add "Deployed to production" to your resume
- Show it in your portfolio

**Questions?** 
- Join Zoom presentation: Sundays 8:00 PM
- Check deployment guide: `DEPLOYMENT_GUIDE.md`

---

**Need Help?** Re-read the detailed `DEPLOYMENT_GUIDE.md` in this directory.

**Ready for More?** Start Phase III - AI Chatbot implementation!
