# Database Migrations Guide

**Project**: Todo Chatbot - Backend (FastAPI / SQLModel)
**Database**: PostgreSQL (Neon Serverless)
**Migration Tool**: Alembic

---

## Overview

This document describes the database migration strategy for Phase III (Conversation features) and Phase V (Advanced Task features).

### Migration Status

| Phase | Description | Status | Migration File |
|-------|-------------|--------|----------------|
| III | Conversation Tables | ✅ Complete | `003_add_conversation_tables.py` |
| V | Task Priority | ✅ Complete | `20250131_add_priority_to_tasks.py` |
| V | Task Due Dates | ✅ Complete | `20250131_add_due_dates_to_tasks.py` |
| V | Task Reminders | ✅ Complete | `20250131_add_reminders_to_tasks.py` |
| V | Task Recurrence | ✅ Complete | `20250131_add_recurrence_to_tasks.py` |
| V | Tags System | ✅ Complete | `20250131_add_tags_tables.py` |
| V | Recurring Tasks | ✅ Complete | `20250131_add_recurring_tasks_table.py` |

---

## Migration Chain

```
ea3540bc87e7 (users table)
    ↓
ba7aa1f810b4 (tasks table)
    ↓
7582d33c41bc (performance indexes)
    ↓
003_add_conversation_tables (Phase III)
    ↓
5b9aae697899 (change task IDs from UUID to TEXT)
    ↓
20250131_add_priority_to_tasks (Phase V)
    ↓
20250131_add_due_dates_to_tasks
    ↓
20250131_add_reminders_to_tasks
    ↓
20250131_add_recurrence_to_tasks
    ↓
20250131_add_tags_tables
    ↓
20250131_add_recurring_tasks_table (HEAD)
```

---

## Phase III: Conversation Tables ✅

**Status**: Already implemented in `003_add_conversation_tables.py`

### Tables

#### `conversations`
Stores chat conversation sessions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Foreign key to user.id |
| title | VARCHAR(255) | Optional conversation title |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes**:
- `ix_conversations_user_id` - Query user's conversations
- `ix_conversations_user_id_created_at` - Sorted conversation list

#### `messages`
Stores individual messages within conversations.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| conversation_id | UUID | Foreign key to conversations.id |
| user_id | UUID | Foreign key to user.id |
| role | VARCHAR | 'user', 'assistant', or 'system' |
| content | TEXT | Message content |
| tool_calls | JSON | Optional tool call data |
| created_at | TIMESTAMP | Message timestamp |

**Indexes**:
- `ix_messages_conversation_id` - Query messages in conversation
- `ix_messages_conversation_id_created_at` - Chronological message order
- `ix_messages_user_id` - Query user's messages
- `ix_messages_user_id_created_at` - User's message history

---

## Phase V: Advanced Features ✅

### 1. Task Priority

**Migration**: `20250131_add_priority_to_tasks.py`

**Schema**:
```sql
ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'
CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
```

**Usage**:
```python
# Get high-priority tasks
high_priority = session.exec(
    select(Task).where(Task.priority == 'high')
).all()

# Sort by priority (custom order)
priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
tasks.sort(key=lambda t: priority_order[t.priority])
```

**API Example**:
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Fix critical bug",
  "priority": "urgent",
  "due_date": "2025-02-01T10:00:00Z"
}
```

---

### 2. Task Due Dates

**Migration**: `20250131_add_due_dates_to_tasks.py`

**Schema**:
```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP;
```

**Usage**:
```python
from datetime import datetime, timedelta

# Get overdue tasks
overdue = session.exec(
    select(Task).where(
        Task.due_date < datetime.utcnow(),
        Task.is_complete == False
    )
).all()

# Get tasks due today
today = datetime.utcnow().replace(hour=0, minute=0, second=0)
tomorrow = today + timedelta(days=1)
due_today = session.exec(
    select(Task).where(
        Task.due_date >= today,
        Task.due_date < tomorrow
    )
).all()
```

**API Example**:
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Submit report",
  "due_date": "2025-02-15T17:00:00Z"
}
```

---

### 3. Task Reminders

**Migration**: `20250131_add_reminders_to_tasks.py`

**Schema**:
```sql
ALTER TABLE tasks ADD COLUMN remind_at TIMESTAMP;
```

**Usage**:
```python
# Get tasks that need reminders (for cron job)
from datetime import datetime, timedelta

window_start = datetime.utcnow()
window_end = window_start + timedelta(minutes=5)

tasks_to_remind = session.exec(
    select(Task).where(
        Task.remind_at >= window_start,
        Task.remind_at < window_end,
        Task.is_complete == False
    )
).all()

# Send reminder notifications
for task in tasks_to_remind:
    send_notification(task.user_id, f"Reminder: {task.title}")
```

**API Example**:
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Team meeting",
  "due_date": "2025-02-01T14:00:00Z",
  "remind_at": "2025-02-01T13:30:00Z"
}
```

---

### 4. Task Recurrence

**Migration**: `20250131_add_recurrence_to_tasks.py`

**Schema**:
```sql
ALTER TABLE tasks ADD COLUMN recurrence_rule JSONB;
```

**Recurrence Rule Format**:
```json
{
  "frequency": "weekly",
  "interval": 1,
  "days": ["mon", "wed", "fri"],
  "end_date": "2025-12-31T23:59:59Z"
}
```

**Supported Frequencies**:
- `daily` - Every N days
- `weekly` - Every N weeks (with optional days filter)
- `monthly` - Every N months
- `yearly` - Every N years

**Usage**:
```python
# Query recurring tasks
recurring = session.exec(
    select(Task).where(Task.recurrence_rule != None)
).all()

# Calculate next due date based on recurrence rule
from dateutil import rrule

def calculate_next_due(current_due: datetime, rule: dict) -> datetime:
    frequency = rule['frequency']
    interval = rule.get('interval', 1)

    if frequency == 'daily':
        return current_due + timedelta(days=interval)
    elif frequency == 'weekly':
        days = rule.get('days', [])
        # Find next matching weekday
        # ...
    elif frequency == 'monthly':
        return current_due + timedelta(days=30 * interval)
    # ...
```

**API Example**:
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Weekly team sync",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "days": ["mon"],
    "end_date": "2025-06-30T23:59:59Z"
  },
  "due_date": "2025-02-03T10:00:00Z"
}
```

---

### 5. Tags System

**Migration**: `20250131_add_tags_tables.py`

#### `tags` Table

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| user_id | TEXT | Foreign key to user.id |
| name | VARCHAR(50) | Tag name (unique per user) |
| color | VARCHAR(7) | Hex color code (default: #007bff) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes**:
- `ix_tags_user_id` - Query user's tags
- `ix_tags_user_id_name` - Unique constraint (one tag name per user)

#### `task_tags` Junction Table

| Column | Type | Description |
|--------|------|-------------|
| task_id | TEXT | Foreign key to tasks.id (CASCADE DELETE) |
| tag_id | TEXT | Foreign key to tags.id (CASCADE DELETE) |
| created_at | TIMESTAMP | Association timestamp |

**Indexes**:
- `ix_task_tags_task_id` - Query tags for a task
- `ix_task_tags_tag_id` - Query tasks with a tag
- `ix_task_tags_task_tag` - Composite unique (prevent duplicates)

**Usage**:
```python
# Create tag
tag = Tag(
    id=str(uuid.uuid4()),
    user_id=user.id,
    name="work",
    color="#007bff"
)
session.add(tag)

# Assign tag to task
task_tag = TaskTag(
    task_id=task.id,
    tag_id=tag.id
)
session.add(task_tag)

# Query tasks by tag
tasks_with_tag = session.exec(
    select(Task)
    .join(TaskTag, Task.id == TaskTag.task_id)
    .where(TaskTag.tag_id == tag_id)
).all()

# Get all tags for a task
tags = session.exec(
    select(Tag)
    .join(TaskTag, Tag.id == TaskTag.tag_id)
    .where(TaskTag.task_id == task_id)
).all()
```

**API Example**:
```http
# Create tag
POST /api/tags
Content-Type: application/json

{
  "name": "work",
  "color": "#007bff"
}

# Assign tags to task
PUT /api/tasks/{task_id}/tags
Content-Type: application/json

{
  "tag_ids": ["tag-uuid-1", "tag-uuid-2"]
}

# Filter tasks by tag
GET /api/tasks?tag_id=tag-uuid-1
```

---

### 6. Recurring Tasks

**Migration**: `20250131_add_recurring_tasks_table.py`

#### `recurring_tasks` Table

Stores templates for auto-generated recurring tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| user_id | TEXT | Foreign key to user.id |
| title | VARCHAR(200) | Task template title |
| description | VARCHAR(2000) | Task template description |
| priority | VARCHAR(20) | Priority (low, medium, high, urgent) |
| recurrence_rule | JSONB | Recurrence pattern |
| next_due_at | TIMESTAMP | Next instance due date |
| is_active | BOOLEAN | Template active flag |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Indexes**:
- `ix_recurring_tasks_user_id` - Query user's recurring tasks
- `ix_recurring_tasks_user_id_next_due_at` - For cron job (find due tasks)
- `ix_recurring_tasks_is_active` - Filter active templates
- `ix_recurring_tasks_recurrence_rule` - GIN index for JSONB queries

**Trigger**:
- `trigger_update_recurring_tasks_updated_at` - Auto-updates `updated_at` on row update

**Usage**:
```python
# Create recurring task template
recurring = RecurringTask(
    id=str(uuid.uuid4()),
    user_id=user.id,
    title="Weekly team meeting",
    description="Sync with engineering team",
    priority="high",
    recurrence_rule={
        "frequency": "weekly",
        "interval": 1,
        "days": ["mon"]
    },
    next_due_at=datetime(2025, 2, 3, 10, 0, 0),
    is_active=True
)
session.add(recurring)

# Cron job: Create task instances for due recurring tasks
from datetime import datetime

due_templates = session.exec(
    select(RecurringTask).where(
        RecurringTask.is_active == True,
        RecurringTask.next_due_at <= datetime.utcnow()
    )
).all()

for template in due_templates:
    # Create new task instance
    task = Task(
        id=str(uuid.uuid4()),
        title=template.title,
        description=template.description,
        priority=template.priority,
        user_id=template.user_id,
        due_date=template.next_due_at
    )
    session.add(task)

    # Calculate next due date
    template.next_due_at = calculate_next_due(
        template.next_due_at,
        template.recurrence_rule
    )
    session.add(template)
```

**API Example**:
```http
# Create recurring task template
POST /api/recurring-tasks
Content-Type: application/json

{
  "title": "Weekly team sync",
  "description": "Status meeting",
  "priority": "medium",
  "recurrence_rule": {
    "frequency": "weekly",
    "interval": 1,
    "days": ["mon", "wed", "fri"]
  },
  "next_due_at": "2025-02-03T10:00:00Z",
  "is_active": true
}

# Pause recurrence
PUT /api/recurring-tasks/{id}
Content-Type: application/json

{
  "is_active": false
}
```

---

## Running Migrations

### Development Environment

```bash
# Navigate to backend directory
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend

# Check current migration status
uv run alembic current

# View migration history
uv run alembic history

# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific revision
uv run alembic downgrade 5b9aae697899

# Rollback all Phase V migrations (use provided script)
chmod +x scripts/rollback_all_phase_v.sh
./scripts/rollback_all_phase_v.sh
```

### Production Environment

⚠️ **WARNING**: Always test migrations in development/staging first!

```bash
# 1. Backup database before migration
# (Use Neon's backup feature or pg_dump)

# 2. Run migration during maintenance window
uv run alembic upgrade head

# 3. Verify migration success
uv run python scripts/verify_migrations.py

# 4. If migration fails, rollback immediately
uv run alembic downgrade -1
```

---

## Verification

### Automated Verification Script

```bash
# Run comprehensive verification
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend
uv run python scripts/verify_migrations.py
```

**Output**:
```
============================================================
DATABASE MIGRATION VERIFICATION
============================================================

============================================================
PHASE III: Conversation Tables
============================================================
✅ conversations table exists
  ✅ conversations.id column exists
  ✅ conversations.user_id column exists
  ✅ conversations.title column exists
  ✅ conversations.created_at column exists
  ✅ conversations.updated_at column exists
✅ messages table exists
  ✅ messages.id column exists
  ✅ messages.conversation_id column exists
  ✅ messages.user_id column exists
  ✅ messages.role column exists
  ✅ messages.content column exists
  ✅ messages.tool_calls column exists
  ✅ messages.created_at column exists
✅ Index ix_conversations_user_id exists
✅ Index ix_conversations_user_id_created_at exists
✅ Index ix_messages_conversation_id exists
✅ Index ix_messages_conversation_id_created_at exists
✅ Index ix_messages_user_id exists
✅ Index ix_messages_user_id_created_at exists

============================================================
PHASE V: Advanced Features
============================================================

--- Tasks Table (Phase V Columns) ---
✅ tasks.priority column exists (Task priority)
✅ tasks.due_date column exists (Task deadline)
✅ tasks.remind_at column exists (Reminder timestamp)
✅ tasks.recurrence_rule column exists (Recurrence pattern)

--- Tags Tables ---
✅ tags table exists
  ✅ tags.id column exists
  ✅ tags.user_id column exists
  ✅ tags.name column exists
  ✅ tags.color column exists
  ✅ tags.created_at column exists
  ✅ tags.updated_at column exists
✅ task_tags junction table exists
  ✅ task_tags.task_id column exists
  ✅ task_tags.tag_id column exists
  ✅ task_tags.created_at column exists

--- Recurring Tasks Table ---
✅ recurring_tasks table exists
  ✅ recurring_tasks.id column exists
  ✅ recurring_tasks.user_id column exists
  ✅ recurring_tasks.title column exists
  ✅ recurring_tasks.description column exists
  ✅ recurring_tasks.priority column exists
  ✅ recurring_tasks.recurrence_rule column exists
  ✅ recurring_tasks.next_due_at column exists
  ✅ recurring_tasks.is_active column exists
  ✅ recurring_tasks.created_at column exists
  ✅ recurring_tasks.updated_at column exists

============================================================
SUMMARY
============================================================
✅ ALL CHECKS PASSED

✅ Phase III (Conversation Tables): Complete
✅ Phase V (Advanced Features): Complete
```

### Manual Verification

```bash
# Connect to database
psql $DATABASE_URL

# Check tables exist
\dt

# Check tasks table structure
\d+ tasks

# Check tags table structure
\d+ tags

# Check indexes
\di

# Exit
\q
```

---

## Rollback Procedures

### Single Migration Rollback

```bash
# Rollback one migration step
uv run alembic downgrade -1

# Verify rollback
uv run alembic current
```

### Complete Phase V Rollback

```bash
# Use provided rollback script
cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend
chmod +x scripts/rollback_all_phase_v.sh
./scripts/rollback_all_phase_v.sh
```

**Manual Rollback (if script fails)**:
```bash
# Rollback each migration in reverse order
uv run alembic downgrade -1  # recurring_tasks
uv run alembic downgrade -1  # tags
uv run alembic downgrade -1  # recurrence
uv run alembic downgrade -1  # reminders
uv run alembic downgrade -1  # due_dates
uv run alembic downgrade -1  # priority
```

---

## Data Migration Considerations

### Existing Data

All Phase V migrations add **new columns with defaults**, so existing tasks will have:
- `priority = 'medium'`
- `due_date = NULL`
- `remind_at = NULL`
- `recurrence_rule = NULL`

No data loss occurs during migration.

### Data Validation

After migration, validate existing tasks:

```sql
-- Check all tasks have priority values
SELECT COUNT(*) FROM tasks WHERE priority IS NULL;

-- Verify priority values are valid
SELECT COUNT(*) FROM tasks WHERE priority NOT IN ('low', 'medium', 'high', 'urgent');

-- Check for invalid JSONB in recurrence_rule
SELECT COUNT(*) FROM tasks WHERE recurrence_rule IS NOT NULL AND NOT jsonb_typeof(recurrence_rule) = 'object';
```

---

## Performance Considerations

### Index Strategy

All Phase V indexes are optimized for common query patterns:

| Index | Purpose | Query Pattern |
|-------|---------|---------------|
| `ix_tasks_priority` | Filter by priority | `WHERE priority = 'high'` |
| `ix_tasks_due_date` | Sort/filter by due date | `WHERE due_date < NOW() ORDER BY due_date` |
| `ix_tasks_remind_at` | Query reminders | `WHERE remind_at BETWEEN NOW() AND NOW() + INTERVAL '5 minutes'` |
| `ix_tasks_recurrence_rule` | JSONB queries | `WHERE recurrence_rule->>'frequency' = 'weekly'` (GIN index) |
| `ix_tags_user_id_name` | Unique tag per user | Prevent duplicate tag names |
| `ix_task_tags_task_id` | Get tags for task | `JOIN task_tags WHERE task_id = ?` |
| `ix_recurring_tasks_user_id_next_due_at` | Cron job | `WHERE next_due_at <= NOW()` |

### Database Size Impact

Estimated storage impact for 10,000 users with 100 tasks each:

| Feature | Storage Impact |
|---------|----------------|
| Priority column | ~80 MB (VARCHAR) |
| Due dates | ~160 MB (TIMESTAMP) |
| Reminders | ~160 MB (TIMESTAMP) |
| Recurrence rules | ~40 MB (JSONB, 10% recurring) |
| Tags (10 per user) | ~20 MB |
| Total | ~460 MB |

**Index overhead**: ~200-300 MB additional

---

## Troubleshooting

### Migration Fails

**Symptom**: `uv run alembic upgrade head` fails

**Diagnosis**:
```bash
# Check current state
uv run alembic current

# Check migration history
uv run alembic history

# View error details
uv run alembic upgrade head --sql
```

**Solutions**:
1. If foreign key constraint fails: Check referenced table/column exists
2. If column already exists: Manually drop column or skip migration
3. If permission denied: Check database user has CREATE TABLE, INDEX privileges

### Verification Fails

**Symptom**: `verify_migrations.py` reports missing columns/tables

**Diagnosis**:
```bash
# Check if migration was applied
uv run alembic current

# Manually check database
psql $DATABASE_URL -c "\d+ tasks"
```

**Solutions**:
1. Re-run migration: `uv run alembic upgrade head`
2. Check for partial migrations: `uv run alembic history`
3. Manually fix schema (last resort)

### Performance Issues

**Symptom**: Slow queries after migration

**Diagnosis**:
```sql
-- Check query plan
EXPLAIN ANALYZE SELECT * FROM tasks WHERE priority = 'high';

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE tablename = 'tasks';
```

**Solutions**:
1. Run `ANALYZE tasks` to update statistics
2. Rebuild indexes: `REINDEX TABLE tasks;`
3. Add composite indexes for multi-column filters

---

## Best Practices

### 1. Always Test Migrations

Run migrations in development/staging before production:
```bash
# Staging database
export DATABASE_URL="postgresql://staging-host/dbname"
uv run alembic upgrade head
uv run python scripts/verify_migrations.py
```

### 2. Backup Before Migration

```bash
# Use Neon backup feature
# Or use pg_dump
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### 3. Use Transactions

Migrations run in transactions by default. If migration fails, all changes rollback.

### 4. Monitor Migration Duration

```bash
# Time migration execution
time uv run alembic upgrade head
```

Expected duration (per migration):
- Simple column add: < 1 second
- Index creation: 5-30 seconds (depending on table size)
- Table creation: < 1 second

### 5. Plan Maintenance Windows

For large databases (> 1M rows):
- Schedule migrations during low-traffic periods
- Use `CONCURRENTLY` for index creation (requires migration code change)
- Notify users of scheduled maintenance

---

## References

- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **PostgreSQL JSONB**: https://www.postgresql.org/docs/current/datatype-json.html
- **PostgreSQL Indexes**: https://www.postgresql.org/docs/current/indexes.html
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/

---

## Support

For issues or questions:
1. Check this documentation
2. Review migration files in `src/db/migrations/versions/`
3. Run verification script to diagnose issues
4. Check Alembic logs: `uv run alembic history`

---

**Last Updated**: 2025-01-31
**Version**: 1.0.0
