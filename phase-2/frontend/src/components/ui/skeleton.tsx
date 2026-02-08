/**
 * Skeleton Component
 *
 * Loading placeholder with shimmer animation for better perceived performance.
 *
 * @example
 * <Skeleton className="w-full h-12 rounded-lg" />
 * <Skeleton className="w-32 h-4 rounded" />
 */

import { cn } from "@/lib/utils";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-neutral-200 dark:bg-neutral-800",
        className
      )}
      {...props}
    />
  );
}

export { Skeleton };
