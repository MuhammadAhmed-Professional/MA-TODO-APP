# 🤖 Automation Skills Guide

## Overview

I've created **three comprehensive automation skills** for your full-stack todo application deployment and testing. These skills automate the entire workflow from code deployment to browser testing.

---

## 📦 Skills Created

### 1. **browser-test-auth** - Browser Testing Automation
**Location**: `.claude/skills/browser-test-auth/skill.md`

**What it does**:
- Automates login testing with Playwright
- Captures network requests/responses
- Verifies cookie settings (SameSite, Secure, HttpOnly)
- Takes screenshots for debugging
- Tests dashboard access
- Generates detailed test reports

**Use when**: You need to verify authentication works after deployment

### 2. **railway-deploy** - Railway Deployment Automation
**Location**: `.claude/skills/railway-deploy/skill.md`

**What it does**:
- Sets environment variables in Railway
- Triggers service deployments
- Monitors deployment progress
- Runs health checks
- Handles rollbacks
- Manages multiple services

**Use when**: You need to deploy or configure Railway services

### 3. **e2e-workflow** - End-to-End Workflow Orchestration
**Location**: `.claude/skills/e2e-workflow/skill.md`

**What it does**:
- Orchestrates full deployment pipeline
- Deploys frontend + backend + auth server
- Configures all environment variables
- Runs comprehensive testing suite
- Auto-rollback on failure
- Generates deployment reports

**Use when**: You need to deploy and test everything at once

---

## 🚀 How to Use These Skills

### Invoking Skills

**Method 1: Direct Command (Future)**
```bash
# Once skills are registered in Claude Code
/browser-test-auth --url https://frontend-six-coral-90.vercel.app
/railway-deploy --service backend --action deploy
/e2e-workflow --workflow deploy-test
```

**Method 2: Via Claude Conversation (Now)**
```
You: "Run the browser-test-auth skill to test login"
Claude: [Executes skill using Playwright MCP]

You: "Deploy backend using railway-deploy skill"
Claude: [Executes deployment using Railway CLI]

You: "Run full e2e-workflow for deploy-test"
Claude: [Orchestrates complete workflow]
```

---

## 📖 Skill Usage Examples

### Example 1: Test Authentication After Deployment

**Problem**: You deployed new code, want to verify login works

**Solution**:
```
You: "Use browser-test-auth skill to test my production frontend"

Claude will:
1. Navigate to https://frontend-six-coral-90.vercel.app/login
2. Fill login form with test credentials
3. Click sign-in button
4. Capture network traffic
5. Verify cookie settings
6. Check dashboard access
7. Generate report (PASS/FAIL)
```

**Expected Output**:
```json
{
  "status": "PASS",
  "login_status": 200,
  "cookie_found": true,
  "cookie_attributes": {
    "sameSite": "None",
    "secure": true,
    "httpOnly": true
  },
  "dashboard_loaded": true
}
```

### Example 2: Deploy Backend with Environment Variables

**Problem**: Need to set AUTH_SERVER_URL and deploy backend

**Solution**:
```
You: "Use railway-deploy skill to set AUTH_SERVER_URL and deploy backend"

Claude will:
1. Set AUTH_SERVER_URL environment variable
2. Trigger backend deployment
3. Wait for "Deployed" status
4. Run health check
5. Verify service is responding
```

**Expected Output**:
```json
{
  "action": "deploy",
  "service": "backend",
  "status": "DEPLOYED",
  "health_check": "PASS",
  "url": "https://backend-production-9a40.up.railway.app"
}
```

### Example 3: Full Deployment Pipeline

**Problem**: Want to deploy all services and run tests automatically

**Solution**:
```
You: "Run e2e-workflow with deploy-test workflow"

Claude will:
Phase 1: Deploy backend to Railway
Phase 2: Deploy auth server to Railway
Phase 3: Deploy frontend to Vercel
Phase 4: Set all environment variables
Phase 5: Run health checks
Phase 6: Run browser authentication tests
Phase 7: Run API tests
Phase 8: Generate deployment report

If ANY test fails → Auto-rollback all services
```

**Expected Output**:
```json
{
  "workflow": "deploy-test",
  "status": "SUCCESS",
  "deployments": {
    "backend": "DEPLOYED",
    "auth_server": "DEPLOYED",
    "frontend": "DEPLOYED"
  },
  "tests": {
    "browser_tests": "PASS",
    "api_tests": "PASS"
  }
}
```

---

## 🔧 Current Situation - What Needs to Be Done

### Step 1: Set AUTH_SERVER_URL Manually (30 seconds)

**Railway dashboard is already open in your browser!**

1. Click **"tda-backend-production"** service (if not already selected)
2. Click **"Variables"** tab (left sidebar)
3. Click **"New Variable"**
4. Add:
   - **Variable Name**: `AUTH_SERVER_URL`
   - **Value**: `https://auth-server-production-cd0e.up.railway.app`
5. Click **"Add"** or **"Save"**
6. Railway will auto-redeploy (~2 minutes)

### Step 2: Test with Playwright (After Redeploy)

**Once Railway shows "Deployed", tell me:**
```
You: "Railway deployed successfully"

I'll run:
- browser-test-auth skill to verify login works
- railway-deploy skill to check health
- Generate report
```

---

## 🎯 Skills Implementation Status

### ✅ Completed
- [x] browser-test-auth skill spec created
- [x] railway-deploy skill spec created
- [x] e2e-workflow skill spec created
- [x] Skills documentation written
- [x] Example usage documented

### 🔄 In Progress
- [ ] Test browser-test-auth with Playwright MCP (waiting for AUTH_SERVER_URL)
- [ ] Test railway-deploy CLI integration
- [ ] Run full e2e-workflow

### 📋 Next Steps
1. **Set AUTH_SERVER_URL in Railway** (you do this - 30 seconds)
2. **Wait for deployment** (Railway auto-deploys - 2 minutes)
3. **I test with skills** (browser-test-auth → verify login works)
4. **Iterate and improve** (add more test cases, optimize workflows)

---

## 🛠️ How Skills Work (Technical Details)

### Skill Structure
```
.claude/skills/
├── browser-test-auth/
│   └── skill.md         # Skill specification
├── railway-deploy/
│   └── skill.md         # Skill specification
└── e2e-workflow/
    └── skill.md         # Skill specification
```

### Skill Invocation Flow
```
User says: "Run browser-test-auth skill"
       ↓
Claude reads: .claude/skills/browser-test-auth/skill.md
       ↓
Claude executes: Uses Playwright MCP tools
       ↓
Claude generates: Test report (JSON/screenshots)
       ↓
Claude responds: "✅ Test passed! Dashboard loads successfully"
```

### Tools Used by Skills

**browser-test-auth uses**:
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_type`
- `mcp__playwright__browser_click`
- `mcp__playwright__browser_network_requests`
- `mcp__playwright__browser_take_screenshot`
- `mcp__playwright__browser_console_messages`

**railway-deploy uses**:
- `railway variables --set`
- `railway up`
- `railway status`
- `railway logs`
- `curl` (for health checks)

**e2e-workflow uses**:
- All of the above
- `vercel --prod`
- `git push`
- Custom orchestration logic

---

## 📚 Future Enhancements

### Planned Features
1. **Slack/Email Notifications**: Alert team on deployment success/failure
2. **Performance Monitoring**: Track response times, memory usage
3. **Security Scanning**: Automated security checks
4. **Load Testing**: Simulate high traffic scenarios
5. **Database Migration Automation**: Auto-run migrations before deployment
6. **Blue-Green Deployments**: Zero-downtime deployments
7. **Canary Releases**: Gradual rollout with monitoring

### Skill Extensions
1. **browser-test-tasks**: Test full task CRUD operations
2. **railway-monitor**: Real-time service monitoring
3. **vercel-deploy**: Automated Vercel deployment skill
4. **database-migration**: Database migration automation
5. **security-audit**: Security vulnerability scanning

---

## 🆘 Troubleshooting

### Skill Not Working

**Problem**: Claude doesn't execute the skill

**Solutions**:
1. Check skill.md exists in `.claude/skills/{skill-name}/`
2. Verify skill specification is valid
3. Try invoking explicitly: "Execute the browser-test-auth skill"

### Playwright Not Available

**Problem**: Browser automation not working

**Solutions**:
1. Verify Playwright MCP is connected: `/mcp` command
2. Restart Claude if needed
3. Check Playwright tools are available

### Railway CLI Not Working

**Problem**: Deployment commands fail

**Solutions**:
1. Check Railway CLI is authenticated: `railway whoami`
2. Verify project/service IDs are correct
3. Use Railway dashboard as fallback

---

## 📊 Success Metrics

### How to Know Skills Are Working

**browser-test-auth SUCCESS**:
- ✅ Can navigate to login page
- ✅ Can fill and submit form
- ✅ Captures network requests
- ✅ Verifies cookie settings
- ✅ Screenshots saved
- ✅ Report generated

**railway-deploy SUCCESS**:
- ✅ Environment variables set
- ✅ Deployment triggered
- ✅ Health check returns 200 OK
- ✅ Service shows "Deployed" in Railway
- ✅ No errors in logs

**e2e-workflow SUCCESS**:
- ✅ All services deployed
- ✅ All health checks passing
- ✅ Browser tests passing
- ✅ API tests passing
- ✅ Zero critical errors

---

## 🎉 What's Next?

### Immediate Actions
1. **You**: Set AUTH_SERVER_URL in Railway (30 sec)
2. **Railway**: Auto-redeploys backend (2 min)
3. **Me**: Run browser-test-auth skill to verify
4. **Me**: Generate full deployment report

### Future Automation
Once these skills are working, you can:
- Deploy with single command
- Test with single command
- Rollback with single command
- Get detailed reports automatically

### CI/CD Integration
Add to GitHub Actions:
```yaml
- name: Deploy and Test
  run: claude-code /e2e-workflow --workflow deploy-test
```

---

**GO SET AUTH_SERVER_URL NOW!**

Tell me when Railway shows "Deployed" and I'll run the browser-test-auth skill to verify everything works! 🚀
