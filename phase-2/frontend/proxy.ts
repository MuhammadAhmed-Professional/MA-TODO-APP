import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * Next.js Middleware for Route Protection
 *
 * Protects dashboard routes and redirects unauthenticated users to login.
 * Redirects authenticated users away from auth pages.
 *
 * @see https://nextjs.org/docs/app/building-your-application/routing/middleware
 */

export function proxy(request: NextRequest) {
  // Check for auth_token cookie (set by Better Auth via FastAPI backend)
  const authToken = request.cookies.get("auth_token");
  const isAuthenticated = !!authToken;

  const { pathname } = request.nextUrl;

  // Protect dashboard routes
  if (pathname.startsWith("/dashboard")) {
    if (!isAuthenticated) {
      // Redirect to login if not authenticated
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("redirect", pathname); // Preserve redirect path
      return NextResponse.redirect(loginUrl);
    }
  }

  // Redirect authenticated users away from auth pages
  if (pathname.startsWith("/login") || pathname.startsWith("/signup")) {
    if (isAuthenticated) {
      // Redirect to dashboard if already authenticated
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
  }

  return NextResponse.next();
}

/**
 * Middleware configuration
 *
 * Specifies which routes to run middleware on.
 * Uses matcher to avoid running on static files, API routes, etc.
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, fonts, etc.)
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
