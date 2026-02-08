/**
 * Header Component
 *
 * Top navigation bar with:
 * - Logo and app name
 * - Add Task button
 * - Language switcher
 * - Theme toggle
 * - User menu with profile and logout
 */

"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useTranslations, useLocale } from "next-intl";
import { CheckCircle2, Plus, User, LogOut, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageSwitcher } from "@/components/layout/LanguageSwitcher";
import { signOut } from "@/lib/auth";
import { getAuthToken } from "@/lib/token-storage";
import { fetchAPI } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

interface HeaderProps {
  onAddTask?: () => void;
}

export function Header({ onAddTask }: HeaderProps) {
  const t = useTranslations('nav');
  const router = useRouter();
  const locale = useLocale();
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      try {
        const token = getAuthToken();
        if (!token) {
          setIsLoading(false);
          return;
        }
        const userData = await fetchAPI<{ id: string; name: string; email: string }>("/api/auth/get-session");
        setUser(userData);
      } catch (error) {
        console.error("Failed to load user:", error);
      } finally {
        setIsLoading(false);
      }
    }
    loadUser();
  }, []);

  const handleLogout = async () => {
    try {
      await signOut();
      toast.success("Logged out successfully");
      router.push(`/${locale}/login`);
    } catch (error) {
      toast.error("Failed to logout");
      console.error("Logout error:", error);
    }
  };

  // Get user initials for avatar
  const getUserInitials = () => {
    if (!user?.name) return "U";
    const names = user.name.split(" ");
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase();
    }
    return user.name[0].toUpperCase();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-200/50 bg-white/80 backdrop-blur-xl dark:border-neutral-800/50 dark:bg-neutral-900/80">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo and Brand */}
        <Link
          href={`/${locale}/dashboard`}
          className="flex items-center gap-2 transition-opacity hover:opacity-80"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <CheckCircle2 className="h-5 w-5 text-white" />
          </div>
          <span className="hidden text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent sm:inline-block">
            TaskFlow
          </span>
        </Link>

        {/* Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Chat Button */}
          <Button
            asChild
            variant="outline"
            size="sm"
            className="gap-1"
          >
            <Link href={`/${locale}/chat`}>
              <MessageSquare className="h-4 w-4 sm:mr-1" />
              <span className="hidden sm:inline">{t('chat')}</span>
            </Link>
          </Button>

          {/* Add Task Button */}
          {onAddTask && (
            <Button
              onClick={onAddTask}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-md hover:shadow-lg transition-all duration-200"
              size="sm"
            >
              <Plus className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">{t('tasks')}</span>
            </Button>
          )}

          {/* Language Switcher */}
          <LanguageSwitcher />

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                className="relative h-9 w-9 rounded-full border-2 border-neutral-200 dark:border-neutral-800"
                disabled={isLoading}
              >
                {isLoading ? (
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-600" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-xs font-semibold text-white">
                    {getUserInitials()}
                  </div>
                )}
                <span className="sr-only">User menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">
                    {user?.name || "User"}
                  </p>
                  <p className="text-xs leading-none text-neutral-500 dark:text-neutral-400">
                    {user?.email || "user@example.com"}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href={`/${locale}/dashboard`} className="cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  <span>{t('dashboard')}</span>
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={handleLogout}
                className="cursor-pointer text-red-600 focus:text-red-600 dark:text-red-400 dark:focus:text-red-400"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span>{t('logout')}</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
