/**
 * E2E Authentication Flow Tests (T040)
 *
 * Tests complete user authentication journeys from signup to logout.
 * Requires backend API to be running at http://localhost:8000
 */

import { test, expect } from '@playwright/test';

/**
 * Generate unique email for test isolation
 */
function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(7);
  return `e2e-test-${timestamp}-${random}@example.com`;
}

test.describe('Authentication Flow - Complete Journey', () => {
  test('should complete full flow: signup → auto-login → dashboard → logout → login redirect', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testName = 'E2E Test User';
    const testPassword = 'E2ETestPassword123!';

    // Step 1: Navigate to signup page
    await page.goto('/signup');
    await expect(page).toHaveURL('/signup');

    // Step 2: Fill out signup form
    await page.getByLabel(/name/i).fill(testName);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);

    // Step 3: Submit signup form
    await page.getByRole('button', { name: /sign up/i }).click();

    // Step 4: Should auto-login and redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 5: Verify user is logged in (check for user name or logout button)
    await expect(page.getByText(testName)).toBeVisible();

    // Step 6: Logout
    const logoutButton = page.getByRole('button', { name: /log out/i });
    await logoutButton.click();

    // Step 7: Should redirect to login page after logout
    await expect(page).toHaveURL('/login', { timeout: 5000 });

    // Step 8: Try to access dashboard without authentication
    await page.goto('/dashboard');

    // Step 9: Should be redirected back to login
    await expect(page).toHaveURL('/login');
  });

  test('should login with existing credentials after signup', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testName = 'Login Test User';
    const testPassword = 'LoginTestPass123!';

    // Step 1: Create account via signup
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill(testName);
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Logout
    await page.getByRole('button', { name: /log out/i }).click();
    await expect(page).toHaveURL('/login');

    // Step 3: Login with same credentials
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/password/i).fill(testPassword);
    await page.getByRole('button', { name: /log in/i }).click();

    // Step 4: Should be logged in and see dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(testName)).toBeVisible();
  });
});

test.describe('Unauthenticated Access Protection', () => {
  test('should redirect unauthenticated user from /dashboard to /login', async ({ page }) => {
    // Clear cookies to ensure unauthenticated state
    await page.context().clearCookies();

    // Try to access dashboard
    await page.goto('/dashboard');

    // Should be redirected to login
    await expect(page).toHaveURL('/login', { timeout: 5000 });
  });

  test('should show login page for unauthenticated user', async ({ page }) => {
    await page.context().clearCookies();

    await page.goto('/login');

    // Should see login form
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /log in/i })).toBeVisible();
  });
});

test.describe('Authenticated User Redirects', () => {
  test('should redirect authenticated user from /login to /dashboard', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testPassword = 'RedirectTest123!';

    // Step 1: Signup to get authenticated
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Redirect Test');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Try to navigate to /login while authenticated
    await page.goto('/login');

    // Step 3: Should be redirected back to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 5000 });
  });

  test('should redirect authenticated user from /signup to /dashboard', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testPassword = 'SignupRedirect123!';

    // Step 1: Signup to get authenticated
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Signup Redirect Test');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Try to navigate to /signup while authenticated
    await page.goto('/signup');

    // Step 3: Should be redirected back to dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 5000 });
  });
});

test.describe('Error Handling', () => {
  test('should display error for duplicate email signup', async ({ page }) => {
    const duplicateEmail = generateTestEmail();
    const testPassword = 'DuplicateTest123!';

    // Step 1: Create first account
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('First User');
    await page.getByLabel(/email/i).fill(duplicateEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for success
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Logout
    await page.getByRole('button', { name: /log out/i }).click();

    // Step 3: Try to signup with same email
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Second User');
    await page.getByLabel(/email/i).fill(duplicateEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Step 4: Should show error message
    await expect(page.getByRole('alert')).toContainText(/already registered/i);

    // Should NOT redirect to dashboard
    await expect(page).toHaveURL('/signup');
  });

  test('should display error for invalid login credentials', async ({ page }) => {
    await page.goto('/login');

    // Try to login with non-existent credentials
    await page.getByLabel(/email/i).fill('nonexistent@example.com');
    await page.getByLabel(/password/i).fill('WrongPassword123!');
    await page.getByRole('button', { name: /log in/i }).click();

    // Should show error message
    await expect(page.getByRole('alert')).toContainText(/invalid/i);

    // Should NOT redirect to dashboard
    await expect(page).toHaveURL('/login');
  });

  test('should display error for wrong password on existing account', async ({ page }) => {
    const testEmail = generateTestEmail();
    const correctPassword = 'CorrectPass123!';
    const wrongPassword = 'WrongPass456!';

    // Step 1: Create account
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Password Test User');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(correctPassword);
    await page.getByLabel(/confirm password/i).fill(correctPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Logout
    await page.getByRole('button', { name: /log out/i }).click();

    // Step 3: Try to login with wrong password
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/password/i).fill(wrongPassword);
    await page.getByRole('button', { name: /log in/i }).click();

    // Step 4: Should show error
    await expect(page.getByRole('alert')).toContainText(/invalid/i);
    await expect(page).toHaveURL('/login');
  });
});

test.describe('Session Persistence', () => {
  test('should maintain session across page reloads', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testPassword = 'SessionTest123!';

    // Step 1: Login
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Session Test User');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Reload page
    await page.reload();

    // Step 3: Should still be on dashboard (session persisted)
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Session Test User')).toBeVisible();
  });

  test('should clear session after logout', async ({ page }) => {
    const testEmail = generateTestEmail();
    const testPassword = 'LogoutSession123!';

    // Step 1: Login
    await page.goto('/signup');
    await page.getByLabel(/name/i).fill('Logout Session Test');
    await page.getByLabel(/email/i).fill(testEmail);
    await page.getByLabel(/^password$/i).fill(testPassword);
    await page.getByLabel(/confirm password/i).fill(testPassword);
    await page.getByRole('button', { name: /sign up/i }).click();

    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Step 2: Logout
    await page.getByRole('button', { name: /log out/i }).click();

    // Step 3: Try to reload dashboard
    await page.goto('/dashboard');

    // Step 4: Should be redirected to login (session cleared)
    await expect(page).toHaveURL('/login');
  });
});
