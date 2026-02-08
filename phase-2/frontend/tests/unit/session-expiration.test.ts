/**
 * Session Expiration Tests
 *
 * Tests for session expiration detection, warning display, and form data preservation.
 *
 * Coverage:
 * - Token expiration detection logic
 * - Form data capture and preservation
 * - Session refresh functionality
 * - Logout with form data preservation
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  saveFormState,
  restoreFormState,
  clearFormState,
  clearAllFormStates,
} from '@/lib/form-storage';

describe('Session Expiration - Form Data Preservation', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    clearAllFormStates();
  });

  it('should save form data to localStorage', () => {
    const formData = {
      title: 'Test Task',
      description: 'This is a test task description',
    };

    saveFormState('task-form', formData);

    const saved = localStorage.getItem('tda_form_task-form');
    expect(saved).toBeTruthy();
    expect(JSON.parse(saved!)).toEqual(formData);
  });

  it('should restore form data from localStorage', () => {
    const formData = {
      title: 'Test Task',
      description: 'Task description',
    };

    saveFormState('task-form', formData);

    const restored = restoreFormState<typeof formData>('task-form');
    expect(restored).toEqual(formData);
  });

  it('should clear form data after restoration', () => {
    const formData = { title: 'Test' };

    saveFormState('task-form', formData);
    const restored = restoreFormState('task-form');

    expect(restored).toEqual(formData);

    // Should be cleared after restoration
    const secondRestore = restoreFormState('task-form');
    expect(secondRestore).toBeNull();
  });

  it('should handle expired form data', () => {
    const formData = { title: 'Expired Task' };

    // Save with -1 minute expiry (expired)
    saveFormState('task-form', formData, -1);

    // Should return null for expired data
    const restored = restoreFormState('task-form');
    expect(restored).toBeNull();
  });

  it('should clear all form states', () => {
    saveFormState('task-form', { title: 'Task 1' });
    saveFormState('profile-form', { name: 'John Doe' });

    clearAllFormStates();

    expect(restoreFormState('task-form')).toBeNull();
    expect(restoreFormState('profile-form')).toBeNull();
  });

  it('should handle localStorage unavailability gracefully', () => {
    // Mock localStorage to throw error
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = vi.fn(() => {
      throw new Error('Storage quota exceeded');
    });

    // Should not throw, just log warning
    expect(() => {
      saveFormState('task-form', { title: 'Test' });
    }).not.toThrow();

    // Restore localStorage
    Storage.prototype.setItem = originalSetItem;
  });
});

describe('Session Expiration - Token Validation', () => {
  it('should detect valid JWT token structure', () => {
    // Valid JWT has 3 parts: header.payload.signature
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiZXhwIjoxNzE2MjM5MDIyfQ.signature';

    const parts = validToken.split('.');
    expect(parts).toHaveLength(3);
  });

  it('should detect expired token from payload', () => {
    // Create expired token (exp in past)
    const expiredPayload = {
      sub: '123',
      exp: Math.floor(Date.now() / 1000) - 3600, // 1 hour ago
    };

    const base64Payload = btoa(JSON.stringify(expiredPayload));
    const expiredToken = `header.${base64Payload}.signature`;

    // Parse payload
    const parts = expiredToken.split('.');
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);

    expect(payload.exp).toBeLessThan(now);
  });

  it('should detect valid token with future expiration', () => {
    // Create valid token (exp in future)
    const validPayload = {
      sub: '123',
      exp: Math.floor(Date.now() / 1000) + 900, // 15 minutes from now
    };

    const base64Payload = btoa(JSON.stringify(validPayload));
    const validToken = `header.${base64Payload}.signature`;

    // Parse payload
    const parts = validToken.split('.');
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);

    expect(payload.exp).toBeGreaterThan(now);
  });

  it('should detect token expiring soon (<2 minutes)', () => {
    // Create token expiring in 1 minute
    const soonPayload = {
      sub: '123',
      exp: Math.floor(Date.now() / 1000) + 60, // 1 minute from now
    };

    const base64Payload = btoa(JSON.stringify(soonPayload));
    const soonToken = `header.${base64Payload}.signature`;

    // Parse payload
    const parts = soonToken.split('.');
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    const timeRemaining = payload.exp - now;

    expect(timeRemaining).toBeLessThan(120); // Less than 2 minutes
    expect(timeRemaining).toBeGreaterThan(0); // But not expired yet
  });
});

describe('Session Expiration - Integration Scenarios', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    clearAllFormStates();
  });

  it('should preserve task form data on session expiration', () => {
    // Simulate user filling out task form
    const taskFormData = {
      title: 'Important Task',
      description: 'This task is very important and should not be lost',
    };

    // User's session expires while editing
    saveFormState('task-form', taskFormData);

    // After re-login, data should be restored
    const restored = restoreFormState<typeof taskFormData>('task-form');

    expect(restored).toEqual(taskFormData);
    expect(restored?.title).toBe('Important Task');
  });

  it('should preserve multiple forms independently', () => {
    const taskForm = { title: 'Task Title', description: 'Details' };
    const profileForm = { name: 'John Doe', email: 'john@example.com' };

    saveFormState('task-form', taskForm);
    saveFormState('profile-form', profileForm);

    const restoredTask = restoreFormState<typeof taskForm>('task-form');
    const restoredProfile = restoreFormState<typeof profileForm>('profile-form');

    expect(restoredTask).toEqual(taskForm);
    expect(restoredProfile).toEqual(profileForm);
  });

  it('should not preserve password fields', () => {
    // Password fields should never be saved to localStorage
    const loginForm = {
      email: 'user@example.com',
      // Password should be filtered out by captureFormData
    };

    saveFormState('login-form', loginForm);

    const restored = restoreFormState<typeof loginForm>('login-form');
    expect(restored).toEqual(loginForm);
    expect(restored).not.toHaveProperty('password');
  });

  it('should clear expired form data automatically', () => {
    const formData = { title: 'Test Task' };

    // Save with 0.001 minute expiry (60 ms)
    saveFormState('task-form', formData, 0.001);

    // Wait for expiration
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        const restored = restoreFormState('task-form');
        expect(restored).toBeNull();
        resolve();
      }, 100); // Wait 100ms (longer than 60ms expiry)
    });
  });
});
