/**
 * TaskCard Component
 *
 * Individual task card with:
 * - Glassmorphism effect
 * - Completion checkbox
 * - Priority badge
 * - Due date display
 * - Tags display
 * - Edit and delete actions
 * - Smooth animations
 */

"use client";

import { useState } from "react";

import { Trash2, Edit2, Check, Calendar } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { PriorityBadge } from "./PriorityBadge";
import { TagBadge } from "./TagBadge";
import { cn } from "@/lib/utils";
import type { Task } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onToggleComplete: (taskId: string, isComplete: boolean) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
  onEdit?: (task: Task) => void;
}

export function TaskCard({
  task,
  onToggleComplete,
  onDelete,
  onEdit,
}: TaskCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const handleToggleComplete = async () => {
    setIsToggling(true);
    try {
      await onToggleComplete(task.id, !task.is_complete);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } catch (error) {
      setIsDeleting(false);
    }
  };

  // Format due date for display
  const formatDueDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    const now = new Date();
    const isOverdue = date < now && !task.is_complete;

    return {
      date: date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      }),
      isOverdue,
    };
  };

  const dueDate = formatDueDate(task.due_date);

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-300",
        "bg-white/60 backdrop-blur-md border border-neutral-200/50",
        "dark:bg-neutral-900/60 dark:border-neutral-800/50",
        "hover:shadow-lg hover:scale-[1.02]",
        task.is_complete && "opacity-75",
        isDeleting && "opacity-50 pointer-events-none"
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Completion animation overlay */}
      {task.is_complete && (
        <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-emerald-500/10 dark:from-green-500/5 dark:to-emerald-500/5" />
      )}

      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* Checkbox */}
          <div className="mt-0.5">
            <Checkbox
              checked={task.is_complete}
              onCheckedChange={handleToggleComplete}
              disabled={isToggling || isDeleting}
              className={cn(
                "h-5 w-5 rounded-md transition-all duration-200",
                task.is_complete &&
                  "bg-gradient-to-br from-green-500 to-emerald-600 border-green-500"
              )}
            />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title and priority row */}
            <div className="flex items-start gap-2">
              <h3
                className={cn(
                  "text-base font-semibold text-neutral-900 dark:text-neutral-100 transition-all duration-200",
                  task.is_complete && "line-through text-neutral-500 dark:text-neutral-400"
                )}
              >
                {task.title}
              </h3>
              <PriorityBadge priority={task.priority} size="sm" />
            </div>

            {/* Description */}
            {task.description && (
              <p
                className={cn(
                  "mt-1 text-sm text-neutral-600 dark:text-neutral-400 transition-all duration-200 line-clamp-2",
                  task.is_complete && "text-neutral-500 dark:text-neutral-500"
                )}
              >
                {task.description}
              </p>
            )}

            {/* Tags */}
            {task.tags.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {task.tags.map((tag) => (
                  <TagBadge key={tag.id} tag={tag} size="sm" />
                ))}
              </div>
            )}

            {/* Due date and created date */}
            <div className="mt-2 flex items-center gap-3 text-xs text-neutral-500 dark:text-neutral-400">
              {dueDate && (
                <div
                  className={cn(
                    "flex items-center gap-1",
                    dueDate.isOverdue && "text-red-600 dark:text-red-400 font-medium"
                  )}
                >
                  <Calendar className="h-3 w-3" />
                  <span>
                    {dueDate.date}
                    {dueDate.isOverdue && " (overdue)"}
                  </span>
                </div>
              )}
              <time dateTime={task.created_at}>
                Created {new Date(task.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })}
              </time>
            </div>
          </div>

          {/* Action Buttons */}
          <div
            className={cn(
              "flex items-center gap-1 transition-all duration-200",
              showActions ? "opacity-100 translate-x-0" : "opacity-0 translate-x-2 pointer-events-none",
              "sm:opacity-100 sm:translate-x-0 sm:pointer-events-auto"
            )}
          >
            {onEdit && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onEdit(task)}
                disabled={isDeleting}
                className="h-8 w-8 text-neutral-600 hover:text-blue-600 hover:bg-blue-50 dark:text-neutral-400 dark:hover:text-blue-400 dark:hover:bg-blue-950/50"
              >
                <Edit2 className="h-4 w-4" />
                <span className="sr-only">Edit task</span>
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDelete}
              disabled={isDeleting}
              className="h-8 w-8 text-neutral-600 hover:text-red-600 hover:bg-red-50 dark:text-neutral-400 dark:hover:text-red-400 dark:hover:bg-red-950/50"
            >
              <Trash2 className="h-4 w-4" />
              <span className="sr-only">Delete task</span>
            </Button>
          </div>
        </div>

        {/* Completion badge */}
        {task.is_complete && (
          <div className="absolute top-2 right-2 flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-emerald-600 shadow-md">
            <Check className="h-3.5 w-3.5 text-white" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
