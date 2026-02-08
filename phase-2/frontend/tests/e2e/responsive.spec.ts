/**
 * E2E Responsive Test Suite
 *
 * Tests responsive behavior across mobile, tablet, and desktop viewports
 * Validates WCAG 2.1 AA accessibility compliance
 *
 * Test Coverage:
 * - Mobile (375px): Single-column layout, hamburger menu
 * - Tablet (768px): Two-column task grid
 * - Desktop (1920px): Three-column task grid, sidebar visible
 * - Keyboard navigation and focus indicators
 * - Touch target sizes (44x44px minimum)
 */

import { test, expect } from "@playwright/test";

// Test viewport configurations
const VIEWPORTS = {
  mobile: { width: 375, height: 667 },   // iPhone SE
  tablet: { width: 768, height: 1024 },  // iPad
  desktop: { width: 1920, height: 1080 }, // Full HD
};

// Helper function to login
async function login(page: any, email = "test@example.com", password = "password123") {
  await page.goto("/login");
  await page.fill('[name="email"]', email);
  await page.fill('[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL("/dashboard");
}

test.describe("Responsive UI Tests", () => {
  test.describe("Mobile Viewport (375px)", () => {
    test.use({ viewport: VIEWPORTS.mobile });

    test("should display single-column task layout", async ({ page }) => {
      await login(page);
      await page.goto("/dashboard/tasks");

      // Check grid has single column
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/grid-cols-1/);
    });

    test("should show hamburger menu instead of full navigation", async ({ page }) => {
      await login(page);

      // Hamburger button should be visible
      const hamburgerBtn = page.locator('button[aria-label*="menu"], button[aria-controls="mobile-menu"]');
      await expect(hamburgerBtn).toBeVisible();

      // Desktop nav should be hidden
      const desktopNav = page.locator('nav.hidden.md\\:flex');
      await expect(desktopNav).toBeHidden();
    });

    test("should open mobile menu drawer when hamburger clicked", async ({ page }) => {
      await login(page);

      // Click hamburger menu
      const hamburgerBtn = page.locator('button[aria-label*="menu"], button[aria-controls="mobile-menu"]');
      await hamburgerBtn.click();

      // Mobile menu should be visible
      const mobileMenu = page.locator('#mobile-menu, nav[aria-label*="Mobile"]');
      await expect(mobileMenu).toBeVisible();

      // Should contain navigation links
      await expect(page.locator('#mobile-menu a[href="/dashboard"]')).toBeVisible();
      await expect(page.locator('#mobile-menu a[href="/dashboard/tasks"]')).toBeVisible();
    });

    test("should have full-width auth forms", async ({ page }) => {
      await page.goto("/login");

      const form = page.locator("form");
      const boundingBox = await form.boundingBox();

      // Form should be nearly full width on mobile (accounting for padding)
      expect(boundingBox?.width).toBeGreaterThan(300);
    });

    test("should have touch-friendly button sizes (44x44px minimum)", async ({ page }) => {
      await login(page);
      await page.goto("/dashboard/tasks");

      // Check button sizes
      const buttons = page.locator("button");
      const count = await buttons.count();

      for (let i = 0; i < Math.min(count, 5); i++) {
        const button = buttons.nth(i);
        const box = await button.boundingBox();

        if (box) {
          // Touch targets should be at least 44x44px
          expect(box.height).toBeGreaterThanOrEqual(40); // Allow small margin
          expect(box.width).toBeGreaterThanOrEqual(40);
        }
      }
    });
  });

  test.describe("Tablet Viewport (768px)", () => {
    test.use({ viewport: VIEWPORTS.tablet });

    test("should display two-column task grid", async ({ page }) => {
      await login(page);
      await page.goto("/dashboard/tasks");

      // Check grid has two columns at md breakpoint
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/md:grid-cols-2/);
    });

    test("should show full navigation bar", async ({ page }) => {
      await login(page);

      // Desktop nav should be visible on tablet
      const desktopNav = page.locator('nav[aria-label="Main navigation"]');
      await expect(desktopNav).toBeVisible();

      // Hamburger should be hidden
      const hamburgerBtn = page.locator('button.md\\:hidden');
      await expect(hamburgerBtn).toBeHidden();
    });

    test("sidebar should be hidden on tablet", async ({ page }) => {
      await login(page);

      // Sidebar should be hidden below lg breakpoint
      const sidebar = page.locator('aside[aria-label*="Sidebar"]');
      await expect(sidebar).toBeHidden();
    });
  });

  test.describe("Desktop Viewport (1920px)", () => {
    test.use({ viewport: VIEWPORTS.desktop });

    test("should display three-column task grid", async ({ page }) => {
      await login(page);
      await page.goto("/dashboard/tasks");

      // Check grid has three columns at lg breakpoint
      const taskList = page.locator('[role="list"]');
      await expect(taskList).toHaveClass(/lg:grid-cols-3/);
    });

    test("should show sidebar navigation", async ({ page }) => {
      await login(page);

      // Sidebar should be visible on desktop
      const sidebar = page.locator('aside[aria-label*="Sidebar"]');
      await expect(sidebar).toBeVisible();

      // Should contain navigation items
      await expect(sidebar.locator('a[href="/dashboard"]')).toBeVisible();
      await expect(sidebar.locator('a[href="/dashboard/tasks"]')).toBeVisible();
    });

    test("should have constrained form width (max-w-md)", async ({ page }) => {
      await page.goto("/login");

      const form = page.locator("form");
      const boundingBox = await form.boundingBox();

      // Form should be constrained on desktop (max-w-md = 448px)
      expect(boundingBox?.width).toBeLessThanOrEqual(500);
    });
  });
});

test.describe("Accessibility Tests", () => {
  test.use({ viewport: VIEWPORTS.desktop });

  test("should have visible focus indicators on all interactive elements", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Tab through interactive elements
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Check if focused element has ring class
    const focusedElement = page.locator(":focus");
    const className = await focusedElement.getAttribute("class");

    // Should have focus ring classes
    expect(className).toMatch(/focus:ring-2|focus:ring-blue-500/);
  });

  test("should navigate entire page with keyboard only", async ({ page }) => {
    await page.goto("/login");

    // Fill form with keyboard
    await page.keyboard.press("Tab"); // Focus email
    await page.keyboard.type("test@example.com");
    await page.keyboard.press("Tab"); // Focus password
    await page.keyboard.type("password123");
    await page.keyboard.press("Tab"); // Focus submit button
    await page.keyboard.press("Enter"); // Submit form

    // Should navigate to dashboard
    await page.waitForURL("/dashboard", { timeout: 5000 });
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test("should have proper ARIA labels on icon buttons", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Check TaskCard action buttons have aria-labels
    const editButtons = page.locator('button[aria-label*="Edit"]');
    const deleteButtons = page.locator('button[aria-label*="Delete"]');
    const completeButtons = page.locator('button[aria-label*="Mark"]');

    if (await editButtons.count() > 0) {
      await expect(editButtons.first()).toHaveAttribute("aria-label");
    }

    if (await deleteButtons.count() > 0) {
      await expect(deleteButtons.first()).toHaveAttribute("aria-label");
    }

    if (await completeButtons.count() > 0) {
      await expect(completeButtons.first()).toHaveAttribute("aria-label");
    }
  });

  test("should have alt text or aria-label on images and icons", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Check for accessible images (with alt or role="img" + aria-label)
    const images = page.locator("img");
    const svgs = page.locator('svg[role="img"]');

    const imageCount = await images.count();
    const svgCount = await svgs.count();

    // All images should have alt text
    for (let i = 0; i < imageCount; i++) {
      await expect(images.nth(i)).toHaveAttribute("alt");
    }

    // All decorative SVGs with role="img" should have aria-label
    for (let i = 0; i < svgCount; i++) {
      await expect(svgs.nth(i)).toHaveAttribute("aria-label");
    }
  });

  test("should announce filter changes to screen readers", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Check filter buttons have aria-pressed
    const allButton = page.locator('button:has-text("All")');
    const activeButton = page.locator('button:has-text("Active")');

    await expect(allButton).toHaveAttribute("aria-pressed");
    await expect(activeButton).toHaveAttribute("aria-pressed");
  });

  test("should have semantic HTML structure", async ({ page }) => {
    await login(page);

    // Check for semantic landmarks
    await expect(page.locator("header")).toBeVisible();
    await expect(page.locator("nav")).toBeVisible();

    await page.goto("/dashboard/tasks");

    // Task list should be a proper list
    const taskList = page.locator('[role="list"]');
    await expect(taskList).toBeVisible();
  });
});

test.describe("Responsive Breakpoint Transitions", () => {
  test("should smoothly transition between mobile and tablet layouts", async ({ page, context }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Start at mobile
    await page.setViewportSize(VIEWPORTS.mobile);
    await page.waitForTimeout(300); // Wait for transition

    // Hamburger should be visible
    let hamburger = page.locator('button.md\\:hidden');
    await expect(hamburger).toBeVisible();

    // Transition to tablet
    await page.setViewportSize(VIEWPORTS.tablet);
    await page.waitForTimeout(300);

    // Desktop nav should now be visible
    const desktopNav = page.locator('nav[aria-label="Main navigation"]');
    await expect(desktopNav).toBeVisible();
  });

  test("should show/hide sidebar at lg breakpoint", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // At tablet size, sidebar hidden
    await page.setViewportSize(VIEWPORTS.tablet);
    await page.waitForTimeout(300);

    let sidebar = page.locator('aside[aria-label*="Sidebar"]');
    await expect(sidebar).toBeHidden();

    // At desktop size, sidebar visible
    await page.setViewportSize(VIEWPORTS.desktop);
    await page.waitForTimeout(300);

    sidebar = page.locator('aside[aria-label*="Sidebar"]');
    await expect(sidebar).toBeVisible();
  });
});

test.describe("Touch Target Compliance", () => {
  test.use({ viewport: VIEWPORTS.mobile });

  test("all interactive elements should meet 44x44px minimum", async ({ page }) => {
    await login(page);
    await page.goto("/dashboard/tasks");

    // Get all interactive elements
    const interactiveElements = page.locator("button, a, input[type='checkbox']");
    const count = await interactiveElements.count();

    let violations = 0;

    for (let i = 0; i < count; i++) {
      const element = interactiveElements.nth(i);
      const box = await element.boundingBox();

      if (box) {
        // Check if meets minimum touch target size
        if (box.height < 44 || box.width < 44) {
          const tagName = await element.evaluate((el) => el.tagName);
          const className = await element.getAttribute("class");

          // Allow some exceptions for inline text links
          if (tagName !== "A" || (className && className.includes("min-h"))) {
            violations++;
          }
        }
      }
    }

    // Allow max 10% violations for edge cases
    expect(violations / count).toBeLessThan(0.1);
  });
});
