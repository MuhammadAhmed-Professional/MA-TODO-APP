#!/usr/bin/env python3
"""
Run Better Auth database migration
Creates all required tables for Better Auth in Neon PostgreSQL
"""

import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Read SQL migration file
sql_file = Path(__file__).parent / "migrations" / "001_create_better_auth_schema.sql"
with open(sql_file, "r") as f:
    sql = f.read()

# Execute migration
print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print(f"Running migration: {sql_file.name}")
cursor.execute(sql)

# Verify tables were created
cursor.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
    ORDER BY table_name;
""")
tables = cursor.fetchall()

print("\nMigration completed successfully!")
print("\nCreated tables:")
for table in tables:
    print(f"   - {table[0]}")

cursor.close()
conn.close()

print("\nBetter Auth database schema is ready!")
