/**
 * JWT Token Storage Utility
 *
 * Provides persistent token storage for cross-domain authentication.
 * Uses localStorage for persistence across browser sessions.
 */

let authToken: string | null = null;

/**
 * Store JWT token in localStorage
 * @param token - JWT token from login response
 */
export function setAuthToken(token: string): void {
  authToken = token;

  // Store in localStorage for persistence across sessions
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);
  }
}

/**
 * Get current JWT token
 * @returns JWT token or null if not authenticated
 */
export function getAuthToken(): string | null {
  // Try memory first
  if (authToken) {
    return authToken;
  }

  // Fallback to localStorage
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth_token");
    if (token) {
      authToken = token; // Restore to memory
      return token;
    }
  }

  return null;
}

/**
 * Clear JWT token (logout)
 */
export function clearAuthToken(): void {
  authToken = null;

  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
  }
}

/**
 * Check if user has valid token
 */
export function hasAuthToken(): boolean {
  return getAuthToken() !== null;
}
