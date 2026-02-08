# Playwright Workflow Tester Skill

## Description
Comprehensive end-to-end testing skill for web applications using Playwright. Tests complete user workflows including authentication, CRUD operations, and UI interactions. Generates detailed test reports with screenshots and network analysis.

## When to Use
- Testing complete user workflows after feature implementation
- Validating authentication flows (signup, login, logout)
- Testing CRUD operations (create, read, update, delete)
- Debugging CORS and network issues
- Generating test reports for deployments
- Creating automated E2E test scripts

## Inputs
- `url`: Base URL of the application to test (required)
- `workflow`: Workflow to test - "auth", "tasks", "full", or "custom" (required)
- `credentials`: User credentials object `{email, password}` (optional, generates random if not provided)
- `report_path`: Path to save test report (optional, defaults to `TEST_REPORT.md`)
- `screenshots`: Whether to capture screenshots (optional, default: true)
- `network_debug`: Whether to capture network requests (optional, default: true)

## Process

### 1. Initialize Playwright Browser
```bash
# Browser is managed by MCP Playwright server
# Navigate to starting URL
```

### 2. Execute Workflow Tests

**Auth Workflow** (`workflow: "auth"`):
1. Test signup flow
   - Navigate to /signup
   - Fill registration form
   - Submit and verify redirect to dashboard
   - Capture success state

2. Test login flow
   - Navigate to /login
   - Fill credentials
   - Submit and verify dashboard access
   - Verify token storage

3. Test logout flow
   - Click logout button
   - Verify redirect to login
   - Verify session cleared

**Tasks Workflow** (`workflow: "tasks"`):
1. Login (prerequisite)
2. Create task
   - Click "Add Task"
   - Fill title and description
   - Submit and verify task appears
   - Capture created task state

3. Toggle task completion
   - Click checkbox/complete button
   - Verify UI updates
   - Capture completed state

4. Delete task
   - Click delete button
   - Confirm deletion
   - Verify task removed

**Full Workflow** (`workflow: "full"`):
- Combines auth + tasks workflows
- Tests complete application lifecycle
- Generates comprehensive report

**Custom Workflow** (`workflow: "custom"`):
- User provides custom Playwright script
- Executes arbitrary test scenarios

### 3. Network Monitoring (if enabled)

Captures for each request:
- URL and method
- Request headers (auth, content-type, origin)
- Response status and headers
- Response body (truncated if > 500 chars)
- CORS headers for debugging

### 4. Error Detection and Debugging

Monitors for:
- Console errors (ERR_FAILED, 401, 404, 500)
- Network failures (CORS, timeout)
- UI validation errors
- Unexpected redirects

### 5. Generate Test Report

Creates markdown report with:
- Test summary table (PASS/FAIL/BLOCKED/PENDING)
- Detailed results for each test case
- Screenshots for key states
- Network request logs
- Error analysis
- Root cause identification
- Recommendations for fixes

## Example Usage

### Test Authentication Flow
```
Use the Playwright Workflow Tester skill to test the authentication flow at https://my-app.vercel.app
```

**Skill invocation**:
```javascript
{
  "url": "https://my-app.vercel.app",
  "workflow": "auth",
  "credentials": {
    "email": "test@example.com",
    "password": "TestPass123!"
  },
  "report_path": "AUTH_TEST_REPORT.md"
}
```

### Test Complete Workflow
```
Test the entire task management workflow on the production app
```

**Skill invocation**:
```javascript
{
  "url": "https://frontend-peach-xi-69.vercel.app",
  "workflow": "full",
  "screenshots": true,
  "network_debug": true,
  "report_path": "FULL_WORKFLOW_TEST.md"
}
```

### Debug CORS Issues
```
Debug why task creation is failing with CORS errors
```

**Skill invocation**:
```javascript
{
  "url": "https://frontend-peach-xi-69.vercel.app",
  "workflow": "tasks",
  "network_debug": true,
  "report_path": "CORS_DEBUG_REPORT.md"
}
```

## Output

### Test Report Structure
```markdown
# Test Report - <Workflow Name>

**Date**: YYYY-MM-DD
**URL**: <tested-url>
**Workflow**: <workflow-type>

## Test Summary

| Test Case | Status | Notes |
|-----------|--------|-------|
| Test 1    | ✅ PASS | ... |
| Test 2    | ❌ FAIL | ... |
| Test 3    | ⏸️ PENDING | ... |

## Detailed Results

### Test 1: <Name>
**Expected**: ...
**Actual**: ...
**Status**: PASS/FAIL
**Evidence**: Screenshot attached
**Network**: <request-details>

## Issues Identified

### Issue 1: <Title>
**Severity**: CRITICAL/HIGH/MEDIUM/LOW
**Location**: <file/component>
**Root Cause**: <explanation>
**Fix**: <recommendations>

## Screenshots
[Embedded screenshots for key states]

## Network Logs
[Request/Response details for debugging]

## Recommendations
1. Immediate actions
2. Long-term improvements
```

## Implementation Details

### Playwright MCP Tools Used
1. `browser_navigate` - Navigate to URLs
2. `browser_snapshot` - Capture page state
3. `browser_fill_form` - Fill form fields
4. `browser_click` - Click buttons/links
5. `browser_take_screenshot` - Capture visuals
6. `browser_console_messages` - Get console logs
7. `browser_network_requests` - Get network activity
8. `browser_run_code` - Execute custom JavaScript
9. `browser_wait_for` - Wait for conditions

### Test Patterns

**Pattern 1: Form Submission Test**
```javascript
// Navigate to form
await browser_navigate({ url: '/signup' });

// Fill fields
await browser_fill_form({
  fields: [
    { name: 'Email', type: 'textbox', ref: 'e1', value: 'test@example.com' },
    { name: 'Password', type: 'textbox', ref: 'e2', value: 'pass123' }
  ]
});

// Submit and verify
await browser_click({ element: 'Submit button', ref: 'e3' });
await browser_snapshot(); // Verify result
```

**Pattern 2: Network Debug**
```javascript
const results = await browser_run_code({
  code: `async (page) => {
    const requests = [];
    page.on('request', req => requests.push({...req}));
    page.on('response', res => requests.push({...res}));

    // Perform action
    await page.click('button');

    return requests;
  }`
});
```

**Pattern 3: Authentication Flow**
```javascript
// Login
await browser_navigate({ url: '/login' });
await browser_fill_form({ fields: [...credentials] });
await browser_click({ element: 'Sign In', ref: 'e1' });

// Verify token stored
const token = await browser_run_code({
  code: `async (page) => localStorage.getItem('auth_token')`
});

// Test protected route
await browser_navigate({ url: '/dashboard' });
const snapshot = await browser_snapshot();
// Verify dashboard loaded
```

## Error Handling

### Common Issues and Solutions

**Issue**: CORS preflight failing
**Detection**: `ERR_FAILED` in console, empty response array
**Debug**: Capture OPTIONS request, check CORS headers
**Report**: Include request/response headers, suggest fixes

**Issue**: 401 Unauthorized
**Detection**: Response status 401
**Debug**: Check token storage, verify session validity
**Report**: Include token value, session database query

**Issue**: 500 Internal Server Error
**Detection**: Response status 500, error_id in response
**Debug**: Check server logs, verify request payload types
**Report**: Include error_id, request payload, suggest fixes

**Issue**: Type mismatch errors
**Detection**: 500 error, validation errors in response
**Debug**: Compare frontend types with backend schema
**Report**: List type mismatches, suggest corrections

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Playwright Tests
        run: |
          claude --skill playwright-workflow-tester \
            --url ${{ secrets.APP_URL }} \
            --workflow full \
            --report-path test-results/report.md
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: test-results/
```

## Best Practices

1. **Always capture network logs for failing tests**
   - Enables debugging of CORS, auth, and API issues
   - Reveals root causes invisible in UI

2. **Use stable selectors**
   - Prefer `ref` from snapshots over text content
   - Test IDs better than CSS selectors

3. **Wait for conditions, not fixed delays**
   - Use `browser_wait_for` with text conditions
   - Avoid `sleep` unless necessary

4. **Generate unique test data**
   - Avoid hardcoded emails (conflicts in shared DB)
   - Generate random credentials per test run

5. **Clean up test data**
   - Delete created resources after tests
   - Use separate test database if possible

6. **Include screenshots for debugging**
   - Capture success states for documentation
   - Capture error states for bug reports

## Maintenance

**Update selectors**: When UI changes, update `ref` values from new snapshots
**Update workflows**: Add new test scenarios as features are added
**Review reports**: Analyze patterns in failures to improve tests
**Optimize timing**: Adjust waits based on actual load times

## Version History

- **v1.0** (2025-12-27): Initial skill creation
  - Auth workflow testing
  - Tasks workflow testing
  - Network debugging
  - CORS issue detection
  - Comprehensive reporting

## Related Skills

- `api-tester`: For backend API testing
- `accessibility-checker`: For WCAG compliance
- `performance-analyzer`: For load time optimization
- `security-scanner`: For vulnerability detection

---

**Created by**: Claude Code
**Last Updated**: 2025-12-27
**Category**: Testing & QA
**Difficulty**: Intermediate
