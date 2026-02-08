/**
 * Better Auth Client Configuration
 *
 * Configures the Better Auth client for frontend authentication
 * with JWT token management and cross-domain support.
 *
 * @see frontend/CLAUDE.md for authentication patterns
 */

import { createAuthClient } from "better-auth/react";
import { setAuthToken as storeToken, clearAuthToken } from "./token-storage";
import { fetchWithRetry } from "./api";

/**
 * Better Auth client instance
 *
 * Configuration:
 * - baseURL: Points to FastAPI backend (which proxies to Better Auth server)
 * - credentials: Include cookies in cross-origin requests
 *
 * ARCHITECTURE FLOW:
 * Frontend → FastAPI Backend (/api/auth/*) → Better Auth Server
 *
 * The FastAPI backend acts as a proxy to the Better Auth server:
 * - POST /api/auth/sign-up/email → Better Auth POST /api/auth/sign-up
 * - POST /api/auth/sign-in/email → Better Auth POST /api/auth/sign-in/email
 * - POST /api/auth/sign-out → Clears auth_token cookie
 * - GET /api/auth/get-session → Better Auth GET /api/auth/get-session
 */
// CRITICAL: Must use BACKEND URL (not auth server URL) so cookies are set on backend domain
const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://tda-backend-production.up.railway.app";

// Debug logging to verify the URL being used
if (typeof window !== "undefined") {
  console.log("🔍 AUTH CLIENT DEBUG:");
  console.log("  process.env.NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
  console.log("  BACKEND_URL:", BACKEND_URL);
}

// Local development: set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local

export const authClient = createAuthClient({
  // CRITICAL: Use BACKEND URL (not auth server) so auth_token cookie is set on backend domain
  baseURL: BACKEND_URL,

  // Include credentials (cookies) in requests
  fetchOptions: {
    credentials: "include", // Required for HttpOnly cookies
  },
});

/**
 * Auth helper functions for common operations
 */

/**
 * Sign up a new user
 * @param name - User's full name
 * @param email - User's email address
 * @param password - User's password (min 8 characters)
 */
export async function signUp(data: {
  name: string;
  email: string;
  password: string;
}) {
  // Use fetchWithRetry to handle Railway cold starts (502 errors)
  const response = await fetchWithRetry(
    `${BACKEND_URL}/api/auth/sign-up/email`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        name: data.name,
        email: data.email,
        password: data.password,
      }),
    },
    3, // Max 3 retries
    2000 // Start with 2 second delay
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Signup failed" }));
    return { error: { message: error.message || error.error || "Failed to create account" } };
  }

  const responseData = await response.json();
  console.log("🔐 SIGNUP RESPONSE:", JSON.stringify(responseData, null, 2));

  // Extract and store token if present
  if (responseData.token) {
    storeToken(responseData.token);
    console.log("✅ Token stored successfully after signup");
  }

  return { data: responseData, error: null };
}

/**
 * Sign in an existing user
 * @param email - User's email address
 * @param password - User's password
 */
export async function signIn(data: { email: string; password: string }) {
  // Use fetchWithRetry to handle Railway cold starts (502 errors)
  const response = await fetchWithRetry(
    `${BACKEND_URL}/api/auth/sign-in/email`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        email: data.email,
        password: data.password,
      }),
    },
    3, // Max 3 retries
    2000 // Start with 2 second delay (Railway can take a few seconds to wake)
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Login failed" }));
    return { error: { message: error.message || error.error || "Invalid email or password" } };
  }

  const responseData = await response.json();
  console.log("🔐 SIGNIN RESPONSE:", JSON.stringify(responseData, null, 2));

  // Extract token from response
  // Better Auth returns: { token: "...", user: {...}, redirect: false }
  if (responseData.token) {
    const token = responseData.token;
    console.log("✅ Token found:", token.substring(0, 20) + "...");
    storeToken(token);
    console.log("✅ Token stored successfully");
  } else {
    console.error("❌ No token in response! Structure:", Object.keys(responseData));
  }

  return { data: responseData, error: null };
}

/**
 * Sign out the current user
 * Clears auth tokens and redirects to login page
 */
export async function signOut() {
  // Clear stored token
  clearAuthToken();

  // Also call Better Auth signOut to clear cookies
  return authClient.signOut();
}

/**
 * Get the current authenticated user
 * Returns null if not authenticated
 */
export async function getCurrentUser() {
  return authClient.getSession();
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getCurrentUser();
  const sessionData = (session as any)?.data;
  return !!sessionData?.user;
}

/**
 * Type exports for TypeScript support
 *
 * Note: User type is defined in @/types/user.ts
 */
export type Session = Awaited<ReturnType<typeof getCurrentUser>>;
