/**
 * Tag Type Definitions
 *
 * MUST match backend Tag model exactly.
 * See: backend/src/models/tag.py
 */

/**
 * Tag model (matches backend TagResponse)
 */
export interface Tag {
  id: string; // UUID
  name: string; // Lowercase, unique per user
  color: string; // Hex color code (e.g., "#3b82f6")
  user_id: string; // UUID
}

/**
 * Tag creation payload
 */
export interface TagCreate {
  name: string; // 1-50 characters
  color?: string; // Hex color code (default: #3b82f6)
}

/**
 * Tag update payload (all fields optional)
 */
export interface TagUpdate {
  name?: string;
  color?: string;
}

/**
 * Tag list response
 */
export interface TagListResponse {
  tags: Tag[];
  total: number;
}

/**
 * Predefined color palette for tags
 */
export const TAG_COLORS = [
  { name: "red", value: "#ef4444" },
  { name: "orange", value: "#f97316" },
  { name: "amber", value: "#f59e0b" },
  { name: "yellow", value: "#eab308" },
  { name: "lime", value: "#84cc16" },
  { name: "green", value: "#22c55e" },
  { name: "emerald", value: "#10b981" },
  { name: "teal", value: "#14b8a6" },
  { name: "cyan", value: "#06b6d4" },
  { name: "sky", value: "#0ea5e9" },
  { name: "blue", value: "#3b82f6" },
  { name: "indigo", value: "#6366f1" },
  { name: "violet", value: "#8b5cf6" },
  { name: "purple", value: "#a855f7" },
  { name: "fuchsia", value: "#d946ef" },
  { name: "pink", value: "#ec4899" },
  { name: "rose", value: "#f43f5e" },
] as const;

/**
 * Get a readable color name from hex value
 */
export function getColorName(hexColor: string): string {
  const color = TAG_COLORS.find((c) => c.value === hexColor);
  return color?.name || "custom";
}
