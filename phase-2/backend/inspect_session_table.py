"""Inspect session table structure and data"""
from sqlmodel import Session, create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_8WSLxbOhQf1a@ep-solitary-morning-a4vdcuab-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)

with Session(engine) as session:
    # Get table schema
    print("Session table columns:")
    result = session.exec(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'session'
        ORDER BY ordinal_position
    """))
    for row in result.all():
        print(f"  {row[0]}: {row[1]}")

    print("\nLatest 3 sessions (all columns):")
    result2 = session.exec(text("SELECT * FROM session ORDER BY \"createdAt\" DESC LIMIT 3"))
    # Get column names
    cols = list(result2.keys())
    print(f"Columns: {cols}")

    for i, row in enumerate(result2.all(), 1):
        print(f"\nSession {i}:")
        for j, col in enumerate(cols):
            value = row[j]
            if isinstance(value, str) and len(value) > 60:
                value = value[:60] + "..."
            print(f"  {col}: {value}")
