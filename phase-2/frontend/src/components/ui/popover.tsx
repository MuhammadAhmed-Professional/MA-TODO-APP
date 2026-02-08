/**
 * Popover Component (shadcn/ui compatible)
 *
 * Minimal popover/dropdown component.
 */

"use client";

import * as React from "react";

interface PopoverContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const PopoverContext = React.createContext<PopoverContextValue>({
  open: false,
  onOpenChange: () => {},
});

export interface PopoverProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

export function Popover({ open = false, onOpenChange, children }: PopoverProps) {
  const [internalOpen, setInternalOpen] = React.useState(open);

  const isControlled = onOpenChange !== undefined;
  const isOpen = isControlled ? open : internalOpen;
  const setIsOpen = isControlled ? onOpenChange : setInternalOpen;

  React.useEffect(() => {
    if (!isControlled) {
      setInternalOpen(open);
    }
  }, [open, isControlled]);

  return (
    <PopoverContext.Provider value={{ open: isOpen, onOpenChange: setIsOpen }}>
      <div className="relative inline-block">{children}</div>
    </PopoverContext.Provider>
  );
}

export interface PopoverTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
}

export function PopoverTrigger({ asChild, children }: PopoverTriggerProps) {
  const { open, onOpenChange } = React.useContext(PopoverContext);

  if (asChild && React.isValidElement(children)) {
    const childProps = children.props as any;
    return React.cloneElement(children, {
      onClick: (e: React.MouseEvent) => {
        e.preventDefault();
        onOpenChange(!open);
        // Call original onClick if exists
        if (childProps?.onClick) {
          childProps.onClick(e);
        }
      },
    } as any);
  }

  return (
    <button type="button" onClick={() => onOpenChange(!open)}>
      {children}
    </button>
  );
}

export interface PopoverContentProps {
  children: React.ReactNode;
  className?: string;
  align?: "start" | "center" | "end";
}

export function PopoverContent({
  children,
  className = "",
  align = "center",
}: PopoverContentProps) {
  const { open, onOpenChange } = React.useContext(PopoverContext);
  const contentRef = React.useRef<HTMLDivElement>(null);

  // Close on click outside
  React.useEffect(() => {
    if (!open) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        contentRef.current &&
        !contentRef.current.contains(event.target as Node)
      ) {
        onOpenChange(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open, onOpenChange]);

  if (!open) return null;

  const alignClass = {
    start: "left-0",
    center: "left-1/2 -translate-x-1/2",
    end: "right-0",
  }[align];

  return (
    <div
      ref={contentRef}
      className={`absolute z-50 mt-2 rounded-md border border-neutral-200 bg-white p-4 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 ${alignClass} ${className}`}
    >
      {children}
    </div>
  );
}
