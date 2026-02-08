/**
 * Dashboard Page
 *
 * Main task management interface with:
 * - Task list display
 * - Filter tabs (All/Active/Completed)
 * - Add/Edit/Delete tasks
 * - Loading and empty states
 * - Real-time task completion toggle
 */

"use client";

import { useState, useEffect } from "react";

import { TaskList } from "@/components/tasks/TaskList";
import { TaskForm } from "@/components/tasks/TaskForm";
import { Header } from "@/components/layout/Header";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  type Task,
  type TaskCreate,
} from "@/lib/api";
import { cn } from "@/lib/utils";
import type { TranslationValues } from "next-intl";

interface DashboardContentProps {
  translations: (key: string, values?: TranslationValues) => string;
}

type FilterType = "all" | "pending" | "completed";

export function DashboardPageContent({ translations: t }: DashboardContentProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<FilterType>("all");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const response = await getTasks();
      setTasks(response || []);  // Handle undefined response safely
    } catch (error) {
      toast.error(t('errors.generic') || "Failed to load tasks");
      console.error("Load tasks error:", error);
      setTasks([]);  // Set empty array on error to prevent crash
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTask = async (data: TaskCreate) => {
    try {
      const newTask = await createTask(data);
      setTasks((prev) => [newTask, ...prev]);
      setIsDialogOpen(false);
      toast.success(t('taskCreated') || "Task created successfully");
    } catch (error) {
      toast.error(t('errors.generic') || "Failed to create task");
      throw error;
    }
  };

  const handleEditTask = async (data: TaskCreate) => {
    if (!editingTask) return;

    try {
      const updatedTask = await updateTask(editingTask.id, data);
      setTasks((prev) =>
        prev.map((task) => (task.id === updatedTask.id ? updatedTask : task))
      );
      setIsDialogOpen(false);
      setEditingTask(null);
      toast.success(t('taskUpdated') || "Task updated successfully");
    } catch (error) {
      toast.error(t('errors.generic') || "Failed to update task");
      throw error;
    }
  };

  const handleToggleComplete = async (taskId: string, isComplete: boolean) => {
    try {
      // Optimistic update
      setTasks((prev) =>
        prev.map((task) =>
          task.id === taskId ? { ...task, is_complete: isComplete } : task
        )
      );

      const updatedTask = await updateTask(taskId, { is_complete: isComplete });

      // Update with server response
      setTasks((prev) =>
        prev.map((task) => (task.id === updatedTask.id ? updatedTask : task))
      );

      toast.success(
        isComplete
          ? (t('taskCompleted') || "Task completed!")
          : (t('markIncomplete') || "Task marked as incomplete")
      );
    } catch (error) {
      toast.error(t('errors.generic') || "Failed to update task");
      // Revert optimistic update
      loadTasks();
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
      toast.success(t('taskDeleted') || "Task deleted successfully");
    } catch (error) {
      toast.error(t('errors.generic') || "Failed to delete task");
      throw error;
    }
  };

  const handleOpenDialog = (task?: Task) => {
    if (task) {
      setEditingTask(task);
    } else {
      setEditingTask(null);
    }
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setEditingTask(null);
  };

  // Calculate task counts
  const taskCounts = {
    all: tasks.length,
    pending: tasks.filter((t) => !t.is_complete).length,
    completed: tasks.filter((t) => t.is_complete).length,
  };

  return (
    <>
      <Header onAddTask={() => handleOpenDialog()} />
      <main className="container mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* Page Header */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {t('title')}
            </h1>
            <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
              {taskCounts.all === 0
                ? t('noTasksYet')
                : `${taskCounts.pending} ${t('pendingTasks')}, ${taskCounts.completed} ${t('tasksCompleted')}`
              }
            </p>
          </div>

          {/* Mobile Add Task Button */}
          <Button
            onClick={() => handleOpenDialog()}
            className="sm:hidden bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all duration-200"
          >
            {t('addTask')}
          </Button>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {(["all", "pending", "completed"] as const).map((filterOption) => (
            <Button
              key={filterOption}
              variant={filter === filterOption ? "default" : "outline"}
              onClick={() => setFilter(filterOption)}
              className={cn(
                "relative",
                filter === filterOption &&
                  "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
              )}
            >
              {t(`${filterOption}`) || filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
              <Badge
                variant={filter === filterOption ? "secondary" : "outline"}
                className={cn(
                  "ml-2",
                  filter === filterOption
                    ? "bg-white/20 text-white border-white/30"
                    : ""
                )}
              >
                {taskCounts[filterOption]}
              </Badge>
            </Button>
          ))}
        </div>

        {/* Task List */}
        <TaskList
          tasks={tasks}
          isLoading={isLoading}
          filter={filter}
          onToggleComplete={handleToggleComplete}
          onDelete={handleDeleteTask}
          onEdit={handleOpenDialog}
          onAddTask={() => handleOpenDialog()}
        />
        </div>
      </main>

      {/* Add/Edit Task Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[500px] bg-white/95 backdrop-blur-xl dark:bg-neutral-900/95">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {editingTask ? t('editTask') : t('createNewTask')}
            </DialogTitle>
            <DialogDescription className="text-neutral-600 dark:text-neutral-400">
              {editingTask
                ? t('updateTaskDetails')
                : t('fillTaskDetails')}
            </DialogDescription>
          </DialogHeader>
          <TaskForm
            onSubmit={editingTask ? handleEditTask : handleAddTask}
            onCancel={handleCloseDialog}
            initialData={editingTask || undefined}
          />
        </DialogContent>
      </Dialog>
    </>
  );
}
