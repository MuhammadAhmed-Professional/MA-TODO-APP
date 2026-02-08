/**
 * TaskForm Component
 *
 * Form for creating and editing tasks with:
 * - React Hook Form for form management
 * - Zod validation
 * - Error handling
 * - Loading states
 * - Priority selection
 * - Due date input
 * - Tag selection
 */

"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { PrioritySelector } from "./PrioritySelector";
import { TagSelector } from "./TagSelector";
import type { Task, TaskCreate, Priority } from "@/types/task";
import type { Tag } from "@/types/tag";
import { getTags } from "@/lib/api";

// Validation schema
const taskSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less"),
  description: z
    .string()
    .max(2000, "Description must be 2000 characters or less")
    .optional()
    .nullable(),
  priority: z.number().int().min(1).max(3).optional(),
  due_date: z.string().optional().nullable(),
  tag_ids: z.array(z.string()).optional(),
});

type TaskFormData = z.infer<typeof taskSchema>;

interface TaskFormProps {
  onSubmit: (taskData: TaskCreate) => Promise<void>;
  onCancel?: () => void;
  initialData?: Task;
  isLoading?: boolean;
  availableTags?: Tag[];
}

export function TaskForm({
  onSubmit,
  onCancel,
  initialData,
  isLoading = false,
  availableTags = [],
}: TaskFormProps) {
  const [tags, setTags] = useState<Tag[]>(availableTags);
  const [selectedTagIds, setSelectedTagIds] = useState<string[]>(
    initialData?.tags.map((t) => t.id) || []
  );

  // Fetch tags if not provided
  useEffect(() => {
    if (availableTags.length === 0) {
      getTags().then(setTags).catch(console.error);
    }
  }, [availableTags]);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    watch,
    setValue,
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initialData?.title || "",
      description: initialData?.description || "",
      priority: initialData?.priority || 2,
      due_date: initialData?.due_date
        ? new Date(initialData.due_date).toISOString().split("T")[0]
        : "",
      tag_ids: initialData?.tags.map((t) => t.id) || [],
    },
  });

  const title = watch("title") || "";
  const description = watch("description") || "";
  const priority = watch("priority") as Priority | undefined;
  const dueDate = watch("due_date");

  const onFormSubmit = async (data: TaskFormData) => {
    try {
      await onSubmit({
        title: data.title.trim(),
        description: data.description?.trim() || null,
        priority: (data.priority as Priority) || 2,
        due_date: data.due_date ? new Date(data.due_date).toISOString() : null,
        tag_ids: selectedTagIds,
      });

      // Reset form if creating new task (no initialData)
      if (!initialData) {
        reset();
        setSelectedTagIds([]);
      }
    } catch (error) {
      // Error is handled by parent component via toast
      console.error("Form submission error:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
      {/* Title Field */}
      <div className="space-y-2">
        <Label htmlFor="title">
          Title <span className="text-red-500">*</span>
        </Label>
        <Input
          id="title"
          {...register("title")}
          disabled={isLoading || isSubmitting}
          placeholder="e.g., Buy groceries"
          maxLength={200}
          className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm"
        />
        {errors.title && (
          <p className="text-sm text-red-600 dark:text-red-400">
            {errors.title.message}
          </p>
        )}
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          {title.length}/200 characters
        </p>
      </div>

      {/* Description Field */}
      <div className="space-y-2">
        <Label htmlFor="description">Description (optional)</Label>
        <Textarea
          id="description"
          {...register("description")}
          disabled={isLoading || isSubmitting}
          placeholder="e.g., Milk, eggs, bread..."
          rows={4}
          maxLength={2000}
          className="resize-none bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm"
        />
        {errors.description && (
          <p className="text-sm text-red-600 dark:text-red-400">
            {errors.description.message}
          </p>
        )}
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          {description.length}/2000 characters
        </p>
      </div>

      {/* Priority Selector */}
      <div className="space-y-2">
        <Label>Priority</Label>
        <PrioritySelector
          value={priority || 2}
          onChange={(p: Priority) => setValue("priority", p as number)}
          disabled={isLoading || isSubmitting}
        />
      </div>

      {/* Due Date Field */}
      <div className="space-y-2">
        <Label htmlFor="due_date">Due Date (optional)</Label>
        <Input
          id="due_date"
          type="date"
          {...register("due_date")}
          disabled={isLoading || isSubmitting}
          className="bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm"
          min={new Date().toISOString().split("T")[0]}
        />
      </div>

      {/* Tag Selector */}
      <div className="space-y-2">
        <Label>Tags</Label>
        <TagSelector
          selectedTagIds={selectedTagIds}
          availableTags={tags}
          onChange={setSelectedTagIds}
          disabled={isLoading || isSubmitting}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <Button
          type="submit"
          disabled={isLoading || isSubmitting}
          className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all duration-200"
        >
          {isLoading || isSubmitting
            ? "Saving..."
            : initialData
            ? "Update Task"
            : "Add Task"}
        </Button>

        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading || isSubmitting}
            className="px-6"
          >
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
