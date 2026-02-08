#!/bin/bash
#
# Rollback Script for Phase V Migrations
#
# This script rolls back all Phase V migrations in reverse order.
# Use this to revert the database schema to Phase IV state.
#
# Usage:
#   cd /mnt/d/Talal/Work/Hackathons-Panaversity/phase-1/phase-2/backend
#   chmod +x scripts/rollback_all_phase_v.sh
#   ./scripts/rollback_all_phase_v.sh
#
# WARNING: This will DELETE data in tags, task_tags, and recurring_tasks tables!
# Make sure to backup your database before running this script.
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MIGRATIONS_TO_ROLLBACK=(
    "20250131_add_recurring_tasks_table"
    "20250131_add_tags_tables"
    "20250131_add_recurrence_to_tasks"
    "20250131_add_reminders_to_tasks"
    "20250131_add_due_dates_to_tasks"
    "20250131_add_priority_to_tasks"
)

TARGET_REVISION="5b9aae697899"  # Revision before Phase V

echo -e "${YELLOW}================================================================${NC}"
echo -e "${YELLOW}Phase V Migration Rollback Script${NC}"
echo -e "${YELLOW}================================================================${NC}"
echo ""
echo "This script will rollback the following migrations:"
echo ""
for migration in "${MIGRATIONS_TO_ROLLBACK[@]}"; do
    echo "  - ${migration}"
done
echo ""
echo "Target revision: ${TARGET_REVISION}"
echo ""

# Check if DATABASE_URL is set
if [ -z "${DATABASE_URL:-}" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable is not set${NC}"
    echo "Please set it with: export DATABASE_URL='postgresql://...'"
    exit 1
fi

# Prompt for confirmation
echo -e "${RED}WARNING: This will DELETE data in the following tables:${NC}"
echo "  - tags"
echo "  - task_tags"
echo "  - recurring_tasks"
echo ""
echo -e "${YELLOW}And will DROP the following columns from tasks:${NC}"
echo "  - priority"
echo "  - due_date"
echo "  - remind_at"
echo "  - recurrence_rule"
echo ""
read -p "Are you sure you want to proceed? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${YELLOW}Rollback cancelled.${NC}"
    exit 0
fi

echo -e "${GREEN}Starting rollback...${NC}"
echo ""

# Check current migration version
echo "Current migration version:"
uv run alembic current
echo ""

# Rollback each migration in reverse order
for migration in "${MIGRATIONS_TO_ROLLBACK[@]}"; do
    echo -e "${YELLOW}Rolling back: ${migration}${NC}"

    uv run alembic downgrade -1

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Successfully rolled back: ${migration}${NC}"
    else
        echo -e "${RED}❌ Failed to rollback: ${migration}${NC}"
        echo -e "${RED}Rollback process stopped. Check the error above.${NC}"
        exit 1
    fi

    echo ""
done

# Verify final state
echo "Verifying final migration state:"
uv run alembic current
echo ""

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}✅ Rollback Complete!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo "Database is now at revision: ${TARGET_REVISION}"
echo ""
echo "To re-apply Phase V migrations:"
echo "  uv run alembic upgrade head"
echo ""
