/**
 * DatePicker Component
 *
 * Date and time picker for task due dates.
 * Features:
 * - Calendar picker for dates
 * - Time picker for specific times
 * - Visual indicator for overdue tasks
 * - Clear button to remove due date
 */

"use client";

import { useState } from "react";
import { Calendar, Clock, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  value?: string | null; // ISO 8601 datetime
  onChange: (date: string | null) => void;
  label?: string;
  disabled?: boolean;
  isOverdue?: boolean;
}

export function DatePicker({
  value,
  onChange,
  label = "Due Date",
  disabled = false,
  isOverdue = false,
}: DatePickerProps) {
  const [dateInput, setDateInput] = useState(
    value ? new Date(value).toISOString().slice(0, 16) : ""
  );

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setDateInput(newValue);

    if (newValue) {
      // Convert to ISO 8601 UTC
      const date = new Date(newValue);
      onChange(date.toISOString());
    } else {
      onChange(null);
    }
  };

  const handleClear = () => {
    setDateInput("");
    onChange(null);
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="due-date" className="flex items-center gap-2">
        <Calendar className="h-4 w-4" />
        {label}
      </Label>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Input
            id="due-date"
            type="datetime-local"
            value={dateInput}
            onChange={handleDateChange}
            disabled={disabled}
            className={cn(
              "bg-white/80 dark:bg-neutral-900/80 backdrop-blur-sm",
              isOverdue && !disabled && "border-red-500 focus:border-red-500"
            )}
          />
          {isOverdue && !disabled && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <span className="text-xs text-red-500 font-medium">Overdue</span>
            </div>
          )}
        </div>

        {value && !disabled && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={handleClear}
            className="h-10 w-10 shrink-0"
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Clear due date</span>
          </Button>
        )}
      </div>

      {value && (
        <p className="text-xs text-neutral-500 dark:text-neutral-400 flex items-center gap-1">
          <Clock className="h-3 w-3" />
          Due: {new Date(value).toLocaleString()}
        </p>
      )}
    </div>
  );
}
