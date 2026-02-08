/**
 * Task Types
 *
 * TypeScript definitions for todo task entities matching backend models.
 */

export interface Task {
  id: string;
  title: string;
  description: string | null;
  is_complete: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
}

export interface TaskToggleComplete {
  is_complete: boolean;
}

export interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}
