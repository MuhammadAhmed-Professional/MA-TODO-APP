/**
 * Theme Provider
 *
 * Wraps the application with next-themes for dark mode support.
 * Provides system preference detection and manual theme switching.
 */

"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
