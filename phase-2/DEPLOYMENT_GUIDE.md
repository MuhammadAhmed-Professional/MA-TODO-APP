# Deployment Guide - Hackathon II Submission

This guide covers all deployment steps needed to complete the hackathon submission.

---

## Quick Start Deployment Checklist

- [ ] 1. Deploy Frontend to Vercel
- [ ] 2. Deploy Backend to Railway/Render
- [ ] 3. Deploy to Minikube (Phase IV verification)
- [ ] 4. Record Demo Video
- [ ] 5. Submit Google Form
- [ ] 6. Prepare for Live Presentation

---

## 1. Deploy Frontend to Vercel

### Prerequisites
- Vercel account (free tier)
- GitHub repository connected to Vercel

### Steps

\`\`\`bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy from frontend directory
cd phase-2/frontend
vercel --prod

# 4. Set environment variables in Vercel dashboard
# Go to https://vercel.com/your-project/settings/environment-variables
# Add:
#   NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
#   NEXT_PUBLIC_BETTER_AUTH_URL=https://your-frontend.vercel.app
#   BETTER_AUTH_SECRET=your-generated-secret
\`\`\`

### Alternative: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Root directory: \`phase-2/frontend\`
4. Click "Deploy"

---

## 2. Deploy Backend to Railway

### Prerequisites
- Railway account (free $200 credit for 60 days)
- Railway CLI

### Steps

\`\`\`bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway create

# 4. Add PostgreSQL database
railway add postgresql

# 5. Add Backend service
railway add --service=backend

# 6. Deploy
railway up
\`\`\`

---

## 3. Minikube Deployment (Phase IV Verification)

### Prerequisites
- Minikube installed
- kubectl installed
- Helm 3 installed
- Dapr CLI installed

### Steps

\`\`\`bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Install Dapr
dapr init -k

# 3. Build and load Docker images
eval \$(minikube docker-env)
cd phase-2/backend && docker build -t todo-backend:latest .
cd ../frontend && docker build -t todo-frontend:latest .

# 4. Create namespace and secrets
kubectl apply -f phase-2/k8s/namespace.yaml

# 5. Deploy using Helm
helm install todo-backend phase-2/helm/todo-backend --namespace todo-app
helm install todo-frontend phase-2/helm/todo-frontend --namespace todo-app

# 6. Access applications
minikube ip
\`\`\`

---

## 4. Record Demo Video

See \`phase-2/DEMO_VIDEO_SCRIPT.md\` for the full script.

### Recording Tools
- OBS Studio (Free)
- Loom (Browser-based)
- Microsoft Teams/Zoom Recording

### Demo Checklist
- [ ] 0:05 - Title screen
- [ ] 0:15 - Authentication
- [ ] 0:30 - Dashboard CRUD
- [ ] 0:55 - AI Chatbot
- [ ] 1:10 - i18n (Urdu)
- [ ] 1:20 - Event architecture
- [ ] 1:30 - Closing

---

## 5. Submit Google Form

**Form**: https://forms.gle/KMKEKaFUD6ZX4UtY8

### Required Information
- GitHub repo link
- Vercel app URL
- Demo video URL
- WhatsApp number

---

## 6. Live Presentation

**When**: Sundays 8PM PKT
**Zoom**: https://us06web.zoom.us/j/84976847088?pwd=Z7t7NaeXWVmmR5fysCv7NiMbfbIda.1
**Meeting ID**: 849 7684 7088
**Passcode**: 305850

---

**Good luck! 🚀**
