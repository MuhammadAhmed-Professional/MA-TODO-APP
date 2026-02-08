#!/usr/bin/env python3
"""
Database Migration Verification Script

This script verifies that all Phase III and Phase V migrations have been
applied correctly and the database schema is as expected.

Usage:
    cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO/phase-2/backend
    uv run python scripts/verify_migrations.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)

Exit Codes:
    0: All checks passed
    1: One or more checks failed
    2: Database connection error
"""

import os
import sys
from typing import List, Tuple

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print("ERROR: psycopg not installed. Install with: uv add psycopg")
    sys.exit(2)


def get_connection():
    """Get database connection from environment variable."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Export it with: export DATABASE_URL='postgresql://...'")
        sys.exit(2)

    try:
        conn = psycopg.connect(database_url, row_factory=dict_row)
        return conn
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(2)


def check_table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
        """, (table_name,))
        result = cur.fetchone()
        return result['exists']


def check_column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            );
        """, (table_name, column_name))
        result = cur.fetchone()
        return result['exists']


def check_index_exists(conn, index_name: str) -> bool:
    """Check if an index exists in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_indexes
                WHERE indexname = %s
            );
        """, (index_name,))
        result = cur.fetchone()
        return result['exists']


def check_constraint_exists(conn, table_name: str, constraint_name: str) -> bool:
    """Check if a constraint exists on a table."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.table_constraints
                WHERE table_name = %s AND constraint_name = %s
            );
        """, (table_name, constraint_name))
        result = cur.fetchone()
        return result['exists']


def verify_phase_iii_migrations(conn) -> Tuple[bool, List[str]]:
    """Verify Phase III migration (conversation tables)."""
    print("\n" + "=" * 60)
    print("PHASE III: Conversation Tables")
    print("=" * 60)

    checks_passed = []
    checks_failed = []

    # Check conversations table
    if check_table_exists(conn, 'conversations'):
        print("✅ conversations table exists")
        checks_passed.append("conversations table")

        # Check conversations columns
        required_columns = ['id', 'user_id', 'title', 'created_at', 'updated_at']
        for col in required_columns:
            if check_column_exists(conn, 'conversations', col):
                print(f"  ✅ conversations.{col} column exists")
                checks_passed.append(f"conversations.{col}")
            else:
                print(f"  ❌ conversations.{col} column MISSING")
                checks_failed.append(f"conversations.{col}")
    else:
        print("❌ conversations table MISSING")
        checks_failed.append("conversations table")

    # Check messages table
    if check_table_exists(conn, 'messages'):
        print("✅ messages table exists")
        checks_passed.append("messages table")

        # Check messages columns
        required_columns = ['id', 'conversation_id', 'user_id', 'role', 'content', 'tool_calls', 'created_at']
        for col in required_columns:
            if check_column_exists(conn, 'messages', col):
                print(f"  ✅ messages.{col} column exists")
                checks_passed.append(f"messages.{col}")
            else:
                print(f"  ❌ messages.{col} column MISSING")
                checks_failed.append(f"messages.{col}")
    else:
        print("❌ messages table MISSING")
        checks_failed.append("messages table")

    # Check indexes
    required_indexes = [
        'ix_conversations_user_id',
        'ix_conversations_user_id_created_at',
        'ix_messages_conversation_id',
        'ix_messages_conversation_id_created_at',
        'ix_messages_user_id',
        'ix_messages_user_id_created_at'
    ]
    for idx in required_indexes:
        if check_index_exists(conn, idx):
            print(f"  ✅ Index {idx} exists")
            checks_passed.append(f"Index {idx}")
        else:
            print(f"  ❌ Index {idx} MISSING")
            checks_failed.append(f"Index {idx}")

    return len(checks_failed) == 0, checks_failed


def verify_phase_v_migrations(conn) -> Tuple[bool, List[str]]:
    """Verify Phase V migrations (advanced features)."""
    print("\n" + "=" * 60)
    print("PHASE V: Advanced Features")
    print("=" * 60)

    checks_passed = []
    checks_failed = []

    # Check tasks table for new columns
    print("\n--- Tasks Table (Phase V Columns) ---")

    phase_v_columns = {
        'priority': 'Task priority (low, medium, high, urgent)',
        'due_date': 'Task deadline',
        'remind_at': 'Reminder timestamp',
        'recurrence_rule': 'Recurrence pattern (JSONB)'
    }

    for col, description in phase_v_columns.items():
        if check_column_exists(conn, 'tasks', col):
            print(f"✅ tasks.{col} column exists ({description})")
            checks_passed.append(f"tasks.{col}")
        else:
            print(f"❌ tasks.{col} column MISSING ({description})")
            checks_failed.append(f"tasks.{col}")

    # Check tags table
    print("\n--- Tags Tables ---")

    if check_table_exists(conn, 'tags'):
        print("✅ tags table exists")
        checks_passed.append("tags table")

        tag_columns = ['id', 'user_id', 'name', 'color', 'created_at', 'updated_at']
        for col in tag_columns:
            if check_column_exists(conn, 'tags', col):
                print(f"  ✅ tags.{col} column exists")
                checks_passed.append(f"tags.{col}")
            else:
                print(f"  ❌ tags.{col} column MISSING")
                checks_failed.append(f"tags.{col}")
    else:
        print("❌ tags table MISSING")
        checks_failed.append("tags table")

    # Check task_tags junction table
    if check_table_exists(conn, 'task_tags'):
        print("✅ task_tags junction table exists")
        checks_passed.append("task_tags table")

        task_tag_columns = ['task_id', 'tag_id', 'created_at']
        for col in task_tag_columns:
            if check_column_exists(conn, 'task_tags', col):
                print(f"  ✅ task_tags.{col} column exists")
                checks_passed.append(f"task_tags.{col}")
            else:
                print(f"  ❌ task_tags.{col} column MISSING")
                checks_failed.append(f"task_tags.{col}")
    else:
        print("❌ task_tags junction table MISSING")
        checks_failed.append("task_tags table")

    # Check recurring_tasks table
    print("\n--- Recurring Tasks Table ---")

    if check_table_exists(conn, 'recurring_tasks'):
        print("✅ recurring_tasks table exists")
        checks_passed.append("recurring_tasks table")

        recurring_columns = [
            'id', 'user_id', 'title', 'description', 'priority',
            'recurrence_rule', 'next_due_at', 'is_active', 'created_at', 'updated_at'
        ]
        for col in recurring_columns:
            if check_column_exists(conn, 'recurring_tasks', col):
                print(f"  ✅ recurring_tasks.{col} column exists")
                checks_passed.append(f"recurring_tasks.{col}")
            else:
                print(f"  ❌ recurring_tasks.{col} column MISSING")
                checks_failed.append(f"recurring_tasks.{col}")
    else:
        print("❌ recurring_tasks table MISSING")
        checks_failed.append("recurring_tasks table")

    # Check Phase V indexes
    print("\n--- Phase V Indexes ---")

    phase_v_indexes = [
        'ix_tasks_priority',
        'ix_tasks_due_date',
        'ix_tasks_remind_at',
        'ix_tasks_recurrence_rule',
        'ix_tags_user_id',
        'ix_tags_user_id_name',
        'ix_task_tags_task_id',
        'ix_task_tags_tag_id',
        'ix_task_tags_task_tag',
        'ix_recurring_tasks_user_id',
        'ix_recurring_tasks_user_id_next_due_at',
        'ix_recurring_tasks_is_active',
        'ix_recurring_tasks_recurrence_rule'
    ]

    for idx in phase_v_indexes:
        if check_index_exists(conn, idx):
            print(f"✅ Index {idx} exists")
            checks_passed.append(f"Index {idx}")
        else:
            print(f"❌ Index {idx} MISSING")
            checks_failed.append(f"Index {idx}")

    # Check constraints
    print("\n--- Phase V Constraints ---")

    constraints = [
        ('tasks', 'ck_tasks_priority_valid'),
        ('tags', 'ix_tags_user_id_name'),  # Unique constraint
        ('recurring_tasks', 'ck_recurring_tasks_priority_valid')
    ]

    for table_name, constraint_name in constraints:
        if check_constraint_exists(conn, table_name, constraint_name):
            print(f"✅ Constraint {constraint_name} exists on {table_name}")
            checks_passed.append(f"Constraint {constraint_name}")
        else:
            print(f"❌ Constraint {constraint_name} MISSING on {table_name}")
            checks_failed.append(f"Constraint {constraint_name}")

    return len(checks_failed) == 0, checks_failed


def main():
    """Main verification function."""
    print("=" * 60)
    print("DATABASE MIGRATION VERIFICATION")
    print("=" * 60)

    conn = get_connection()

    try:
        # Verify Phase III
        phase_iii_ok, phase_iii_failures = verify_phase_iii_migrations(conn)

        # Verify Phase V
        phase_v_ok, phase_v_failures = verify_phase_v_migrations(conn)

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        if phase_iii_ok and phase_v_ok:
            print("✅ ALL CHECKS PASSED")
            print("\n✅ Phase III (Conversation Tables): Complete")
            print("✅ Phase V (Advanced Features): Complete")
            return 0
        else:
            print("❌ SOME CHECKS FAILED")

            if not phase_iii_ok:
                print(f"\n❌ Phase III Failures ({len(phase_iii_failures)}):")
                for failure in phase_iii_failures:
                    print(f"   - {failure}")

            if not phase_v_ok:
                print(f"\n❌ Phase V Failures ({len(phase_v_failures)}):")
                for failure in phase_v_failures:
                    print(f"   - {failure}")

            print("\n💡 To fix failed migrations:")
            print("   1. Check migration status: uv run alembic current")
            print("   2. Apply pending migrations: uv run alembic upgrade head")
            print("   3. Verify migration chain: uv run alembic history")

            return 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
