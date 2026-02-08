-- Add missing token column to session table
-- Required by Better Auth v1.4

ALTER TABLE "session" ADD COLUMN IF NOT EXISTS "token" TEXT;

-- Make token column UNIQUE and NOT NULL
UPDATE "session" SET "token" = "id" WHERE "token" IS NULL;
ALTER TABLE "session" ALTER COLUMN "token" SET NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS "session_token_idx" ON "session"("token");
