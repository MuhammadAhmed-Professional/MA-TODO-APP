/**
 * FilterPanel Component
 *
 * Advanced filtering panel for tasks.
 * Filter by priority, tags, status, and due date.
 */

"use client";

import { useState } from "react";
import type { Priority, Tag } from "@/types/task";
import { PRIORITY_LABELS } from "@/types/task";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Filter, X, Calendar } from "lucide-react";

export interface TaskFilters {
  is_complete?: boolean;
  priority?: Priority;
  tag_ids: string[];
  due_date_before?: string;
  due_date_after?: string;
}

interface FilterPanelProps {
  filters: TaskFilters;
  onChange: (filters: TaskFilters) => void;
  availableTags: Tag[];
  disabled?: boolean;
}

const PRIORITIES: Priority[] = [1, 2, 3]; // low, medium, high

export function FilterPanel({
  filters,
  onChange,
  availableTags,
  disabled = false,
}: FilterPanelProps) {
  const [isDueDateOpen, setIsDueDateOpen] = useState(false);

  const activeFilterCount = [
    filters.is_complete !== undefined,
    filters.priority !== undefined,
    filters.tag_ids.length > 0,
    filters.due_date_before || filters.due_date_after,
  ].filter(Boolean).length;

  const handleClearAll = () => {
    onChange({
      tag_ids: [],
    });
  };

  const toggleComplete = (checked: boolean) => {
    onChange({
      ...filters,
      is_complete: checked ? true : undefined,
    });
  };

  const toggleIncomplete = (checked: boolean) => {
    onChange({
      ...filters,
      is_complete: checked ? false : undefined,
    });
  };

  const togglePriority = (priority: Priority) => {
    onChange({
      ...filters,
      priority: filters.priority === priority ? undefined : priority,
    });
  };

  const toggleTag = (tagId: string) => {
    const newTagIds = filters.tag_ids.includes(tagId)
      ? filters.tag_ids.filter((id) => id !== tagId)
      : [...filters.tag_ids, tagId];
    onChange({ ...filters, tag_ids: newTagIds });
  };

  const setDueDateRange = (before?: string, after?: string) => {
    onChange({
      ...filters,
      due_date_before: before,
      due_date_after: after,
    });
  };

  const selectedTags = availableTags.filter((tag) =>
    filters.tag_ids.includes(tag.id)
  );

  return (
    <div className="flex items-center gap-2">
      {/* Status Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2"
          >
            Status
            {filters.is_complete !== undefined && (
              <span className="h-2 w-2 rounded-full bg-blue-500" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          <DropdownMenuLabel>Filter by status</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuCheckboxItem
            checked={filters.is_complete === true}
            onCheckedChange={toggleComplete}
          >
            Complete
          </DropdownMenuCheckboxItem>
          <DropdownMenuCheckboxItem
            checked={filters.is_complete === false}
            onCheckedChange={toggleIncomplete}
          >
            Incomplete
          </DropdownMenuCheckboxItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Priority Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2"
          >
            Priority
            {filters.priority !== undefined && (
              <span className="h-2 w-2 rounded-full bg-blue-500" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-48">
          <DropdownMenuLabel>Filter by priority</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {PRIORITIES.map((priority) => (
            <DropdownMenuCheckboxItem
              key={priority}
              checked={filters.priority === priority}
              onCheckedChange={() => togglePriority(priority)}
            >
              {PRIORITY_LABELS[priority]}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Tags Filter */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2"
          >
            Tags
            {filters.tag_ids.length > 0 && (
              <span className="ml-1 text-xs text-muted-foreground">
                ({filters.tag_ids.length})
              </span>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-56 max-h-96 overflow-y-auto">
          <DropdownMenuLabel>Filter by tags</DropdownMenuLabel>
          <DropdownMenuSeparator />
          {availableTags.length === 0 ? (
            <div className="px-2 py-4 text-sm text-muted-foreground text-center">
              No tags available
            </div>
          ) : (
            availableTags.map((tag) => (
              <DropdownMenuCheckboxItem
                key={tag.id}
                checked={filters.tag_ids.includes(tag.id)}
                onCheckedChange={() => toggleTag(tag.id)}
                className="gap-2 pl-2"
              >
                <div className="flex items-center gap-2 flex-1">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: tag.color }}
                  />
                  <span className="capitalize">{tag.name}</span>
                </div>
              </DropdownMenuCheckboxItem>
            ))
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Due Date Filter */}
      <DropdownMenu open={isDueDateOpen} onOpenChange={setIsDueDateOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2"
          >
            <Calendar className="h-4 w-4" />
            Due Date
            {(filters.due_date_before || filters.due_date_after) && (
              <span className="h-2 w-2 rounded-full bg-blue-500" />
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-72 p-3">
          <DropdownMenuLabel className="mb-2">Filter by due date</DropdownMenuLabel>
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="due-after" className="text-xs text-muted-foreground">
                After
              </Label>
              <Input
                id="due-after"
                type="date"
                value={filters.due_date_after?.split("T")[0] || ""}
                onChange={(e) =>
                  setDueDateRange(
                    filters.due_date_before,
                    e.target.value ? `${e.target.value}T00:00:00Z` : undefined
                  )
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="due-before" className="text-xs text-muted-foreground">
                Before
              </Label>
              <Input
                id="due-before"
                type="date"
                value={filters.due_date_before?.split("T")[0] || ""}
                onChange={(e) =>
                  setDueDateRange(
                    e.target.value ? `${e.target.value}T23:59:59Z` : undefined,
                    filters.due_date_after
                  )
                }
              />
            </div>
            {(filters.due_date_before || filters.due_date_after) && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setDueDateRange(undefined, undefined)}
                className="w-full"
              >
                Clear dates
              </Button>
            )}
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Active filters display & clear all */}
      {activeFilterCount > 0 && (
        <>
          {/* Selected tags badges */}
          {selectedTags.length > 0 && (
            <div className="flex gap-1">
              {selectedTags.slice(0, 2).map((tag) => (
                <span
                  key={tag.id}
                  className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium text-white"
                  style={{ backgroundColor: tag.color }}
                >
                  {tag.name}
                  <button
                    type="button"
                    onClick={() => toggleTag(tag.id)}
                    className="hover:bg-white/20 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" strokeWidth={2.5} />
                  </button>
                </span>
              ))}
              {selectedTags.length > 2 && (
                <span className="text-xs text-muted-foreground">
                  +{selectedTags.length - 2} more
                </span>
              )}
            </div>
          )}

          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleClearAll}
            className="h-8 text-xs"
          >
            Clear all ({activeFilterCount})
          </Button>
        </>
      )}
    </div>
  );
}
