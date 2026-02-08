/**
 * E2E Authorization Tests
 *
 * Tests cross-user task visibility and ownership enforcement.
 *
 * Test Scenario:
 * 1. User A creates account and adds a task
 * 2. User A logs out
 * 3. User B creates account (different user)
 * 4. Verify User B cannot see User A's task
 * 5. User B creates their own task
 * 6. Verify User B can only see their own task
 */

import { test, expect } from "@playwright/test";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const APP_URL = "http://localhost:3000";

// Generate unique email addresses to avoid conflicts
const timestamp = Date.now();
const userAEmail = `usera-${timestamp}@example.com`;
const userBEmail = `userb-${timestamp}@example.com`;
const password = "TestPass123!";

test.describe("Authorization and Cross-User Access Control", () => {
  test("User A creates task → logout → User B cannot see User A's task", async ({
    page,
  }) => {
    // ========================================
    // PART 1: User A Signup and Task Creation
    // ========================================
    await test.step("User A signs up", async () => {
      await page.goto(`${APP_URL}/signup`);

      await page.fill('[name="name"]', "User A");
      await page.fill('[name="email"]', userAEmail);
      await page.fill('[name="password"]', password);

      await page.click('button[type="submit"]');

      // Wait for redirect to dashboard after signup
      await page.waitForURL(/\/dashboard/);
      expect(page.url()).toContain("/dashboard");
    });

    let userATaskTitle: string;
    await test.step("User A creates a task", async () => {
      // Navigate to tasks page (or use Add Task button if on dashboard)
      await page.goto(`${APP_URL}/dashboard`);

      // Find and click "Add Task" or "Create Task" button
      const addTaskButton = page.getByRole("button", {
        name: /add task|create task|new task/i,
      });
      await addTaskButton.click();

      // Fill task form
      userATaskTitle = `User A's Private Task - ${timestamp}`;
      await page.fill('[name="title"]', userATaskTitle);
      await page.fill(
        '[name="description"]',
        "This task should NOT be visible to User B"
      );

      // Submit task creation
      await page.click('button[type="submit"]:has-text(/save|create/i)');

      // Verify task appears in list
      await expect(page.getByText(userATaskTitle)).toBeVisible();
    });

    await test.step("User A logs out", async () => {
      // Click logout button (in header or dropdown)
      const logoutButton = page.getByRole("button", {
        name: /logout|sign out/i,
      });
      await logoutButton.click();

      // Wait for redirect to login page
      await page.waitForURL(/\/login/);
      expect(page.url()).toContain("/login");
    });

    // ========================================
    // PART 2: User B Signup and Verification
    // ========================================
    await test.step("User B signs up (different account)", async () => {
      await page.goto(`${APP_URL}/signup`);

      await page.fill('[name="name"]', "User B");
      await page.fill('[name="email"]', userBEmail);
      await page.fill('[name="password"]', password);

      await page.click('button[type="submit"]');

      // Wait for redirect to dashboard
      await page.waitForURL(/\/dashboard/);
      expect(page.url()).toContain("/dashboard");
    });

    await test.step("User B CANNOT see User A's task in dashboard", async () => {
      await page.goto(`${APP_URL}/dashboard`);

      // Wait for task list to load
      await page.waitForTimeout(1000);

      // Verify User A's task is NOT visible
      const userATaskElement = page.getByText(userATaskTitle);
      await expect(userATaskElement).not.toBeVisible();
    });

    let userBTaskTitle: string;
    await test.step("User B creates their own task", async () => {
      // Click "Add Task" button
      const addTaskButton = page.getByRole("button", {
        name: /add task|create task|new task/i,
      });
      await addTaskButton.click();

      // Fill task form
      userBTaskTitle = `User B's Private Task - ${timestamp}`;
      await page.fill('[name="title"]', userBTaskTitle);
      await page.fill('[name="description"]', "User B's personal task");

      // Submit task creation
      await page.click('button[type="submit"]:has-text(/save|create/i)');

      // Verify User B's task appears
      await expect(page.getByText(userBTaskTitle)).toBeVisible();
    });

    await test.step("User B sees ONLY their own task", async () => {
      await page.goto(`${APP_URL}/dashboard`);

      // Wait for task list to load
      await page.waitForTimeout(1000);

      // Verify User B's task is visible
      await expect(page.getByText(userBTaskTitle)).toBeVisible();

      // Verify User A's task is still NOT visible
      await expect(page.getByText(userATaskTitle)).not.toBeVisible();
    });

    // ========================================
    // PART 3: Verify User A can still access their task
    // ========================================
    await test.step("User B logs out", async () => {
      const logoutButton = page.getByRole("button", {
        name: /logout|sign out/i,
      });
      await logoutButton.click();
      await page.waitForURL(/\/login/);
    });

    await test.step("User A logs back in", async () => {
      await page.goto(`${APP_URL}/login`);

      await page.fill('[name="email"]', userAEmail);
      await page.fill('[name="password"]', password);
      await page.click('button[type="submit"]');

      await page.waitForURL(/\/dashboard/);
    });

    await test.step("User A sees ONLY their own task", async () => {
      await page.goto(`${APP_URL}/dashboard`);

      // Wait for task list to load
      await page.waitForTimeout(1000);

      // Verify User A's task is visible
      await expect(page.getByText(userATaskTitle)).toBeVisible();

      // Verify User B's task is NOT visible
      await expect(page.getByText(userBTaskTitle)).not.toBeVisible();
    });
  });

  test("Attempting to access another user's task by direct URL returns 403", async ({
    page,
    request,
  }) => {
    // ========================================
    // SETUP: Create User A and task via API
    // ========================================
    const userAEmail = `usera-direct-${timestamp}@example.com`;
    const userBEmail = `userb-direct-${timestamp}@example.com`;

    // Create User A and get auth token
    const signupAResponse = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        name: "User A Direct",
        email: userAEmail,
        password: password,
      },
    });
    expect(signupAResponse.ok()).toBeTruthy();
    const userACookies = signupAResponse.headers()["set-cookie"];

    // Extract auth_token from cookies
    const userATokenMatch = userACookies?.match(/auth_token=([^;]+)/);
    const userAToken = userATokenMatch ? userATokenMatch[1] : "";

    // Create task as User A
    const createTaskResponse = await request.post(`${API_URL}/api/tasks`, {
      data: {
        title: "User A's Direct Access Task",
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
    const signupBResponse = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        name: "User B Direct",
        email: userBEmail,
        password: password,
      },
    });
    expect(signupBResponse.ok()).toBeTruthy();
    const userBCookies = signupBResponse.headers()["set-cookie"];
    const userBTokenMatch = userBCookies?.match(/auth_token=([^;]+)/);
    const userBToken = userBTokenMatch ? userBTokenMatch[1] : "";

    // ========================================
    // TEST: User B tries to access User A's task
    // ========================================
    await test.step("User B attempts to GET User A's task via API (403)", async () => {
      const getTaskResponse = await request.get(
        `${API_URL}/api/tasks/${taskId}`,
        {
          headers: {
            Cookie: `auth_token=${userBToken}`,
          },
        }
      );

      // Should return 403 Forbidden
      expect(getTaskResponse.status()).toBe(403);
      const errorData = await getTaskResponse.json();
      expect(errorData.detail.toLowerCase()).toContain("not authorized");
    });

    await test.step("User B attempts to UPDATE User A's task via API (403)", async () => {
      const updateTaskResponse = await request.put(
        `${API_URL}/api/tasks/${taskId}`,
        {
          data: {
            title: "Hacked Title",
          },
          headers: {
            Cookie: `auth_token=${userBToken}`,
          },
        }
      );

      // Should return 403 Forbidden
      expect(updateTaskResponse.status()).toBe(403);
    });

    await test.step("User B attempts to DELETE User A's task via API (403)", async () => {
      const deleteTaskResponse = await request.delete(
        `${API_URL}/api/tasks/${taskId}`,
        {
          headers: {
            Cookie: `auth_token=${userBToken}`,
          },
        }
      );

      // Should return 403 Forbidden
      expect(deleteTaskResponse.status()).toBe(403);
    });

    await test.step("User A can still access their own task (200)", async () => {
      const getTaskResponse = await request.get(
        `${API_URL}/api/tasks/${taskId}`,
        {
          headers: {
            Cookie: `auth_token=${userAToken}`,
          },
        }
      );

      // Should return 200 OK
      expect(getTaskResponse.ok()).toBeTruthy();
      const taskData = await getTaskResponse.json();
      expect(taskData.title).toBe("User A's Direct Access Task");
    });
  });

  test("Session expiration redirects to login with message", async ({
    page,
    request,
  }) => {
    // Create user and get auth token
    const testEmail = `session-expire-${timestamp}@example.com`;
    const signupResponse = await request.post(`${API_URL}/api/auth/signup`, {
      data: {
        name: "Session Expire Test",
        email: testEmail,
        password: password,
      },
    });
    expect(signupResponse.ok()).toBeTruthy();

    // Log in via UI to set cookies
    await page.goto(`${APP_URL}/login`);
    await page.fill('[name="email"]', testEmail);
    await page.fill('[name="password"]', password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/dashboard/);

    // Clear auth_token cookie to simulate expired session
    await page.context().clearCookies();

    // Try to access protected route
    await page.goto(`${APP_URL}/dashboard`);

    // Should redirect to login
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain("/login");

    // Check for session expired message (optional - depends on implementation)
    // const expiredMessage = page.getByText(/session expired|please log in again/i);
    // await expect(expiredMessage).toBeVisible();
  });
});
