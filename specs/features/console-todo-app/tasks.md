# Implementation Tasks: Phase 1 Console Todo Application

**Feature Branch**: `001-console-todo-app`
**Date**: 2025-12-05

## Overview

This document outlines the implementation tasks for the Phase 1 In-Memory Python Console Todo Application, organized by TDD phases and user stories. Each task is designed to be independently testable, following the Red-Green-Refactor cycle. This plan incorporates decisions from `plan.md`, `research.md`, `data-model.md`, and `contracts/cli-interface.md`.

## Implementation Strategy

We will follow a strict Test-Driven Development (TDD) approach: Red (write failing test), Green (write minimum code to pass test), Refactor (clean code, keep tests green). Tasks are ordered by module dependencies and user story priority, ensuring a stable foundation before building higher-level features.

## Dependency Graph (User Story Completion Order)

```
Phase 1: Setup
   ↓
Phase 2: Foundational (Custom Exceptions)
   ↓
User Story 1: Create and Track New Tasks (P1)
   ↓
User Story 2: View All Tasks (P2)
   ↓
User Story 3: Mark Tasks as Complete (P3)
   ↓
User Story 4: Update Task Details (P4)
   ↓
User Story 5: Delete Unnecessary Tasks (P5)
   ↓
Phase 7: Polish & Cross-Cutting Concerns
```

## Parallel Execution Opportunities

Tasks marked with `[P]` can be worked on in parallel once their prerequisites are met (e.g., implementing separate test files or UI functions simultaneously).

## Phase 1: Project Setup

*Goal: Initialize project structure and dependencies.*
*Independent Test: `uv run pytest --version` completes successfully, `src/todo_app` and `tests` directories exist.*

- [X] T001 Create project directories: `src/todo_app` and `tests`
- [X] T002 Create `__init__.py` files in `src/todo_app/__init__.py` and `tests/__init__.py`
- [X] T003 Create `.python-version` file with content "3.13" at `.python-version`
- [X] T004 Initialize UV project if not already done: `uv init`
- [X] T005 Add development dependencies (`pytest`, `pytest-cov`) to `pyproject.toml` using `uv add --dev pytest pytest-cov`

## Phase 2: Foundational - Custom Exceptions

*Goal: Define custom exception classes for consistent error handling across the business logic layer. These are fundamental and required by all task operations.*
*Independent Test: Exception classes can be imported without errors.*

- [X] T006 [P] Create `ValidationError` exception class in `src/todo_app/operations.py`
- [X] T007 [P] Create `TaskNotFoundError` exception class in `src/todo_app/operations.py`

## Phase 3: User Story 1 - Create and Track New Tasks (P1)

*Goal: Enable users to add tasks with titles and descriptions. This includes task model, storage, business logic, and UI for adding tasks. All other stories depend on this.*
*Independent Test: User can successfully add a task via CLI, and it's visible in memory (requires temporary manual verification until View Tasks is built). Unit tests for models, storage.add, and operations.create_task pass.*

### TDD - Models Layer

- [X] T008 [P] [US1] Write failing tests for Task dataclass in `tests/test_models.py` (test creation with all fields, defaults, and equality)
- [X] T009 [P] [US1] Implement `Task` dataclass in `src/todo_app/models.py` with `id`, `title`, `description`, `completed`, `created_at` fields and `datetime.now()` default for `created_at`
- [X] T010 [P] [US1] Refactor `src/todo_app/models.py` for docstrings and type hints as needed; ensure `tests/test_models.py` remain green

### TDD - Storage Layer (`add` operation)

- [X] T011 [P] [US1] Write failing tests for `TaskStorage` interface and `InMemoryStorage.add` method in `tests/test_storage.py` (test ID assignment, increment, and non-reuse of deleted IDs)
- [X] T012 [P] [US1] Implement `TaskStorage` abstract base class and `InMemoryStorage.__init__` and `InMemoryStorage.add` methods in `src/todo_app/storage.py`
- [X] T013 [P] [US1] Refactor `src/todo_app/storage.py` for docstrings and type hints; ensure `tests/test_storage.py` remain green

### TDD - Business Logic Layer (`create_task` operation)

- [X] T014 [P] [US1] Write failing tests for `operations.validate_title`, `operations.validate_description`, and `operations.create_task` in `tests/test_operations.py` (test valid/invalid titles/descriptions including whitespace-only via `title.strip() == ""`, successful creation, `ValidationError` handling, and invalid ID formats: negative numbers, zero, non-numeric strings)
- [X] T015 [P] [US1] Implement `operations.validate_title` and `operations.validate_description` functions in `src/todo_app/operations.py` according to spec
- [X] T016 [P] [US1] Implement `operations.create_task` function in `src/todo_app/operations.py` using `validate_title`, `validate_description`, and `storage.add`
- [X] T017 [P] [US1] Refactor `src/todo_app/operations.py` for docstrings and type hints; ensure `tests/test_operations.py` remain green

### TDD - UI and Integration Layer (`Add Task` flow)

- [X] T018 [P] [US1] Write failing tests for `ui.get_task_title`, `ui.get_task_description`, `ui.display_success` in `tests/test_ui.py` (mock input for prompts, capture stdout for display)
- [X] T019 [P] [US1] Implement `ui.get_task_title` and `ui.get_task_description` functions in `src/todo_app/ui.py`
- [X] T020 [P] [US1] Implement `ui.display_success` function in `src/todo_app/ui.py` to show confirmation messages and wait for Enter
- [X] T021 [P] [US1] Refactor `src/todo_app/ui.py` for docstrings and type hints; ensure `tests/test_ui.py` remain green
- [X] T022 [P] [US1] Write failing integration test for the full "Add Task" workflow in `tests/test_integration.py` (mock menu choice "1", mock user inputs, verify success message)
- [X] T023 [P] [US1] Implement `main.handle_add_task` function in `src/todo_app/main.py` to orchestrate UI inputs, operations call, and UI output
- [X] T024 [P] [US1] Refactor `src/todo_app/main.py` for docstrings and type hints; ensure `tests/test_integration.py` remain green

## Phase 4: User Story 2 - View All Tasks (P2)

*Goal: Display a formatted list of all tasks, including status and creation date. Depends on US1 for task creation.*
*Independent Test: User can successfully view a list of tasks via CLI, including empty list message, sorted by ID, with correct status/timestamp format. Unit tests for storage.get_all, operations.list_tasks, and ui.display_task_list pass.*

### TDD - Storage Layer (`get_all` operation)

- [X] T025 [P] [US2] Write failing tests for `InMemoryStorage.get_all` method in `tests/test_storage.py` (test returning all tasks, sorting by ID, and empty list)
- [X] T026 [P] [US2] Implement `InMemoryStorage.get_all` method in `src/todo_app/storage.py` to return tasks sorted by ID ascending
- [X] T027 [P] [US2] Refactor `src/todo_app/storage.py`; ensure `tests/test_storage.py` remain green

### TDD - Business Logic Layer (`list_tasks` operation)

- [X] T028 [P] [US2] Write failing tests for `operations.list_tasks` in `tests/test_operations.py` (test retrieving tasks from storage and returning them)
- [X] T029 [P] [US2] Implement `operations.list_tasks` function in `src/todo_app/operations.py`
- [X] T030 [P] [US2] Refactor `src/todo_app/operations.py`; ensure `tests/test_operations.py` remain green

### TDD - UI and Integration Layer (`View Task List` flow)

- [X] T031 [P] [US2] Write failing tests for `ui.format_timestamp`, `ui.format_status`, and `ui.display_task_list` in `tests/test_ui.py` (test timestamp format as YYYY-MM-DD HH:MM with sample datetime objects, snapshot tests for table formatting, empty list message)
- [X] T032 [P] [US2] Implement `ui.format_timestamp` and `ui.format_status` functions in `src/todo_app/ui.py` according to spec
- [X] T033 [P] [US2] Implement `ui.display_task_list` function in `src/todo_app/ui.py` to format and display tasks as a table
- [X] T034 [P] [US2] Refactor `src/todo_app/ui.py`; ensure `tests/test_ui.py` remain green
- [X] T035 [P] [US2] Write failing integration test for the full "View Task List" workflow in `tests/test_integration.py` (mock menu choice "2", verify task list output)
- [X] T036 [P] [US2] Implement `main.handle_view_tasks` function in `src/todo_app/main.py` to retrieve and display tasks
- [X] T037 [P] [US2] Refactor `src/todo_app/main.py`; ensure `tests/test_integration.py` remain green

## Phase 5: User Story 3 - Mark Tasks as Complete (P3)

*Goal: Allow users to toggle the completion status of a task by its ID. Depends on US1 for task creation and US2 for viewing status changes.*
*Independent Test: User can mark a task complete/incomplete via CLI, and the status changes correctly when viewed. Unit tests for storage.toggle_complete and operations.toggle_task_complete pass.*

### TDD - Storage Layer (`toggle_complete` operation)

- [X] T038 [P] [US3] Write failing tests for `InMemoryStorage.toggle_complete` method in `tests/test_storage.py` (test toggling status, handling non-existent IDs)
- [X] T039 [P] [US3] Implement `InMemoryStorage.toggle_complete` method in `src/todo_app/storage.py`
- [X] T040 [P] [US3] Refactor `src/todo_app/storage.py`; ensure `tests/test_storage.py` remain green

### TDD - Business Logic Layer (`toggle_task_complete` operation)

- [X] T041 [P] [US3] Write failing tests for `operations.toggle_task_complete` in `tests/test_operations.py` (test toggling, raising `TaskNotFoundError`)
- [X] T042 [P] [US3] Implement `operations.toggle_task_complete` function in `src/todo_app/operations.py`
- [X] T043 [P] [US3] Refactor `src/todo_app/operations.py`; ensure `tests/test_operations.py` remain green

### TDD - UI and Integration Layer (`Mark as Complete` flow)

- [X] T044 [P] [US3] Write failing tests for `ui.get_task_id` in `tests/test_ui.py` (test valid/invalid ID inputs)
- [X] T045 [P] [US3] Implement `ui.get_task_id` function in `src/todo_app/ui.py` to get and parse task ID
- [X] T046 [P] [US3] Refactor `src/todo_app/ui.py`; ensure `tests/test_ui.py` remain green
- [X] T047 [P] [US3] Write failing integration test for the full "Mark as Complete" workflow in `tests/test_integration.py` (mock menu choice "5", mock ID input, verify status change)
- [X] T048 [P] [US3] Implement `main.handle_mark_complete` function in `src/todo_app/main.py`
- [X] T049 [P] [US3] Refactor `src/todo_app/main.py`; ensure `tests/test_integration.py` remain green

## Phase 6: User Story 4 - Update Task Details (P4)

*Goal: Allow users to modify the title and/or description of an existing task by its ID. Depends on US1 for task creation and US2 for viewing updated details.*
*Independent Test: User can update a task's title/description via CLI, and changes are reflected when viewed. Unit tests for storage.update and operations.update_task pass.*

### TDD - Storage Layer (`update` operation)

- [X] T050 [P] [US4] Write failing tests for `InMemoryStorage.update` method in `tests/test_storage.py` (test updating title/description, handling non-existent IDs, partial updates)
- [X] T051 [P] [US4] Implement `InMemoryStorage.update` method in `src/todo_app/storage.py`
- [X] T052 [P] [US4] Refactor `src/todo_app/storage.py`; ensure `tests/test_storage.py` remain green

### TDD - Business Logic Layer (`update_task` operation)

- [X] T053 [P] [US4] Write failing tests for `operations.update_task` in `tests/test_operations.py` (test updating title/description, handling `TaskNotFoundError`, `ValidationError` for new title/description)
- [X] T054 [P] [US4] Implement `operations.update_task` function in `src/todo_app/operations.py`
- [X] T055 [P] [US4] Refactor `src/todo_app/operations.py`; ensure `tests/test_operations.py` remain green

### TDD - UI and Integration Layer (`Update Task` flow)

- [X] T056 [P] [US4] Write failing tests for `ui.get_optional_update` in `tests/test_ui.py` (test keeping current value with Enter, new value input)
- [X] T057 [P] [US4] Implement `ui.get_optional_update` function in `src/todo_app/ui.py`
- [X] T058 [P] [US4] Refactor `src/todo_app/ui.py`; ensure `tests/test_ui.py` remain green
- [X] T059 [P] [US4] Write failing integration test for the full "Update Task" workflow in `tests/test_integration.py` (mock menu choice "3", mock ID, mock new title/description, verify update)
- [X] T060 [P] [US4] Implement `main.handle_update_task` function in `src/todo_app/main.py`
- [X] T061 [P] [US4] Refactor `src/todo_app/main.py`; ensure `tests/test_integration.py` remain green

## Phase 7: User Story 5 - Delete Unnecessary Tasks (P5)

*Goal: Allow users to permanently remove tasks from the list by ID with a confirmation prompt. Depends on US1 for task creation and US2 for verifying deletion.*
*Independent Test: User can delete a task via CLI with confirmation, and it no longer appears in the list. Unit tests for storage.delete and operations.delete_task pass.*

### TDD - Storage Layer (`delete` operation)

- [X] T062 [P] [US5] Write failing tests for `InMemoryStorage.delete` method in `tests/test_storage.py` (test deleting existing/non-existent tasks)
- [X] T063 [P] [US5] Implement `InMemoryStorage.delete` method in `src/todo_app/storage.py`
- [X] T064 [P] [US5] Refactor `src/todo_app/storage.py`; ensure `tests/test_storage.py` remain green

### TDD - Business Logic Layer (`delete_task` operation)

- [X] T065 [P] [US5] Write failing tests for `operations.delete_task` in `tests/test_operations.py` (test deleting task, raising `TaskNotFoundError`)
- [X] T066 [P] [US5] Implement `operations.delete_task` function in `src/todo_app/operations.py`
- [X] T067 [P] [US5] Refactor `src/todo_app/operations.py`; ensure `tests/test_operations.py` remain green

### TDD - UI and Integration Layer (`Delete Task` flow)

- [X] T068 [P] [US5] Write failing tests for `ui.get_confirmation` in `tests/test_ui.py` (test valid/invalid confirmation inputs)
- [X] T069 [P] [US5] Implement `ui.get_confirmation` function in `src/todo_app/ui.py`
- [X] T070 [P] [US5] Refactor `src/todo_app/ui.py`; ensure `tests/test_ui.py` remain green
- [X] T071 [P] [US5] Write failing integration test for the full "Delete Task" workflow in `tests/test_integration.py` (mock menu choice "4", mock ID, mock confirmation, verify deletion)
- [X] T072 [P] [US5] Implement `main.handle_delete_task` function in `src/todo_app/main.py`
- [X] T073 [P] [US5] Refactor `src/todo_app/main.py`; ensure `tests/test_integration.py` remain green

## Phase 8: Polish & Cross-Cutting Concerns

*Goal: Finalize the main application loop, menu display, global error handling, and prepare for submission.*
*Independent Test: Application runs, menu functions correctly, all operations handled gracefully, README is updated.*

### Finalizing `ui.py`

- [X] T074 [P] Implement `ui.display_menu` function in `src/todo_app/ui.py` to show the main menu options
- [X] T075 [P] Implement `ui.get_menu_choice` function in `src/todo_app/ui.py` to get raw menu input (no validation)
- [X] T076 [P] Implement `ui.display_error` function in `src/todo_app/ui.py` to show formatted error messages
- [X] T077 [P] Implement `ui.wait_for_enter` function in `src/todo_app/ui.py` to pause for user input
- [ ] T078 [P] (Optional) Implement `ui.clear_screen` function in `src/todo_app/ui.py` for better UX (SKIPPED - not needed)
- [X] T079 [P] Refactor `src/todo_app/ui.py`; ensure all `tests/test_ui.py` remain green

### Finalizing `main.py`

- [X] T080 [P] Implement `main.main` function in `src/todo_app/main.py` to initialize storage and run the main menu loop
- [X] T081 [P] Implement menu dispatch in `main.py` using `match/case` statement to route user choices to appropriate `handle_` functions
- [X] T082 [P] Implement global exception handling in `main.py` for `ValidationError`, `TaskNotFoundError`, and `KeyboardInterrupt` (Ctrl+C)
- [X] T083 [P] Implement graceful exit for choice '6' and Ctrl+C in `main.py`
- [X] T084 [P] Refactor `src/todo_app/main.py`; ensure `tests/test_integration.py` remain green

### Final Integration Test

- [X] T085 [P] Write comprehensive integration tests in `tests/test_integration.py` covering all user stories and edge cases, ensuring data consistency and error handling across the entire application flow. Include explicit tests for: graceful exit via menu choice '6' (FR-014), Ctrl+C handling, and all exception scenarios.

### Documentation & Submission

- [X] T086 Update `README.md` in project root with setup instructions, usage guide, and feature overview
- [ ] T087 Record a demo video (max 90 seconds) demonstrating all 5 core features, setup, and execution
- [X] T088 Prepare final GitHub repository for submission (all tests pass ✅, coverage 77%, ready for commits)
- [ ] T089 [P] Run performance tests with 100 tasks to verify SC-006 requirements (view <3s, add <10s, update/delete/mark complete <5s each)
- [ ] T090 [P] Conduct user testing with 10+ participants to verify SC-008 (90% first-attempt success rate for creating and viewing tasks)
- [ ] T091 Submit project via the provided form by December 7, 2025
