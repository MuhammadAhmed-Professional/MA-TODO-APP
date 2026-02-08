/**
 * E2E Task Management Flow Tests (T065)
 *
 * Tests complete CRUD operations for tasks: create, view, edit, toggle complete, delete.
 * Requires backend API to be running at http://localhost:8000
 */

import { test, expect } from '@playwright/test';

/**
 * Generate unique email for test isolation
 */
function generateTestEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(7);
  return `task-test-${timestamp}-${random}@example.com`;
}

/**
 * Helper function to login a test user
 */
async function loginTestUser(page: any) {
  const testEmail = generateTestEmail();
  const testName = 'Task Test User';
  const testPassword = 'TaskTest123!';

  // Signup to create account
  await page.goto('/signup');
  await page.getByLabel(/name/i).fill(testName);
  await page.getByLabel(/email/i).fill(testEmail);
  await page.getByLabel(/^password$/i).fill(testPassword);
  await page.getByLabel(/confirm password/i).fill(testPassword);
  await page.getByRole('button', { name: /sign up/i }).click();

  // Wait for redirect to dashboard
  await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

  return { testEmail, testName, testPassword };
}

test.describe('Task Management Flow - Complete CRUD Journey', () => {
  test('user can create, view, edit, toggle, and delete task', async ({ page }) => {
    // Step 1: Login
    await loginTestUser(page);

    // Step 2: Navigate to tasks page
    await page.goto('/dashboard/tasks');
    await expect(page).toHaveURL('/dashboard/tasks');

    // Step 3: Click "New Task" button to open create modal
    await page.getByRole('button', { name: /new task/i }).click();

    // Step 4: Verify create modal is visible
    await expect(page.getByText(/create new task/i)).toBeVisible();

    // Step 5: Fill task form with title and description
    await page.getByLabel(/^title/i).fill('Buy milk');
    await page.getByLabel(/description/i).fill('From grocery store');

    // Step 6: Click Save/Create button
    await page.getByRole('button', { name: /create task/i }).click();

    // Step 7: Verify modal closes and task appears in list
    await expect(page.getByText(/create new task/i)).not.toBeVisible();
    await expect(page.getByText('Buy milk')).toBeVisible();
    await expect(page.getByText('From grocery store')).toBeVisible();

    // Step 8: Click Edit button for the task
    const taskCard = page.locator('div', { has: page.getByText('Buy milk') }).first();
    await taskCard.getByRole('button', { name: /edit task/i }).click();

    // Step 9: Verify edit modal opens with pre-filled data
    await expect(page.getByText(/edit task/i)).toBeVisible();
    await expect(page.getByLabel(/^title/i)).toHaveValue('Buy milk');

    // Step 10: Change title to "Buy organic milk"
    await page.getByLabel(/^title/i).clear();
    await page.getByLabel(/^title/i).fill('Buy organic milk');

    // Step 11: Click Save/Update button
    await page.getByRole('button', { name: /update task/i }).click();

    // Step 12: Verify modal closes and updated task appears in list
    await expect(page.getByText(/edit task/i)).not.toBeVisible();
    await expect(page.getByText('Buy organic milk')).toBeVisible();

    // Step 13: Click toggle complete checkbox
    const updatedTaskCard = page.locator('div', { has: page.getByText('Buy organic milk') }).first();
    await updatedTaskCard.getByRole('button', { name: /mark as complete/i }).click();

    // Step 14: Verify task shows as complete (strikethrough or checkmark)
    // Wait for the update to complete
    await page.waitForTimeout(500);

    // Check for completion styling - the title should have line-through class
    const taskTitle = updatedTaskCard.locator('h3', { hasText: 'Buy organic milk' });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Verify checkbox shows checkmark (button label changes to "Mark as incomplete")
    await expect(updatedTaskCard.getByRole('button', { name: /mark as incomplete/i })).toBeVisible();

    // Step 15: Click Delete button
    await updatedTaskCard.getByRole('button', { name: /delete task/i }).click();

    // Step 16: Confirm deletion in browser dialog
    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Are you sure');
      expect(dialog.message()).toContain('Buy organic milk');
      await dialog.accept();
    });

    // Trigger the confirmation (already clicked in step 15)
    await page.waitForTimeout(500);

    // Step 17: Verify task is removed from list
    await expect(page.getByText('Buy organic milk')).not.toBeVisible();
  });

  test('multiple tasks are sorted by creation date (newest first)', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Create first task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('First Task');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('First Task')).toBeVisible();

    // Wait a moment to ensure different timestamps
    await page.waitForTimeout(1000);

    // Create second task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Second Task');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Second Task')).toBeVisible();

    // Wait a moment
    await page.waitForTimeout(1000);

    // Create third task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Third Task');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Third Task')).toBeVisible();

    // Verify order: Third Task should appear before Second Task, which appears before First Task
    const taskTitles = page.locator('h3');
    const firstVisibleTask = taskTitles.first();
    await expect(firstVisibleTask).toContainText('Third Task');
  });
});

test.describe('Task Validation and Error Handling', () => {
  test('shows validation error for empty title', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Step 1: Click "New Task" button
    await page.getByRole('button', { name: /new task/i }).click();

    // Step 2: Leave title empty and try to submit
    await page.getByLabel(/description/i).fill('This task has no title');

    // Step 3: Click Save button
    await page.getByRole('button', { name: /create task/i }).click();

    // Step 4: Verify error message appears
    await expect(page.getByText(/title is required/i)).toBeVisible();

    // Step 5: Verify modal is still open (not submitted)
    await expect(page.getByText(/create new task/i)).toBeVisible();
  });

  test('shows validation error for title exceeding 200 characters', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Click "New Task" button
    await page.getByRole('button', { name: /new task/i }).click();

    // Fill title with 201 characters
    const longTitle = 'A'.repeat(201);
    await page.getByLabel(/^title/i).fill(longTitle);

    // Try to submit
    await page.getByRole('button', { name: /create task/i }).click();

    // Verify error message
    await expect(page.getByText(/title must be 200 characters or less/i)).toBeVisible();

    // Verify modal is still open
    await expect(page.getByText(/create new task/i)).toBeVisible();
  });

  test('shows validation error for description exceeding 2000 characters', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Click "New Task" button
    await page.getByRole('button', { name: /new task/i }).click();

    // Fill valid title
    await page.getByLabel(/^title/i).fill('Valid Title');

    // Fill description with 2001 characters
    const longDescription = 'B'.repeat(2001);
    await page.getByLabel(/description/i).fill(longDescription);

    // Try to submit
    await page.getByRole('button', { name: /create task/i }).click();

    // Verify error message
    await expect(page.getByText(/description must be 2000 characters or less/i)).toBeVisible();

    // Verify modal is still open
    await expect(page.getByText(/create new task/i)).toBeVisible();
  });

  test('can cancel task creation without saving', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Click "New Task" button
    await page.getByRole('button', { name: /new task/i }).click();

    // Fill form
    await page.getByLabel(/^title/i).fill('Cancel Test Task');
    await page.getByLabel(/description/i).fill('This should not be saved');

    // Click Cancel button
    await page.getByRole('button', { name: /cancel/i }).click();

    // Verify modal closes
    await expect(page.getByText(/create new task/i)).not.toBeVisible();

    // Verify task was NOT created
    await expect(page.getByText('Cancel Test Task')).not.toBeVisible();
  });

  test('can cancel task editing without saving changes', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Create a task first
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Original Title');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Original Title')).toBeVisible();

    // Click Edit button
    const taskCard = page.locator('div', { has: page.getByText('Original Title') }).first();
    await taskCard.getByRole('button', { name: /edit task/i }).click();

    // Change title but don't save
    await page.getByLabel(/^title/i).clear();
    await page.getByLabel(/^title/i).fill('Modified Title');

    // Click Cancel
    await page.getByRole('button', { name: /cancel/i }).click();

    // Verify modal closes
    await expect(page.getByText(/edit task/i)).not.toBeVisible();

    // Verify original title is still there (not modified)
    await expect(page.getByText('Original Title')).toBeVisible();
    await expect(page.getByText('Modified Title')).not.toBeVisible();
  });
});

test.describe('Task Persistence and State Management', () => {
  test('task persists across page refresh', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Step 1: Create task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Persistent Task');
    await page.getByLabel(/description/i).fill('Should survive page refresh');
    await page.getByRole('button', { name: /create task/i }).click();

    // Verify task appears
    await expect(page.getByText('Persistent Task')).toBeVisible();

    // Step 2: Refresh page
    await page.reload();

    // Step 3: Verify task still exists
    await expect(page.getByText('Persistent Task')).toBeVisible();
    await expect(page.getByText('Should survive page refresh')).toBeVisible();
  });

  test('completed task state persists across page refresh', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Create task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Complete State Test');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Complete State Test')).toBeVisible();

    // Mark as complete
    const taskCard = page.locator('div', { has: page.getByText('Complete State Test') }).first();
    await taskCard.getByRole('button', { name: /mark as complete/i }).click();

    // Wait for update
    await page.waitForTimeout(500);

    // Verify completion state
    const taskTitle = taskCard.locator('h3', { hasText: 'Complete State Test' });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Refresh page
    await page.reload();

    // Verify task is still marked as complete after refresh
    const refreshedTaskCard = page.locator('div', { has: page.getByText('Complete State Test') }).first();
    const refreshedTaskTitle = refreshedTaskCard.locator('h3', { hasText: 'Complete State Test' });
    await expect(refreshedTaskTitle).toHaveClass(/line-through/);
    await expect(refreshedTaskCard.getByRole('button', { name: /mark as incomplete/i })).toBeVisible();
  });

  test('can toggle task from complete back to incomplete', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Create task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Toggle Test');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Toggle Test')).toBeVisible();

    // Mark as complete
    let taskCard = page.locator('div', { has: page.getByText('Toggle Test') }).first();
    await taskCard.getByRole('button', { name: /mark as complete/i }).click();
    await page.waitForTimeout(500);

    // Verify completed
    let taskTitle = taskCard.locator('h3', { hasText: 'Toggle Test' });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Mark as incomplete
    await taskCard.getByRole('button', { name: /mark as incomplete/i }).click();
    await page.waitForTimeout(500);

    // Verify back to incomplete (no line-through)
    taskCard = page.locator('div', { has: page.getByText('Toggle Test') }).first();
    taskTitle = taskCard.locator('h3', { hasText: 'Toggle Test' });
    await expect(taskTitle).not.toHaveClass(/line-through/);
    await expect(taskCard.getByRole('button', { name: /mark as complete/i })).toBeVisible();
  });
});

test.describe('Task Deletion Confirmation', () => {
  test('shows confirmation dialog before deleting task', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Create task
    await page.getByRole('button', { name: /new task/i }).click();
    await page.getByLabel(/^title/i).fill('Delete Confirmation Test');
    await page.getByRole('button', { name: /create task/i }).click();
    await expect(page.getByText('Delete Confirmation Test')).toBeVisible();

    // Set up dialog handler to cancel deletion
    let dialogShown = false;
    page.on('dialog', async (dialog) => {
      dialogShown = true;
      expect(dialog.message()).toContain('Are you sure');
      expect(dialog.message()).toContain('Delete Confirmation Test');
      await dialog.dismiss(); // Cancel deletion
    });

    // Click delete button
    const taskCard = page.locator('div', { has: page.getByText('Delete Confirmation Test') }).first();
    await taskCard.getByRole('button', { name: /delete task/i }).click();

    // Wait for dialog
    await page.waitForTimeout(500);

    // Verify dialog was shown
    expect(dialogShown).toBe(true);

    // Verify task still exists (deletion was cancelled)
    await expect(page.getByText('Delete Confirmation Test')).toBeVisible();
  });
});

test.describe('Empty State', () => {
  test('shows appropriate UI when no tasks exist', async ({ page }) => {
    // Login
    await loginTestUser(page);

    // Navigate to tasks page
    await page.goto('/dashboard/tasks');

    // Verify page loads
    await expect(page.getByText(/my tasks/i)).toBeVisible();

    // Verify "New Task" button is visible even with no tasks
    await expect(page.getByRole('button', { name: /new task/i })).toBeVisible();
  });
});
