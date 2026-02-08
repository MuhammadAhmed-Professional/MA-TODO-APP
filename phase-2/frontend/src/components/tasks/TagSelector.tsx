/**
 * TagSelector Component
 *
 * Multi-select dropdown for selecting tags on tasks.
 * Allows creating new tags inline.
 */

"use client";

import { useState, useMemo } from "react";
import type { Tag } from "@/types/tag";
import { TAG_COLORS } from "@/types/tag";
import { getTags, createTag } from "@/lib/api";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tag as TagIcon, X, Plus, Check } from "lucide-react";

interface TagSelectorProps {
  selectedTagIds: string[];
  availableTags: Tag[];
  onChange: (tagIds: string[]) => void;
  onCreateTag?: (name: string, color: string) => Promise<Tag>;
  disabled?: boolean;
}

export function TagSelector({
  selectedTagIds,
  availableTags,
  onChange,
  onCreateTag,
  disabled = false,
}: TagSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [newTagName, setNewTagName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [selectedColorIndex, setSelectedColorIndex] = useState(9); // Default to blue

  const selectedTags = useMemo(
    () => availableTags.filter((tag) => selectedTagIds.includes(tag.id)),
    [availableTags, selectedTagIds]
  );

  const handleToggleTag = (tagId: string) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter((id) => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  };

  const handleCreateTag = async () => {
    const trimmedName = newTagName.trim().toLowerCase();
    if (!trimmedName) return;

    // Check if tag already exists
    const existingTag = availableTags.find((tag) => tag.name === trimmedName);
    if (existingTag) {
      handleToggleTag(existingTag.id);
      setNewTagName("");
      return;
    }

    setIsCreating(true);
    try {
      let newTag;
      if (onCreateTag) {
        newTag = await onCreateTag(trimmedName, TAG_COLORS[selectedColorIndex].value);
      } else {
        newTag = await createTag({
          name: trimmedName,
          color: TAG_COLORS[selectedColorIndex].value,
        });
      }

      onChange([...selectedTagIds, newTag.id]);
      setNewTagName("");
      setSelectedColorIndex(9); // Reset to blue
    } catch (error) {
      console.error("Failed to create tag:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleRemoveTag = (tagId: string) => {
    onChange(selectedTagIds.filter((id) => id !== tagId));
  };

  return (
    <div className="space-y-2">
      {/* Selected tags display */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <div
              key={tag.id}
              className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-sm font-medium text-white"
              style={{ backgroundColor: tag.color }}
            >
              <span className="capitalize">{tag.name}</span>
              <button
                type="button"
                onClick={() => handleRemoveTag(tag.id)}
                disabled={disabled}
                className="rounded-full bg-white/20 hover:bg-white/30 transition-colors p-0.5"
                aria-label={`Remove ${tag.name} tag`}
              >
                <X className="h-3 w-3" strokeWidth={2.5} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Tag selector dropdown */}
      <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={disabled}
            className="gap-2"
          >
            <TagIcon className="h-4 w-4" />
            {selectedTags.length === 0 ? "Add tags" : `${selectedTags.length} tag${selectedTags.length > 1 ? "s" : ""}`}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-72 p-3">
          {/* Existing tags */}
          {availableTags.length > 0 && (
            <div className="space-y-1 mb-3">
              <Label className="text-xs text-muted-foreground">Existing tags</Label>
              {availableTags.map((tag) => (
                <DropdownMenuCheckboxItem
                  key={tag.id}
                  checked={selectedTagIds.includes(tag.id)}
                  onCheckedChange={() => handleToggleTag(tag.id)}
                  className="gap-2 pl-2"
                >
                  <div className="flex items-center gap-2 flex-1">
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: tag.color }}
                    />
                    <span className="capitalize">{tag.name}</span>
                  </div>
                  {selectedTagIds.includes(tag.id) && (
                    <Check className="h-4 w-4 ml-auto text-muted-foreground" />
                  )}
                </DropdownMenuCheckboxItem>
              ))}
            </div>
          )}

          {availableTags.length > 0 && <DropdownMenuSeparator />}

          {/* Create new tag */}
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Create new tag</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Tag name..."
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleCreateTag();
                  }
                }}
                className="h-8 text-sm"
              />
              <Button
                type="button"
                size="sm"
                onClick={handleCreateTag}
                disabled={!newTagName.trim() || isCreating}
                className="h-8 px-3"
              >
                {isCreating ? (
                  <span className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
              </Button>
            </div>

            {/* Color picker */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {TAG_COLORS.map((color, index) => (
                <button
                  key={color.value}
                  type="button"
                  onClick={() => setSelectedColorIndex(index)}
                  className={`h-5 w-5 rounded-full transition-all ${
                    selectedColorIndex === index
                      ? "ring-2 ring-offset-1 ring-foreground"
                      : "opacity-60 hover:opacity-100"
                  }`}
                  style={{ backgroundColor: color.value }}
                  title={color.name}
                  aria-label={`Select ${color.name} color`}
                />
              ))}
            </div>
          </div>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
