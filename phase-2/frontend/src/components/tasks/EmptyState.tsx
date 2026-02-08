/**
 * EmptyState Component
 *
 * Displayed when no tasks match the current filter
 */

"use client";

import { CheckCircle2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  onAddTask?: () => void;
  filter?: "all" | "pending" | "completed";
}

export function EmptyState({ onAddTask, filter = "all" }: EmptyStateProps) {
  const getMessage = () => {
    switch (filter) {
      case "pending":
        return {
          title: "No pending tasks",
          description: "All caught up! You have no pending tasks.",
        };
      case "completed":
        return {
          title: "No completed tasks",
          description: "Complete some tasks to see them here.",
        };
      default:
        return {
          title: "No tasks yet",
          description: "Get started by creating your first task.",
        };
    }
  };

  const { title, description } = getMessage();

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-in fade-in duration-500">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-3xl rounded-full" />
        <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-950 dark:to-purple-950">
          <CheckCircle2 className="h-12 w-12 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
      <h3 className="mt-6 text-xl font-semibold text-neutral-900 dark:text-neutral-100">
        {title}
      </h3>
      <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400 max-w-md text-center">
        {description}
      </p>
      {onAddTask && filter === "all" && (
        <Button
          onClick={onAddTask}
          className="mt-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Your First Task
        </Button>
      )}
    </div>
  );
}
