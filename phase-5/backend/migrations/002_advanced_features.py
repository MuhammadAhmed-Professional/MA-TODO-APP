"""
Database Migration: Advanced Features (Phase V)

Migration to add:
- due_date, remind_at, priority, category_id columns to tasks table
- recurring_tasks table
- task_reminders table
- task_categories table
"""

import os
from datetime import datetime
import uuid
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import text

from src.models.task import Task
from src.models.advanced_task import (
    RecurringTask,
    TaskReminder,
    TaskCategory,
)


def upgrade():
    """
    Apply migration: Add advanced feature columns and tables.

    Run this to upgrade the database schema.
    """
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://todo_user:todo_password@localhost:5432/todo_db",
    )
    engine = create_engine(database_url)

    with Session(engine) as session:
        # Add columns to tasks table
        session.exec(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS due_date TIMESTAMP NULL,
            ADD COLUMN IF NOT EXISTS remind_at TIMESTAMP NULL,
            ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'medium',
            ADD COLUMN IF NOT EXISTS category_id VARCHAR(255) NULL;
        """))

        # Add indexes for new columns
        session.exec(text("""
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_tasks_remind_at ON tasks(remind_at);
            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
            CREATE INDEX IF NOT EXISTS idx_tasks_category_id ON tasks(category_id);
        """))

        # Create recurring_tasks table
        session.exec(text("""
            CREATE TABLE IF NOT EXISTS recurring_tasks (
                id VARCHAR(255) PRIMARY KEY,
                task_id VARCHAR(255) NOT NULL UNIQUE REFERENCES tasks(id) ON DELETE CASCADE,
                frequency VARCHAR(20) NOT NULL,
                interval INTEGER NOT NULL DEFAULT 1,
                next_due_at TIMESTAMP NULL,
                cron_expression VARCHAR(100) NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        session.exec(text("""
            CREATE INDEX IF NOT EXISTS idx_recurring_tasks_task_id ON recurring_tasks(task_id);
            CREATE INDEX IF NOT EXISTS idx_recurring_tasks_is_active ON recurring_tasks(is_active);
        """))

        # Create task_reminders table
        session.exec(text("""
            CREATE TABLE IF NOT EXISTS task_reminders (
                id VARCHAR(255) PRIMARY KEY,
                task_id VARCHAR(255) NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                remind_at TIMESTAMP NOT NULL,
                is_sent BOOLEAN DEFAULT FALSE,
                notification_type VARCHAR(20) DEFAULT 'in_app',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                sent_at TIMESTAMP NULL
            );
        """))

        session.exec(text("""
            CREATE INDEX IF NOT EXISTS idx_task_reminders_task_id ON task_reminders(task_id);
            CREATE INDEX IF NOT EXISTS idx_task_reminders_is_sent ON task_reminders(is_sent);
        """))

        # Create task_categories table
        session.exec(text("""
            CREATE TABLE IF NOT EXISTS task_categories (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
                name VARCHAR(50) NOT NULL,
                color VARCHAR(7) DEFAULT '#3b82f6',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """))

        session.exec(text("""
            CREATE INDEX IF NOT EXISTS idx_task_categories_user_id ON task_categories(user_id);
        """))

        session.commit()
        print("Migration completed successfully!")


def downgrade():
    """
    Rollback migration: Remove advanced feature columns and tables.

    Run this to rollback the database schema.
    """
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://todo_user:todo_password@localhost:5432/todo_db",
    )
    engine = create_engine(database_url)

    with Session(engine) as session:
        # Drop tables
        session.exec(text("DROP TABLE IF EXISTS task_reminders CASCADE;"))
        session.exec(text("DROP TABLE IF EXISTS recurring_tasks CASCADE;"))
        session.exec(text("DROP TABLE IF EXISTS task_categories CASCADE;"))

        # Remove columns from tasks table
        session.exec(text("""
            ALTER TABLE tasks
            DROP COLUMN IF EXISTS due_date,
            DROP COLUMN IF EXISTS remind_at,
            DROP COLUMN IF EXISTS priority,
            DROP COLUMN IF EXISTS category_id;
        """))

        session.commit()
        print("Rollback completed successfully!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
