#!/bin/bash
#
# Validation Script: Verify Phase-Wise Structure Migration
# Version: 1.0.0
# Date: 2025-12-11
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

ERRORS=0
WARNINGS=0

echo -e "${BLUE}🔍 Validating Phase-Wise Structure Migration${NC}\n"

# Helper functions
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} Directory exists: $1"
        return 0
    else
        echo -e "${RED}❌${NC} Missing directory: $1"
        ((ERRORS++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} File exists: $1"
        return 0
    else
        echo -e "${RED}❌${NC} Missing file: $1"
        ((ERRORS++))
        return 1
    fi
}

warn_if_exists() {
    if [ -e "$1" ]; then
        echo -e "${YELLOW}⚠️${NC}  Old structure still exists: $1 (should be removed)"
        ((WARNINGS++))
        return 0
    else
        echo -e "${GREEN}✅${NC} Old structure removed: $1"
        return 1
    fi
}

#──────────────────────────────────────────────────────────────
echo -e "${BLUE}📁 Checking Shared Directories${NC}"
#──────────────────────────────────────────────────────────────
check_dir ".specify/memory"
check_dir ".claude/agents"
check_dir "specs/features"
check_dir "specs/api"
check_dir "specs/database"
check_dir "specs/ui"
check_dir "history/prompts"
check_dir "history/adr"
check_dir "shared/types"

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}📁 Checking Phase I Structure${NC}"
#──────────────────────────────────────────────────────────────
check_dir "phase-1"
check_dir "phase-1/src/todo_app"
check_dir "phase-1/tests"
check_file "phase-1/pyproject.toml"
check_file "phase-1/README.md"

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}📁 Checking Phase II Structure${NC}"
#──────────────────────────────────────────────────────────────
check_dir "phase-2"
check_dir "phase-2/backend"
check_dir "phase-2/frontend"
check_file "phase-2/README.md"
check_file "phase-2/backend/pyproject.toml"
check_file "phase-2/frontend/package.json"

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}📁 Checking Spec Organization${NC}"
#──────────────────────────────────────────────────────────────
check_dir "specs/features/console-todo-app"
check_dir "specs/features/cli-banner"
check_dir "specs/features/project-readme"
check_dir "specs/features/web-todo-app"
check_dir "specs/api/auth"
check_dir "specs/api/tasks"
check_dir "specs/database/todo-app"

# Check old numbered specs are gone
if [ ! -d "specs/001-console-todo-app" ] && \
   [ ! -d "specs/002-cli-banner" ] && \
   [ ! -d "specs/003-project-readme" ] && \
   [ ! -d "specs/004-phase-2-web-app" ]; then
    echo -e "${GREEN}✅${NC} Old numbered specs removed"
else
    echo -e "${RED}❌${NC} Old numbered specs still exist"
    ((ERRORS++))
fi

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}📁 Checking PHR References${NC}"
#──────────────────────────────────────────────────────────────
check_dir "history/prompts/console-todo-app"
check_dir "history/prompts/cli-banner"
check_dir "history/prompts/project-readme"
check_dir "history/prompts/web-todo-app"

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}⚠️  Checking for Old Structure (Should Clean Up)${NC}"
#──────────────────────────────────────────────────────────────
warn_if_exists "src"
warn_if_exists "tests"
warn_if_exists "backend"
warn_if_exists "frontend"

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}🧪 Running Phase I Tests${NC}"
#──────────────────────────────────────────────────────────────
if [ -d "phase-1/tests" ]; then
    cd phase-1
    if uv run pytest tests/ -v --tb=short 2>&1 | tee /tmp/phase1-tests.log; then
        PASSED=$(grep -c "passed" /tmp/phase1-tests.log || echo "0")
        echo -e "${GREEN}✅${NC} Phase I: $PASSED tests passed"
    else
        echo -e "${RED}❌${NC} Phase I: Tests failed"
        ((ERRORS++))
    fi
    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}⚠️${NC}  Phase I tests directory not found, skipping"
    ((WARNINGS++))
fi

#──────────────────────────────────────────────────────────────
echo -e "\n${BLUE}📊 Validation Summary${NC}"
#──────────────────────────────────────────────────────────────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ MIGRATION VALIDATED SUCCESSFULLY${NC}"
    echo -e "${GREEN}   No errors or warnings found.${NC}"
    EXIT_CODE=0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  MIGRATION COMPLETE WITH WARNINGS${NC}"
    echo -e "${YELLOW}   Errors: $ERRORS${NC}"
    echo -e "${YELLOW}   Warnings: $WARNINGS${NC}"
    echo -e "\n${YELLOW}   Please address warnings (old files to clean up)${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ MIGRATION VALIDATION FAILED${NC}"
    echo -e "${RED}   Errors: $ERRORS${NC}"
    echo -e "${YELLOW}   Warnings: $WARNINGS${NC}"
    echo -e "\n${RED}   Please fix errors before proceeding${NC}"
    EXIT_CODE=1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

exit $EXIT_CODE
