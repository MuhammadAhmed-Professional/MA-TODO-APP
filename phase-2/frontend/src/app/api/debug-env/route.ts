/**
 * Debug endpoint to check environment variables
 * Access at: /api/debug-env
 */

export async function GET() {
  return Response.json({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "NOT SET",
    NEXT_PUBLIC_AUTH_URL: process.env.NEXT_PUBLIC_AUTH_URL || "NOT SET",
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || "NOT SET",
    NODE_ENV: process.env.NODE_ENV,
    VERCEL_ENV: process.env.VERCEL_ENV || "NOT SET",
  });
}
