"""Check the latest session in the database"""
from sqlmodel import Session, create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    result = session.exec(text('''
        SELECT id, "userId", "expiresAt", "createdAt"
        FROM session
        ORDER BY "createdAt" DESC
        LIMIT 1
    '''))
    row = result.first()
    if row:
        print("Latest session:")
        print(f'  id: {row[0]}')
        print(f'  userId: {row[1]}')
        print(f'  expiresAt: {row[2]}')
        print(f'  createdAt: {row[3]}')

        # Check if the token from the response matches
        expected_token = "ICUYkPUbXkT2vvu02Y3MHGTj74BbCQvb"
        if row[0] == expected_token:
            print(f"\n✅ Token matches! The session ID is correct.")
        else:
            print(f"\n❌ Token mismatch!")
            print(f"   Expected: {expected_token}")
            print(f"   Got:      {row[0]}")
    else:
        print("No sessions found")
