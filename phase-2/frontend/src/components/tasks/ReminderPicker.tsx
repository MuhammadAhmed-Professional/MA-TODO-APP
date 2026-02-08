/**
 * ReminderPicker Component
 *
 * Set reminder notifications for tasks.
 * Features:
 * - Relative time presets (15min, 1hr, 1day before)
 * - Custom date/time picker
 * - Notification type selector
 * - Multiple reminders support
 */

"use client";

import { useState } from "react";
import { Bell, Plus, Trash2 } from "lucide-react";
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
import type { TaskReminderCreate, NotificationType } from "@/types/advanced-task";

interface ReminderPreset {
  label: string;
  minutes: number;
}

const REMINDER_PRESETS: ReminderPreset[] = [
  { label: "15 minutes before", minutes: 15 },
  { label: "1 hour before", minutes: 60 },
  { label: "4 hours before", minutes: 240 },
  { label: "1 day before", minutes: 1440 },
];

interface ReminderPickerProps {
  dueDate?: string | null;
  onAddReminder: (reminder: TaskReminderCreate) => void;
  onRemoveReminder?: (index: number) => void;
  reminders?: Array<{ remind_at: string; notification_type: NotificationType }>;
  disabled?: boolean;
}

export function ReminderPicker({
  dueDate,
  onAddReminder,
  onRemoveReminder,
  reminders = [],
  disabled = false,
}: ReminderPickerProps) {
  const [customTime, setCustomTime] = useState("");
  const [notificationType, setNotificationType] = useState<NotificationType>("in_app");

  const handlePresetClick = (minutesBefore: number) => {
    if (!dueDate) {
      alert("Please set a due date first");
      return;
    }

    const due = new Date(dueDate);
    const remindAt = new Date(due.getTime() - minutesBefore * 60 * 1000);

    // Don't set reminder in the past
    if (remindAt < new Date()) {
      alert("Reminder time would be in the past. Please choose a different option.");
      return;
    }

    onAddReminder({
      remind_at: remindAt.toISOString(),
      notification_type: notificationType,
    });
  };

  const handleCustomReminder = () => {
    if (!customTime) return;

    onAddReminder({
      remind_at: new Date(customTime).toISOString(),
      notification_type: notificationType,
    });

    setCustomTime("");
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Bell className="h-4 w-4" />
        <Label>Reminders</Label>
      </div>

      {reminders.length > 0 && (
        <div className="space-y-2">
          {reminders.map((reminder, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-2 rounded-md bg-neutral-100 dark:bg-neutral-800"
            >
              <span className="text-sm">
                {new Date(reminder.remind_at).toLocaleString()}
              </span>
              {onRemoveReminder && !disabled && (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => onRemoveReminder(index)}
                  className="h-6 w-6"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          ))}
        </div>
      )}

      {!disabled && (
        <div className="space-y-3">
          {/* Presets */}
          <div>
            <Label className="text-xs text-neutral-500 dark:text-neutral-400">
              Quick presets
            </Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {REMINDER_PRESETS.map((preset) => (
                <Button
                  key={preset.minutes}
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => handlePresetClick(preset.minutes)}
                  disabled={!dueDate}
                  className="text-xs"
                >
                  {preset.label}
                </Button>
              ))}
            </div>
          </div>

          {/* Custom time */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <Input
              type="datetime-local"
              value={customTime}
              onChange={(e) => setCustomTime(e.target.value)}
              className="sm:col-span-2"
            />
            <Select value={notificationType} onValueChange={(v: any) => setNotificationType(v)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="in_app">In App</SelectItem>
                <SelectItem value="email">Email</SelectItem>
                <SelectItem value="push">Push</SelectItem>
              </SelectContent>
            </Select>
            <Button
              type="button"
              variant="outline"
              onClick={handleCustomReminder}
              disabled={!customTime}
              className="sm:col-span-3"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Custom Reminder
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
