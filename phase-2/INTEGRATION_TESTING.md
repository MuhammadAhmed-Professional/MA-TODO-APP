# Integration Testing Guide

**Last Updated**: 2025-12-20
**Purpose**: Verify all services work together correctly

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Test Suite](#quick-test-suite)
3. [Manual Testing](#manual-testing)
4. [Automated Testing](#automated-testing)
5. [Common Issues](#common-issues)
6. [Test Scenarios](#test-scenarios)

---

## Prerequisites

Before testing, ensure:

- [ ] All services are running (auth server, backend, frontend)
- [ ] Environment variables are configured correctly
- [ ] Database is accessible (Neon PostgreSQL)
- [ ] CORS is configured properly

**Start all services**:
```bash
# Windows
start-all-services.bat

# Linux/Mac
chmod +x start-all-services.sh
./start-all-services.sh
```

**Verify services are running**:
```bash
# Auth Server
curl http://localhost:3001/health

# Backend API
curl http://localhost:8000/health

# Frontend (open in browser)
# http://localhost:3000
```

---

## Quick Test Suite

### Test 1: Health Checks

Verify all services are responding.

**Auth Server**:
```bash
curl http://localhost:3001/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-20T...",
  "service": "better-auth-server",
  "version": "1.0.0"
}
```

**Backend API**:
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy"
}
```

**Frontend**:
- Open http://localhost:3000 in browser
- Should see landing page (no errors)

**Status**: ✓ Pass / ✗ Fail

---

### Test 2: User Signup

Create a new user account.

**Command**:
```bash
curl -X POST http://localhost:3001/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }' \
  -c cookies.txt \
  -v
```

**Expected Response** (201 Created):
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "name": "Test User"
  },
  "session": {
    "token": "...",
    "expiresAt": "..."
  }
}
```

**Expected Headers**:
```
Set-Cookie: better_auth.session_token=...; HttpOnly; Secure; SameSite=Lax
```

**Verify**:
- [ ] Response status is 201
- [ ] Response contains user data
- [ ] Cookie is set (check cookies.txt)
- [ ] User created in database

**Status**: ✓ Pass / ✗ Fail

---

### Test 3: User Login

Login with existing credentials.

**Command**:
```bash
curl -X POST http://localhost:3001/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }' \
  -c cookies.txt \
  -v
```

**Expected Response** (200 OK):
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "name": "Test User"
  },
  "session": {
    "token": "...",
    "expiresAt": "..."
  }
}
```

**Expected Headers**:
```
Set-Cookie: better_auth.session_token=...; HttpOnly; Secure; SameSite=Lax
```

**Verify**:
- [ ] Response status is 200
- [ ] Response contains user data
- [ ] Cookie is set

**Status**: ✓ Pass / ✗ Fail

---

### Test 4: Get Current Session

Verify session cookie works.

**Command**:
```bash
curl http://localhost:3001/auth/get-session \
  -b cookies.txt \
  -v
```

**Expected Response** (200 OK):
```json
{
  "user": {
    "id": "...",
    "email": "test@example.com",
    "name": "Test User"
  },
  "session": {
    "expiresAt": "..."
  }
}
```

**Verify**:
- [ ] Response status is 200
- [ ] User data matches logged-in user
- [ ] No authentication error

**Status**: ✓ Pass / ✗ Fail

---

### Test 5: Create Task (Authenticated)

Create a task using backend API with auth cookie.

**Command**:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Test Task",
    "description": "This is a test task"
  }' \
  -v
```

**Expected Response** (201 Created):
```json
{
  "id": "...",
  "title": "Test Task",
  "description": "This is a test task",
  "is_complete": false,
  "user_id": "...",
  "created_at": "2025-12-20T...",
  "updated_at": "2025-12-20T..."
}
```

**Verify**:
- [ ] Response status is 201
- [ ] Task created successfully
- [ ] user_id matches authenticated user
- [ ] Task saved in database

**Status**: ✓ Pass / ✗ Fail

---

### Test 6: List Tasks (Authenticated)

Retrieve all tasks for authenticated user.

**Command**:
```bash
curl http://localhost:8000/api/tasks \
  -b cookies.txt \
  -v
```

**Expected Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "...",
      "title": "Test Task",
      "description": "This is a test task",
      "is_complete": false,
      "user_id": "...",
      "created_at": "2025-12-20T...",
      "updated_at": "2025-12-20T..."
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Verify**:
- [ ] Response status is 200
- [ ] Tasks array contains created task
- [ ] Total count is correct

**Status**: ✓ Pass / ✗ Fail

---

### Test 7: Update Task (Authenticated)

Mark task as complete.

**Command** (replace `TASK_ID` with actual ID):
```bash
curl -X PATCH http://localhost:8000/api/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "is_complete": true
  }' \
  -v
```

**Expected Response** (200 OK):
```json
{
  "id": "TASK_ID",
  "title": "Test Task",
  "description": "This is a test task",
  "is_complete": true,
  "user_id": "...",
  "created_at": "2025-12-20T...",
  "updated_at": "2025-12-20T..."
}
```

**Verify**:
- [ ] Response status is 200
- [ ] is_complete is true
- [ ] updated_at timestamp changed

**Status**: ✓ Pass / ✗ Fail

---

### Test 8: Delete Task (Authenticated)

Delete a task.

**Command** (replace `TASK_ID`):
```bash
curl -X DELETE http://localhost:8000/api/tasks/TASK_ID \
  -b cookies.txt \
  -v
```

**Expected Response** (204 No Content):
```
(empty response body)
```

**Verify**:
- [ ] Response status is 204
- [ ] Task deleted from database
- [ ] GET /api/tasks no longer includes deleted task

**Status**: ✓ Pass / ✗ Fail

---

### Test 9: Unauthenticated Request (Should Fail)

Attempt to access protected endpoint without cookie.

**Command**:
```bash
curl http://localhost:8000/api/tasks \
  -v
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Not authenticated"
}
```

**Verify**:
- [ ] Response status is 401
- [ ] Error message indicates authentication required

**Status**: ✓ Pass / ✗ Fail

---

### Test 10: Logout

Clear session and verify cookies are deleted.

**Command**:
```bash
curl -X POST http://localhost:3001/auth/sign-out \
  -b cookies.txt \
  -c cookies.txt \
  -v
```

**Expected Response** (200 OK):
```json
{
  "success": true
}
```

**Expected Headers**:
```
Set-Cookie: better_auth.session_token=; Max-Age=0
```

**Verify**:
- [ ] Response status is 200
- [ ] Cookie is cleared (Max-Age=0)
- [ ] Subsequent requests fail with 401

**Status**: ✓ Pass / ✗ Fail

---

## Manual Testing

### Browser Testing Flow

1. **Open Frontend**:
   - Navigate to http://localhost:3000
   - Should see landing page

2. **Sign Up**:
   - Click "Sign Up" button
   - Fill form:
     - Name: "Test User"
     - Email: "test@example.com"
     - Password: "password123"
   - Submit form
   - Should redirect to dashboard
   - Check browser cookies (DevTools → Application → Cookies)
   - Should see `better_auth.session_token`

3. **Create Task**:
   - Click "Add Task" button
   - Fill form:
     - Title: "Buy groceries"
     - Description: "Milk, eggs, bread"
   - Submit
   - Task should appear in list

4. **Complete Task**:
   - Click checkbox next to task
   - Task should be marked as complete (strikethrough)

5. **Edit Task**:
   - Click "Edit" button
   - Update title or description
   - Save changes
   - Verify changes appear

6. **Delete Task**:
   - Click "Delete" button
   - Confirm deletion
   - Task should disappear from list

7. **Logout**:
   - Click "Logout" button
   - Should redirect to login page
   - Check cookies - `better_auth.session_token` should be cleared

8. **Login Again**:
   - Enter email and password
   - Should redirect to dashboard
   - Tasks should persist (from database)

9. **Test Session Expiration**:
   - Wait 15 minutes (or change `ACCESS_TOKEN_EXPIRE_MINUTES` to 1)
   - Try to perform any action
   - Should get redirected to login (session expired)

---

## Automated Testing

### Frontend E2E Tests (Playwright)

**Run E2E tests**:
```bash
cd frontend
npm run test:e2e
```

**Sample test** (`frontend/tests/e2e/auth-flow.spec.ts`):
```typescript
import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test("complete signup and login flow", async ({ page }) => {
    // Signup
    await page.goto("http://localhost:3000/signup");
    await page.fill('[name="name"]', "E2E Test User");
    await page.fill('[name="email"]', `e2e-${Date.now()}@example.com`);
    await page.fill('[name="password"]', "password123");
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator("text=Welcome")).toBeVisible();

    // Logout
    await page.click("text=Logout");
    await expect(page).toHaveURL(/.*login/);

    // Login again
    await page.fill('[name="email"]', "e2e@example.com");
    await page.fill('[name="password"]', "password123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test("complete task CRUD flow", async ({ page, context }) => {
    // Login first
    await page.goto("http://localhost:3000/login");
    await page.fill('[name="email"]', "test@example.com");
    await page.fill('[name="password"]', "password123");
    await page.click('button[type="submit"]');

    // Create task
    await page.click("text=Add Task");
    await page.fill('[name="title"]', "E2E Test Task");
    await page.fill('[name="description"]', "Created by E2E test");
    await page.click('button:has-text("Save")');
    await expect(page.locator("text=E2E Test Task")).toBeVisible();

    // Complete task
    await page.click('[aria-label="Mark complete"]');
    await expect(page.locator("text=E2E Test Task")).toHaveClass(/line-through/);

    // Delete task
    await page.click('[aria-label="Delete task"]');
    await page.click('button:has-text("Confirm")');
    await expect(page.locator("text=E2E Test Task")).not.toBeVisible();
  });
});
```

**Run tests**:
```bash
npm run test:e2e
```

---

### Backend Integration Tests (pytest)

**Run backend tests**:
```bash
cd backend
uv run pytest tests/integration/
```

**Sample test** (`backend/tests/integration/test_auth_flow.py`):
```python
import pytest
from fastapi.testclient import TestClient

def test_signup_login_flow(client: TestClient):
    """Test complete signup and login flow"""
    # Signup
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "name": "Integration Test User",
            "email": "integration@example.com",
            "password": "password123"
        }
    )
    assert signup_response.status_code == 201
    assert "auth_token" in signup_response.cookies

    # Get session
    session_response = client.get("/api/auth/me")
    assert session_response.status_code == 200
    user_data = session_response.json()
    assert user_data["email"] == "integration@example.com"

    # Logout
    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 204

    # Try to access protected endpoint (should fail)
    tasks_response = client.get("/api/tasks")
    assert tasks_response.status_code == 401

def test_task_crud_flow(client: TestClient, auth_headers: dict):
    """Test complete task CRUD flow"""
    # Create task
    create_response = client.post(
        "/api/tasks",
        json={"title": "Integration Test Task", "description": "Test"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    task = create_response.json()
    task_id = task["id"]

    # List tasks
    list_response = client.get("/api/tasks", headers=auth_headers)
    assert list_response.status_code == 200
    assert len(list_response.json()["tasks"]) > 0

    # Update task
    update_response = client.patch(
        f"/api/tasks/{task_id}",
        json={"is_complete": True},
        headers=auth_headers
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_complete"] is True

    # Delete task
    delete_response = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 204
```

---

## Common Issues

### Issue 1: "CORS error" in browser

**Symptom**: Browser console shows CORS policy error

**Fix**:
1. Check `CORS_ORIGINS` in all `.env` files
2. Ensure `credentials: "include"` in frontend fetch
3. Restart all services after changing `.env`

**Verify**:
```bash
# Check auth server CORS
curl -H "Origin: http://localhost:3000" -v http://localhost:3001/health | grep -i access-control

# Check backend CORS
curl -H "Origin: http://localhost:3000" -v http://localhost:8000/health | grep -i access-control
```

---

### Issue 2: "401 Unauthorized" on backend requests

**Symptom**: Backend returns 401 even after login

**Causes**:
1. JWT secret mismatch between auth server and backend
2. Cookie not being sent with request
3. Token expired (15 minutes)

**Fix**:
1. Verify `BETTER_AUTH_SECRET` (auth server) matches `JWT_SECRET` (backend)
2. Check browser DevTools → Network → Request Headers → Cookie
3. Re-login if token expired

**Debug**:
```bash
# Check if cookie is set
curl http://localhost:3001/auth/get-session -b cookies.txt

# Check if backend accepts token
curl http://localhost:8000/api/tasks -b cookies.txt
```

---

### Issue 3: Database connection errors

**Symptom**: Services fail to start with database error

**Fix**:
1. Verify `DATABASE_URL` in all `.env` files is identical
2. Check Neon PostgreSQL is accessible
3. Test connection with psql

**Test**:
```bash
# Test PostgreSQL connection
psql "postgresql://neondb_owner:***@ep-***.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

---

## Test Scenarios

### Scenario 1: New User Journey

**Steps**:
1. User visits frontend (http://localhost:3000)
2. Clicks "Sign Up"
3. Fills form and submits
4. Redirected to dashboard
5. Creates first task
6. Marks task as complete
7. Logs out
8. Logs back in
9. Sees previous task (persisted)

**Expected Result**: All steps complete without errors

---

### Scenario 2: Multiple Users

**Steps**:
1. Create User A account
2. User A creates tasks
3. User A logs out
4. Create User B account
5. User B creates tasks
6. User B should NOT see User A's tasks
7. User A logs back in
8. User A should see only their tasks

**Expected Result**: Task isolation between users

---

### Scenario 3: Session Expiration

**Steps**:
1. User logs in
2. User creates task
3. Wait 15 minutes (or change token expiry to 1 minute)
4. User tries to create another task
5. Should get redirected to login
6. User logs in again
7. Previous tasks still exist

**Expected Result**: Session expires, redirects to login, data persists

---

### Scenario 4: Token Invalidation

**Steps**:
1. User logs in
2. Manually delete `better_auth.session_token` cookie (DevTools)
3. User tries to access dashboard
4. Should get redirected to login

**Expected Result**: Invalid token redirects to login

---

## Test Checklist

Before declaring integration complete:

- [ ] All health checks pass
- [ ] User can sign up
- [ ] User can log in
- [ ] User can log out
- [ ] Session persists across page refreshes
- [ ] User can create tasks
- [ ] User can list tasks
- [ ] User can update tasks
- [ ] User can delete tasks
- [ ] Unauthenticated requests return 401
- [ ] CORS works correctly
- [ ] Cookies are set properly
- [ ] Database saves data correctly
- [ ] Frontend displays data correctly
- [ ] Token expiration works
- [ ] Multiple users are isolated
- [ ] All E2E tests pass
- [ ] All integration tests pass

---

## Resources

- [Playwright Testing Docs](https://playwright.dev)
- [pytest Documentation](https://docs.pytest.org)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Better Auth Testing](https://better-auth.com/docs/concepts/testing)
