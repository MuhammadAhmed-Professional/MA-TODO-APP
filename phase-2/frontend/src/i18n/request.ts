/**
 * Request Locale Configuration
 *
 * Handles locale detection from incoming requests for next-intl.
 * Priority: URL parameter > Cookie > Accept-Language header > Default
 */

import { getRequestConfig } from 'next-intl/server';
import { locales, defaultLocale, type Locale } from './config';

export default getRequestConfig(async ({ requestLocale }) => {
  // This typically corresponds to the `[locale]` segment
  let locale = await requestLocale;

  // Validate that the incoming locale parameter is valid
  if (!locale || !locales.includes(locale as Locale)) {
    locale = defaultLocale;
  }

  return {
    locale,
    messages: (await import(`@/locales/${locale}.json`)).default,
  };
});
