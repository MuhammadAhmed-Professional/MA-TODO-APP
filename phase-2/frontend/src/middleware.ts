/**
 * Middleware Configuration
 *
 * Handles internationalization by:
 * 1. Detecting locale from Accept-Language header, cookie, or URL
 * 2. Redirecting to locale-prefixed URLs
 * 3. Preserving locale selection in cookies
 */

import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';

export default createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale matches
  defaultLocale,

  // Always use locale prefix (e.g., /en/tasks, /ur/tasks)
  localePrefix: 'always',

  // Detect locale from Accept-Language header
  localeDetection: true,
});

export const config = {
  // Match all pathnames except for
  // - API routes
  // - _next (Next.js internals)
  // - Static files (images, fonts, etc.)
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)'],
};
