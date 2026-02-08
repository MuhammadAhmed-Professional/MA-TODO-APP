/**
 * PrioritySelector Component
 *
 * Dropdown for selecting task priority.
 */

"use client";

import { PRIORITY_LABELS, type Priority } from "@/types/task";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { PriorityBadge } from "./PriorityBadge";
import { ChevronDown } from "lucide-react";

interface PrioritySelectorProps {
  value: Priority;
  onChange: (priority: Priority) => void;
  disabled?: boolean;
}

const PRIORITIES: Priority[] = [1, 2, 3]; // low, medium, high

export function PrioritySelector({
  value,
  onChange,
  disabled = false,
}: PrioritySelectorProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={disabled}
          className="gap-2"
        >
          <PriorityBadge priority={value} showLabel={true} size="sm" />
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-40">
        {PRIORITIES.map((priority) => (
          <DropdownMenuItem
            key={priority}
            onClick={() => onChange(priority)}
            className="gap-2"
          >
            <PriorityBadge priority={priority} showLabel={true} size="sm" />
            {value === priority && (
              <span className="ml-auto text-xs text-muted-foreground">
                (current)
              </span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
