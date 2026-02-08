/**
 * RecurrencePicker Component
 *
 * Configure recurring task patterns.
 * Features:
 * - Frequency selector (daily, weekly, monthly)
 * - Interval input (every X days/weeks/months)
 * - Day of week selector for weekly
 * - Day of month selector for monthly
 */

"use client";

import { useState } from "react";
import { Repeat, Clock, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import type { FrequencyType, RecurringTaskCreate } from "@/types/advanced-task";

const WEEKDAYS = [
  { value: "1", label: "Monday" },
  { value: "2", label: "Tuesday" },
  { value: "3", label: "Wednesday" },
  { value: "4", label: "Thursday" },
  { value: "5", label: "Friday" },
  { value: "6", label: "Saturday" },
  { value: "0", label: "Sunday" },
];

interface RecurrencePickerProps {
  value?: RecurringTaskCreate | null;
  onChange: (value: RecurringTaskCreate | null) => void;
  disabled?: boolean;
}

export function RecurrencePicker({
  value,
  onChange,
  disabled = false,
}: RecurrencePickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const frequency = value?.frequency || "weekly";
  const interval = value?.interval || 1;

  const handleFrequencyChange = (freq: FrequencyType) => {
    onChange({ frequency: freq, interval: 1 });
  };

  const handleIntervalChange = (int: number) => {
    if (value) {
      onChange({ ...value, interval: int });
    }
  };

  const handleRemove = () => {
    onChange(null);
    setIsOpen(false);
  };

  const getDisplayText = () => {
    if (!value) return "Set recurrence";

    const freqText = {
      daily: "day",
      weekly: "week",
      monthly: "month",
      custom: "custom",
    }[value.frequency];

    if (value.interval === 1) {
      return `Every ${freqText}`;
    }
    return `Every ${value.interval} ${freqText}s`;
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant={value ? "default" : "outline"}
          disabled={disabled}
          className="w-full justify-start"
        >
          <Repeat className="h-4 w-4 mr-2" />
          {getDisplayText()}
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-80" align="start">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="flex items-center gap-2">
              <Repeat className="h-4 w-4" />
              Recurrence
            </Label>
            {value && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleRemove}
                className="text-xs"
              >
                Remove
              </Button>
            )}
          </div>

          {/* Frequency */}
          <div className="space-y-2">
            <Label className="text-xs text-neutral-500 dark:text-neutral-400">
              Repeat
            </Label>
            <div className="grid grid-cols-2 gap-2">
              {(["daily", "weekly", "monthly"] as FrequencyType[]).map((freq) => (
                <Button
                  key={freq}
                  type="button"
                  variant={frequency === freq ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleFrequencyChange(freq)}
                  className="capitalize"
                >
                  {freq}
                </Button>
              ))}
            </div>
          </div>

          {/* Interval */}
          <div className="space-y-2">
            <Label className="text-xs text-neutral-500 dark:text-neutral-400">
              Every
            </Label>
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min={1}
                max={52}
                value={interval}
                onChange={(e) => handleIntervalChange(parseInt(e.target.value) || 1)}
                className="w-20"
              />
              <span className="text-sm text-neutral-600 dark:text-neutral-400">
                {{
                  daily: "day(s)",
                  weekly: "week(s)",
                  monthly: "month(s)",
                  custom: "period(s)",
                }[frequency]}
              </span>
            </div>
          </div>

          {/* Apply button */}
          <Button
            type="button"
            className="w-full"
            onClick={() => setIsOpen(false)}
          >
            Apply Recurrence
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
