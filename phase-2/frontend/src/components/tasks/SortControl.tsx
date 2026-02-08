/**
 * SortControl Component
 *
 * Sort controls for task list.
 * Sort by created_at, due_date, priority, title.
 */

"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

type SortField = "created_at" | "due_date" | "priority" | "title" | "updated_at";
type SortOrder = "asc" | "desc";

interface SortControlProps {
  sortBy: SortField;
  sortOrder: SortOrder;
  onChange: (sortBy: SortField, sortOrder: SortOrder) => void;
  disabled?: boolean;
}

const SORT_OPTIONS: { field: SortField; label: string }[] = [
  { field: "created_at", label: "Created date" },
  { field: "due_date", label: "Due date" },
  { field: "priority", label: "Priority" },
  { field: "title", label: "Title" },
  { field: "updated_at", label: "Updated date" },
];

export function SortControl({
  sortBy,
  sortOrder,
  onChange,
  disabled = false,
}: SortControlProps) {
  const currentLabel = SORT_OPTIONS.find((opt) => opt.field === sortBy)?.label || "Sort";

  const toggleOrder = () => {
    onChange(sortBy, sortOrder === "asc" ? "desc" : "asc");
  };

  return (
    <div className="flex items-center gap-1">
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2 min-w-[160px] justify-between"
          >
            <span className="truncate">{currentLabel}</span>
            <ArrowUpDown className="h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56">
          <DropdownMenuLabel>Sort by</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {SORT_OPTIONS.map((option) => (
            <DropdownMenuItem
              key={option.field}
              onClick={() => onChange(option.field, sortOrder)}
              className="justify-between"
            >
              <span>{option.label}</span>
              {sortBy === option.field && (
                <span className="text-xs text-muted-foreground">✓</span>
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={toggleOrder}
        disabled={disabled}
        className="px-2"
        title={`Sort order: ${sortOrder === "asc" ? "ascending" : "descending"}`}
      >
        {sortOrder === "asc" ? (
          <ArrowUp className="h-4 w-4" />
        ) : (
          <ArrowDown className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
