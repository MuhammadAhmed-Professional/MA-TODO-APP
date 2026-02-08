/**
 * Better Auth Express Server
 *
 * Standalone authentication server that handles:
 * - User signup (POST /auth/signup)
 * - User login (POST /auth/login)
 * - User logout (POST /auth/logout)
 * - Session management (GET /auth/session)
 * - JWT token generation
 *
 * Works in tandem with FastAPI backend:
 * - Better Auth: Authentication endpoints
 * - FastAPI: Business logic (tasks CRUD)
 * - Shared: Same database, same JWT secret
 */

import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import dotenv from "dotenv";
import { auth } from "./auth.js";
import { testConnection } from "./db.js";
import { toNodeHandler } from "better-auth/node";

// Load environment variables
dotenv.config();

/**
 * Express Application
 */
const app = express();

/**
 * Middleware Configuration
 */

// CORS Configuration
// Allow frontend AND backend to make authenticated cross-origin requests
const CORS_ORIGINS = process.env.CORS_ORIGINS?.split(",") || [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "https://frontend-six-coral-90.vercel.app",
  "https://backend-production-9a40.up.railway.app",
];

console.log("🌐 CORS Origins:", CORS_ORIGINS);

app.use(
  cors({
    origin: CORS_ORIGINS,
    credentials: true, // Required for cookies
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);

/**
 * Request Logging Middleware (Development)
 */
if (process.env.NODE_ENV !== "production") {
  app.use((req: Request, res: Response, next: NextFunction) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
  });
}

/**
 * Health Check Endpoints
 */
app.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    service: "better-auth-server",
    version: "1.0.1",  // Updated after Kysely fix
  });
});

// Railway healthcheck endpoint
app.get("/api/auth/health", (req: Request, res: Response) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    service: "better-auth-server",
    version: "1.0.1",  // Updated after Kysely fix
  });
});

// Debug middleware: log all incoming requests
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

/**
 * Better Auth Routes
 *
 * CRITICAL: Mounted BEFORE express.json() middleware
 * Better Auth needs raw request bodies for authentication
 *
 * Using app.all() with wildcard route per Better Auth docs
 * @see https://www.better-auth.com/docs/integrations/express
 *
 * Provides endpoints:
 * - POST /api/auth/sign-up (create account)
 * - POST /api/auth/sign-in/email (login)
 * - POST /api/auth/sign-out (logout)
 * - GET /api/auth/get-session (current user)
 */
app.all("/api/auth/*", toNodeHandler(auth));

/**
 * JSON Body Parser
 *
 * IMPORTANT: Placed AFTER Better Auth to avoid consuming request stream
 */
app.use(express.json());

/**
 * 404 Handler
 */
app.use((req: Request, res: Response) => {
  res.status(404).json({
    error: "Not Found",
    message: `Cannot ${req.method} ${req.path}`,
    availableRoutes: [
      "GET /health",
      "POST /api/auth/sign-up",
      "POST /api/auth/sign-in/email",
      "POST /api/auth/sign-out",
      "GET /api/auth/get-session",
    ],
  });
});

/**
 * Global Error Handler
 */
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error("❌ Server error:", err);
  res.status(500).json({
    error: "Internal Server Error",
    message:
      process.env.NODE_ENV === "production"
        ? "An unexpected error occurred"
        : err.message,
  });
});

/**
 * Server Startup
 */
const PORT = parseInt(process.env.PORT || "3001", 10);

async function startServer() {
  try {
    console.log("🔌 Testing database connection...");
    const connected = await testConnection();

    if (!connected) {
      throw new Error("Database connection failed");
    }

    console.log("🔧 Initializing Better Auth...");
    // Try to initialize auth to see the exact error
    try {
      const testHandler = auth.handler;
      console.log("✅ Better Auth initialized successfully");
    } catch (authError) {
      console.error("❌ Better Auth initialization failed:");
      console.error("Error:", authError);
      if (authError instanceof Error) {
        console.error("Message:", authError.message);
        console.error("Stack:", authError.stack);
        console.error("Cause:", authError.cause);
      }
      throw authError;
    }

    // Start Express server
    app.listen(PORT, () => {
      console.log(`\n✅ Better Auth server started successfully\n`);
      console.log(`   Port: ${PORT}`);
      console.log(`   Base URL: ${process.env.BETTER_AUTH_URL}`);
      console.log(`   Environment: ${process.env.NODE_ENV || "development"}`);
      console.log(`   CORS Origins: ${CORS_ORIGINS.join(", ")}`);
      console.log(`\n📋 Available Endpoints:`);
      console.log(`   GET  /health                 - Health check`);
      console.log(`   POST /auth/sign-up           - Create account`);
      console.log(`   POST /auth/sign-in/email     - Login`);
      console.log(`   POST /auth/sign-out          - Logout`);
      console.log(`   GET  /auth/get-session       - Current user\n`);
    });
  } catch (error) {
    console.error("❌ Failed to start server:", error);
    if (error instanceof Error) {
      console.error("❌ Error message:", error.message);
      console.error("❌ Error stack:", error.stack);
      console.error("❌ Error cause:", error.cause);
    }
    process.exit(1);
  }
}

// Start the server
startServer();

/**
 * Graceful Shutdown
 */
process.on("SIGTERM", () => {
  console.log("\n⚠️  SIGTERM received, shutting down gracefully...");
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("\n⚠️  SIGINT received, shutting down gracefully...");
  process.exit(0);
});
