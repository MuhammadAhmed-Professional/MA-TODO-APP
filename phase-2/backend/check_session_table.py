"""Quick script to check session table structure"""
from sqlmodel import Session, create_engine, text
import os

DATABASE_URL = "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    # Query the session table to see what columns exist
    result = session.exec(text('''
        SELECT id, "userId", "expiresAt", "createdAt", "updatedAt", "ipAddress", "userAgent"
        FROM session
        ORDER BY "createdAt" DESC
        LIMIT 5
    '''))
    rows = result.all()
    if rows:
        print(f'Found {len(rows)} sessions\n')
        for i, row in enumerate(rows, 1):
            print(f'Session {i}:')
            print(f'  id: {row[0]}')
            print(f'  userId: {row[1]}')
            print(f'  expiresAt: {row[2]}')
            print(f'  createdAt: {row[3]}')
            print(f'  updatedAt: {row[4]}')
            print(f'  ipAddress: {row[5]}')
            print(f'  userAgent: {row[6]}')
            print()
    else:
        print('No sessions found')
