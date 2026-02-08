/**
 * Database Connection Test for Better Auth
 *
 * Tests PostgreSQL connection since Better Auth handles
 * the database setup and migrations internally.
 */

import dotenv from "dotenv";
import postgres from "postgres";

// Load environment variables
dotenv.config();

/**
 * Test PostgreSQL database connection
 * Verifies DATABASE_URL is set and can connect
 */
export async function testConnection(): Promise<boolean> {
  try {
    const databaseUrl = process.env.DATABASE_URL;

    if (!databaseUrl) {
      console.error("❌ DATABASE_URL environment variable is not set");
      return false;
    }

    console.log("🔌 Testing PostgreSQL connection...");

    // Test connection with a simple query
    const sql = postgres(databaseUrl, {
      max: 1, // Only need one connection for testing
      idle_timeout: 20,
      connect_timeout: 10,
    });

    // Test with a simple query
    await sql`SELECT 1 as test`;

    // Close the test connection
    await sql.end();

    console.log("✅ PostgreSQL connection successful");
    console.log("✅ Better Auth will handle database initialization");
    return true;
  } catch (error) {
    console.error("❌ PostgreSQL connection failed:");
    console.error(error);
    return false;
  }
}
