#!/usr/bin/env python3
"""
Add token column to session table
"""

import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

sql_file = Path(__file__).parent / "migrations" / "002_add_session_token.sql"
with open(sql_file, "r") as f:
    sql = f.read()

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print(f"Running migration: {sql_file.name}")
cursor.execute(sql)

# Verify column was added
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'session' AND column_name = 'token';
""")
result = cursor.fetchone()

if result:
    print("\nMigration completed successfully!")
    print(f"Added column: {result[0]} ({result[1]}, nullable: {result[2]})")
else:
    print("\nERROR: Column not added!")

cursor.close()
conn.close()
