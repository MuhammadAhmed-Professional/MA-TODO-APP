# Skill: Generate Database Migration

## Description
Creates an Alembic migration script for database schema changes (create table, add column, add index, modify constraint). Migrations are reversible and include both upgrade and downgrade operations.

## Inputs
- **migration_name**: Descriptive name (e.g., "add_user_table", "add_task_indexes")
- **operation_type**: Type of change (CREATE_TABLE, ADD_COLUMN, ADD_INDEX, MODIFY_CONSTRAINT)
- **entity_name**: Table name (e.g., "user", "task")
- **columns**: List of column definitions with types (for CREATE_TABLE)
- **column_changes**: List of column modifications (for ADD_COLUMN)
- **indexes**: List of index definitions (for ADD_INDEX)
- **constraints**: List of foreign key/unique constraints
- **file_path**: Backend path (e.g., "backend/src/db/migrations/")

## Process

1. **Validate Migration Type**
   - Ensure operation_type is one of: CREATE_TABLE, ADD_COLUMN, ADD_INDEX, MODIFY_CONSTRAINT
   - Check for entity naming consistency (snake_case)

2. **Generate Migration File**
   - Create timestamped file: {timestamp}_{migration_name}.py
   - Include Alembic imports and revision metadata
   - Generate upgrade() function with SQL operations
   - Generate downgrade() function (reverse operations)

3. **SQL Operation Templates**

   **CREATE_TABLE**:
   ```python
   op.create_table(
       'entity_name',
       sa.Column('id', sa.UUID(), server_default=sa.func.gen_random_uuid(), nullable=False),
       sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
       sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
       sa.PrimaryKeyConstraint('id'),
       # Unique constraints
       sa.UniqueConstraint('email', name='uq_entity_email'),
       # Foreign keys
       sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
   )
   ```

   **ADD_INDEX**:
   ```python
   op.create_index('ix_entity_column', 'entity_name', ['column_name'], unique=False)
   ```

   **ADD_COLUMN**:
   ```python
   op.add_column('entity_name', sa.Column('new_column', sa.String(100), nullable=True))
   ```

4. **Downgrade Operations**
   - Drop table: `op.drop_table('entity_name')`
   - Drop index: `op.drop_index('ix_entity_column', table_name='entity_name')`
   - Drop column: `op.drop_column('entity_name', 'column_name')`
   - Drop constraint: `op.drop_constraint('constraint_name', 'entity_name')`

5. **Generate and Apply**
   - Save migration file to backend/src/db/migrations/versions/
   - Run: `uv run alembic upgrade head` to apply
   - Verify with: `uv run alembic current`

## Example Usage
```
/skill generate-database-migration \
  --migration_name add_user_table \
  --operation_type CREATE_TABLE \
  --entity_name user \
  --columns "id:UUID:pk, email:String:unique, name:String, hashed_password:String, created_at:DateTime, updated_at:DateTime" \
  --constraints "unique:email" \
  --file_path backend/src/db/migrations/
```

## Output
- Complete Alembic migration script (.py file)
- Reversible upgrade/downgrade operations
- Ready to apply with `alembic upgrade head`
- Can be rolled back with `alembic downgrade -1`
