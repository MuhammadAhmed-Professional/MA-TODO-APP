# E2E Test Suite Documentation

## Overview

This directory contains comprehensive End-to-End (E2E) tests for the Phase II Todo Application, covering all user stories and critical user journeys.

## Test Files

### 1. `regression.spec.ts` - Comprehensive Regression Suite (T104)

**Purpose**: Consolidated test suite covering all user stories for smoke testing and regression prevention.

**Coverage**:
- **US1 - Authentication** (8 tests)
  - Signup with valid credentials
  - Login with valid credentials
  - Logout functionality
  - Invalid login error handling
  - Protected route access control
  - Authenticated user redirects
  - Duplicate email validation

- **US2 - Task Management** (10 tests)
  - Create task with title and description
  - View task list sorted by creation date
  - Edit task title and description
  - Mark task as complete (toggle)
  - Toggle task from complete to incomplete
  - Delete task with confirmation
  - Validation error for empty title
  - Task persistence across page refresh
  - Completed task state persistence

- **US3 - Authorization** (2 tests)
  - Cross-user task isolation (user can only see their own tasks)
  - API 403 errors when accessing another user's task

- **US4 - Responsive UI** (6 tests)
  - Mobile layout (375px): single-column, hamburger menu, touch targets
  - Tablet layout (768px): two-column grid
  - Desktop layout (1920px): three-column grid, sidebar visible
  - Responsive transitions between viewports

- **US5 - API Documentation** (3 tests)
  - /docs endpoint accessible
  - Swagger UI renders correctly
  - Authentication and task endpoints documented

- **Comprehensive Smoke Test** (1 test)
  - Complete user journey from signup to delete

**Total Tests**: 30 test cases

**Test Isolation**: Each test uses unique email addresses generated with timestamps to prevent conflicts.

**Helper Functions**:
- `generateTestEmail()` - Generate unique test emails
- `signupUser()` - Create new user account
- `loginUser()` - Login existing user
- `logoutUser()` - Logout current user
- `createTask()` - Create task with title and description
- `editTask()` - Update task details
- `toggleTaskCompletion()` - Mark task as complete/incomplete
- `deleteTask()` - Delete task with confirmation

### 2. `auth.spec.ts` - Authentication Flow Tests (T040)

**Purpose**: Detailed authentication flow testing.

**Coverage**:
- Complete authentication journey (signup → auto-login → logout → login)
- Session persistence across page reloads
- Unauthenticated access protection
- Authenticated user redirects
- Error handling (duplicate email, invalid credentials)

**Total Tests**: 10 test cases

### 3. `tasks.spec.ts` - Task Management Tests (T065)

**Purpose**: Comprehensive CRUD operations for tasks.

**Coverage**:
- Complete CRUD journey (create → view → edit → toggle → delete)
- Task sorting by creation date
- Form validation (empty title, title length, description length)
- Cancel operations (create and edit)
- Task persistence and state management
- Deletion confirmation

**Total Tests**: 14 test cases

### 4. `authorization.spec.ts` - Authorization Tests

**Purpose**: Cross-user access control validation.

**Coverage**:
- User A creates task → User B cannot see it
- Direct API access returns 403 for unauthorized users
- Session expiration handling

**Total Tests**: 3 test cases

### 5. `responsive.spec.ts` - Responsive UI Tests

**Purpose**: Responsive design and accessibility validation.

**Coverage**:
- Mobile viewport (375px): single-column, hamburger menu, touch targets
- Tablet viewport (768px): two-column grid, full navigation
- Desktop viewport (1920px): three-column grid, sidebar
- Responsive breakpoint transitions
- Accessibility: focus indicators, keyboard navigation, ARIA labels, semantic HTML
- Touch target compliance (44x44px minimum)

**Total Tests**: 19 test cases

## Running Tests

### Run All E2E Tests

```bash
# From frontend directory
pnpm test:e2e

# Or with npm
npm run test:e2e
```

### Run Specific Test File

```bash
# Regression suite only
npx playwright test regression.spec.ts

# Authentication tests only
npx playwright test auth.spec.ts

# Task management tests only
npx playwright test tasks.spec.ts

# Authorization tests only
npx playwright test authorization.spec.ts

# Responsive UI tests only
npx playwright test responsive.spec.ts
```

### Run Specific Test by Name

```bash
# Run specific test by grep
npx playwright test --grep "should signup with valid credentials"

# Run all US1 tests
npx playwright test --grep "US1:"

# Run all mobile tests
npx playwright test --grep "Mobile"
```

### Run Tests in Headed Mode (See Browser)

```bash
npx playwright test --headed
```

### Run Tests in Debug Mode

```bash
npx playwright test --debug
```

### Run Tests on Specific Browser

```bash
# Chrome only
npx playwright test --project=chromium

# Firefox only
npx playwright test --project=firefox

# Mobile Chrome
npx playwright test --project="Mobile Chrome"
```

### Generate Test Report

```bash
# Run tests and open HTML report
npx playwright test
npx playwright show-report
```

## Test Configuration

Configuration is defined in `/frontend/playwright.config.ts`:

- **Base URL**: `http://localhost:3000` (frontend)
- **API URL**: `http://localhost:8000` (backend)
- **Browsers**: Chromium, Firefox, WebKit (Safari)
- **Mobile Devices**: Pixel 5, iPhone 12
- **Parallel Execution**: Enabled
- **Retries**: 2 retries on CI, 0 locally
- **Trace**: Captured on first retry
- **Screenshots**: Captured on failure
- **Videos**: Retained on failure

## Prerequisites

Before running E2E tests:

1. **Backend API must be running**:
   ```bash
   cd backend
   uv run uvicorn src.main:app --reload
   ```

2. **Frontend dev server must be running** (or use Playwright's webServer config):
   ```bash
   cd frontend
   pnpm dev
   ```

3. **Database must be accessible**:
   - Neon Postgres connection configured in backend
   - Migrations applied

## Test Best Practices

### Test Isolation

- **Each test creates its own user** with unique email address
- **No shared state** between tests
- **Tests can run in parallel** without conflicts

### Selectors

- **Prefer role-based selectors**: `getByRole('button', { name: /submit/i })`
- **Use label associations**: `getByLabel(/email/i)`
- **Use text content**: `getByText('Welcome')`
- **Avoid CSS selectors**: Only when necessary for specific elements

### Assertions

- **Use specific assertions**: `toBeVisible()`, `toHaveURL()`, `toContainText()`
- **Wait for conditions**: `await expect(element).toBeVisible()` (auto-waits)
- **Avoid fixed timeouts**: Use `waitForURL()`, `waitForSelector()` with conditions

### Error Handling

- **Dialog handling**: Always set up dialog listeners before triggering dialogs
- **API errors**: Verify error messages are displayed to users
- **Network failures**: Test graceful degradation

### Accessibility

- **Keyboard navigation**: Test Tab, Enter, Escape key interactions
- **ARIA labels**: Verify icon buttons have accessible names
- **Focus indicators**: Check visible focus rings on interactive elements
- **Screen reader support**: Use semantic HTML and ARIA attributes

## Debugging Failed Tests

### 1. View Test Artifacts

```bash
# Open HTML report with screenshots and videos
npx playwright show-report
```

### 2. Run in Debug Mode

```bash
# Step through test with Playwright Inspector
npx playwright test --debug regression.spec.ts
```

### 3. View Traces

```bash
# Open trace viewer for detailed execution timeline
npx playwright show-trace trace.zip
```

### 4. Common Issues

**Issue**: "Timeout waiting for element"
- **Solution**: Element may not be visible yet. Increase timeout or check selector.

**Issue**: "Navigation timeout"
- **Solution**: Backend API may be slow. Check backend logs.

**Issue**: "Dialog not handled"
- **Solution**: Set up dialog listener before triggering action that shows dialog.

**Issue**: "Test passes locally but fails in CI"
- **Solution**: CI may be slower. Increase timeouts or use retry logic.

## Continuous Integration

Tests are configured to run in CI with:
- **2 retries** on failure
- **Trace capture** on first retry
- **Parallel execution** across browsers
- **HTML report** artifact upload

CI configuration in `.github/workflows/test.yml` (if configured).

## Test Metrics

### Coverage Summary

- **Total E2E Test Files**: 5
- **Total Test Cases**: 76+
- **User Stories Covered**: 5 (US1-US5)
- **Browsers Tested**: 3 (Chromium, Firefox, WebKit)
- **Mobile Devices Tested**: 2 (Pixel 5, iPhone 12)

### Test Execution Time (Estimated)

- **Regression Suite**: ~3-5 minutes (parallel)
- **Full E2E Suite**: ~8-12 minutes (parallel)
- **Single Browser**: ~4-6 minutes

## Maintenance Guidelines

### When to Update Tests

1. **New User Story**: Create dedicated test file or add to regression suite
2. **UI Changes**: Update selectors if component structure changes
3. **API Changes**: Update request/response assertions
4. **New Feature**: Add test coverage before merging to main

### Test Review Checklist

- [ ] Test is isolated (no shared state)
- [ ] Uses semantic selectors (role, label, text)
- [ ] Has clear test description
- [ ] Waits for conditions (no fixed timeouts)
- [ ] Handles errors gracefully
- [ ] Tests accessibility where applicable
- [ ] Uses helper functions for common operations

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
- [Accessibility Testing](https://playwright.dev/docs/accessibility-testing)

---

**Last Updated**: 2025-12-12
**Maintainer**: Testing & QA Agent
**Version**: 1.0.0
