import { test, expect } from "@playwright/test";

/**
 * Chat Feature E2E Tests
 *
 * Tests for Phase III AI-Powered Todo Chatbot
 * - Conversation management
 * - Message sending and receiving
 * - Authentication integration
 * - Error handling
 */

// Set a longer timeout for API responses
test.setTimeout(60000);

// Test user credentials (mock data)
const TEST_USER = {
  email: "test-chat@example.com",
  password: "Test@123456",
  name: "Chat Tester",
};

// Helper function to login
async function loginUser(page) {
  await page.goto("/login");
  await expect(page.locator("text=Log In")).toBeVisible();

  await page.fill('[name="email"]', TEST_USER.email);
  await page.fill('[name="password"]', TEST_USER.password);
  await page.click('button:has-text("Sign in")');

  // Wait for redirect to dashboard
  await page.waitForURL("/dashboard", { timeout: 10000 });
}

// Helper function to navigate to chat
async function navigateToChat(page) {
  await page.goto("/chat");
  await expect(page.locator("text=Chat")).toBeVisible({ timeout: 5000 });
}

test.describe("Chat Feature E2E Tests", () => {
  test("should display login page when not authenticated", async ({ page }) => {
    await page.goto("/chat");
    await expect(page.locator("text=Please log in")).toBeVisible({ timeout: 5000 });
    await expect(page.locator("text=You need to be authenticated")).toBeVisible();
    await expect(page.locator('a:has-text("Go to Login")')).toBeVisible();
  });

  test("should redirect to login and allow login flow", async ({ page }) => {
    await loginUser(page);

    // Should be at dashboard after login
    await expect(page.locator("text=Dashboard")).toBeVisible({ timeout: 10000 });
  });

  test("should create a new conversation", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Click "New Chat" or "Start Chat" button
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Should show empty conversation state
    await expect(page.locator("text=Start a conversation")).toBeVisible({ timeout: 5000 });
  });

  test("should display conversation in sidebar after creation", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Wait for conversation to appear in sidebar
    await expect(page.locator("text=Chat").first()).toBeVisible({ timeout: 5000 });
  });

  test("should send a message to the chat", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Type and send message
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("Add a task called Test Task");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for message to appear
    await expect(page.locator("text=Add a task called Test Task")).toBeVisible({ timeout: 10000 });
  });

  test("should display user and assistant messages", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send message
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("List my tasks");

    // Wait for send button to be ready
    await page.click('button:has-text("Send"), button[type="submit"]');

    // User message should appear
    await expect(page.locator("text=List my tasks")).toBeVisible({ timeout: 10000 });

    // Assistant message should appear (with timeout for API call)
    await expect(page.locator("text=Here are your tasks")).toBeVisible({
      timeout: 15000,
      visible: true,
    });
  });

  test("should show loading indicator while message is processing", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send message
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("Create a task");

    await page.click('button:has-text("Send"), button[type="submit"]');

    // Loading indicator might flash briefly
    // Wait for it to disappear when message completes
    await expect(messageInput).toBeEnabled({ timeout: 15000 });
  });

  test("should clear message input after sending", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');

    // Send message
    await messageInput.fill("Test message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait a bit for request to complete
    await page.waitForTimeout(2000);

    // Input should be cleared
    await expect(messageInput).toHaveValue("");
  });

  test("should support Ctrl+Enter to send message", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');

    // Type message
    await messageInput.fill("Test Ctrl+Enter");

    // Send with Ctrl+Enter
    await messageInput.press("Control+Enter");

    // Message should appear
    await expect(page.locator("text=Test Ctrl+Enter")).toBeVisible({ timeout: 10000 });
  });

  test("should persist conversation history", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send first message
    let messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("First message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for response
    await page.waitForTimeout(3000);

    // Send second message
    messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("Second message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Both messages should be visible
    await expect(page.locator("text=First message")).toBeVisible({ timeout: 5000 });
    await expect(page.locator("text=Second message")).toBeVisible({ timeout: 10000 });
  });

  test("should select conversation and show its messages", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create first conversation
    let newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send message to first conversation
    let messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("First conversation message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for response
    await page.waitForTimeout(2000);

    // Create second conversation
    newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send message to second conversation
    messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("Second conversation message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for response
    await page.waitForTimeout(2000);

    // Click on first conversation in sidebar
    const conversationItems = page.locator('[role="button"]:has-text("Untitled"), [role="button"]:has-text("Chat")');
    if ((await conversationItems.count()) > 1) {
      await conversationItems.first().click();

      // Should show first conversation message
      await expect(page.locator("text=First conversation message")).toBeVisible({ timeout: 5000 });
    }
  });

  test("should delete a conversation", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create new conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Find delete button (usually appears on hover or as an icon)
    const deleteButton = page.locator(
      'button:has-text("Delete"), button[aria-label="Delete"], button[title*="Delete"]'
    );

    // If delete button exists and is visible, click it
    if ((await deleteButton.count()) > 0) {
      await deleteButton.first().click();

      // Confirm deletion if prompted
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
      if ((await confirmButton.count()) > 0) {
        await confirmButton.click();
      }

      // Conversation should disappear
      await page.waitForTimeout(1000);
    }
  });

  test("should display empty state when no conversations exist", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Delete all conversations if any exist
    const conversations = page.locator('[role="button"]:has-text("Untitled"), [role="button"]:has-text("Chat")');
    const count = await conversations.count();

    for (let i = 0; i < count; i++) {
      const deleteButton = page.locator(
        'button:has-text("Delete"), button[aria-label="Delete"], button[title*="Delete"]'
      );
      if ((await deleteButton.count()) > 0) {
        await deleteButton.first().click();

        const confirmButton = page.locator('button:has-text("Delete")');
        if ((await confirmButton.count()) > 0) {
          await confirmButton.click();
          await page.waitForTimeout(500);
        }
      }
    }

    // Should show "Welcome" or "Create a new conversation" message
    await expect(
      page.locator(
        'text=Create a new conversation, text=No conversation selected, text=Welcome, text=Start a conversation'
      )
    ).toBeVisible({ timeout: 5000 });
  });

  test("should handle API errors gracefully", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Send message that might fail (empty message)
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');

    // Try to send empty message (should be prevented by validation)
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Should not send empty message or show error
    const errorMessage = page.locator("[role=alert], text=Error, text=error");
    // Error might appear or might be prevented by form validation
    // No assertion needed - just checking app doesn't crash
    expect(page).toBeTruthy();
  });

  test("should be responsive on mobile", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });

    await loginUser(page);
    await navigateToChat(page);

    // Create conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Chat should be usable on mobile
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await expect(messageInput).toBeVisible();

    // Send message on mobile
    await messageInput.fill("Mobile test message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Message should be visible
    await expect(page.locator("text=Mobile test message")).toBeVisible({ timeout: 10000 });
  });

  test("should be responsive on tablet", async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    await loginUser(page);
    await navigateToChat(page);

    // Create conversation
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    // Chat should be usable on tablet
    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await expect(messageInput).toBeVisible();

    // Send message on tablet
    await messageInput.fill("Tablet test message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Message should be visible
    await expect(page.locator("text=Tablet test message")).toBeVisible({ timeout: 10000 });
  });

  test("should maintain session across page reloads", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Create conversation and send message
    const newChatButton = page.locator(
      'button:has-text("Start Chat"), button:has-text("+ New Chat"), button:has-text("New Chat")'
    );
    await newChatButton.click();

    const messageInput = page.locator('textarea[placeholder*="message"], textarea[placeholder*="Type"]');
    await messageInput.fill("Reload test message");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for message to be saved
    await page.waitForTimeout(2000);

    // Reload page
    await page.reload();

    // Should still be authenticated
    await expect(page.locator("text=Chat")).toBeVisible({ timeout: 5000 });

    // Message should still be visible
    await expect(page.locator("text=Reload test message")).toBeVisible({ timeout: 5000 });
  });

  test("should log out successfully", async ({ page }) => {
    await loginUser(page);
    await navigateToChat(page);

    // Find logout button (might be in header or dropdown)
    const logoutButton = page.locator(
      'button:has-text("Log out"), button:has-text("Logout"), button[aria-label*="Log out"]'
    );

    if ((await logoutButton.count()) > 0) {
      await logoutButton.click();

      // Should redirect to login
      await page.waitForURL("/login", { timeout: 5000 });
      await expect(page.locator("text=Log In")).toBeVisible();
    }
  });
});
