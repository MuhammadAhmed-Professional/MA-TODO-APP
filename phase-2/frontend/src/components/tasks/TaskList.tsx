/**
 * TaskList Component
 *
 * Grid layout for displaying tasks with:
 * - Responsive columns
 * - Smooth animations
 * - Loading states
 * - Empty state
 */

"use client";

import { TaskCard } from "./TaskCard";
import { EmptyState } from "./EmptyState";
import { Skeleton } from "@/components/ui/skeleton";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  isLoading?: boolean;
  onToggleComplete: (taskId: string, isComplete: boolean) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
  onEdit?: (task: Task) => void;
  onAddTask?: () => void;
  filter?: "all" | "pending" | "completed";
}

export function TaskList({
  tasks,
  isLoading = false,
  onToggleComplete,
  onDelete,
  onEdit,
  onAddTask,
  filter = "all",
}: TaskListProps) {
  // Filter tasks based on the filter prop
  const filteredTasks = tasks.filter((task) => {
    if (filter === "pending") return !task.is_complete;
    if (filter === "completed") return task.is_complete;
    return true; // "all"
  });

  // Loading state
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <TaskCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  // Empty state
  if (filteredTasks.length === 0) {
    return <EmptyState onAddTask={onAddTask} filter={filter} />;
  }

  // Task list
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-in fade-in duration-500">
      {filteredTasks.map((task, index) => (
        <div
          key={task.id}
          className="animate-in fade-in slide-in-from-bottom-4"
          style={{ animationDelay: `${index * 50}ms` }}
        >
          <TaskCard
            task={task}
            onToggleComplete={onToggleComplete}
            onDelete={onDelete}
            onEdit={onEdit}
          />
        </div>
      ))}
    </div>
  );
}

/**
 * TaskCardSkeleton Component
 *
 * Loading placeholder for task cards
 */
function TaskCardSkeleton() {
  return (
    <div className="rounded-lg border border-neutral-200/50 bg-white/60 backdrop-blur-md p-4 dark:border-neutral-800/50 dark:bg-neutral-900/60">
      <div className="flex items-start gap-3">
        <Skeleton className="h-5 w-5 rounded-md" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-3 w-24" />
        </div>
      </div>
    </div>
  );
}
