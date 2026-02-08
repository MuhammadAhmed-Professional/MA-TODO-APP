/**
 * E2E Regression Test Suite (T104)
 *
 * Comprehensive test suite covering all user stories:
 * - US1: Authentication (signup, login, logout, error handling, protected routes)
 * - US2: Task Management (CRUD operations, sorting, validation)
 * - US3: Authorization (cross-user task isolation, 403 errors)
 * - US4: Responsive UI (mobile, tablet, desktop layouts)
 * - US5: API Documentation (Swagger UI accessibility)
 *
 * This suite serves as a smoke test for production deployments and regression prevention.
 */

import { test, expect, Page } from "@playwright/test";

// ============================================================================
// CONFIGURATION
// ============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const APP_URL = "http://localhost:3000";

const VIEWPORTS = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Generate unique email for test isolation
 */
function generateTestEmail(prefix = "regression"): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(7);
  return `${prefix}-${timestamp}-${random}@example.com`;
}

/**
 * Signup a new user and return credentials
 */
async function signupUser(
  page: Page,
  name = "Test User",
  emailPrefix = "test"
): Promise<{ email: string; password: string; name: string }> {
  const email = generateTestEmail(emailPrefix);
  const password = "TestPass123!";

  await page.goto(`${APP_URL}/signup`);
  await page.getByLabel(/name/i).fill(name);
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/^password$/i).fill(password);
  await page.getByLabel(/confirm password/i).fill(password);
  await page.getByRole("button", { name: /sign up/i }).click();

  // Wait for redirect to dashboard
  await expect(page).toHaveURL("/dashboard", { timeout: 10000 });

  return { email, password, name };
}

/**
 * Login an existing user
 */
async function loginUser(page: Page, email: string, password: string): Promise<void> {
  await page.goto(`${APP_URL}/login`);
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole("button", { name: /log in/i }).click();

  // Wait for redirect to dashboard
  await expect(page).toHaveURL("/dashboard", { timeout: 10000 });
}

/**
 * Logout current user
 */
async function logoutUser(page: Page): Promise<void> {
  const logoutButton = page.getByRole("button", { name: /log out|sign out/i });
  await logoutButton.click();

  // Wait for redirect to login page
  await expect(page).toHaveURL("/login", { timeout: 5000 });
}

/**
 * Create a task with title and optional description
 */
async function createTask(
  page: Page,
  title: string,
  description?: string
): Promise<void> {
  // Navigate to tasks page or dashboard
  await page.goto(`${APP_URL}/dashboard`);

  // Click "Add Task" or "New Task" button
  const addTaskButton = page.getByRole("button", {
    name: /add task|create task|new task/i,
  });
  await addTaskButton.click();

  // Fill task form
  await page.getByLabel(/^title/i).fill(title);
  if (description) {
    await page.getByLabel(/description/i).fill(description);
  }

  // Submit task creation
  await page.getByRole("button", { name: /create task/i }).click();

  // Verify task appears
  await expect(page.getByText(title)).toBeVisible();
}

/**
 * Edit a task by title
 */
async function editTask(
  page: Page,
  oldTitle: string,
  newTitle: string,
  newDescription?: string
): Promise<void> {
  // Find task card by title
  const taskCard = page.locator("div", { has: page.getByText(oldTitle) }).first();

  // Click edit button
  await taskCard.getByRole("button", { name: /edit task/i }).click();

  // Wait for edit modal
  await expect(page.getByText(/edit task/i)).toBeVisible();

  // Update title
  await page.getByLabel(/^title/i).clear();
  await page.getByLabel(/^title/i).fill(newTitle);

  // Update description if provided
  if (newDescription !== undefined) {
    await page.getByLabel(/description/i).clear();
    if (newDescription) {
      await page.getByLabel(/description/i).fill(newDescription);
    }
  }

  // Submit update
  await page.getByRole("button", { name: /update task/i }).click();

  // Verify modal closes
  await expect(page.getByText(/edit task/i)).not.toBeVisible();

  // Verify updated task appears
  await expect(page.getByText(newTitle)).toBeVisible();
}

/**
 * Toggle task completion status
 */
async function toggleTaskCompletion(page: Page, taskTitle: string): Promise<void> {
  const taskCard = page.locator("div", { has: page.getByText(taskTitle) }).first();

  // Click toggle complete button (could be "Mark as complete" or "Mark as incomplete")
  const toggleButton = taskCard.locator("button", {
    hasText: /mark as (complete|incomplete)/i,
  });
  await toggleButton.click();

  // Wait for update to complete
  await page.waitForTimeout(500);
}

/**
 * Delete a task by title
 */
async function deleteTask(page: Page, taskTitle: string): Promise<void> {
  const taskCard = page.locator("div", { has: page.getByText(taskTitle) }).first();

  // Set up dialog handler to accept deletion
  page.on("dialog", async (dialog) => {
    expect(dialog.message()).toContain("Are you sure");
    await dialog.accept();
  });

  // Click delete button
  await taskCard.getByRole("button", { name: /delete task/i }).click();

  // Wait for deletion to complete
  await page.waitForTimeout(500);

  // Verify task is removed
  await expect(page.getByText(taskTitle)).not.toBeVisible();
}

// ============================================================================
// USER STORY 1: AUTHENTICATION
// ============================================================================

test.describe("US1: Authentication", () => {
  test("should signup with valid credentials and redirect to dashboard", async ({
    page,
  }) => {
    const { name } = await signupUser(page, "Signup Test User", "signup");

    // Verify redirect to dashboard
    await expect(page).toHaveURL("/dashboard");

    // Verify user is logged in
    await expect(page.getByText(name)).toBeVisible();
  });

  test("should login with valid credentials and redirect to dashboard", async ({
    page,
  }) => {
    // Step 1: Create account
    const { email, password, name } = await signupUser(page, "Login Test User", "login");

    // Step 2: Logout
    await logoutUser(page);

    // Step 3: Login with same credentials
    await loginUser(page, email, password);

    // Verify redirect to dashboard
    await expect(page).toHaveURL("/dashboard");

    // Verify user is logged in
    await expect(page.getByText(name)).toBeVisible();
  });

  test("should logout and redirect to login page", async ({ page }) => {
    // Login first
    await signupUser(page, "Logout Test User", "logout");

    // Logout
    await logoutUser(page);

    // Verify redirect to login page
    await expect(page).toHaveURL("/login");
  });

  test("should show error for invalid login credentials", async ({ page }) => {
    await page.goto(`${APP_URL}/login`);

    // Try to login with non-existent credentials
    await page.getByLabel(/email/i).fill("nonexistent@example.com");
    await page.getByLabel(/password/i).fill("WrongPassword123!");
    await page.getByRole("button", { name: /log in/i }).click();

    // Should show error message
    await expect(page.getByRole("alert")).toContainText(/invalid/i);

    // Should NOT redirect to dashboard
    await expect(page).toHaveURL("/login");
  });

  test("should redirect unauthenticated user from protected route to login", async ({
    page,
  }) => {
    // Clear cookies to ensure unauthenticated state
    await page.context().clearCookies();

    // Try to access protected route
    await page.goto(`${APP_URL}/dashboard`);

    // Should be redirected to login
    await expect(page).toHaveURL("/login", { timeout: 5000 });
  });

  test("should redirect authenticated user from login page to dashboard", async ({
    page,
  }) => {
    // Login first
    await signupUser(page, "Redirect Test User", "redirect");

    // Try to navigate to login page while authenticated
    await page.goto(`${APP_URL}/login`);

    // Should be redirected back to dashboard
    await expect(page).toHaveURL("/dashboard", { timeout: 5000 });
  });

  test("should show error for duplicate email signup", async ({ page }) => {
    const email = generateTestEmail("duplicate");
    const password = "DuplicateTest123!";

    // Step 1: Create first account
    await page.goto(`${APP_URL}/signup`);
    await page.getByLabel(/name/i).fill("First User");
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole("button", { name: /sign up/i }).click();

    // Wait for success
    await expect(page).toHaveURL("/dashboard", { timeout: 10000 });

    // Step 2: Logout
    await logoutUser(page);

    // Step 3: Try to signup with same email
    await page.goto(`${APP_URL}/signup`);
    await page.getByLabel(/name/i).fill("Second User");
    await page.getByLabel(/email/i).fill(email);
    await page.getByLabel(/^password$/i).fill(password);
    await page.getByLabel(/confirm password/i).fill(password);
    await page.getByRole("button", { name: /sign up/i }).click();

    // Step 4: Should show error message
    await expect(page.getByRole("alert")).toContainText(/already registered/i);

    // Should NOT redirect to dashboard
    await expect(page).toHaveURL("/signup");
  });
});

// ============================================================================
// USER STORY 2: TASK MANAGEMENT
// ============================================================================

test.describe("US2: Task Management", () => {
  test("should create task with title and description", async ({ page }) => {
    await signupUser(page, "Task Create User", "task-create");

    await createTask(page, "Buy groceries", "Milk, eggs, bread");

    // Verify task appears with title and description
    await expect(page.getByText("Buy groceries")).toBeVisible();
    await expect(page.getByText("Milk, eggs, bread")).toBeVisible();
  });

  test("should view task list sorted by creation date (newest first)", async ({
    page,
  }) => {
    await signupUser(page, "Task List User", "task-list");

    // Create three tasks with delays to ensure different timestamps
    await createTask(page, "First Task");
    await page.waitForTimeout(1000);

    await createTask(page, "Second Task");
    await page.waitForTimeout(1000);

    await createTask(page, "Third Task");

    // Navigate to tasks page
    await page.goto(`${APP_URL}/dashboard`);

    // Verify order: Third Task should appear before Second Task
    const taskTitles = page.locator("h3");
    const firstVisibleTask = taskTitles.first();
    await expect(firstVisibleTask).toContainText("Third Task");
  });

  test("should edit task title and description", async ({ page }) => {
    await signupUser(page, "Task Edit User", "task-edit");

    // Create task
    await createTask(page, "Original Title", "Original description");

    // Edit task
    await editTask(page, "Original Title", "Updated Title", "Updated description");

    // Verify updated task appears
    await expect(page.getByText("Updated Title")).toBeVisible();
    await expect(page.getByText("Updated description")).toBeVisible();

    // Verify old title is gone
    await expect(page.getByText("Original Title")).not.toBeVisible();
  });

  test("should mark task as complete (toggle)", async ({ page }) => {
    await signupUser(page, "Task Complete User", "task-complete");

    // Create task
    await createTask(page, "Complete Me");

    // Mark as complete
    await toggleTaskCompletion(page, "Complete Me");

    // Verify task shows as complete (strikethrough)
    const taskCard = page.locator("div", { has: page.getByText("Complete Me") }).first();
    const taskTitle = taskCard.locator("h3", { hasText: "Complete Me" });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Verify button changes to "Mark as incomplete"
    await expect(
      taskCard.getByRole("button", { name: /mark as incomplete/i })
    ).toBeVisible();
  });

  test("should toggle task from complete back to incomplete", async ({ page }) => {
    await signupUser(page, "Task Toggle User", "task-toggle");

    // Create task
    await createTask(page, "Toggle Task");

    // Mark as complete
    await toggleTaskCompletion(page, "Toggle Task");

    // Verify completed
    let taskCard = page.locator("div", { has: page.getByText("Toggle Task") }).first();
    let taskTitle = taskCard.locator("h3", { hasText: "Toggle Task" });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Mark as incomplete
    await toggleTaskCompletion(page, "Toggle Task");

    // Verify back to incomplete (no line-through)
    taskCard = page.locator("div", { has: page.getByText("Toggle Task") }).first();
    taskTitle = taskCard.locator("h3", { hasText: "Toggle Task" });
    await expect(taskTitle).not.toHaveClass(/line-through/);
  });

  test("should delete task with confirmation", async ({ page }) => {
    await signupUser(page, "Task Delete User", "task-delete");

    // Create task
    await createTask(page, "Delete Me");

    // Delete task (helper function handles confirmation dialog)
    await deleteTask(page, "Delete Me");

    // Verify task is removed
    await expect(page.getByText("Delete Me")).not.toBeVisible();
  });

  test("should show validation error for empty title", async ({ page }) => {
    await signupUser(page, "Task Validation User", "task-validation");

    await page.goto(`${APP_URL}/dashboard`);

    // Click "New Task" button
    await page.getByRole("button", { name: /new task/i }).click();

    // Leave title empty and try to submit
    await page.getByLabel(/description/i).fill("This task has no title");
    await page.getByRole("button", { name: /create task/i }).click();

    // Verify error message appears
    await expect(page.getByText(/title is required/i)).toBeVisible();

    // Verify modal is still open (not submitted)
    await expect(page.getByText(/create new task/i)).toBeVisible();
  });

  test("should persist task across page refresh", async ({ page }) => {
    await signupUser(page, "Task Persist User", "task-persist");

    // Create task
    await createTask(page, "Persistent Task", "Should survive refresh");

    // Refresh page
    await page.reload();

    // Verify task still exists
    await expect(page.getByText("Persistent Task")).toBeVisible();
    await expect(page.getByText("Should survive refresh")).toBeVisible();
  });

  test("should persist completed task state across page refresh", async ({ page }) => {
    await signupUser(page, "Task State Persist User", "task-state-persist");

    // Create task
    await createTask(page, "Stateful Task");

    // Mark as complete
    await toggleTaskCompletion(page, "Stateful Task");

    // Verify completion state
    let taskCard = page.locator("div", { has: page.getByText("Stateful Task") }).first();
    let taskTitle = taskCard.locator("h3", { hasText: "Stateful Task" });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Refresh page
    await page.reload();

    // Verify task is still marked as complete after refresh
    taskCard = page.locator("div", { has: page.getByText("Stateful Task") }).first();
    taskTitle = taskCard.locator("h3", { hasText: "Stateful Task" });
    await expect(taskTitle).toHaveClass(/line-through/);
    await expect(
      taskCard.getByRole("button", { name: /mark as incomplete/i })
    ).toBeVisible();
  });
});

// ============================================================================
// USER STORY 3: AUTHORIZATION
// ============================================================================

test.describe("US3: Authorization", () => {
  test("user can only see their own tasks (cross-user isolation)", async ({ page }) => {
    const timestamp = Date.now();

    // Step 1: User A creates account and task
    const userA = await signupUser(page, "User A", "user-a");
    const userATaskTitle = `User A Task - ${timestamp}`;
    await createTask(page, userATaskTitle, "User A's private task");

    // Logout User A
    await logoutUser(page);

    // Step 2: User B creates account
    const userB = await signupUser(page, "User B", "user-b");

    // Step 3: Verify User B cannot see User A's task
    await page.goto(`${APP_URL}/dashboard`);
    await page.waitForTimeout(1000);
    await expect(page.getByText(userATaskTitle)).not.toBeVisible();

    // Step 4: User B creates their own task
    const userBTaskTitle = `User B Task - ${timestamp}`;
    await createTask(page, userBTaskTitle, "User B's private task");

    // Step 5: Verify User B sees only their own task
    await expect(page.getByText(userBTaskTitle)).toBeVisible();
    await expect(page.getByText(userATaskTitle)).not.toBeVisible();

    // Step 6: Logout User B and login User A
    await logoutUser(page);
    await loginUser(page, userA.email, userA.password);

    // Step 7: Verify User A sees only their own task
    await page.goto(`${APP_URL}/dashboard`);
    await page.waitForTimeout(1000);
    await expect(page.getByText(userATaskTitle)).toBeVisible();
    await expect(page.getByText(userBTaskTitle)).not.toBeVisible();
  });

  test("accessing another user's task via API returns 403", async ({
    page,
    request,
  }) => {
    const timestamp = Date.now();
    const password = "TestPass123!";

    // Create User A and task via API
    const userAEmail = `user-a-api-${timestamp}@example.com`;
    const signupAResponse = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        name: "User A API",
        email: userAEmail,
        password: password,
      },
    });
    expect(signupAResponse.ok()).toBeTruthy();
    const userACookies = signupAResponse.headers()["set-cookie"];
    const userATokenMatch = userACookies?.match(/auth_token=([^;]+)/);
    const userAToken = userATokenMatch ? userATokenMatch[1] : "";

    // Create task as User A
    const createTaskResponse = await request.post(`${API_URL}/api/tasks`, {
      data: {
        title: "User A's Protected Task",
        description: "Should be 403 for User B",
      },
      headers: {
        Cookie: `auth_token=${userAToken}`,
      },
    });
    expect(createTaskResponse.ok()).toBeTruthy();
    const taskData = await createTaskResponse.json();
    const taskId = taskData.id;

    // Create User B
    const userBEmail = `user-b-api-${timestamp}@example.com`;
    const signupBResponse = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        name: "User B API",
        email: userBEmail,
        password: password,
      },
    });
    expect(signupBResponse.ok()).toBeTruthy();
    const userBCookies = signupBResponse.headers()["set-cookie"];
    const userBTokenMatch = userBCookies?.match(/auth_token=([^;]+)/);
    const userBToken = userBTokenMatch ? userBTokenMatch[1] : "";

    // Verify User B cannot GET User A's task (403)
    const getTaskResponse = await request.get(`${API_URL}/api/tasks/${taskId}`, {
      headers: {
        Cookie: `auth_token=${userBToken}`,
      },
    });
    expect(getTaskResponse.status()).toBe(403);

    // Verify User B cannot UPDATE User A's task (403)
    const updateTaskResponse = await request.put(`${API_URL}/api/tasks/${taskId}`, {
      data: { title: "Hacked Title" },
      headers: {
        Cookie: `auth_token=${userBToken}`,
      },
    });
    expect(updateTaskResponse.status()).toBe(403);

    // Verify User B cannot DELETE User A's task (403)
    const deleteTaskResponse = await request.delete(`${API_URL}/api/tasks/${taskId}`, {
      headers: {
        Cookie: `auth_token=${userBToken}`,
      },
    });
    expect(deleteTaskResponse.status()).toBe(403);

    // Verify User A can still access their own task (200)
    const userAGetResponse = await request.get(`${API_URL}/api/tasks/${taskId}`, {
      headers: {
        Cookie: `auth_token=${userAToken}`,
      },
    });
    expect(userAGetResponse.ok()).toBeTruthy();
    const verifyTaskData = await userAGetResponse.json();
    expect(verifyTaskData.title).toBe("User A's Protected Task");
  });
});

// ============================================================================
// USER STORY 4: RESPONSIVE UI
// ============================================================================

test.describe("US4: Responsive UI", () => {
  test.describe("Mobile Layout (375px)", () => {
    test.use({ viewport: VIEWPORTS.mobile });

    test("should display single-column task layout", async ({ page }) => {
      await signupUser(page, "Mobile User", "mobile");
      await createTask(page, "Mobile Task");

      await page.goto(`${APP_URL}/dashboard`);

      // Task list should have single column
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/grid-cols-1/);
    });

    test("should show hamburger menu", async ({ page }) => {
      await signupUser(page, "Mobile Menu User", "mobile-menu");

      // Hamburger button should be visible
      const hamburgerBtn = page.locator(
        'button[aria-label*="menu"], button[aria-controls="mobile-menu"]'
      );
      await expect(hamburgerBtn).toBeVisible();
    });

    test("should have touch-friendly button sizes (44x44px minimum)", async ({
      page,
    }) => {
      await signupUser(page, "Mobile Touch User", "mobile-touch");
      await createTask(page, "Touch Test Task");

      await page.goto(`${APP_URL}/dashboard`);

      // Check button sizes
      const buttons = page.locator("button");
      const count = await buttons.count();

      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = buttons.nth(i);
        const box = await button.boundingBox();

        if (box) {
          // Touch targets should be at least 44x44px (allow small margin)
          expect(box.height).toBeGreaterThanOrEqual(40);
          expect(box.width).toBeGreaterThanOrEqual(40);
        }
      }
    });
  });

  test.describe("Tablet Layout (768px)", () => {
    test.use({ viewport: VIEWPORTS.tablet });

    test("should display two-column task grid", async ({ page }) => {
      await signupUser(page, "Tablet User", "tablet");
      await createTask(page, "Tablet Task");

      await page.goto(`${APP_URL}/dashboard`);

      // Task list should have two columns at md breakpoint
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/md:grid-cols-2/);
    });
  });

  test.describe("Desktop Layout (1920px)", () => {
    test.use({ viewport: VIEWPORTS.desktop });

    test("should display three-column task grid", async ({ page }) => {
      await signupUser(page, "Desktop User", "desktop");
      await createTask(page, "Desktop Task");

      await page.goto(`${APP_URL}/dashboard`);

      // Task list should have three columns at lg breakpoint
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/lg:grid-cols-3/);
    });

    test("should show sidebar navigation", async ({ page }) => {
      await signupUser(page, "Desktop Sidebar User", "desktop-sidebar");

      // Sidebar should be visible on desktop
      const sidebar = page.locator('aside[aria-label*="Sidebar"]');
      await expect(sidebar).toBeVisible();
    });
  });

  test.describe("Responsive Transitions", () => {
    test("should smoothly transition between viewport sizes", async ({ page }) => {
      await signupUser(page, "Responsive User", "responsive");

      // Start at mobile
      await page.setViewportSize(VIEWPORTS.mobile);
      await page.waitForTimeout(300);

      // Hamburger should be visible
      let hamburger = page.locator('button.md\\:hidden');
      await expect(hamburger).toBeVisible();

      // Transition to desktop
      await page.setViewportSize(VIEWPORTS.desktop);
      await page.waitForTimeout(300);

      // Sidebar should now be visible
      const sidebar = page.locator('aside[aria-label*="Sidebar"]');
      await expect(sidebar).toBeVisible();
    });
  });
});

// ============================================================================
// USER STORY 5: API DOCUMENTATION
// ============================================================================

test.describe("US5: API Documentation", () => {
  test("/docs endpoint is accessible and renders Swagger UI", async ({ page }) => {
    // Navigate directly to API docs endpoint
    await page.goto(`${API_URL}/docs`);

    // Verify Swagger UI elements are present
    // Check for OpenAPI/Swagger UI specific elements
    await expect(page.locator(".swagger-ui")).toBeVisible();

    // Verify page title contains "API" or "Swagger"
    await expect(page).toHaveTitle(/API|Swagger|Docs/i);

    // Verify API endpoints are listed
    await expect(page.getByText(/\/api\/tasks/i)).toBeVisible();
    await expect(page.getByText(/\/api\/auth/i)).toBeVisible();
  });

  test("API docs show authentication endpoints", async ({ page }) => {
    await page.goto(`${API_URL}/docs`);

    // Verify authentication endpoints are documented
    await expect(page.getByText(/signup/i)).toBeVisible();
    await expect(page.getByText(/login/i)).toBeVisible();
  });

  test("API docs show task management endpoints", async ({ page }) => {
    await page.goto(`${API_URL}/docs`);

    // Verify task endpoints are documented
    await expect(page.getByText(/POST.*\/api\/tasks/i)).toBeVisible();
    await expect(page.getByText(/GET.*\/api\/tasks/i)).toBeVisible();
    await expect(page.getByText(/PUT.*\/api\/tasks/i)).toBeVisible();
    await expect(page.getByText(/DELETE.*\/api\/tasks/i)).toBeVisible();
  });
});

// ============================================================================
// COMPREHENSIVE SMOKE TEST
// ============================================================================

test.describe("Comprehensive Smoke Test", () => {
  test("complete user journey: signup → create task → edit → complete → logout → login → delete", async ({
    page,
  }) => {
    // Step 1: Signup
    const { email, password, name } = await signupUser(
      page,
      "Smoke Test User",
      "smoke"
    );
    await expect(page).toHaveURL("/dashboard");
    await expect(page.getByText(name)).toBeVisible();

    // Step 2: Create task
    await createTask(page, "Smoke Test Task", "End-to-end test");
    await expect(page.getByText("Smoke Test Task")).toBeVisible();

    // Step 3: Edit task
    await editTask(page, "Smoke Test Task", "Updated Smoke Task", "Modified");
    await expect(page.getByText("Updated Smoke Task")).toBeVisible();

    // Step 4: Mark as complete
    await toggleTaskCompletion(page, "Updated Smoke Task");
    const taskCard = page
      .locator("div", { has: page.getByText("Updated Smoke Task") })
      .first();
    const taskTitle = taskCard.locator("h3", { hasText: "Updated Smoke Task" });
    await expect(taskTitle).toHaveClass(/line-through/);

    // Step 5: Logout
    await logoutUser(page);
    await expect(page).toHaveURL("/login");

    // Step 6: Login
    await loginUser(page, email, password);
    await expect(page).toHaveURL("/dashboard");

    // Step 7: Verify task persisted
    await expect(page.getByText("Updated Smoke Task")).toBeVisible();

    // Step 8: Delete task
    await deleteTask(page, "Updated Smoke Task");
    await expect(page.getByText("Updated Smoke Task")).not.toBeVisible();

    // Step 9: Logout again
    await logoutUser(page);
    await expect(page).toHaveURL("/login");
  });
});
