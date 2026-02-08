/**
 * Button Component
 *
 * Versatile button component with multiple variants and sizes.
 * Built with Radix UI primitives and class-variance-authority.
 *
 * Accessibility:
 * - Keyboard accessible (Enter/Space)
 * - Focus visible indicators
 * - Disabled state properly announced
 * - Minimum 44x44px touch target
 *
 * @example
 * <Button variant="default" size="md">Click me</Button>
 * <Button variant="outline" size="sm" disabled>Disabled</Button>
 */

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  // Base styles - always applied
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:shadow-lg hover:from-blue-700 hover:to-purple-700 focus-visible:ring-blue-500",
        destructive:
          "bg-red-600 text-white shadow-md hover:bg-red-700 hover:shadow-lg focus-visible:ring-red-500",
        outline:
          "border-2 border-neutral-300 bg-transparent text-neutral-900 shadow-sm hover:bg-neutral-100 hover:border-neutral-400 focus-visible:ring-neutral-500 dark:border-neutral-700 dark:text-neutral-100 dark:hover:bg-neutral-800 dark:hover:border-neutral-600",
        secondary:
          "bg-neutral-100 text-neutral-900 shadow-sm hover:bg-neutral-200 focus-visible:ring-neutral-500 dark:bg-neutral-800 dark:text-neutral-100 dark:hover:bg-neutral-700",
        ghost:
          "text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900 focus-visible:ring-neutral-500 dark:text-neutral-300 dark:hover:bg-neutral-800 dark:hover:text-neutral-100",
        link:
          "text-blue-600 underline-offset-4 hover:underline focus-visible:ring-blue-500 dark:text-blue-400",
      },
      size: {
        sm: "h-9 px-3 text-xs",
        md: "h-11 px-5 text-sm min-h-[44px] min-w-[44px]", // Touch-friendly
        lg: "h-12 px-6 text-base min-h-[44px]",
        icon: "h-11 w-11 min-h-[44px] min-w-[44px]", // Perfect square, touch-friendly
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * If true, the button will render as a child component (for composition)
   */
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
