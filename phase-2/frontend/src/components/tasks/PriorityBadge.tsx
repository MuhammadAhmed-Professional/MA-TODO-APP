/**
 * PriorityBadge Component
 *
 * Displays task priority with color coding.
 */

import type { Priority } from "@/types/task";
import { PRIORITY_COLORS, PRIORITY_LABELS } from "@/types/task";

interface PriorityBadgeProps {
  priority: Priority;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

const SIZE_CLASSES = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-sm",
  lg: "px-3 py-1.5 text-base",
};

export function PriorityBadge({
  priority,
  size = "md",
  showLabel = true,
}: PriorityBadgeProps) {
  const color = PRIORITY_COLORS[priority];
  const label = PRIORITY_LABELS[priority];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${SIZE_CLASSES[size]}`}
      style={{
        backgroundColor: `${color}20`,
        color: color,
        border: `1px solid ${color}40`,
      }}
      title={`Priority: ${label}`}
    >
      <span
        className="rounded-full"
        style={{
          backgroundColor: color,
          width: size === "sm" ? "6px" : size === "md" ? "8px" : "10px",
          height: size === "sm" ? "6px" : size === "md" ? "8px" : "10px",
        }}
      />
      {showLabel && <span className="capitalize">{label.toLowerCase()}</span>}
    </span>
  );
}
