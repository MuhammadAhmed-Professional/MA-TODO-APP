/**
 * Task Type Definitions
 *
 * MUST match backend TaskResponse model exactly.
 * See: backend/src/models/task.py
 */

import type { Tag } from "./tag";

// Re-export Tag for convenience
export type { Tag };

/**
 * Priority levels (matches backend Priority enum)
 */
export type Priority = 1 | 2 | 3; // low | medium | high

/**
 * Priority labels
 */
export const PRIORITY_LABELS: Record<Priority, string> = {
  1: "Low",
  2: "Medium",
  3: "High",
};

/**
 * Priority colors (for UI display)
 */
export const PRIORITY_COLORS: Record<Priority, string> = {
  1: "#22c55e", // green
  2: "#eab308", // yellow
  3: "#ef4444", // red
};

/**
 * Task model (matches backend TaskResponse)
 */
export interface Task {
  id: string; // UUID
  title: string;
  description: string | null;
  is_complete: boolean;
  priority: Priority;
  due_date: string | null; // ISO 8601 datetime
  user_id: string; // UUID
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  tags: Tag[]; // Associated tags
}

/**
 * Task creation payload
 */
export interface TaskCreate {
  title: string;
  description?: string | null;
  priority?: Priority;
  due_date?: string | null; // ISO 8601 datetime
  tag_ids?: string[]; // Array of tag UUIDs
}

/**
 * Task update payload (all fields optional)
 */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  is_complete?: boolean;
  priority?: Priority;
  due_date?: string | null; // ISO 8601 datetime
}

/**
 * Task list query parameters (for filtering, searching, sorting)
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
