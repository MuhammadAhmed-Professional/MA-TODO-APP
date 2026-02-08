# Skill: Create E2E Tests

## Description
Generate comprehensive Playwright end-to-end tests for complete user flows with proper page object patterns and assertions.

## Inputs
- `user_story`: User story ID (e.g., "US2 - Task Management")
- `flow_steps`: List of steps in the user flow (e.g., "signup → create task → edit task → delete task")
- `acceptance_criteria`: Acceptance criteria from spec.md

## Process

### 1. Analyze User Flow
- Break down the flow into discrete steps
- Identify pages/routes involved
- Identify user interactions (clicks, typing, navigation)
- Identify expected outcomes (redirects, UI changes, data persistence)

### 2. Set Up Test Structure
Create `frontend/tests/e2e/<feature>.spec.ts`:
- Use `test.describe()` to group related flows
- Use `test.beforeEach()` for setup (auth, navigation)
- Use `test.afterEach()` for cleanup (logout, clear data)

**Pattern**:
```typescript
import { test, expect } from '@playwright/test';

test.describe('Task Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app and login
    await page.goto('http://localhost:3000');
    await page.getByRole('button', { name: /login/i }).click();
    // ... login steps
  });

  test('user can create, edit, and delete task', async ({ page }) => {
    // Create task
    await page.getByRole('button', { name: /add task/i }).click();
    await page.getByLabel(/title/i).fill('Buy groceries');
    await page.getByRole('button', { name: /save/i }).click();

    // Verify task appears
    await expect(page.getByText('Buy groceries')).toBeVisible();

    // Edit task
    await page.getByRole('button', { name: /edit/i }).first().click();
    await page.getByLabel(/title/i).fill('Buy organic groceries');
    await page.getByRole('button', { name: /save/i }).click();

    // Verify edit
    await expect(page.getByText('Buy organic groceries')).toBeVisible();

    // Delete task
    await page.getByRole('button', { name: /delete/i }).first().click();
    await page.getByRole('button', { name: /confirm/i }).click();

    // Verify deletion
    await expect(page.getByText('Buy organic groceries')).not.toBeVisible();
  });
});
```

### 3. Test Critical Paths
For each user story, test:
- **Happy path**: All steps succeed
- **Error path**: Invalid inputs show error messages
- **Authentication**: Unauthenticated access redirects to login
- **Authorization**: User A cannot access User B's resources
- **Navigation**: Back button, breadcrumbs, direct URL access work correctly

### 4. Test Multiple Viewports
Use Playwright's viewport configuration to test responsive design:
```typescript
test.describe('Responsive design', () => {
  test('mobile layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    // Test mobile-specific UI
  });

  test('tablet layout', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    // Test tablet-specific UI
  });

  test('desktop layout', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    // Test desktop-specific UI
  });
});
```

### 5. Test Accessibility
- Test keyboard navigation (Tab, Enter, Space, Escape)
- Test screen reader (use Playwright's accessibility tree)
- Test focus indicators (verify visible focus styles)

## Example Usage

**Scenario**: Generate E2E test for task CRUD flow

```bash
# Context: Task T065 from tasks.md
# T065: Write E2E test in frontend/tests/e2e/tasks.spec.ts (create → view → edit → toggle → delete)
```

**Agent invocation**:
```
Create E2E test for User Story 2 (Task Management):
- User story: US2 - Task Management
- Flow steps: login → create task "Buy milk" → verify in list → edit to "Buy organic milk" → toggle complete → delete with confirmation → verify removed
- Acceptance criteria: All CRUD operations work, tasks persist across page refreshes
```

## Constitution Compliance
- **Principle III**: TDD - E2E tests validate complete user flows
- **Principle V**: Multi-interface - Tests include responsive and accessibility validation
- **Principle II**: Clean code - Tests use page object pattern, descriptive test names

## Output
- `frontend/tests/e2e/<feature>.spec.ts` (E2E test file)
- Test execution report showing all flows passing
- Screenshots/videos of test runs for debugging
