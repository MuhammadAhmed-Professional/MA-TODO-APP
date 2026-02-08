/**
 * Select Component (shadcn/ui compatible)
 *
 * Minimal select dropdown component.
 */

"use client";

import * as React from "react";

interface SelectContextValue {
  value?: string;
  onValueChange?: (value: string) => void;
  disabled?: boolean;
}

const SelectContext = React.createContext<SelectContextValue>({});

export interface SelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  disabled?: boolean;
  children: React.ReactNode;
}

export function Select({
  value,
  onValueChange,
  disabled = false,
  children,
}: SelectProps) {
  return (
    <SelectContext.Provider value={{ value, onValueChange, disabled }}>
      {children}
    </SelectContext.Provider>
  );
}

export interface SelectTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
}

export const SelectTrigger = React.forwardRef<
  HTMLButtonElement,
  SelectTriggerProps
>(({ children, className = "", ...props }, ref) => {
  const { disabled } = React.useContext(SelectContext);
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <button
      ref={ref}
      type="button"
      disabled={disabled}
      onClick={() => setIsOpen(!isOpen)}
      className={`inline-flex items-center justify-between rounded-md border border-neutral-300 bg-white px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-50 dark:border-neutral-700 dark:bg-neutral-900 ${className}`}
      data-open={isOpen}
      {...props}
    >
      {children}
    </button>
  );
});
SelectTrigger.displayName = "SelectTrigger";

export interface SelectValueProps {
  placeholder?: string;
}

export function SelectValue({ placeholder }: SelectValueProps) {
  const { value } = React.useContext(SelectContext);
  return <span>{value || placeholder || "Select..."}</span>;
}

export interface SelectContentProps {
  children: React.ReactNode;
  className?: string;
}

export function SelectContent({ children, className = "" }: SelectContentProps) {
  return (
    <div
      className={`absolute z-50 mt-1 max-h-60 overflow-auto rounded-md border border-neutral-200 bg-white shadow-lg dark:border-neutral-700 dark:bg-neutral-900 ${className}`}
    >
      {children}
    </div>
  );
}

export interface SelectItemProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export function SelectItem({ value, children, className = "" }: SelectItemProps) {
  const { onValueChange, value: selectedValue } = React.useContext(SelectContext);
  const isSelected = value === selectedValue;

  return (
    <div
      onClick={() => onValueChange?.(value)}
      className={`cursor-pointer px-3 py-2 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-800 ${
        isSelected ? "bg-neutral-100 dark:bg-neutral-800" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
}
