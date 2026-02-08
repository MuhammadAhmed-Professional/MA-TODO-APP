# Browser Test Auth Skill

## Description
Automated browser testing for authentication flows using Playwright MCP. Tests login, cookie handling, network requests, and dashboard access across different deployment environments.

## Capabilities
- Navigate to login pages
- Fill authentication forms
- Capture network traffic
- Verify cookie settings (SameSite, Secure, HttpOnly)
- Take screenshots for debugging
- Check console errors
- Test redirect flows
- Validate dashboard access

## Inputs
- `--url` (required): Frontend URL to test (e.g., https://frontend-six-coral-90.vercel.app)
- `--email` (optional): Test user email (default: test@example.com)
- `--password` (optional): Test user password (default: password123)
- `--screenshot-dir` (optional): Directory for screenshots (default: .playwright-screenshots)

## Process

### 1. Navigate to Login Page
```
Navigate to: {url}/login
Wait for page load
Capture initial screenshot
Check console for errors
```

### 2. Fill Login Form
```
Find email input field
Fill with: {email}
Find password input field
Fill with: {password}
Capture form-filled screenshot
```

### 3. Submit Login
```
Click "Sign In" button
Wait for network response
Capture network requests
Filter for /api/auth/sign-in/email
```

### 4. Verify Response
```
Check HTTP status code:
  - 200 OK → Login successful
  - 401 Unauthorized → Invalid credentials
  - 504 Gateway Timeout → Backend can't reach auth server
  - 429 Too Many Requests → Rate limited
```

### 5. Inspect Cookies
```
Get all cookies from browser context
Filter for 'auth_token' cookie
Verify attributes:
  - Domain: Should match backend domain
  - SameSite: Should be 'None' for cross-domain
  - Secure: Should be true
  - HttpOnly: Should be true
```

### 6. Test Dashboard Access
```
If login successful:
  - Wait for redirect to /dashboard
  - Capture dashboard screenshot
  - Check for task list
  - Verify user profile in header
If login failed:
  - Capture error message
  - Take screenshot
  - Get console errors
```

### 7. Generate Test Report
```
Create JSON report with:
  - Test timestamp
  - All HTTP requests/responses
  - Cookies captured
  - Screenshots taken
  - Console errors
  - Final verdict (PASS/FAIL)
```

## Output Format

### Success
```json
{
  "status": "PASS",
  "timestamp": "2025-12-27T10:30:00Z",
  "login_status": 200,
  "cookie_found": true,
  "cookie_attributes": {
    "domain": "backend-production-9a40.up.railway.app",
    "sameSite": "None",
    "secure": true,
    "httpOnly": true
  },
  "dashboard_loaded": true,
  "screenshots": [
    ".playwright-screenshots/login-page.png",
    ".playwright-screenshots/dashboard.png"
  ]
}
```

### Failure
```json
{
  "status": "FAIL",
  "timestamp": "2025-12-27T10:30:00Z",
  "login_status": 504,
  "error": "Gateway Timeout",
  "cookie_found": false,
  "console_errors": [
    "Failed to load resource: 504"
  ],
  "screenshots": [
    ".playwright-screenshots/login-error.png"
  ]
}
```

## Example Usage

### Test Production
```bash
claude-code /browser-test-auth --url https://frontend-six-coral-90.vercel.app
```

### Test with Custom Credentials
```bash
claude-code /browser-test-auth --url https://frontend-six-coral-90.vercel.app --email user@example.com --password mypass123
```

### Test Local Development
```bash
claude-code /browser-test-auth --url http://localhost:3000 --email dev@test.com --password dev123
```

## Common Issues & Solutions

### Issue: 504 Gateway Timeout
**Cause**: Backend can't reach auth server
**Solution**: Check AUTH_SERVER_URL environment variable in Railway backend

### Issue: 401 Unauthorized
**Cause**: Invalid credentials
**Solution**: Verify user exists in database, check password

### Issue: Cookie not set
**Cause**: SameSite settings or CORS issues
**Solution**: Verify backend sets SameSite=None with Secure=True

### Issue: Redirect loop
**Cause**: Cookie not being sent with requests
**Solution**: Check cookie domain matches backend domain

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Test Authentication
  run: |
    claude-code /browser-test-auth --url ${{ env.FRONTEND_URL }}
    if [ $? -ne 0 ]; then
      echo "Authentication test failed!"
      exit 1
    fi
```

### Pre-Deployment Check
```bash
# Before deploying to production
claude-code /browser-test-auth --url https://staging-frontend.vercel.app
if [ $? -eq 0 ]; then
  echo "✅ Auth test passed, deploying to production"
  vercel --prod
else
  echo "❌ Auth test failed, blocking deployment"
  exit 1
fi
```

## Dependencies
- Playwright MCP server (must be connected)
- Target frontend must be accessible
- Test credentials must exist in database

## Success Criteria
- ✅ Login request returns 200 OK
- ✅ auth_token cookie is set
- ✅ Cookie has correct attributes (SameSite=None, Secure=True)
- ✅ Dashboard loads after login
- ✅ No console errors (except expected 404s)

## Maintenance Notes
- Update test credentials when rotating passwords
- Add new test cases for new auth features (OAuth, 2FA, etc.)
- Keep screenshots for debugging failed tests
- Archive test reports for compliance/auditing
