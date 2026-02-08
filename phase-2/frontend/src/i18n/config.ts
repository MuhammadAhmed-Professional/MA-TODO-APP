/**
 * i18n Configuration
 *
 * Internationalization configuration for next-intl.
 * Supports English (en) and Urdu (ur) locales.
 */

export const locales = ['en', 'ur'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ur: 'اردو',
};

export const localeDirections: Record<Locale, 'ltr' | 'rtl'> = {
  en: 'ltr',
  ur: 'rtl',
};

export function getLocaleDirection(locale: Locale): 'ltr' | 'rtl' {
  return localeDirections[locale];
}

export function isLocale(locale: string): locale is Locale {
  return locales.includes(locale as Locale);
}

export function getLocaleFromPathname(pathname: string): Locale {
  const segments = pathname.split('/');
  const locale = segments[1];

  if (isLocale(locale)) {
    return locale;
  }

  return defaultLocale;
}
