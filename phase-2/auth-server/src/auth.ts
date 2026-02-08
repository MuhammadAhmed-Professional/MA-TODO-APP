/**
 * Better Auth Configuration
 *
 * Configures Better Auth with:
 * - Email/password authentication
 * - SQLite database (direct connection)
 * - JWT tokens (compatible with FastAPI validation)
 * - Cookie-based session storage
 */

import { betterAuth } from "better-auth";
import { Pool } from "pg";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Validate required environment variables
const REQUIRED_ENV_VARS = ["BETTER_AUTH_SECRET", "DATABASE_URL"];
for (const envVar of REQUIRED_ENV_VARS) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}

/**
 * Better Auth Instance
 *
 * Configured with PostgreSQL using connection string
 * Better Auth will handle Kysely setup internally
 */
export const auth = betterAuth({
  /**
   * Application Configuration
   */
  appName: "Phase II Todo Application",
  baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3001",
  // basePath defaults to "/api/auth" - we mount at root "/" in server.ts

  /**
   * Secret for JWT token signing
   * CRITICAL: Must match backend JWT_SECRET for token validation
   */
  secret: process.env.BETTER_AUTH_SECRET!,

  /**
   * Database Configuration
   * Pass Pool instance directly - Better Auth wraps it with Kysely internally
   * @see https://www.better-auth.com/docs/adapters/postgresql
   */
  database: new Pool({
    connectionString: process.env.DATABASE_URL!,
    ssl: process.env.NODE_ENV === "production" ? { rejectUnauthorized: false } : false,
  }),

  /**
   * Email and Password Authentication
   */
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 6,
    requireEmailVerification: false,
    autoSignIn: true,
  },

  /**
   * Session Configuration
   */
  session: {
    expiresIn: 60 * 15, // 15 minutes
    updateAge: 60 * 5, // Update if older than 5 minutes
  },

  /**
   * CORS Configuration
   */
  trustedOrigins: [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://talal-s-tda.vercel.app",
    "https://talal-s-tda-production.up.railway.app", // Backend needs to proxy requests
  ],

  /**
   * Rate Limiting
   * TEMPORARILY DISABLED for testing (was causing login timeouts)
   */
  rateLimit: {
    enabled: false, // Disabled to eliminate rate limiting as timeout cause
    window: 60,
    max: 10,
  },
});

/**
 * Type exports for TypeScript support
 */
export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
