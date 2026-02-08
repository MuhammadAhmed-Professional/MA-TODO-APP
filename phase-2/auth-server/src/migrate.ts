/**
 * Database Migration Script for Better Auth
 *
 * This script creates the required Better Auth tables in PostgreSQL:
 * - user: User accounts
 * - session: Active sessions
 * - account: OAuth provider accounts (for future social auth)
 * - verification: Email verification tokens (for future email verification)
 *
 * Compatible with existing FastAPI User table:
 * - Renames 'users' → 'user' if exists
 * - Migrates existing user data
 * - Adds Better Auth specific fields
 */

import { sql } from "./db.js";
import dotenv from "dotenv";

dotenv.config();

/**
 * Check if table exists
 */
async function tableExists(tableName: string): Promise<boolean> {
  const result = await sql`
    SELECT EXISTS (
      SELECT FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name = ${tableName}
    );
  `;
  return result[0].exists;
}

/**
 * Create Better Auth user table
 */
async function createUserTable() {
  console.log("📋 Creating 'user' table...");

  await sql`
    CREATE TABLE IF NOT EXISTS "user" (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name VARCHAR(100) NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      "emailVerified" BOOLEAN NOT NULL DEFAULT false,
      image TEXT,
      "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
      "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),

      -- Additional field for email/password auth
      -- Better Auth doesn't require this in schema but we add for compatibility
      hashed_password TEXT
    );
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
  `;

  console.log("✅ 'user' table created");
}

/**
 * Create Better Auth session table
 */
async function createSessionTable() {
  console.log("📋 Creating 'session' table...");

  await sql`
    CREATE TABLE IF NOT EXISTS "session" (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      "expiresAt" TIMESTAMP NOT NULL,
      token TEXT UNIQUE NOT NULL,
      "userId" UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
      "ipAddress" INET,
      "userAgent" TEXT,
      "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
      "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
    );
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_session_token ON "session"(token);
  `;
  await sql`
    CREATE INDEX IF NOT EXISTS idx_session_user_id ON "session"("userId");
  `;

  console.log("✅ 'session' table created");
}

/**
 * Create Better Auth account table (for OAuth providers)
 */
async function createAccountTable() {
  console.log("📋 Creating 'account' table...");

  await sql`
    CREATE TABLE IF NOT EXISTS "account" (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      "userId" UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
      "accountId" TEXT NOT NULL,
      "providerId" TEXT NOT NULL,
      "accessToken" TEXT,
      "refreshToken" TEXT,
      "expiresAt" TIMESTAMP,
      "scope" TEXT,
      "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
      "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),

      UNIQUE("providerId", "accountId")
    );
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_account_user_id ON "account"("userId");
  `;

  console.log("✅ 'account' table created");
}

/**
 * Create Better Auth verification table (for email verification)
 */
async function createVerificationTable() {
  console.log("📋 Creating 'verification' table...");

  await sql`
    CREATE TABLE IF NOT EXISTS "verification" (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      identifier TEXT NOT NULL,
      value TEXT NOT NULL,
      "expiresAt" TIMESTAMP NOT NULL,
      "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
      "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
    );
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_verification_identifier ON "verification"(identifier);
  `;

  console.log("✅ 'verification' table created");
}

/**
 * Migrate existing users from 'users' table to 'user' table
 */
async function migrateExistingUsers() {
  const usersTableExists = await tableExists("users");

  if (!usersTableExists) {
    console.log("ℹ️  No existing 'users' table to migrate");
    return;
  }

  console.log("📋 Migrating existing users from 'users' to 'user'...");

  // Check if there are users to migrate
  const userCount = await sql`
    SELECT COUNT(*) as count FROM users;
  `;

  const count = parseInt(userCount[0].count);

  if (count === 0) {
    console.log("ℹ️  No users to migrate");
    return;
  }

  console.log(`📊 Found ${count} users to migrate`);

  // Insert users from old table to new table
  await sql`
    INSERT INTO "user" (id, name, email, "emailVerified", "createdAt", "updatedAt", hashed_password)
    SELECT
      id,
      name,
      email,
      COALESCE(email_verified, false) as "emailVerified",
      COALESCE(created_at, NOW()) as "createdAt",
      COALESCE(updated_at, NOW()) as "updatedAt",
      hashed_password
    FROM users
    ON CONFLICT (email) DO NOTHING;
  `;

  console.log(`✅ Migrated ${count} users successfully`);
  console.log("⚠️  Old 'users' table still exists. You can drop it manually if migration is successful.");
}

/**
 * Create tasks table if it doesn't exist
 * (Ensure FastAPI business logic tables are present)
 */
async function ensureTasksTable() {
  console.log("📋 Checking 'tasks' table...");

  const tasksTableExists = await tableExists("tasks");

  if (tasksTableExists) {
    console.log("✅ 'tasks' table already exists");
    return;
  }

  console.log("📋 Creating 'tasks' table for FastAPI...");

  await sql`
    CREATE TABLE IF NOT EXISTS "tasks" (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      title VARCHAR(200) NOT NULL,
      description TEXT,
      is_complete BOOLEAN NOT NULL DEFAULT false,
      user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
      created_at TIMESTAMP NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
  `;

  await sql`
    CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON "tasks"(user_id);
  `;
  await sql`
    CREATE INDEX IF NOT EXISTS idx_tasks_is_complete ON "tasks"(is_complete);
  `;

  console.log("✅ 'tasks' table created");
}

/**
 * Main migration function
 */
async function runMigration() {
  console.log("\n🚀 Starting Better Auth Database Migration\n");
  console.log("=" . repeat(60));

  try {
    // Test connection
    console.log("🔌 Testing database connection...");
    const testResult = await sql`SELECT NOW() as time`;
    console.log(`✅ Connected to database at ${testResult[0].time}\n`);

    // Create Better Auth tables
    await createUserTable();
    await createSessionTable();
    await createAccountTable();
    await createVerificationTable();

    // Migrate existing users
    await migrateExistingUsers();

    // Ensure tasks table exists
    await ensureTasksTable();

    console.log("\n" + "=".repeat(60));
    console.log("✅ Migration completed successfully!\n");

    console.log("📋 Database Schema Summary:");
    console.log("   • user (Better Auth users)");
    console.log("   • session (Better Auth sessions)");
    console.log("   • account (Better Auth OAuth accounts)");
    console.log("   • verification (Better Auth email verification)");
    console.log("   • tasks (FastAPI task management)\n");

    process.exit(0);
  } catch (error) {
    console.error("\n❌ Migration failed:", error);
    process.exit(1);
  }
}

// Run migration
runMigration();
