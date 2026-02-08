/**
 * Centralized API Client
 *
 * Provides type-safe HTTP methods for backend API calls with automatic
 * authentication header handling and error management.
 *
 * Features:
 * - Automatic auth token inclusion (from HttpOnly cookies)
 * - Type-safe request/response handling
 * - Centralized error handling
 * - Base URL configuration from environment
 * - Toast notifications for 403 Forbidden errors
 *
 * Usage:
 *   import { api } from '@/lib/api';
 *
 *   // GET request
 *   const tasks = await api.get<Task[]>('/api/tasks');
 *
 *   // POST request
 *   const newTask = await api.post<Task>('/api/tasks', {
 *     title: 'New Task',
 *     description: 'Task description'
 *   });
 */

import { toast } from "sonner";
import { saveFormState } from "./form-storage";

// Base API URL from environment variable
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API Error class for typed error handling
 */
export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Request options interface
 */
interface RequestOptions extends RequestInit {
  headers?: HeadersInit;
}

/**
 * Capture unsaved form data from the page before session expiration redirect
 *
 * Scans for common form elements and saves their current values to localStorage.
 * Supports task forms, profile forms, and other input fields.
 */
function captureFormData(): void {
  try {
    // Find all forms on the page
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
      const formData: Record<string, unknown> = {};
      let hasData = false;

      // Get all input, textarea, and select elements
      const inputs = form.querySelectorAll<
        HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
      >("input, textarea, select");

      inputs.forEach((input) => {
        // Skip empty values, buttons, and submit inputs
        if (
          !input.value ||
          input.type === "submit" ||
          input.type === "button" ||
          input.type === "password" // Never save passwords
        ) {
          return;
        }

        // Save the value
        const name = input.name || input.id;
        if (name) {
          formData[name] = input.value;
          hasData = true;
        }
      });

      // Save if form has data
      if (hasData) {
        // Try to determine form key from form attributes or first input name
        const formKey =
          form.getAttribute("data-form-key") ||
          form.id ||
          Object.keys(formData)[0]?.split(/[_-]/)[0] ||
          "default";

        saveFormState(formKey, formData);
        console.log(`[API] Captured form data for '${formKey}' before session expiration`);
      }
    });
  } catch (error) {
    console.error("[API] Failed to capture form data:", error);
  }
}

/**
 * Generic fetch wrapper with error handling
 */
async function fetchJSON<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "include", // Include HttpOnly cookies for authentication
  };

  try {
    const response = await fetch(url, config);

    // Parse response body (may be empty for 204 No Content)
    let data: unknown;
    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    // Handle error responses
    if (!response.ok) {
      const errorMessage =
        typeof data === "object" && data !== null && "detail" in data
          ? String(data.detail)
          : "Request failed";

      // Handle 403 Forbidden - authenticated but not authorized
      if (response.status === 403) {
        // Show user-friendly error toast
        if (typeof window !== "undefined") {
          toast.error("Access Denied", {
            description:
              errorMessage ||
              "You don't have permission to access this resource.",
            duration: 5000,
          });

          // Redirect to dashboard after a brief delay (user is authenticated, just not authorized)
          setTimeout(() => {
            window.location.href = "/dashboard";
          }, 1500);
        }

        throw new APIError(
          response.status,
          response.statusText,
          errorMessage,
          data
        );
      }

      // Handle 401 Unauthorized - need to re-authenticate
      if (response.status === 401) {
        if (typeof window !== "undefined") {
          // Save any unsaved form data before redirecting
          captureFormData();

          // Redirect to login with session_expired flag
          window.location.href = "/login?session_expired=true";
        }

        throw new APIError(
          response.status,
          response.statusText,
          "Your session has expired. Please log in again.",
          data
        );
      }

      throw new APIError(
        response.status,
        response.statusText,
        errorMessage,
        data
      );
    }

    return data as T;
  } catch (error) {
    // Re-throw APIError as-is
    if (error instanceof APIError) {
      throw error;
    }

    // Network errors or other fetch failures
    throw new APIError(
      0,
      "Network Error",
      error instanceof Error ? error.message : "Unknown error occurred"
    );
  }
}

/**
 * API client with typed methods
 */
const apiMethods = {
  /**
   * GET request
   *
   * @param endpoint - API endpoint (e.g., '/api/tasks')
   * @param options - Additional fetch options
   * @returns Promise with typed response data
   *
   * @example
   * const tasks = await api.get<Task[]>('/api/tasks');
   */
  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return fetchJSON<T>(endpoint, {
      ...options,
      method: "GET",
    });
  },

  /**
   * POST request
   *
   * @param endpoint - API endpoint
   * @param data - Request body data
   * @param options - Additional fetch options
   * @returns Promise with typed response data
   *
   * @example
   * const newTask = await api.post<Task>('/api/tasks', {
   *   title: 'New Task',
   *   description: 'Description'
   * });
   */
  async post<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return fetchJSON<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PUT request (full update)
   *
   * @param endpoint - API endpoint
   * @param data - Request body data
   * @param options - Additional fetch options
   * @returns Promise with typed response data
   *
   * @example
   * const updatedTask = await api.put<Task>('/api/tasks/123', {
   *   title: 'Updated Title',
   *   description: 'Updated Description'
   * });
   */
  async put<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return fetchJSON<T>(endpoint, {
      ...options,
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * PATCH request (partial update)
   *
   * @param endpoint - API endpoint
   * @param data - Request body data (partial)
   * @param options - Additional fetch options
   * @returns Promise with typed response data
   *
   * @example
   * const task = await api.patch<Task>('/api/tasks/123/complete', {
   *   is_complete: true
   * });
   */
  async patch<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return fetchJSON<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  /**
   * DELETE request
   *
   * @param endpoint - API endpoint
   * @param options - Additional fetch options
   * @returns Promise (typically void for 204 responses)
   *
   * @example
   * await api.delete('/api/tasks/123');
   */
  async delete<T = void>(
    endpoint: string,
    options?: RequestOptions
  ): Promise<T> {
    return fetchJSON<T>(endpoint, {
      ...options,
      method: "DELETE",
    });
  },

  /**
   * Health check helper
   *
   * @returns Promise with health status
   *
   * @example
   * const health = await api.healthCheck();
   * console.log(health.database); // "connected" or "disconnected"
   */
  async healthCheck(): Promise<{
    status: string;
    database: string;
    version: string;
  }> {
    return this.get("/api/health");
  },
};

export const api = apiMethods;
