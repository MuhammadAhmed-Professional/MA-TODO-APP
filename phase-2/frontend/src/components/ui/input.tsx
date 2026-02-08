/**
 * Input Component
 *
 * Styled text input with proper focus states and accessibility.
 *
 * Accessibility:
 * - Always pair with a <label> element
 * - Focus indicators meet WCAG 2.1 AA (2px solid)
 * - Error states announced via aria-invalid
 *
 * @example
 * <label htmlFor="email">Email</label>
 * <Input id="email" type="email" placeholder="you@example.com" />
 */

import * as React from "react";

import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-lg border border-neutral-300 bg-white px-4 py-2 text-sm text-neutral-900 placeholder:text-neutral-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-100 dark:placeholder:text-neutral-500 dark:focus:border-blue-400 dark:focus:ring-blue-400",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
