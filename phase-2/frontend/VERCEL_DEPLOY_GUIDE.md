# Vercel CLI Deployment Guide

## Quick Deploy (Automated)

### Option 1: Using the Deploy Script (Recommended)

```bash
cd phase-2/frontend

# 1. First, login to Vercel
vercel login

# 2. Run the automated deployment script
./deploy.sh
```

The script will:
- ✅ Check Vercel authentication
- ✅ Set all environment variables automatically
- ✅ Deploy to production
- ✅ Provide deployment URL

---

## Manual Deploy (Step-by-Step)

If you prefer manual control, follow these steps:

### Step 1: Login to Vercel

```bash
cd phase-2/frontend
vercel login
```

This will:
1. Show you a URL like: `https://vercel.com/oauth/device?user_code=XXXX-XXXX`
2. Open your browser (or manually visit the URL)
3. Click "Confirm" to authenticate
4. Press ENTER in the terminal

### Step 2: Set Environment Variables

You need to set these environment variables in Vercel:

#### Required Variables:

1. **NEXT_PUBLIC_API_URL** (Backend URL)
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # When prompted, enter: https://backend-production-9a40.up.railway.app
   ```

2. **BETTER_AUTH_SECRET** (Authentication Secret)
   ```bash
   vercel env add BETTER_AUTH_SECRET production
   # When prompted, enter: 9TNI5WqJgVWRDvg8J5053/yEH7dnnLUNliT3x7CI0Qw=
   ```

3. **NEXT_PUBLIC_ENVIRONMENT** (Environment Name)
   ```bash
   vercel env add NEXT_PUBLIC_ENVIRONMENT production
   # When prompted, enter: production
   ```

4. **NEXT_PUBLIC_APP_NAME** (Application Name)
   ```bash
   vercel env add NEXT_PUBLIC_APP_NAME production
   # When prompted, enter: Phase II Todo
   ```

**Note:** For each variable, you'll be asked:
- "Which Environments (Use arrow keys)?"
- Select: `Production`, `Preview`, and `Development` (use spacebar to select multiple)

### Step 3: Deploy to Vercel

```bash
# Deploy to production
vercel --prod
```

This will:
1. Build your Next.js application
2. Upload to Vercel
3. Deploy to production
4. Show you the deployment URL

### Step 4: Verify Deployment

After deployment completes, you'll see:

```
✅ Production: https://frontend-six-coral-90.vercel.app [copied to clipboard]
```

Visit the URL to verify:
- ✅ Landing page loads
- ✅ Signup/Login works
- ✅ Dashboard is accessible after login
- ✅ Tasks can be created, edited, completed, deleted

---

## Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | `https://backend-production-9a40.up.railway.app` | Backend API endpoint |
| `BETTER_AUTH_SECRET` | `9TNI5WqJgVWRDvg8J5053/yEH7dnnLUNliT3x7CI0Qw=` | Auth encryption secret |
| `NEXT_PUBLIC_ENVIRONMENT` | `production` | Environment identifier |
| `NEXT_PUBLIC_APP_NAME` | `Phase II Todo` | Application display name |

---

## Vercel CLI Commands Reference

### Check login status
```bash
vercel whoami
```

### List projects
```bash
vercel ls
```

### View environment variables
```bash
vercel env ls
```

### Remove an environment variable
```bash
vercel env rm VARIABLE_NAME production
```

### View deployment logs
```bash
vercel logs
```

### List all deployments
```bash
vercel ls ma-todo-app
```

### Promote a preview deployment to production
```bash
vercel promote [deployment-url]
```

---

## Troubleshooting

### "No existing credentials found"
**Solution:** Run `vercel login` first

### "Project not found"
**Solution:** The project is already linked. If you see this error, run:
```bash
vercel link --yes
```

### "Build failed"
**Solution:** Check build logs with:
```bash
vercel logs
```
Common issues:
- Missing environment variables
- TypeScript errors
- Missing dependencies

### "Environment variables not working"
**Solution:**
1. Verify they're set for the right environment:
   ```bash
   vercel env ls
   ```
2. Redeploy after setting new variables:
   ```bash
   vercel --prod
   ```

### "CORS errors in browser"
**Solution:** Update backend CORS settings in Railway to allow your Vercel URL:
```env
CORS_ORIGINS=https://frontend-six-coral-90.vercel.app
```

---

## Deployment Checklist

Before submitting to hackathon:

- [ ] Logged in to Vercel CLI (`vercel whoami` works)
- [ ] All 4 environment variables set in production
- [ ] Deployment successful (`vercel --prod` completed)
- [ ] Deployment URL accessible (e.g., `https://frontend-six-coral-90.vercel.app`)
- [ ] Can signup/login successfully
- [ ] Can create tasks
- [ ] Can edit tasks
- [ ] Can complete tasks
- [ ] Can delete tasks
- [ ] Backend API responding (check Network tab in browser DevTools)
- [ ] No CORS errors in browser console

---

## Next Steps After Deployment

1. **Test All Features:**
   - Visit your deployment URL
   - Create a test account
   - Test all CRUD operations

2. **Update Documentation:**
   - Add deployment URL to README.md
   - Update PHASE_2_READY.md with live URL

3. **Record Demo Video:**
   - Screen record showing all features
   - Upload to YouTube/Vimeo
   - Keep under 90 seconds

4. **Submit to Hackathon:**
   - Form: https://forms.gle/CQsSEGM3GeCrL43c8
   - Include: GitHub URL, Vercel URL, Demo video, WhatsApp number

---

## Production URLs

After deployment, your URLs will be:

- **Frontend:** `https://frontend-six-coral-90.vercel.app` (or similar)
- **Backend API:** `https://backend-production-9a40.up.railway.app`
- **API Docs:** `https://backend-production-9a40.up.railway.app/docs`

---

## Support

- **Vercel Docs:** https://vercel.com/docs
- **Vercel CLI Docs:** https://vercel.com/docs/cli
- **Project Deployment Guide:** `../DEPLOYMENT_GUIDE.md`
- **Quick Start:** `../DEPLOYMENT_QUICKSTART.md`

---

**Generated:** 2025-12-18
**Backend:** Railway (Already Deployed ✅)
**Database:** Neon PostgreSQL (Already Configured ✅)
**Frontend:** Vercel (Ready to Deploy 🚀)
