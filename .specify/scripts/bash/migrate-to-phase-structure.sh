#!/bin/bash
#
# Migration Script: Reorganize to Phase-Wise Structure
# Version: 1.0.0
# Date: 2025-12-11
# Description: Migrates current structure to phase-wise organization
#
# Usage: bash scripts/migrate-to-phase-structure.sh [--dry-run]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}\n"
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}📦 Starting Phase-Wise Structure Migration${NC}"
echo -e "${BLUE}Project Root: ${PROJECT_ROOT}${NC}\n"

# Function to execute or simulate command
execute() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} $*"
    else
        echo -e "${GREEN}[EXECUTE]${NC} $*"
        eval "$@"
    fi
}

# Function to log step
log_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📍 STEP $1: $2${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

cd "$PROJECT_ROOT"

#──────────────────────────────────────────────────────────────
# STEP 1: Create New Directory Structure
#──────────────────────────────────────────────────────────────
log_step "1" "Creating New Phase-Wise Directory Structure"

execute "mkdir -p specs/{features,api/{auth,tasks},database/todo-app,ui/dashboard}"
execute "mkdir -p history/adr"
execute "mkdir -p shared/{types,utils}"
execute "mkdir -p phase-1/{src/todo_app,tests}"
execute "mkdir -p phase-2/{backend,frontend}"
execute "mkdir -p {phase-3,phase-4,phase-5}"
execute "mkdir -p docs"
execute "mkdir -p scripts"

echo -e "${GREEN}✅ Directory structure created${NC}"

#──────────────────────────────────────────────────────────────
# STEP 2: Reorganize Specs (Type-Based Organization)
#──────────────────────────────────────────────────────────────
log_step "2" "Reorganizing Specs to Type-Based Structure"

# Move Phase I feature specs
if [ -d "specs/001-console-todo-app" ]; then
    execute "mv specs/001-console-todo-app specs/features/console-todo-app"
fi
if [ -d "specs/002-cli-banner" ]; then
    execute "mv specs/002-cli-banner specs/features/cli-banner"
fi
if [ -d "specs/003-project-readme" ]; then
    execute "mv specs/003-project-readme specs/features/project-readme"
fi

# Handle Phase II specs (004-phase-2-web-app)
if [ -d "specs/004-phase-2-web-app" ]; then
    echo -e "${YELLOW}📦 Splitting Phase II specs...${NC}"

    # Move API contracts
    if [ -f "specs/004-phase-2-web-app/contracts/auth.md" ]; then
        execute "mv specs/004-phase-2-web-app/contracts/auth.md specs/api/auth/spec.md"
    fi
    if [ -f "specs/004-phase-2-web-app/contracts/tasks.md" ]; then
        execute "mv specs/004-phase-2-web-app/contracts/tasks.md specs/api/tasks/spec.md"
    fi

    # Move database schema
    if [ -f "specs/004-phase-2-web-app/data-model.md" ]; then
        execute "mv specs/004-phase-2-web-app/data-model.md specs/database/todo-app/schema.md"
    fi

    # Move remaining files to features/web-todo-app
    execute "mkdir -p specs/features/web-todo-app"
    execute "mv specs/004-phase-2-web-app/* specs/features/web-todo-app/ 2>/dev/null || true"
    execute "rmdir specs/004-phase-2-web-app/contracts 2>/dev/null || true"
    execute "rmdir specs/004-phase-2-web-app 2>/dev/null || true"
fi

echo -e "${GREEN}✅ Specs reorganized${NC}"

#──────────────────────────────────────────────────────────────
# STEP 3: Update PHR References
#──────────────────────────────────────────────────────────────
log_step "3" "Updating Prompt History Record (PHR) References"

if [ -d "history/prompts/001-console-todo-app" ]; then
    execute "mv history/prompts/001-console-todo-app history/prompts/console-todo-app"
fi
if [ -d "history/prompts/002-cli-banner" ]; then
    execute "mv history/prompts/002-cli-banner history/prompts/cli-banner"
fi
if [ -d "history/prompts/003-project-readme" ]; then
    execute "mv history/prompts/003-project-readme history/prompts/project-readme"
fi
if [ -d "history/prompts/004-phase-2-web-app" ]; then
    execute "mv history/prompts/004-phase-2-web-app history/prompts/web-todo-app"
fi

echo -e "${GREEN}✅ PHR references updated${NC}"

#──────────────────────────────────────────────────────────────
# STEP 4: Move Phase I Implementation
#──────────────────────────────────────────────────────────────
log_step "4" "Moving Phase I Implementation to phase-1/"

# Move source code
if [ -d "src/todo_app" ]; then
    execute "cp -r src/todo_app phase-1/src/"
fi

# Move tests
if [ -d "tests" ] && [ "$(ls -A tests 2>/dev/null)" ]; then
    execute "cp -r tests/* phase-1/tests/"
fi

# Copy Phase I specific files
if [ -f "pyproject.toml" ]; then
    execute "cp pyproject.toml phase-1/"
fi
if [ -f "pytest.ini" ]; then
    execute "cp pytest.ini phase-1/"
fi
if [ -f ".python-version" ]; then
    execute "cp .python-version phase-1/"
fi
if [ -f "TEST_IMPLEMENTATION_REPORT.md" ]; then
    execute "mv TEST_IMPLEMENTATION_REPORT.md phase-1/PHASE_COMPLETION.md"
fi

echo -e "${GREEN}✅ Phase I moved to phase-1/${NC}"

#──────────────────────────────────────────────────────────────
# STEP 5: Move Phase II Implementation
#──────────────────────────────────────────────────────────────
log_step "5" "Moving Phase II Implementation to phase-2/"

# Move backend
if [ -d "backend" ]; then
    execute "mv backend phase-2/"
fi

# Move frontend
if [ -d "frontend" ]; then
    execute "mv frontend phase-2/"
fi

# Create Phase II docker-compose if it doesn't exist
if [ ! -f "phase-2/docker-compose.yml" ]; then
    echo -e "${YELLOW}📝 Note: Create phase-2/docker-compose.yml for local dev${NC}"
fi

echo -e "${GREEN}✅ Phase II moved to phase-2/${NC}"

#──────────────────────────────────────────────────────────────
# STEP 6: Move Documentation
#──────────────────────────────────────────────────────────────
log_step "6" "Organizing Documentation"

if [ -f "docs/neon-setup.md" ]; then
    echo -e "${GREEN}✅ docs/ already exists${NC}"
else
    execute "mkdir -p docs"
    echo -e "${YELLOW}📝 Note: Create docs/architecture.md and docs/deployment.md${NC}"
fi

#──────────────────────────────────────────────────────────────
# STEP 7: Update Root pyproject.toml (Workspace Config)
#──────────────────────────────────────────────────────────────
log_step "7" "Updating Root Workspace Configuration"

if [ "$DRY_RUN" = false ]; then
    cat > pyproject.toml.new <<'EOF'
[project]
name = "ma-todo-app-workspace"
version = "1.0.0"
description = "Monorepo workspace for multi-phase Todo App (Phases I-V)"
requires-python = ">=3.13"
dependencies = []

[tool.uv.workspace]
members = [
    "phase-1",
    "phase-2/backend",
    # Future phases:
    # "phase-3/chatbot",
    # "phase-4/analytics",
]

[dependency-groups]
dev = [
    "pytest>=9.0.1",
    "pytest-cov>=7.0.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["phase-1/tests", "phase-2/backend/tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
EOF

    echo -e "${GREEN}✅ Created new pyproject.toml.new${NC}"
    echo -e "${YELLOW}⚠️  Review and rename: mv pyproject.toml.new pyproject.toml${NC}"
else
    echo -e "${YELLOW}[DRY RUN] Would create new pyproject.toml${NC}"
fi

#──────────────────────────────────────────────────────────────
# STEP 8: Create Phase-Specific READMEs
#──────────────────────────────────────────────────────────────
log_step "8" "Creating Phase-Specific READMEs"

# Phase I README
if [ ! -f "phase-1/README.md" ] && [ "$DRY_RUN" = false ]; then
    cat > phase-1/README.md <<'EOF'
# Phase I: Console Todo App

**Status**: ✅ Complete (100%)
**Tests**: 87 passing
**Coverage**: 77%

## Features
- ✅ Create, read, update, delete tasks
- ✅ Mark tasks as complete
- ✅ View tasks by status
- ✅ Search tasks
- ✅ CLI banner with ASCII art

## Running

```bash
# From project root
uv run python -m phase-1.src.todo_app.main

# Or from phase-1/
cd phase-1
uv run python -m src.todo_app.main
```

## Testing

```bash
cd phase-1
uv run pytest tests/ -v --cov=src/todo_app
```

## Architecture
- **Pattern**: Layered (UI → Operations → Storage)
- **Storage**: In-memory (data lost on exit)
- **Tests**: Unit + Integration (87 tests)

See `PHASE_COMPLETION.md` for full test report.
EOF
    echo -e "${GREEN}✅ Created phase-1/README.md${NC}"
fi

# Phase II README
if [ ! -f "phase-2/README.md" ] && [ "$DRY_RUN" = false ]; then
    cat > phase-2/README.md <<'EOF'
# Phase II: Web Todo App

**Status**: 🚧 In Progress (65%)
**Stack**: Next.js 16 + FastAPI + PostgreSQL (Neon)

## Architecture
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript
- **Backend**: FastAPI 0.110, SQLModel, Alembic
- **Database**: Neon Serverless PostgreSQL
- **Auth**: JWT with HttpOnly cookies

## Running

### Backend
```bash
cd phase-2/backend
cp .env.example .env  # Configure DATABASE_URL, JWT_SECRET
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd phase-2/frontend
cp .env.local.example .env.local  # Configure NEXT_PUBLIC_API_URL
pnpm install
pnpm dev  # http://localhost:3000
```

### Docker Compose (Full Stack)
```bash
cd phase-2
docker-compose up
```

## Testing

### Backend Tests
```bash
cd phase-2/backend
uv run pytest tests/ -v
```

### Frontend Tests
```bash
cd phase-2/frontend
pnpm test          # Unit tests (Vitest)
pnpm test:e2e      # E2E tests (Playwright)
```

## Progress
- ✅ User signup/login API
- ✅ JWT authentication
- ✅ Task model + migrations
- ✅ Basic UI scaffolding
- ⚠️ Missing: Update/delete endpoints, task filters, search

See `backend/CLAUDE.md` and `frontend/CLAUDE.md` for detailed instructions.
EOF
    echo -e "${GREEN}✅ Created phase-2/README.md${NC}"
fi

# Phase III placeholder
if [ ! -f "phase-3/README.md" ] && [ "$DRY_RUN" = false ]; then
    cat > phase-3/README.md <<'EOF'
# Phase III: RAG Chatbot

**Status**: ❌ Not Started (0%)
**Deadline**: TBD

## Planned Features
- Conversational interface for task management
- RAG (Retrieval-Augmented Generation) with documentation
- MCP tools for task operations
- Multi-language support (English + Urdu)

## Stack (Planned)
- OpenAI Agents SDK
- Qdrant (vector database)
- MCP Server (tool integration)
- FastAPI backend extension

See `/specs/features/chatbot/` (to be created)
EOF
    echo -e "${GREEN}✅ Created phase-3/README.md${NC}"
fi

#──────────────────────────────────────────────────────────────
# STEP 9: Create Placeholder Future Phase Directories
#──────────────────────────────────────────────────────────────
log_step "9" "Creating Placeholder Directories for Future Phases"

for phase in phase-4 phase-5; do
    if [ ! -f "$phase/README.md" ] && [ "$DRY_RUN" = false ]; then
        cat > "$phase/README.md" <<EOF
# ${phase^}: Coming Soon

**Status**: ❌ Not Started (0%)

See project README for phase details.
EOF
    fi
done

echo -e "${GREEN}✅ Future phase placeholders created${NC}"

#──────────────────────────────────────────────────────────────
# STEP 10: Update Root README
#──────────────────────────────────────────────────────────────
log_step "10" "Updating Root README with New Structure"

if [ "$DRY_RUN" = false ]; then
    # Backup existing README
    if [ -f "README.md" ]; then
        execute "cp README.md README.md.backup"
    fi

    echo -e "${YELLOW}📝 Note: Update README.md with new phase-wise structure${NC}"
    echo -e "${YELLOW}   Backup saved as README.md.backup${NC}"
fi

#──────────────────────────────────────────────────────────────
# STEP 11: Clean Up Old Structure (Optional)
#──────────────────────────────────────────────────────────────
log_step "11" "Cleaning Up Old Structure (After Validation)"

if [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}⚠️  MANUAL STEP REQUIRED:${NC}"
    echo -e "${YELLOW}   After validating migration, clean up:${NC}"
    echo -e "${YELLOW}   - Remove old src/ directory: rm -rf src/${NC}"
    echo -e "${YELLOW}   - Remove old tests/ directory: rm -rf tests/${NC}"
    echo -e "${YELLOW}   - Remove old backend/ (now in phase-2/)${NC}"
    echo -e "${YELLOW}   - Remove old frontend/ (now in phase-2/)${NC}"
    echo ""
    echo -e "${YELLOW}   Run validation first: bash scripts/validate-migration.sh${NC}"
else
    echo -e "${YELLOW}[DRY RUN] Would prompt for cleanup${NC}"
fi

#──────────────────────────────────────────────────────────────
# SUMMARY
#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ MIGRATION COMPLETE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 This was a DRY RUN. No changes were made.${NC}"
    echo -e "${YELLOW}   Remove --dry-run flag to execute migration.${NC}\n"
else
    echo -e "${GREEN}📋 Next Steps:${NC}"
    echo -e "   1. Review new pyproject.toml.new and rename it"
    echo -e "   2. Update imports in code (phase-1.src.todo_app...)"
    echo -e "   3. Run validation: bash scripts/validate-migration.sh"
    echo -e "   4. Run Phase I tests: cd phase-1 && uv run pytest"
    echo -e "   5. Run Phase II tests: cd phase-2/backend && uv run pytest"
    echo -e "   6. Clean up old directories after validation"
    echo -e "   7. Commit changes: git add . && git commit -m 'Migrate to phase-wise structure'"
    echo ""
    echo -e "${BLUE}📖 Documentation Updates Needed:${NC}"
    echo -e "   - Update CLAUDE.md with new structure"
    echo -e "   - Update Constitution v2.0.0 references"
    echo -e "   - Create ADRs in history/adr/"
    echo ""
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
