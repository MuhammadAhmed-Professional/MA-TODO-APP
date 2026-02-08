/**
 * CategoryPicker Component
 *
 * Select or create task categories.
 * Features:
 * - List user's categories
 * - Color swatches
 * - Create new category inline
 * - No category option
 */

"use client";

import { useState } from "react";
import { Folder, FolderOpen, Plus, X } from "lucide-react";
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
import type { TaskCategory } from "@/types/advanced-task";

interface CategoryPickerProps {
  categories: TaskCategory[];
  value?: string | null;
  onChange: (categoryId: string | null) => void;
  onCreateCategory?: (name: string, color: string) => void;
  disabled?: boolean;
}

const CATEGORY_COLORS = [
  "#3b82f6", // blue
  "#ef4444", // red
  "#22c55e", // green
  "#f59e0b", // amber
  "#8b5cf6", // violet
  "#ec4899", // pink
  "#06b6d4", // cyan
  "#64748b", // slate
];

export function CategoryPicker({
  categories,
  value,
  onChange,
  onCreateCategory,
  disabled = false,
}: CategoryPickerProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [selectedColor, setSelectedColor] = useState(CATEGORY_COLORS[0]);

  const selectedCategory = categories.find((c) => c.id === value);

  const handleCreateCategory = () => {
    if (!newCategoryName.trim()) return;

    if (onCreateCategory) {
      onCreateCategory(newCategoryName.trim(), selectedColor);
    }

    setNewCategoryName("");
    setIsCreating(false);
  };

  return (
    <div className="space-y-2">
      <Label className="flex items-center gap-2">
        {selectedCategory ? (
          <FolderOpen className="h-4 w-4" />
        ) : (
          <Folder className="h-4 w-4" />
        )}
        Category
      </Label>

      {!isCreating ? (
        <div className="flex gap-2">
          <Select
            value={value || "none"}
            onValueChange={(v: string) => onChange(v === "none" ? null : v)}
            disabled={disabled}
          >
            <SelectTrigger className="flex-1">
              <SelectValue placeholder="No category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">
                <div className="flex items-center gap-2">
                  <Folder className="h-4 w-4 text-neutral-400" />
                  No category
                </div>
              </SelectItem>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.id}>
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: category.color }}
                    />
                    {category.name}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {onCreateCategory && !disabled && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => setIsCreating(true)}
            >
              <Plus className="h-4 w-4" />
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-3 p-3 border rounded-lg bg-neutral-50 dark:bg-neutral-900">
          <Input
            placeholder="Category name..."
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleCreateCategory();
            }}
            autoFocus
          />

          <div className="flex flex-wrap gap-2">
            {CATEGORY_COLORS.map((color) => (
              <button
                key={color}
                type="button"
                onClick={() => setSelectedColor(color)}
                className={cn(
                  "w-6 h-6 rounded-full transition-transform",
                  selectedColor === color
                    ? "ring-2 ring-offset-2 ring-neutral-900 dark:ring-white scale-110"
                    : "opacity-60 hover:opacity-100"
                )}
                style={{ backgroundColor: color }}
              />
            ))}
          </div>

          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              onClick={handleCreateCategory}
              disabled={!newCategoryName.trim()}
            >
              Create
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => {
                setIsCreating(false);
                setNewCategoryName("");
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(" ");
}
