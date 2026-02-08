/**
 * Advanced Task Type Definitions
 *
 * Types for recurring tasks, reminders, and categories.
 * Matches backend models in phase-5.
 */

/**
 * Task priority levels
 */
export type TaskPriority = "low" | "medium" | "high" | "urgent";

/**
 * Recurrence frequency types
 */
export type FrequencyType = "daily" | "weekly" | "monthly" | "custom";

/**
 * Notification delivery methods
 */
export type NotificationType = "email" | "push" | "in_app";

/**
 * Recurring task configuration
 */
export interface RecurringTask {
  id: string;
  task_id: string;
  frequency: FrequencyType;
  interval: number;
  next_due_at: string | null; // ISO 8601 datetime
  cron_expression: string | null;
  is_active: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * Create recurring task request
 */
export interface RecurringTaskCreate {
  frequency: FrequencyType;
  interval?: number;
  cron_expression?: string | null;
}

/**
 * Task reminder
 */
export interface TaskReminder {
  id: string;
  task_id: string;
  remind_at: string; // ISO 8601 datetime
  is_sent: boolean;
  notification_type: NotificationType;
  created_at: string; // ISO 8601 datetime
  sent_at: string | null;
}

/**
 * Create reminder request
 */
export interface TaskReminderCreate {
  remind_at: string; // ISO 8601 datetime
  notification_type?: NotificationType;
}

/**
 * Task category
 */
export interface TaskCategory {
  id: string;
  user_id: string;
  name: string;
  color: string; // Hex color code
  created_at: string; // ISO 8601 datetime
}

/**
 * Create category request
 */
export interface TaskCategoryCreate {
  name: string;
  color?: string;
}

/**
 * Extended task with advanced fields
 */
export interface AdvancedTask {
  id: string;
  title: string;
  description: string | null;
  is_complete: boolean;
  due_date: string | null; // ISO 8601 datetime
  remind_at: string | null; // ISO 8601 datetime
  priority: TaskPriority;
  category_id: string | null;
  user_id: string;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  // Optional related objects
  recurring?: RecurringTask | null;
  reminders?: TaskReminder[];
  category?: TaskCategory | null;
}

/**
 * Task with due date check (helper type)
 */
export interface TaskWithDueStatus extends AdvancedTask {
  is_overdue: boolean;
  is_due_soon: boolean; // Within 24 hours
}
