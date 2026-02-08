# Skill: Write E2E Test (Playwright)

## Description
Generates comprehensive Playwright end-to-end tests for critical user flows, including setup/teardown, fixtures, assertions, and error scenarios. Tests verify entire workflows from UI interaction to database state.

## Inputs
- **test_name**: Descriptive test name (e.g., "signup_and_login_flow", "create_task_workflow")
- **test_type**: Type (auth, task_crud, responsive, accessibility)
- **user_flow**: Step-by-step user actions (comma-separated)
- **assertions**: Expected outcomes/verifications
- **fixtures**: Any test data/setup needed
- **file_path**: Where to create (e.g., "frontend/tests/e2e/auth.spec.ts")
- **base_url**: API base URL for backend (e.g., "http://localhost:3000")

## Process

1. **Analyze User Flow**
   - Break down steps: navigation, form input, clicks, submissions
   - Identify critical assertions and wait conditions
   - Determine test data requirements (fixtures)

2. **Generate Test Structure**
   ```typescript
   import { test, expect, Page } from '@playwright/test';

   test.describe('[Feature Name] E2E Tests', () => {
     let page: Page;

     test.beforeEach(async ({ browser }) => {
       // Setup: Clear test data, navigate to starting page
       page = await browser.newPage();
       await page.goto('http://localhost:3000');
       // Clear auth cookies/localStorage
       await page.context().clearCookies();
     });

     test.afterEach(async () => {
       // Teardown: Close page, clear test data
       await page.close();
     });

     test('should [user action outcome]', async () => {
       // Step 1: Navigate
       await page.goto('http://localhost:3000/signup');

       // Step 2: Interact with UI
       await page.fill('input[name="email"]', 'test@example.com');
       await page.fill('input[name="password"]', 'password123');

       // Step 3: Submit
       await page.click('button[type="submit"]');

       // Step 4: Wait for navigation
       await page.waitForNavigation();

       // Step 5: Assert outcome
       expect(page.url()).toContain('/dashboard');

       // Step 6: Verify state change
       const welcome = await page.textContent('h1');
       expect(welcome).toContain('Welcome');
     });
   });
   ```

3. **Add Wait Conditions**
   - Use `waitForNavigation()` for page changes
   - Use `waitForSelector()` for element appearance
   - Use `waitForFunction()` for custom conditions
   - Avoid hardcoded `sleep()` - always use waits

4. **Test Fixture Management**
   ```typescript
   test.beforeEach(async ({ page }) => {
     // Create test user
     await page.evaluate(() => localStorage.clear());

     // Or: Call API to seed test data
     await fetch('http://localhost:8000/api/test-setup', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ email: 'test@example.com' })
     });
   });

   test.afterEach(async ({ page }) => {
     // Cleanup: Delete test user, clear data
     await fetch('http://localhost:8000/api/test-cleanup', {
       method: 'DELETE'
     });
   });
   ```

5. **Add Error Scenarios**
   - Test invalid input handling
   - Test network errors/timeouts
   - Test unauthorized access
   - Test edge cases (empty fields, max length, etc.)

6. **Responsive Testing** (if needed)
   ```typescript
   test('should work on mobile viewport', async ({ page }) => {
     await page.setViewportSize({ width: 375, height: 667 });
     // Rest of test...
   });
   ```

7. **Accessibility Testing** (if needed)
   ```typescript
   test('should be keyboard navigable', async ({ page }) => {
     await page.keyboard.press('Tab'); // Focus first element
     await page.keyboard.type('test@example.com'); // Type in focused field
     await page.keyboard.press('Tab'); // Focus password field
     await page.keyboard.type('password123');
     await page.keyboard.press('Enter'); // Submit
   });
   ```

## Example Usage
```
/skill write-e2e-test \
  --test_name signup_flow \
  --test_type auth \
  --user_flow "navigate_to_signup,fill_email,fill_password,submit_form,verify_dashboard" \
  --assertions "url_contains_dashboard,header_shows_username,tasks_list_visible" \
  --file_path frontend/tests/e2e/auth.spec.ts \
  --base_url http://localhost:3000
```

## Output
- Complete Playwright test spec (.ts file)
- Includes setup/teardown and fixtures
- Multiple test cases with assertions
- Ready to run with `pnpm playwright test`
- Can be debugged with `pnpm playwright test --debug`

## Common Playwright Selectors
- CSS: `input[name="email"]`
- Text: `text=Login`
- Role: `[role="button"]`
- Label: `[aria-label="Submit"]`
- Data attribute: `[data-testid="task-card"]`
