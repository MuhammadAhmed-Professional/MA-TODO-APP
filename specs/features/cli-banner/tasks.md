# Tasks: CLI Banner with Branding

**Input**: Design documents from `/specs/002-cli-banner/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), quickstart.md (complete)

**Tests**: Following TDD approach with RED-GREEN-REFACTOR cycle as specified in constitution

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/todo_app/`, `tests/` at repository root
- Project structure follows 5-layer architecture: Models → Storage → Operations → UI → Main

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and banner module structure

- [X] T001 Create banner module file at src/todo_app/banner.py with module docstring
- [X] T002 Create test file at tests/test_banner.py with initial imports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core banner constants and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Define ANSI color code constants in src/todo_app/banner.py (BOLD, BRIGHT_CYAN, CYAN, GRAY, RESET)
- [X] T004 [P] Define ASCII art constant ASCII_ART_LINES in src/todo_app/banner.py (80x5 lines, "Big" font from research.md)
- [X] T005 [P] Define TAGLINE constant in src/todo_app/banner.py ("Your Personal Task Manager")
- [X] T006 [P] Define COPYRIGHT constant in src/todo_app/banner.py ("© 2025 Muhammad Ahmed - Phase I Hackathon Project")
- [X] T007 [P] Define BORDER constant in src/todo_app/banner.py (80 "=" characters)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Application Launch with Branded Banner (Priority: P1) 🎯 MVP

**Goal**: Display "MA-TODO-APP" ASCII art banner at application startup with tagline

**Independent Test**: Launch application and verify banner displays with correct branding, proper formatting within 80 columns, and tagline appears beneath ASCII art

### Tests for User Story 1 (TDD - RED Phase)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Write test_get_banner_content_plain_text() in tests/test_banner.py to verify plain banner structure
- [X] T009 [P] [US1] Write test_banner_width_constraint() in tests/test_banner.py to verify no line exceeds 80 characters
- [X] T010 [P] [US1] Write test_banner_height_constraint() in tests/test_banner.py to verify total height ≤ 15 lines
- [X] T011 [P] [US1] Write test_banner_contains_tagline() in tests/test_banner.py to verify tagline appears in output
- [X] T012 [US1] Run pytest tests/test_banner.py and verify all 4 tests FAIL (RED phase complete)

### Implementation for User Story 1 (GREEN Phase)

- [X] T013 [US1] Implement get_banner_content(use_color: bool = False) -> str in src/todo_app/banner.py
- [X] T014 [US1] Build PLAIN_TEXT_BANNER constant using ASCII_ART_LINES, TAGLINE, BORDER in src/todo_app/banner.py
- [X] T015 [US1] Implement display_banner() skeleton function in src/todo_app/banner.py (plain text only for now)
- [X] T016 [US1] Run pytest tests/test_banner.py and verify all 4 tests PASS (GREEN phase complete)

### Integration for User Story 1

- [X] T017 [US1] Import display_banner in src/todo_app/main.py
- [X] T018 [US1] Add display_banner() call at startup in main() function before welcome message in src/todo_app/main.py
- [X] T019 [US1] Manual test: Run python -m src.todo_app.main and verify banner displays before menu
- [X] T020 [US1] Add blank line separator between banner and menu in src/todo_app/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional - banner displays with ASCII art and tagline at application startup

---

## Phase 4: User Story 2 - Version and Copyright Information (Priority: P2)

**Goal**: Display application version and copyright information in banner

**Independent Test**: Launch application and verify version displays in "Version X.Y.Z" format, copyright shows correct year and attribution, and version matches pyproject.toml

### Tests for User Story 2 (TDD - RED Phase)

- [X] T021 [P] [US2] Write test_get_version_from_metadata() in tests/test_banner.py to verify version extraction from importlib.metadata
- [X] T022 [P] [US2] Write test_get_version_from_pyproject() in tests/test_banner.py to verify version extraction from pyproject.toml with mocked metadata failure
- [X] T023 [P] [US2] Write test_get_version_fallback() in tests/test_banner.py to verify fallback to "dev" when both sources fail
- [X] T024 [P] [US2] Write test_banner_contains_version() in tests/test_banner.py to verify version appears in banner output
- [X] T025 [P] [US2] Write test_banner_contains_copyright() in tests/test_banner.py to verify copyright appears in banner output
- [X] T026 [US2] Run pytest tests/test_banner.py -k "version or copyright" and verify all 5 new tests FAIL (RED phase)

### Implementation for User Story 2 (GREEN Phase)

- [X] T027 [US2] Implement get_version() -> str in src/todo_app/banner.py with three-tier fallback (importlib.metadata → tomllib → "dev")
- [X] T028 [US2] Update get_banner_content() to include version line in src/todo_app/banner.py
- [X] T029 [US2] Update get_banner_content() to include copyright line in src/todo_app/banner.py
- [X] T030 [US2] Rebuild PLAIN_TEXT_BANNER constant to include version and copyright in src/todo_app/banner.py
- [X] T031 [US2] Run pytest tests/test_banner.py and verify all tests PASS (GREEN phase complete)

### Integration for User Story 2

- [X] T032 [US2] Manual test: Run python -m src.todo_app.main and verify version displays correctly
- [X] T033 [US2] Manual test: Verify version in banner matches version in pyproject.toml
- [X] T034 [US2] Manual test: Verify copyright shows "© 2025 Muhammad Ahmed - Phase I Hackathon Project"

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - banner shows ASCII art, tagline, version, and copyright

---

## Phase 5: User Story 3 - Optional Banner Color/Style Enhancement (Priority: P3)

**Goal**: Display banner with ANSI colors when terminal supports it, with graceful fallback to plain text

**Independent Test**: Run application in color-supporting terminal (verify cyan title, gray metadata), run in non-color terminal or piped output (verify plain text, no errors)

### Tests for User Story 3 (TDD - RED Phase)

- [X] T035 [P] [US3] Write test_detect_terminal_capabilities_interactive() in tests/test_banner.py to verify color detection when stdout.isatty() is True
- [X] T036 [P] [US3] Write test_detect_terminal_capabilities_non_interactive() in tests/test_banner.py to verify no color when stdout.isatty() is False
- [X] T037 [P] [US3] Write test_detect_terminal_width_success() in tests/test_banner.py to verify os.get_terminal_size() success case
- [X] T038 [P] [US3] Write test_detect_terminal_width_fallback() in tests/test_banner.py to verify width fallback to 80 on OSError
- [X] T039 [P] [US3] Write test_get_banner_content_with_color() in tests/test_banner.py to verify ANSI codes present when use_color=True
- [X] T040 [P] [US3] Write test_display_banner_auto_detect_color() in tests/test_banner.py to verify display_banner() uses terminal detection
- [X] T041 [US3] Run pytest tests/test_banner.py -k "color or terminal" and verify all 6 new tests FAIL (RED phase)

### Implementation for User Story 3 (GREEN Phase)

- [X] T042 [US3] Implement detect_terminal_capabilities() -> dict[str, bool | int] in src/todo_app/banner.py
- [X] T043 [US3] Add TERM and COLORTERM environment variable checks in detect_terminal_capabilities() in src/todo_app/banner.py
- [X] T044 [US3] Build COLORED_BANNER constant with ANSI color codes (Bright Cyan for title, Gray for metadata) in src/todo_app/banner.py
- [X] T045 [US3] Update get_banner_content(use_color: bool) to return COLORED_BANNER when use_color=True in src/todo_app/banner.py
- [X] T046 [US3] Update display_banner() to call detect_terminal_capabilities() and select appropriate banner in src/todo_app/banner.py
- [X] T047 [US3] Run pytest tests/test_banner.py and verify ALL tests PASS (GREEN phase complete for entire feature)

### Integration for User Story 3

- [X] T048 [US3] Manual test: Run python -m src.todo_app.main in interactive terminal and verify colors display (cyan title, gray metadata)
- [X] T049 [US3] Manual test: Run python -m src.todo_app.main | cat and verify plain text output (no ANSI codes visible)
- [X] T050 [US3] Manual test: Run in Windows Terminal, Linux Terminal, macOS Terminal to verify cross-platform compatibility
- [X] T051 [US3] Manual test: Run with TERM="" python -m src.todo_app.main to verify color fallback works

**Checkpoint**: All user stories should now be independently functional - banner displays with full color support and graceful degradation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T052 [P] Add comprehensive docstrings to all banner functions in src/todo_app/banner.py (display_banner, get_banner_content, detect_terminal_capabilities, get_version)
- [X] T053 [P] Add type hints to all function signatures in src/todo_app/banner.py
- [X] T054 [P] Verify PEP 8 compliance for src/todo_app/banner.py using linting tools
- [X] T055 [P] Verify 100% test coverage for banner module by running pytest --cov=src.todo_app.banner tests/test_banner.py
- [X] T056 Performance validation: Run banner display 100 times and verify average time <1ms
- [X] T057 [P] Update README.md to mention CLI banner feature in application description
- [X] T058 Verify all acceptance criteria from spec.md are met (SC-001 through SC-006)
- [X] T059 Run full test suite: pytest tests/ -v and verify all tests pass
- [X] T060 Final manual validation: Follow quickstart.md testing scenarios and verify all pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User Story 1 (P1) can proceed after Foundational
  - User Story 2 (P2) extends User Story 1 (adds version/copyright to banner)
  - User Story 3 (P3) extends User Story 2 (adds color to existing banner)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Extends User Story 1 - Must complete after US1 (modifies get_banner_content function)
- **User Story 3 (P3)**: Extends User Story 2 - Must complete after US2 (adds terminal detection to display_banner)

**Note**: Unlike typical features, these user stories are sequential enhancements to the same banner. Each builds on the previous rather than being fully independent.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD RED-GREEN-REFACTOR)
- Constants before functions
- Core functions before integration
- All tests pass before moving to next priority
- Manual testing after integration to verify acceptance scenarios

### Parallel Opportunities

- **Phase 1**: Both tasks can run in parallel
- **Phase 2**: All 5 constant definitions marked [P] can run in parallel
- **User Story 1 Tests (T008-T011)**: All 4 test writing tasks marked [P] can run in parallel
- **User Story 2 Tests (T021-T025)**: All 5 test writing tasks marked [P] can run in parallel
- **User Story 3 Tests (T035-T040)**: All 6 test writing tasks marked [P] can run in parallel
- **Phase 6 Polish**: T052, T053, T054, T055, T057 can all run in parallel (different concerns)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all test writing for User Story 1 together (RED phase):
Task T008: "Write test_get_banner_content_plain_text() in tests/test_banner.py"
Task T009: "Write test_banner_width_constraint() in tests/test_banner.py"
Task T010: "Write test_banner_height_constraint() in tests/test_banner.py"
Task T011: "Write test_banner_contains_tagline() in tests/test_banner.py"

# Then verify all FAIL together:
Task T012: "Run pytest tests/test_banner.py and verify all 4 tests FAIL"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T007) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T008-T020)
4. **STOP and VALIDATE**: Test banner displays with ASCII art and tagline
5. Demo/review if ready (basic professional banner working)

### Incremental Delivery

1. Complete Setup + Foundational → Banner constants ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - basic banner!)
3. Add User Story 2 → Test independently → Deploy/Demo (banner with version/copyright)
4. Add User Story 3 → Test independently → Deploy/Demo (full color banner)
5. Complete Polish → Final validation → Production ready

### Sequential Enhancement Strategy

Since each user story builds on the previous (all modify the same banner):

1. Complete Setup + Foundational together
2. Complete User Story 1 fully (tests + implementation + integration)
3. Validate US1 works perfectly before moving on
4. Complete User Story 2 fully (extends US1)
5. Validate US1+US2 work together before moving on
6. Complete User Story 3 fully (extends US2)
7. Validate entire banner feature
8. Polish and finalize

---

## Performance Targets

Based on research.md findings:

- **Banner display time**: <1ms actual (target was <100ms - achieved 100x better!)
- **Terminal detection**: <0.1ms
- **Version extraction**: <1ms (file I/O at module load, cached)
- **Total startup overhead**: <5ms (imperceptible to users)

---

## Notes

- [P] tasks = different files/functions, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3)
- Each user story builds on previous (sequential enhancements to same banner)
- **TDD CRITICAL**: Verify tests FAIL (RED) before implementing (GREEN)
- Follow RED-GREEN-REFACTOR cycle strictly per constitution
- Commit after each logical task group (e.g., after each user story phase)
- Stop at checkpoints to validate story independently
- All constants are UPPERCASE per Python conventions
- Type hints required for all functions (Python 3.13+ with `|` operator)
- Docstrings required for all public functions
- Target 100% test coverage for banner module
- ASCII art is exactly 80 columns wide (from research.md Design 1 selection)
- Total banner height is 12 lines (within 15 line constraint)
- Colors: Bright Cyan (#00FFFF) for title, Gray (#808080) for metadata
- Cross-platform tested: Linux, macOS, Windows/WSL2
- No external dependencies (Python stdlib only)

---

## Test Coverage Requirements

**Required Test Scenarios** (from spec.md and quickstart.md):

### Unit Tests (tests/test_banner.py):
- ✅ Banner content structure (plain text)
- ✅ Width constraint (≤80 columns per line)
- ✅ Height constraint (≤15 lines total)
- ✅ Tagline presence
- ✅ Version extraction (3 fallback strategies)
- ✅ Copyright presence
- ✅ Terminal detection (interactive/non-interactive)
- ✅ Terminal width detection (success/fallback)
- ✅ Color support detection (TERM env vars)
- ✅ Colored banner content (ANSI codes present)
- ✅ Color auto-detection in display_banner()

### Integration Tests (manual, documented in quickstart.md):
- ✅ Application startup displays banner before menu
- ✅ Version matches pyproject.toml
- ✅ Colors display in interactive terminal
- ✅ Plain text fallback in piped output
- ✅ Cross-platform compatibility (Linux, macOS, Windows)
- ✅ No errors in non-color terminals

### Acceptance Criteria Validation (from spec.md):
- ✅ SC-001: 100% of launches display banner before menu
- ✅ SC-002: No wrapping in 80+ column terminals
- ✅ SC-003: <100ms display time (actually <1ms)
- ✅ SC-004: Brand visible within 1 second
- ✅ SC-005: Version matches app version 100% of cases
- ✅ SC-006: 95%+ compatibility across terminal environments

**Target**: 100% code coverage for src/todo_app/banner.py

---

## Success Validation Checklist

Before marking feature complete, verify:

- [ ] All 60 tasks completed (T001-T060)
- [ ] All pytest tests pass (100% coverage for banner module)
- [ ] All 6 success criteria from spec.md validated (SC-001 through SC-006)
- [ ] All 9 functional requirements met (FR-001 through FR-009)
- [ ] All 3 user stories delivered with acceptance scenarios validated
- [ ] Manual testing completed per quickstart.md scenarios
- [ ] Performance target met (<100ms, actually <1ms)
- [ ] Cross-platform compatibility verified (Linux, macOS, Windows/WSL2)
- [ ] Code follows constitution principles (PEP 8, type hints, docstrings)
- [ ] README.md updated with banner feature mention
- [ ] No regressions in existing application functionality

**When all items checked**: CLI Banner feature is COMPLETE and ready for production! 🎉
