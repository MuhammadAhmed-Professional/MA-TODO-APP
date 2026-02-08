"""Check the latest session with token field"""
from sqlmodel import Session, create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    # Check latest session with ALL fields including token
    result = session.exec(text('''
        SELECT id, token, "userId", "expiresAt", "createdAt"
        FROM session
        ORDER BY "createdAt" DESC
        LIMIT 1
    '''))
    row = result.first()
    if row:
        print("Latest session:")
        print(f'  id: {row[0]}')
        print(f'  token: {row[1]}')
        print(f'  userId: {row[2]}')
        print(f'  expiresAt: {row[3]}')
        print(f'  createdAt: {row[4]}')

        print(f"\nComparison:")
        print(f'  id == token: {row[0] == row[1]}')
    else:
        print("No sessions found")
