/**
 * Badge Component
 *
 * Small status indicators and labels with semantic color variants.
 *
 * @example
 * <Badge variant="default">New</Badge>
 * <Badge variant="success">Active</Badge>
 * <Badge variant="destructive">Error</Badge>
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
        secondary:
          "border-transparent bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300",
        success:
          "border-transparent bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
        destructive:
          "border-transparent bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
        warning:
          "border-transparent bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-300",
        outline:
          "border-neutral-300 text-neutral-700 dark:border-neutral-700 dark:text-neutral-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
