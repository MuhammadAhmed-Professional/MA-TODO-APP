/**
 * TagBadge Component
 *
 * Displays a tag with color background and optional remove button.
 */

"use client";

import type { Tag } from "@/types/tag";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TagBadgeProps {
  tag: Tag;
  onRemove?: () => void;
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES = {
  sm: "px-2 py-0.5 text-xs gap-1",
  md: "px-2.5 py-1 text-sm gap-1.5",
  lg: "px-3 py-1.5 text-base gap-2",
};

const BUTTON_SIZE_CLASSES = {
  sm: "h-3 w-3",
  md: "h-4 w-4",
  lg: "h-5 w-5",
};

export function TagBadge({ tag, onRemove, size = "md" }: TagBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium text-white ${SIZE_CLASSES[size]}`}
      style={{
        backgroundColor: tag.color,
      }}
      title={tag.name}
    >
      <span className="capitalize">{tag.name}</span>
      {onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onRemove();
          }}
          className="rounded-full bg-white/20 hover:bg-white/30 transition-colors flex items-center justify-center"
          aria-label={`Remove ${tag.name} tag`}
        >
          <X className={BUTTON_SIZE_CLASSES[size]} strokeWidth={2.5} />
        </button>
      )}
    </span>
  );
}
