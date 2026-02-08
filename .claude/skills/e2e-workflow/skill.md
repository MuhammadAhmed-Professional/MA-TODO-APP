# E2E Workflow Skill

## Description
Complete end-to-end workflow automation for deploying and testing full-stack applications. Orchestrates code deployment, environment configuration, health checks, browser testing, and rollback procedures.

## Capabilities
- Full deployment pipeline (frontend + backend + auth server)
- Automated environment configuration
- Multi-service health verification
- Comprehensive browser testing
- Automated rollback on failure
- Deployment reports and notifications
- Performance monitoring
- Security verification

## Inputs
- `--workflow` (required): Workflow to execute (deploy-all|test-all|deploy-test|rollback-all)
- `--environment` (optional): Target environment (production|staging|development, default: production)
- `--skip-tests` (optional): Skip browser tests (default: false)
- `--rollback-on-failure` (optional): Auto-rollback if tests fail (default: true)
- `--notify` (optional): Send notifications (email|slack|none, default: none)

## Process

### Workflow: deploy-all
```
Phase 1: Pre-Deployment Checks
├── Verify all services are accessible
├── Check current deployment status
├── Backup current environment variables
└── Run pre-deployment tests

Phase 2: Backend Deployment
├── Deploy backend to Railway
├── Wait for "Deployed" status
├── Run backend health check
└── Verify database connectivity

Phase 3: Auth Server Deployment
├── Deploy auth server to Railway
├── Wait for "Deployed" status
├── Run auth server health check
└── Verify database connectivity

Phase 4: Frontend Deployment
├── Deploy frontend to Vercel
├── Wait for deployment complete
├── Run frontend health check
└── Verify static assets loaded

Phase 5: Environment Configuration
├── Set AUTH_SERVER_URL in backend
├── Set CORS_ORIGINS in all services
├── Verify all environment variables
└── Trigger redeployment if needed

Phase 6: Post-Deployment Verification
├── Run health checks on all services
├── Test inter-service communication
├── Run browser authentication tests
└── Generate deployment report
```

### Workflow: test-all
```
Phase 1: Service Health Checks
├── Backend: GET /health
├── Auth Server: GET /health
├── Frontend: GET /
└── Database: Connection test

Phase 2: API Testing
├── Test /api/auth/sign-up/email
├── Test /api/auth/sign-in/email
├── Test /api/auth/sign-out
├── Test /api/auth/get-session
├── Test /api/tasks (CRUD operations)
└── Verify authentication middleware

Phase 3: Browser Testing
├── Navigate to login page
├── Fill credentials and login
├── Verify cookie settings
├── Test dashboard access
├── Test task creation/deletion
└── Test logout functionality

Phase 4: Integration Testing
├── Test full user journey
├── Test error handling
├── Test rate limiting
├── Test CORS configuration
└── Test session management

Phase 5: Performance Testing
├── Measure page load times
├── Measure API response times
├── Check for memory leaks
├── Verify resource usage
└── Test under load (optional)

Phase 6: Security Testing
├── Verify HTTPS enforcement
├── Check cookie security attributes
├── Test CSRF protection
├── Verify input sanitization
└── Check for XSS vulnerabilities
```

### Workflow: deploy-test
```
Execute: deploy-all
Then: test-all
If tests fail AND rollback-on-failure=true:
  Execute: rollback-all
  Notify: Deployment failed, rolled back
Else:
  Notify: Deployment successful
```

### Workflow: rollback-all
```
Phase 1: Identify Last Stable Deployment
├── Query Railway for recent deployments
├── Identify last known good deployment
└── Confirm rollback target

Phase 2: Rollback Services
├── Rollback backend to previous version
├── Rollback auth server to previous version
├── Wait for rollback completion
└── Restore environment variables

Phase 3: Verify Rollback
├── Run health checks
├── Test authentication flow
├── Verify services are operational
└── Generate rollback report

Phase 4: Notify Team
├── Send rollback notification
├── Include rollback reason
├── Attach verification report
└── Suggest next steps
```

## Configuration

### Production Environment
```yaml
frontend:
  url: https://frontend-six-coral-90.vercel.app
  platform: Vercel
  deploy_command: vercel --prod

backend:
  url: https://backend-production-9a40.up.railway.app
  platform: Railway
  project_id: 1a580b9d-e43b-4faf-a523-b3454b9d3bf1
  service_id: ac8b8441-def7-49e9-af64-47dd171ae1c2
  required_vars:
    - AUTH_SERVER_URL
    - DATABASE_URL
    - CORS_ORIGINS

auth_server:
  url: https://auth-server-production-cd0e.up.railway.app
  platform: Railway
  required_vars:
    - DATABASE_URL
    - BETTER_AUTH_SECRET
    - CORS_ORIGINS

database:
  provider: Neon PostgreSQL
  connection_pooling: enabled
```

### Staging Environment
```yaml
frontend:
  url: https://staging-frontend.vercel.app

backend:
  url: https://staging-backend.railway.app

auth_server:
  url: https://staging-auth.railway.app

database:
  provider: Neon PostgreSQL (staging branch)
```

## Output Format

### Deploy-All Success
```json
{
  "workflow": "deploy-all",
  "environment": "production",
  "status": "SUCCESS",
  "timestamp": "2025-12-27T10:30:00Z",
  "duration": "5m 32s",
  "deployments": {
    "backend": {
      "status": "DEPLOYED",
      "version": "7bcf9b7",
      "health_check": "PASS"
    },
    "auth_server": {
      "status": "DEPLOYED",
      "version": "8400e1d",
      "health_check": "PASS"
    },
    "frontend": {
      "status": "DEPLOYED",
      "version": "833784f",
      "health_check": "PASS"
    }
  },
  "tests": {
    "health_checks": "PASS",
    "browser_tests": "PASS",
    "integration_tests": "PASS"
  },
  "urls": {
    "frontend": "https://frontend-six-coral-90.vercel.app",
    "backend": "https://backend-production-9a40.up.railway.app",
    "auth_server": "https://auth-server-production-cd0e.up.railway.app"
  }
}
```

### Deploy-Test Failure with Rollback
```json
{
  "workflow": "deploy-test",
  "environment": "production",
  "status": "FAILED_ROLLED_BACK",
  "timestamp": "2025-12-27T10:30:00Z",
  "failure_reason": "Browser authentication test failed: 504 Gateway Timeout",
  "rollback_performed": true,
  "rollback_status": "SUCCESS",
  "previous_version_restored": true,
  "services_operational": true,
  "error_details": {
    "service": "backend",
    "test": "browser_auth_test",
    "error": "Backend cannot reach auth server",
    "http_status": 504
  },
  "recommendation": "Check AUTH_SERVER_URL environment variable in backend service"
}
```

## Example Usage

### Deploy Everything to Production
```bash
claude-code /e2e-workflow --workflow deploy-all --environment production
```

### Deploy and Test with Auto-Rollback
```bash
claude-code /e2e-workflow --workflow deploy-test --environment production --rollback-on-failure true
```

### Run All Tests (No Deployment)
```bash
claude-code /e2e-workflow --workflow test-all --environment production
```

### Emergency Rollback
```bash
claude-code /e2e-workflow --workflow rollback-all --environment production
```

### Deploy to Staging
```bash
claude-code /e2e-workflow --workflow deploy-test --environment staging
```

## Quality Gates

### Pre-Deployment Gates
- ✅ All unit tests passing
- ✅ No critical security vulnerabilities
- ✅ Database migrations ready
- ✅ Environment variables documented
- ✅ No uncommitted changes

### Post-Deployment Gates
- ✅ All services return 200 OK on health checks
- ✅ Frontend loads in < 3 seconds
- ✅ API response times < 500ms
- ✅ Authentication flow works end-to-end
- ✅ No errors in logs

### Test Gates
- ✅ Browser tests pass (100%)
- ✅ API tests pass (100%)
- ✅ Integration tests pass (100%)
- ✅ Security tests pass (100%)
- ✅ Performance tests meet SLA

## Failure Handling

### Deployment Failure Scenarios

#### Backend Deployment Fails
```
Action: Rollback backend to previous version
Notify: Backend deployment failed
Keep: Frontend and auth server on current versions
Test: Verify system still operational
```

#### Auth Server Deployment Fails
```
Action: Rollback auth server to previous version
Notify: Auth server deployment failed
Impact: Authentication will continue with previous version
Test: Verify login still works
```

#### Tests Fail After Deployment
```
Action: Rollback all services to previous versions
Notify: Post-deployment tests failed
Reason: Include test failure details
Recovery: Review logs, fix issue, redeploy
```

#### Environment Variable Misconfiguration
```
Action: Restore previous environment variables
Trigger: Redeployment with correct configuration
Verify: Run tests to confirm fix
```

## Monitoring & Alerts

### Real-Time Monitoring
- Service uptime (99.9% SLA)
- API response times (p95 < 500ms)
- Error rates (< 0.1%)
- CPU/Memory usage (< 80%)
- Database connections (< max pool)

### Alert Conditions
- Service health check fails (2+ consecutive)
- API response time > 2 seconds
- Error rate > 1% (5 min window)
- Memory usage > 90%
- Failed deployment
- Test failure after deployment

### Notification Channels
- Email: Critical alerts only
- Slack: All deployment updates
- Dashboard: Real-time metrics
- Logs: Detailed troubleshooting info

## Integration with CI/CD

### GitHub Actions Integration
```yaml
name: E2E Workflow

on:
  push:
    branches: [main]

jobs:
  deploy-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run E2E Workflow
        run: |
          claude-code /e2e-workflow \
            --workflow deploy-test \
            --environment production \
            --rollback-on-failure true \
            --notify slack

      - name: Upload Deployment Report
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: deployment-report
          path: deployment-report.json
```

### Manual Deployment Trigger
```bash
# From local machine
claude-code /e2e-workflow \
  --workflow deploy-all \
  --environment production \
  --notify email
```

## Dependencies
- Railway CLI (authenticated)
- Vercel CLI (authenticated)
- Playwright MCP (browser testing)
- Git (for version control)
- curl/httpx (for API testing)

## Success Criteria
- ✅ All services deployed successfully
- ✅ All health checks passing
- ✅ All tests passing (browser, API, integration)
- ✅ Zero errors in logs (post-deployment)
- ✅ Performance SLAs met
- ✅ Security checks passed

## Maintenance Notes
- Review deployment reports weekly
- Update test cases for new features
- Monitor failure patterns and improve gates
- Keep rollback history (last 30 days)
- Document all configuration changes
- Schedule regular disaster recovery drills

## Best Practices

### Before Deployment
1. Run tests locally
2. Review pending database migrations
3. Check for breaking changes
4. Notify team of deployment window
5. Have rollback plan ready

### During Deployment
1. Monitor logs in real-time
2. Watch for errors/warnings
3. Track deployment progress
4. Be ready to abort if issues arise

### After Deployment
1. Run comprehensive tests
2. Monitor metrics for 30 minutes
3. Check user feedback/reports
4. Document any issues encountered
5. Update deployment notes

### Rollback Decision Tree
```
Is service responding? NO → Rollback immediately
Are tests passing? NO → Investigate, rollback if critical
Are users affected? YES → Rollback, fix, redeploy
Is error rate elevated? YES → Monitor, rollback if worsening
All systems nominal? YES → Deployment successful
```
