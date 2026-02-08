/**
 * Language Switcher Component
 *
 * Dropdown component for switching between supported languages.
 * Persists selection in a cookie and updates the URL.
 */

"use client";

import { useLocale, useTranslations } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Globe } from 'lucide-react';
import { locales, localeNames, type Locale } from '@/i18n/config';
import { useState, useTransition } from 'react';

export function LanguageSwitcher() {
  const t = useTranslations('settings');
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();
  const [open, setOpen] = useState(false);

  const handleLanguageChange = (newLocale: Locale) => {
    // Close the dropdown
    setOpen(false);

    // Start the transition
    startTransition(() => {
      // Get the current pathname without the locale prefix
      const segments = pathname.split('/');
      const currentLocale = segments[1];

      // Build the new pathname
      let newPathname: string;
      if (segments.length > 1 && locales.includes(currentLocale as Locale)) {
        // Replace the current locale with the new one
        segments[1] = newLocale;
        newPathname = segments.join('/');
      } else {
        // No locale prefix, add the new one
        newPathname = `/${newLocale}${pathname}`;
      }

      // Navigate to the new locale
      router.push(newPathname);
    });
  };

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="relative h-9 w-9"
          disabled={isPending}
        >
          <Globe className="h-4 w-4" />
          <span className="sr-only">{t('language')}</span>
          {isPending && (
            <div className="absolute inset-0 flex items-center justify-center bg-background/50">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {locales.map((loc) => (
          <DropdownMenuItem
            key={loc}
            onClick={() => handleLanguageChange(loc)}
            className={locale === loc ? 'bg-accent' : ''}
          >
            <span className="flex-1">{localeNames[loc]}</span>
            {locale === loc && (
              <span className="text-xs text-muted-foreground">✓</span>
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
