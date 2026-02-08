/**
 * PriorityPicker Component
 *
 * Select task priority level.
 * Features:
 * - Visual priority levels with colors
 * - Single selection
 * - Clear labels
 */

"use client";

import { Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import type { TaskPriority } from "@/types/advanced-task";

interface PriorityPickerProps {
  value: TaskPriority;
  onChange: (value: TaskPriority) => void;
  disabled?: boolean;
}

const PRIORITIES: Array<{
  value: TaskPriority;
  label: string;
  className: string;
}> = [
  {
    value: "low",
    label: "Low",
    className: "bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50",
  },
  {
    value: "medium",
    label: "Medium",
    className: "bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:hover:bg-yellow-900/50",
  },
  {
    value: "high",
    label: "High",
    className: "bg-orange-100 text-orange-700 hover:bg-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:hover:bg-orange-900/50",
  },
  {
    value: "urgent",
    label: "Urgent",
    className: "bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50",
  },
];

export function PriorityPicker({
  value,
  onChange,
  disabled = false,
}: PriorityPickerProps) {
  return (
    <div className="space-y-2">
      <Label className="flex items-center gap-2">
        <Flag className="h-4 w-4" />
        Priority
      </Label>

      <div className="flex flex-wrap gap-2">
        {PRIORITIES.map((priority) => (
          <Button
            key={priority.value}
            type="button"
            variant={value === priority.value ? "default" : "outline"}
            size="sm"
            onClick={() => onChange(priority.value)}
            disabled={disabled}
            className={cn(
              value === priority.value
                ? priority.className
                : "border-neutral-300 dark:border-neutral-700",
              "capitalize"
            )}
          >
            {priority.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
