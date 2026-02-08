"""Check if specific session token exists"""
from sqlmodel import Session, create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

# Token from latest login (with debug logging)
token = "C6VgqxLfXcK4upZdq7hnfdsigktmxkH2"

with Session(engine) as session:
    result = session.exec(text(f'''
        SELECT id, "userId", "expiresAt", "createdAt"
        FROM session
        WHERE id = '{token}'
    '''))
    row = result.first()
    if row:
        print("Session found!")
        print(f'  id: {row[0]}')
        print(f'  userId: {row[1]}')
        print(f'  expiresAt: {row[2]}')
        print(f'  createdAt: {row[3]}')
    else:
        print(f"Session not found for token: {token}")
        print("\nSearching for recent sessions (last 10)...")
        result2 = session.exec(text('''
            SELECT id, "userId", "expiresAt", "createdAt"
            FROM session
            ORDER BY "createdAt" DESC
            LIMIT 10
        '''))
        rows = result2.all()
        for i, row in enumerate(rows, 1):
            print(f'{i}. id={row[0]}, createdAt={row[3]}')
