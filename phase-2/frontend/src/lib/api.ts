/**
 * API Client for Backend Requests
 *
 * Centralized fetch wrapper with authentication and error handling.
 * Uses JWT tokens in Authorization header for cross-domain authentication.
 *
 * @see frontend/CLAUDE.md for API integration patterns
 *
 * CACHE BUST: v5.0 - ADD PRIORITY, TAGS, SEARCH, FILTER, SORT
 * Last updated: 2025-01-31 02:40 UTC
 */

import { getAuthToken } from "./token-storage";

// ==============================================================================
// Retry Logic for Railway Cold Start
// ==============================================================================

/**
 * Fetch with automatic retry for Railway cold starts
 * Retries on 502/503 errors which indicate server is waking up
 */
export async function fetchWithRetry(
  url: string,
  options?: RequestInit,
  maxRetries = 3,
  baseDelay = 1000
): Promise<Response> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);

      // If server is waking up (502/503), retry
      if (response.status === 502 || response.status === 503) {
        if (attempt < maxRetries - 1) {
          const delay = baseDelay * Math.pow(2, attempt); // Exponential backoff
          console.log(`⏳ Server waking up... retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
          await new Promise((resolve) => setTimeout(resolve, delay));
          continue;
        }
      }

      return response;
    } catch (error) {
      lastError = error as Error;
      // Network error - retry
      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(`⏳ Network error, retrying in ${delay}ms (attempt ${attempt + 1}/${maxRetries})`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        continue;
      }
    }
  }

  throw lastError || new Error("Request failed after retries");
}

// Use environment variable from Vercel, fallback to production URL
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "https://tda-backend-production.up.railway.app";

// Debug logging to verify the URL being used
if (typeof window !== "undefined") {
  console.log("🔍 API CLIENT DEBUG:");
  console.log("  process.env.NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
  console.log("  API_BASE_URL:", API_BASE_URL);
}

// Local development: set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Centralized fetch wrapper with authentication
 *
 * Features:
 * - Automatic cookie inclusion (auth_token)
 * - JSON request/response handling
 * - Error parsing and type-safe errors
 * - Automatic redirect on 401 (session expired)
 *
 * @param endpoint - API endpoint path (e.g., "/api/tasks")
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Parsed JSON response
 * @throws APIError on HTTP error status
 */
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get JWT token from storage
  const token = getAuthToken();

  // Build headers with Authorization if token exists
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Merge with provided headers
  if (options?.headers) {
    Object.assign(headers, options.headers);
  }

  try {
    const response = await fetch(url, {
      ...options,
      credentials: "include", // Still include cookies as fallback
      headers,
    });

    // Handle 401 Unauthorized (session expired)
    if (response.status === 401) {
      // Redirect to login page
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new APIError("Session expired. Please log in again.", 401);
    }

    // Handle other HTTP errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: "Unknown error occurred",
      }));
      throw new APIError(
        error.detail || `Request failed: ${response.statusText}`,
        response.status,
        error
      );
    }

    // Handle 204 No Content (e.g., DELETE requests)
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse and return JSON response
    return response.json();
  } catch (error) {
    // Re-throw APIError as-is
    if (error instanceof APIError) {
      throw error;
    }

    // Wrap network errors
    if (error instanceof Error) {
      throw new APIError(
        `Network error: ${error.message}`,
        0,
        error
      );
    }

    // Unknown error
    throw new APIError("An unexpected error occurred", 0, error);
  }
}

// ==============================================================================
// Type Definitions
// ==============================================================================

/**
 * Priority levels (matches backend Priority enum)
 */
export type Priority = 1 | 2 | 3; // low | medium | high

/**
 * Tag model (matches backend TagResponse)
 */
export interface Tag {
  id: string; // UUID
  name: string; // Lowercase, unique per user
  color: string; // Hex color code (e.g., "#3b82f6")
  user_id: string; // UUID
}

/**
 * Task model (matches backend TaskResponse)
 */
export interface Task {
  id: string; // UUID
  title: string;
  description: string | null;
  is_complete: boolean;
  priority: Priority;
  due_date: string | null; // ISO 8601
  user_id: string; // UUID
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  tags: Tag[]; // Associated tags
}

/**
 * Task creation input
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: Priority;
  due_date?: string | null; // ISO 8601
  tag_ids?: string[]; // Array of tag UUIDs
}

/**
 * Task update input (all fields optional)
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  is_complete?: boolean;
  priority?: Priority;
  due_date?: string | null;
}

/**
 * Task list query parameters
 */
export interface TaskListParams {
  is_complete?: boolean; // Filter by completion status
  priority?: Priority; // Filter by priority
  tags?: string; // Comma-separated tag IDs
  search?: string; // Search query for title/description
  due_date_before?: string; // ISO 8601 datetime
  due_date_after?: string; // ISO 8601 datetime
  sort_by?: "created_at" | "due_date" | "priority" | "title" | "updated_at";
  sort_order?: "asc" | "desc";
  limit?: number; // Max tasks to return (1-100)
  offset?: number; // Skip first N tasks
}

/**
 * Task list response
 */
export interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Tag creation input
 */
export interface TagCreate {
  name: string;
  color?: string;
}

/**
 * Tag update input (all fields optional)
 */
export interface TagUpdate {
  name?: string;
  color?: string;
}

// ==============================================================================
// Tag API Functions
// ==============================================================================

/**
 * Get all tags for authenticated user
 */
export async function getTags(): Promise<Tag[]> {
  return fetchAPI<Tag[]>("/api/tags");
}

/**
 * Get a single tag by ID
 */
export async function getTag(tagId: string): Promise<Tag> {
  return fetchAPI<Tag>(`/api/tags/${tagId}`);
}

/**
 * Create a new tag
 */
export async function createTag(data: TagCreate): Promise<Tag> {
  return fetchAPI<Tag>("/api/tags", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update a tag
 */
export async function updateTag(tagId: string, data: TagUpdate): Promise<Tag> {
  return fetchAPI<Tag>(`/api/tags/${tagId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a tag
 */
export async function deleteTag(tagId: string): Promise<void> {
  return fetchAPI<void>(`/api/tags/${tagId}`, {
    method: "DELETE",
  });
}

// ==============================================================================
// Task-Tag Association Functions
// ==============================================================================

/**
 * Add a tag to a task
 */
export async function addTagToTask(taskId: string, tagId: string): Promise<Task> {
  return fetchAPI<Task>(`/api/tags/tasks/${taskId}/tags/${tagId}`, {
    method: "POST",
  });
}

/**
 * Remove a tag from a task
 */
export async function removeTagFromTask(taskId: string, tagId: string): Promise<Task> {
  return fetchAPI<Task>(`/api/tags/tasks/${taskId}/tags/${tagId}`, {
    method: "DELETE",
  });
}

/**
 * Replace all tags on a task
 */
export async function setTaskTags(taskId: string, tagIds: string[]): Promise<Task> {
  return fetchAPI<Task>(`/api/tags/tasks/${taskId}/tags`, {
    method: "PUT",
    body: JSON.stringify({ tag_ids: tagIds }),
  });
}

// ==============================================================================
// Task API Functions
// ==============================================================================

/**
 * Get all tasks for authenticated user
 *
 * @param params - Optional filter, search, sort, and pagination params
 * @returns List of tasks with pagination metadata
 * @throws APIError on failure
 *
 * @example
 * ```typescript
 * // Get all tasks
 * const tasks = await getTasks();
 *
 * // Get incomplete high-priority tasks
 * const tasks = await getTasks({
 *   is_complete: false,
 *   priority: 3,
 *   sort_by: "priority",
 *   sort_order: "desc"
 * });
 *
 * // Search for tasks with "urgent"
 * const tasks = await getTasks({ search: "urgent" });
 *
 * // Filter by tags and due date
 * const tasks = await getTasks({
 *   tags: "tag_id1,tag_id2",
 *   due_date_after: "2025-12-01T00:00:00Z"
 * });
 * ```
 */
export async function getTasks(
  params?: TaskListParams
): Promise<Task[]> {
  const searchParams = new URLSearchParams();

  if (params?.is_complete !== undefined) {
    searchParams.set("is_complete", String(params.is_complete));
  }
  if (params?.priority !== undefined) {
    searchParams.set("priority", String(params.priority));
  }
  if (params?.tags !== undefined) {
    searchParams.set("tags", params.tags);
  }
  if (params?.search !== undefined) {
    searchParams.set("search", params.search);
  }
  if (params?.due_date_before !== undefined) {
    searchParams.set("due_date_before", params.due_date_before);
  }
  if (params?.due_date_after !== undefined) {
    searchParams.set("due_date_after", params.due_date_after);
  }
  if (params?.sort_by !== undefined) {
    searchParams.set("sort_by", params.sort_by);
  }
  if (params?.sort_order !== undefined) {
    searchParams.set("sort_order", params.sort_order);
  }
  if (params?.limit !== undefined) {
    searchParams.set("limit", String(params.limit));
  }
  if (params?.offset !== undefined) {
    searchParams.set("offset", String(params.offset));
  }

  const query = searchParams.toString();
  return fetchAPI<Task[]>(`/api/tasks${query ? `?${query}` : ""}`);
}

/**
 * Get a single task by ID
 */
export async function getTask(taskId: string): Promise<Task> {
  return fetchAPI<Task>(`/api/tasks/${taskId}`);
}

/**
 * Create a new task
 */
export async function createTask(data: TaskCreate): Promise<Task> {
  return fetchAPI<Task>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing task
 */
export async function updateTask(
  taskId: string,
  data: TaskUpdate
): Promise<Task> {
  return fetchAPI<Task>(`/api/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

/**
 * Delete a task
 */
export async function deleteTask(taskId: string): Promise<void> {
  return fetchAPI<void>(`/api/tasks/${taskId}`, {
    method: "DELETE",
  });
}

/**
 * Toggle task completion status
 *
 * Convenience function to toggle is_complete field.
 */
export async function toggleTaskComplete(task: Task): Promise<Task> {
  return updateTask(task.id, { is_complete: !task.is_complete });
}
