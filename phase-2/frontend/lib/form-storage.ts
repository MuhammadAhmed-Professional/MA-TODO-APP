/**
 * Form State Storage Utility
 *
 * Provides localStorage-based form state preservation for session expiration scenarios.
 * Saves unsaved form data before redirect and restores it after re-authentication.
 *
 * Features:
 * - Type-safe form data storage and retrieval
 * - Automatic expiration (data cleared after retrieval)
 * - Supports any form structure via generics
 * - Safe handling of localStorage unavailability (SSR, incognito mode)
 *
 * Usage:
 *   // Before redirect (on 401)
 *   saveFormState('task-form', { title: 'My task', description: 'Details' });
 *
 *   // After login
 *   const savedData = restoreFormState<TaskFormData>('task-form');
 *   if (savedData) {
 *     form.reset(savedData); // Restore to react-hook-form
 *   }
 */

const STORAGE_PREFIX = "tda_form_";
const STORAGE_EXPIRY_KEY = "_expiry";

/**
 * Check if localStorage is available
 * Returns false in SSR or when storage is disabled/full
 */
function isStorageAvailable(): boolean {
  if (typeof window === "undefined") return false;

  try {
    const test = "__storage_test__";
    window.localStorage.setItem(test, test);
    window.localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Save form state to localStorage with expiration
 *
 * @param formKey - Unique identifier for the form (e.g., 'task-form', 'profile-form')
 * @param data - Form data object to save
 * @param expiryMinutes - Minutes until data expires (default: 30)
 *
 * @example
 * saveFormState('task-form', { title: 'Buy milk', description: 'From store' });
 */
export function saveFormState<T extends Record<string, unknown>>(
  formKey: string,
  data: T,
  expiryMinutes: number = 30
): void {
  if (!isStorageAvailable()) {
    console.warn("[FormStorage] localStorage not available");
    return;
  }

  try {
    const key = `${STORAGE_PREFIX}${formKey}`;
    const expiryTime = Date.now() + expiryMinutes * 60 * 1000;

    // Save data and expiry time
    window.localStorage.setItem(key, JSON.stringify(data));
    window.localStorage.setItem(
      `${key}${STORAGE_EXPIRY_KEY}`,
      expiryTime.toString()
    );

    console.log(`[FormStorage] Saved form state for '${formKey}'`);
  } catch (error) {
    console.error("[FormStorage] Failed to save form state:", error);
  }
}

/**
 * Restore form state from localStorage and clear it
 *
 * @param formKey - Unique identifier for the form
 * @returns Saved form data or null if not found/expired
 *
 * @example
 * const savedData = restoreFormState<TaskFormData>('task-form');
 * if (savedData) {
 *   form.reset(savedData);
 * }
 */
export function restoreFormState<T extends Record<string, unknown>>(
  formKey: string
): T | null {
  if (!isStorageAvailable()) return null;

  try {
    const key = `${STORAGE_PREFIX}${formKey}`;
    const expiryKey = `${key}${STORAGE_EXPIRY_KEY}`;

    // Check if data exists
    const savedData = window.localStorage.getItem(key);
    const expiryTime = window.localStorage.getItem(expiryKey);

    if (!savedData) return null;

    // Check expiration
    if (expiryTime && Date.now() > parseInt(expiryTime, 10)) {
      console.log(`[FormStorage] Data expired for '${formKey}'`);
      clearFormState(formKey);
      return null;
    }

    // Parse and clear storage
    const data = JSON.parse(savedData) as T;
    clearFormState(formKey);

    console.log(`[FormStorage] Restored form state for '${formKey}'`);
    return data;
  } catch (error) {
    console.error("[FormStorage] Failed to restore form state:", error);
    clearFormState(formKey);
    return null;
  }
}

/**
 * Clear saved form state
 *
 * @param formKey - Unique identifier for the form
 *
 * @example
 * clearFormState('task-form');
 */
export function clearFormState(formKey: string): void {
  if (!isStorageAvailable()) return;

  try {
    const key = `${STORAGE_PREFIX}${formKey}`;
    window.localStorage.removeItem(key);
    window.localStorage.removeItem(`${key}${STORAGE_EXPIRY_KEY}`);
  } catch (error) {
    console.error("[FormStorage] Failed to clear form state:", error);
  }
}

/**
 * Get all saved form keys (for debugging)
 *
 * @returns Array of form keys that have saved data
 */
export function getAllFormKeys(): string[] {
  if (!isStorageAvailable()) return [];

  try {
    const keys: string[] = [];
    for (let i = 0; i < window.localStorage.length; i++) {
      const key = window.localStorage.key(i);
      if (key?.startsWith(STORAGE_PREFIX) && !key.endsWith(STORAGE_EXPIRY_KEY)) {
        keys.push(key.replace(STORAGE_PREFIX, ""));
      }
    }
    return keys;
  } catch {
    return [];
  }
}

/**
 * Clear all saved form states (useful for logout)
 */
export function clearAllFormStates(): void {
  if (!isStorageAvailable()) return;

  try {
    const keys = getAllFormKeys();
    keys.forEach((key) => clearFormState(key));
    console.log(`[FormStorage] Cleared ${keys.length} form states`);
  } catch (error) {
    console.error("[FormStorage] Failed to clear all form states:", error);
  }
}
