/**
 * Advanced Features API Client
 *
 * API functions for recurring tasks, reminders, and categories.
 * Extends the base API client with Phase V features.
 */

import { fetchAPI, APIError } from "./api";
import type {
  RecurringTask,
  RecurringTaskCreate,
  TaskReminder,
  TaskReminderCreate,
  TaskCategory,
  TaskCategoryCreate,
} from "@/types/advanced-task";

// ================== RECURRING TASKS ==================

/**
 * Set up recurring pattern for a task
 */
export async function setTaskRecurring(
  taskId: string,
  data: RecurringTaskCreate
): Promise<RecurringTask> {
  return fetchAPI<RecurringTask>(`/api/tasks/${taskId}/recurring`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Get recurring configuration for a task
 */
export async function getTaskRecurring(taskId: string): Promise<RecurringTask | null> {
  try {
    return await fetchAPI<RecurringTask>(`/api/tasks/${taskId}/recurring`);
  } catch (error) {
    if (error instanceof APIError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

/**
 * Remove recurring configuration from a task
 */
export async function deleteTaskRecurring(taskId: string): Promise<void> {
  return fetchAPI<void>(`/api/tasks/${taskId}/recurring`, {
    method: "DELETE",
  });
}

// ================== REMINDERS ==================

/**
 * Schedule a reminder for a task
 */
export async function createReminder(
  taskId: string,
  data: TaskReminderCreate
): Promise<TaskReminder> {
  return fetchAPI<TaskReminder>(`/api/tasks/${taskId}/reminder`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Get all reminders for a task
 */
export async function getTaskReminders(taskId: string): Promise<TaskReminder[]> {
  return fetchAPI<TaskReminder[]>(`/api/tasks/${taskId}/reminders`);
}

/**
 * Delete a reminder
 */
export async function deleteReminder(reminderId: string): Promise<void> {
  return fetchAPI<void>(`/api/tasks/reminders/${reminderId}`, {
    method: "DELETE",
  });
}

// ================== CATEGORIES ==================

/**
 * Get all categories for the authenticated user
 */
export async function getCategories(): Promise<TaskCategory[]> {
  return fetchAPI<TaskCategory[]>("/api/tasks/categories");
}

/**
 * Create a new category
 */
export async function createCategory(data: TaskCategoryCreate): Promise<TaskCategory> {
  return fetchAPI<TaskCategory>("/api/tasks/categories", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

/**
 * Get a specific category
 */
export async function getCategory(categoryId: string): Promise<TaskCategory> {
  return fetchAPI<TaskCategory>(`/api/tasks/categories/${categoryId}`);
}

/**
 * Delete a category
 */
export async function deleteCategory(categoryId: string): Promise<void> {
  return fetchAPI<void>(`/api/tasks/categories/${categoryId}`, {
    method: "DELETE",
  });
}

// ================== SEARCH ==================

/**
 * Search and filter tasks with advanced criteria
 */
export async function searchTasks(params: {
  q?: string;
  priority?: string;
  category?: string;
  is_complete?: boolean;
  due_before?: string;
  due_after?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  limit?: number;
  offset?: number;
}): Promise<any[]> {
  const searchParams = new URLSearchParams();

  if (params.q) searchParams.set("q", params.q);
  if (params.priority) searchParams.set("priority", params.priority);
  if (params.category) searchParams.set("category", params.category);
  if (params.is_complete !== undefined) searchParams.set("is_complete", String(params.is_complete));
  if (params.due_before) searchParams.set("due_before", params.due_before);
  if (params.due_after) searchParams.set("due_after", params.due_after);
  if (params.sort_by) searchParams.set("sort_by", params.sort_by);
  if (params.sort_order) searchParams.set("sort_order", params.sort_order);
  if (params.limit) searchParams.set("limit", String(params.limit));
  if (params.offset) searchParams.set("offset", String(params.offset));

  const query = searchParams.toString();
  return fetchAPI<any[]>(`/api/tasks/search${query ? `?${query}` : ""}`);
}
