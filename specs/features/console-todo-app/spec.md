# Feature Specification: In-Memory Python Console Todo Application (Phase 1)

**Feature Branch**: `001-console-todo-app`
**Created**: 2025-12-04
**Status**: Draft
**Input**: User description: "Phase 1: In-Memory Python Console Todo Application - Build a command-line todo application with 5 core features (Add, View, Update, Delete, Mark Complete) using TDD, clean code practices, and in-memory storage."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and Track New Tasks (Priority: P1)

As a user, I need to create tasks with titles and descriptions so I can capture what needs to be done and remember important details about each task.

**Why this priority**: This is the foundation of any todo application - without the ability to create tasks, no other feature has value. This establishes the minimum viable product.

**Independent Test**: Can be fully tested by launching the application, selecting "Add Task", entering a title and optional description, and verifying the task is created with a unique ID and confirmation message. Delivers immediate value as users can start capturing their todos.

**Acceptance Scenarios**:

1. **Given** the application is running and the main menu is displayed, **When** I select "Add Task" and enter a title "Buy groceries", **Then** the system assigns a unique ID, displays a confirmation "Task #1 'Buy groceries' created successfully", and returns to the main menu
2. **Given** I'm adding a new task, **When** I provide both a title "Call dentist" and description "Schedule annual checkup for next month", **Then** both the title and description are stored and confirmed
3. **Given** I'm prompted for a task title, **When** I enter an empty title or only whitespace (validated using `title.strip() == ""`), **Then** the system displays an error "Title cannot be empty" and prompts me again
4. **Given** I'm adding a task, **When** I enter a title with 200 characters, **Then** the system accepts it successfully
5. **Given** I'm adding a task, **When** I try to enter a title with 201 characters, **Then** the system displays an error "Title must be between 1-200 characters" and prompts me again
6. **Given** I'm adding a task description, **When** I enter 1000 characters, **Then** the system accepts it successfully
7. **Given** I'm adding a task description, **When** I try to enter 1001 characters, **Then** the system displays an error "Description cannot exceed 1000 characters" and prompts me again

---

### User Story 2 - View All Tasks (Priority: P2)

As a user, I need to see all my tasks in an organized list so I can review what I need to do and check the status of each task.

**Why this priority**: After creating tasks (P1), viewing them is the next most critical feature. Users need to see what tasks exist before they can update, delete, or mark them complete. This completes the basic read/write cycle.

**Independent Test**: Can be fully tested by creating a few tasks (using P1 functionality), then selecting "View Tasks" and verifying all tasks appear in a formatted table with ID, title, status indicator, and created date. Works independently even if update/delete features don't exist yet.

**Acceptance Scenarios**:

1. **Given** I have created 3 tasks, **When** I select "View Task List", **Then** all 3 tasks are displayed in a formatted table showing ID, Title, Status ([ ] for incomplete), and Created Date
2. **Given** I have one completed task and two incomplete tasks, **When** I view the task list, **Then** the completed task shows [✓] and incomplete tasks show [ ] as status indicators
3. **Given** I have not created any tasks yet, **When** I select "View Task List", **Then** the system displays "No tasks found. Create your first task to get started!" and returns to the main menu
4. **Given** I have 10 tasks in the list, **When** I view tasks, **Then** all 10 tasks are displayed with consistent formatting and clear separation between entries
5. **Given** tasks were created at different times, **When** I view the task list, **Then** each task shows its creation timestamp in a readable format (e.g., "2025-12-04 14:30")
6. **Given** I have tasks #1 (complete), #2 (incomplete), #3 (complete), #4 (incomplete), **When** I view the task list, **Then** tasks appear in order: #1, #2, #3, #4 (ascending by ID, with completed and incomplete tasks intermixed)

---

### User Story 3 - Mark Tasks as Complete (Priority: P3)

As a user, I need to mark tasks as complete so I can track my progress and distinguish between finished and pending work.

**Why this priority**: After creating (P1) and viewing (P2) tasks, marking them complete is the next logical step. This enables users to track progress without modifying or deleting tasks, maintaining a record of completed work.

**Independent Test**: Can be fully tested by creating tasks (P1), viewing them (P2), marking one complete, and verifying the status changes from [ ] to [✓] when viewing again. Delivers value as a standalone "done tracking" feature.

**Acceptance Scenarios**:

1. **Given** I have an incomplete task with ID 5, **When** I select "Mark as Complete", enter ID 5, **Then** the system confirms "Task #5 marked as complete" and updates the status to [✓]
2. **Given** I have a completed task with ID 3, **When** I select "Mark as Complete", enter ID 3, **Then** the system confirms "Task #3 marked as incomplete" and updates the status to [ ] (toggle behavior)
3. **Given** I'm prompted to enter a task ID to mark complete, **When** I enter a non-existent ID 99, **Then** the system displays "Error: Task #99 not found" and returns to the main menu
4. **Given** I'm prompted to enter a task ID, **When** I enter invalid input like "abc" or negative numbers, **Then** the system displays "Error: Invalid task ID. Please enter a valid number" and prompts again
5. **Given** I mark task #2 as complete, **When** I view the task list, **Then** task #2 shows [✓] status while other tasks remain unchanged

---

### User Story 4 - Update Task Details (Priority: P4)

As a user, I need to modify task titles and descriptions so I can correct mistakes or update tasks as requirements change.

**Why this priority**: This feature enhances usability but isn't critical for the MVP. Users can work around missing update functionality by deleting and recreating tasks. It's valuable for user experience but not blocking.

**Independent Test**: Can be fully tested by creating a task (P1), updating its title and/or description, and verifying the changes are saved when viewing (P2). Delivers value as a "task editing" feature independent of deletion.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 2 titled "Old Title", **When** I select "Update Task", enter ID 2, provide new title "Updated Title", and press Enter to skip description, **Then** the system confirms "Task #2 updated successfully" and the title changes to "Updated Title" while description remains unchanged
2. **Given** I'm updating task #4, **When** I press Enter to skip the title prompt and then provide a new description, **Then** only the description is updated and the title remains the same
3. **Given** I'm updating a task, **When** I provide both a new title and new description (not pressing Enter to skip either field), **Then** both fields are updated simultaneously
4. **Given** I'm prompted to update a task, **When** I enter a non-existent task ID 50, **Then** the system displays "Error: Task #50 not found" and returns to the main menu
5. **Given** I'm updating a task title, **When** I try to set an empty title or one exceeding 200 characters, **Then** the system displays the appropriate validation error and prompts again
6. **Given** I'm updating a task description, **When** I try to enter more than 1000 characters, **Then** the system displays "Description cannot exceed 1000 characters" and prompts again
7. **Given** I successfully update a task, **When** I view the task list, **Then** I see the updated information reflected immediately

---

### User Story 5 - Delete Unnecessary Tasks (Priority: P5)

As a user, I need to remove tasks I no longer need so I can keep my task list clean and focused on relevant work.

**Why this priority**: This is the lowest priority feature because users can simply ignore unwanted tasks or mark them complete. While useful for list management, it's not essential for core todo tracking functionality.

**Independent Test**: Can be fully tested by creating tasks (P1), selecting a task to delete, confirming the deletion, and verifying it no longer appears when viewing tasks (P2). Delivers value as a standalone "cleanup" feature.

**Acceptance Scenarios**:

1. **Given** I have a task with ID 7, **When** I select "Delete Task", enter ID 7, and confirm with "y", **Then** the system confirms "Task #7 deleted successfully" and the task is permanently removed
2. **Given** I'm prompted to delete task #3, **When** I enter "n" to the confirmation prompt, **Then** the deletion is cancelled, task #3 remains in the list, and the system displays "Deletion cancelled"
3. **Given** I'm prompted to enter a task ID to delete, **When** I enter a non-existent ID 100, **Then** the system displays "Error: Task #100 not found" and returns to the main menu
4. **Given** I have 5 tasks, **When** I delete task #3, **Then** only task #3 is removed and the other 4 tasks remain with their original IDs unchanged
5. **Given** I'm prompted for deletion confirmation, **When** I enter invalid input (not 'y' or 'n'), **Then** the system displays "Please enter 'y' for yes or 'n' for no" and prompts again
6. **Given** I successfully delete a task, **When** I view the task list, **Then** the deleted task no longer appears
7. **Given** I have tasks #1, #2, #3 and delete task #2, **When** I create a new task, **Then** it receives ID #4 (not #2), confirming IDs are never reused after deletion

---

### Edge Cases

- What happens when a user enters an invalid menu choice (e.g., "7", "abc", empty input)?
  - System should display "Invalid choice. Please enter a number between 1 and 6" and re-display the menu

- What happens when a user tries to create a task with special characters or unicode in the title/description?
  - System should accept all valid Unicode characters (emojis, non-Latin scripts, symbols)

- What happens when a user enters a very large number (e.g., 999999999) as a task ID?
  - System should validate and display "Error: Task #999999999 not found"

- What happens when a user presses Ctrl+C or tries to exit during an input prompt?
  - System should handle gracefully, display "Operation cancelled", and return to main menu (or exit cleanly if at main menu)

- What happens when the system has many tasks (e.g., 100+) and the display exceeds terminal height?
  - All tasks should display without truncation (user scrolls terminal); no pagination needed for Phase 1

- What happens when the user runs the application multiple times?
  - Each session starts fresh with no tasks (in-memory storage resets between runs)

- What happens when a user tries to mark a non-existent task as complete?
  - System displays "Error: Task #[ID] not found" and returns to main menu

- What happens when a user tries to update or delete the same task ID multiple times in one session?
  - System should handle each operation independently based on current state

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a numbered menu interface with 6 options: (1) Add Task, (2) View Task List, (3) Update Task, (4) Delete Task, (5) Mark as Complete, (6) Exit
- **FR-001a**: System MUST validate menu input and display "Invalid choice. Please enter a number between 1 and 6" for any input outside the valid range (including non-numeric input, empty/whitespace-only input determined by `input.strip() == ""`, or numbers <1 or >6), then re-display the menu
- **FR-002**: System MUST allow users to create tasks with a required title (1-200 characters) and optional description (max 1000 characters)
- **FR-003**: System MUST assign a unique, auto-incrementing integer ID to each created task
- **FR-004**: System MUST store the following information for each task: ID, title, description, completion status (true/false), and creation timestamp
- **FR-005**: System MUST display all tasks in a formatted table showing: ID, Title, Status indicator ([✓] or [ ]), and Created Date, ordered by ID in ascending order (creation order, with completed and incomplete tasks intermixed)
- **FR-006**: System MUST allow users to toggle task completion status by task ID
- **FR-007**: System MUST allow users to update task title and/or description by task ID, prompting for each field separately with the option to skip (press Enter with empty input) to keep the current value unchanged; skipping both fields is valid and results in a no-op update with success confirmation
- **FR-008**: System MUST allow users to permanently delete tasks by task ID with confirmation prompt ("Are you sure? y/n")
- **FR-009**: System MUST validate all user inputs and display clear error messages for invalid data (empty/whitespace-only titles determined by `title.strip() == ""`, exceeding character limits, invalid IDs including negative numbers/zero/non-numeric strings, non-existent tasks)
- **FR-010**: System MUST store all data in memory during program execution (no file I/O or database persistence)
- **FR-011**: System MUST return to the main menu after completing each operation (except Exit)
- **FR-012**: System MUST display confirmation messages after successful operations (e.g., "Task #5 created successfully")
- **FR-013**: System MUST handle empty task lists gracefully by displaying "No tasks found. Create your first task to get started!"
- **FR-014**: System MUST accept the "Exit" command and terminate cleanly
- **FR-015**: System MUST format creation timestamps in human-readable format with minute-level precision: YYYY-MM-DD HH:MM (e.g., "2025-12-04 14:30", no seconds displayed), using system local timezone with no timezone conversion
- **FR-016**: System MUST use `ValidationError` exception class for all input validation failures (empty titles, exceeding character limits, invalid format)
- **FR-017**: System MUST use `TaskNotFoundError` exception class when operations reference non-existent task IDs

### Key Entities *(include if feature involves data)*

- **Task**: Represents a single todo item with the following attributes:
  - ID (integer): Unique identifier, auto-incremented starting from 1
  - Title (string): Required, 1-200 characters, describes the task
  - Description (string): Optional, max 1000 characters, provides additional details
  - Completed (boolean): Indicates completion status, defaults to false/incomplete
  - Created At (timestamp): Records when the task was created, displayed in YYYY-MM-DD HH:MM format (minute-level precision)

- **Task Storage**: Manages the in-memory collection of tasks
  - Maintains a dictionary/map of Task ID to Task object for fast lookup
  - Tracks the next available ID for auto-increment (never reuses deleted IDs)
  - ID assignment: continues incrementing from highest ID ever assigned, even after deletions
  - Provides operations: add, get, update, delete, list all, toggle complete

### Implementation Notes

**ID Assignment Strategy**: Task IDs are assigned automatically by the storage layer's `add()` method. Callers do not provide IDs when creating tasks; instead, the storage layer creates the Task object internally with an auto-generated ID starting from 1 and incrementing with each new task. IDs are never reused after deletion to prevent user confusion and maintain consistency with future database implementations.

**Validation Strategy**: Empty and whitespace-only inputs are validated using `input.strip() == ""` for consistency across all input fields (titles, descriptions, menu choices).

**Timezone Handling**: All timestamps use `datetime.now()` with system local timezone. No timezone conversion is performed in Phase 1.

**Delete Operation Behavior**: The delete operation (FR-008) prompts for confirmation ("Are you sure? y/n"), then permanently removes the task from storage. The operation returns no value (void/None) after successful deletion; confirmation of deletion is communicated via success message display only.

**Screen Management**: Returning to the main menu (FR-011) does not require clearing the terminal screen. The menu is displayed via standard output, allowing users to scroll their terminal history. Screen clearing is an optional enhancement and not required for Phase 1 compliance.

**Terminology - "Mark as Complete"**: User-facing language uses "Mark as Complete" (menu option, user story title) while implementation uses "toggle completion status" (FR-006) to accurately describe the technical behavior (incomplete→complete, complete→incomplete). This dual terminology is intentional: user language emphasizes the primary use case (marking tasks done), while technical language describes the actual behavior (bidirectional toggle).

**Terminology - "Task Storage"**: The entity concept is written as "Task Storage" (Key Entities section) while the interface class name is `TaskStorage` (code and technical documentation). This follows standard naming conventions: title-cased concept names in specifications, PascalCase class names in implementation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

All success criteria must be verified by **December 7, 2025** (Phase 1 submission deadline).

- **SC-001**: Users can create a new task in under 10 seconds (from menu selection to confirmation), verified by manual testing with 5+ test users completing task creation workflow

- **SC-002**: Users can view their complete task list in under 3 seconds regardless of task count (tested with 10, 50, and 100 tasks), measured via automated timing tests

- **SC-003**: System displays error messages within 1 second for all invalid inputs, where each message includes:
  - What went wrong (e.g., "Title cannot be empty")
  - What to do next (e.g., "Please enter a title between 1-200 characters")
  - No technical jargon, stack traces, variable names, or code references
  - Verified by checklist review: 100% of error messages meet these criteria

- **SC-004**: All 5 core operations (Add, View, Update, Delete, Mark Complete) execute without crashes or unhandled exceptions when:
  - Given valid inputs: 100% success rate (10+ test cases per operation)
  - Given invalid inputs: Return to menu with error message, no crashes (10+ test cases per operation)
  - Tested with automated test suite achieving 80%+ code coverage

- **SC-005**: All user input validations catch and handle errors according to specification:
  - Empty titles rejected: 100% of test cases pass (5+ tests)
  - Titles >200 chars rejected: 100% of test cases pass (3+ tests)
  - Descriptions >1000 chars rejected: 100% of test cases pass (3+ tests)
  - Invalid task IDs rejected: 100% of test cases pass (5+ tests)
  - Non-numeric IDs rejected: 100% of test cases pass (3+ tests)
  - Overall test suite achieves 80%+ code coverage

- **SC-006**: System maintains performance with 100 tasks in memory:
  - View operation completes in <3 seconds (same as SC-002 baseline)
  - Add operation completes in <10 seconds (same as SC-001 baseline)
  - Update/Delete/Mark Complete operations complete in <5 seconds each
  - No operation exceeds 2x the baseline time measured with 10 tasks
  - Verified via automated performance tests

- **SC-007**: All error messages follow this format (verified by manual review):
  - State what went wrong in plain language (e.g., "Title is too long")
  - State valid input requirements (e.g., "Title must be 1-200 characters")
  - Allow user to retry immediately (return to input prompt, not menu)
  - Contain zero instances of: technical terms, stack traces, variable names, "Error:", "Exception", or code references
  - Checklist verification: 100% of error messages (15+ unique error scenarios) meet all 4 criteria

- **SC-008**: Users successfully complete their primary task (creating and viewing tasks) on first attempt 90% of the time:
  - Measured via user testing with 10+ participants
  - Each participant performs: Launch app → Add task → View task list
  - Success = completion without errors or confusion
  - Target: ≥9 out of 10 users succeed on first attempt
  - Testing completed by December 6, 2025 (day before submission)

- **SC-009**: Task data remains accurate throughout program session:
  - Created tasks retain exact title and description after creation (100% character-by-character match)
  - Updated tasks reflect new values immediately when viewed (100% match, verified within same session)
  - Task IDs never change, duplicate, or skip during session (verified via automated tests)
  - Completed status persists correctly between operations (100% accuracy verified)
  - Task count equals: (create operations) minus (delete operations) at all times
  - Tested with 50+ sequential mixed operations with zero data discrepancies

- **SC-010**: System handles all boundary conditions without crashes (100% pass rate):
  - Accepts task title with exactly 200 characters (verified with test case)
  - Accepts task description with exactly 1000 characters (verified with test case)
  - Rejects task title with 201 characters with appropriate error message
  - Rejects task description with 1001 characters with appropriate error message
  - Handles task ID 999999999 gracefully (displays "Task #999999999 not found", no crash)
  - Handles negative task IDs gracefully (displays error message, no crash)
  - Handles task ID 0 gracefully (displays error message, no crash)
  - All 7+ boundary test cases achieve 100% pass rate in test suite

## Scope & Constraints

### In Scope for Phase 1

- Command-line interface with numbered menu system
- Five core CRUD operations (Create, Read, Update, Delete, Mark Complete)
- In-memory task storage using Python data structures
- Input validation with user-friendly error messages
- Formatted task display with status indicators
- Confirmation prompts for destructive operations (delete)
- Auto-incrementing task IDs
- Task creation timestamps

### Out of Scope for Phase 1

- Persistent storage (file I/O or database) - deferred to Phase 2
- Multi-user support or user authentication - deferred to Phase 2
- Task search, filtering, or sorting - deferred to Phases 2-5
- Task priorities, tags, or categories - deferred to Phases 2-5
- Recurring tasks or reminders - deferred to Phase 5
- Due dates or time-based features - deferred to Phase 5
- Web interface, API, or GUI - deferred to Phase 2
- AI chatbot integration - deferred to Phase 3
- Containerization or cloud deployment - deferred to Phases 4-5

### Technical Constraints

- Technology stack: Python 3.13+, UV for dependency management
- Testing framework: pytest with minimum 80% code coverage
- Code quality: Type hints required, PEP 8 compliance, max 50 lines per function
- Development approach: Spec-driven development with TDD (Red-Green-Refactor)
- Architecture: Must be designed to accommodate future database persistence (Phase 2)

### Timeline & Submission

- Completion deadline: Sunday, December 7, 2025
- Demo video: Maximum 90 seconds
- Submission: Via form at https://forms.gle/CQsSEGM3GeCrL43c8

## Assumptions

1. **Terminal Environment**: Users have access to a standard terminal/command-line interface with support for basic text formatting
2. **Single User Session**: Only one user operates the application at a time (no concurrent access)
3. **Session-Based Usage**: Users accept that data is lost when the application exits (documented as expected behavior for Phase 1)
4. **Character Encoding**: Terminal supports UTF-8 for unicode characters in task titles/descriptions
5. **Input Method**: Users interact via keyboard text input (no mouse, touch, or voice input)
6. **Task ID Display**: Task IDs can be displayed without privacy concerns (no sensitive data implied by sequential numbering)
7. **Error Recovery**: Users can retry operations after receiving error messages without restarting the application
8. **Memory Limits**: System memory is sufficient to hold at least 1000 tasks (reasonable for in-memory Phase 1)
9. **Display Width**: Terminal width is at least 80 characters for proper table formatting
10. **Timestamp Format**: System timezone is used for timestamps (no timezone conversion needed)

## Dependencies

- Python 3.13+ runtime environment
- UV package manager (for dependency management and project setup)
- pytest framework (for test execution)
- Standard library modules only (no external dependencies for core functionality)

## Risks & Mitigations

### Risk 1: Data Loss Between Sessions
**Impact**: Users lose all tasks when application closes
**Mitigation**: Clearly document this as expected Phase 1 behavior; Phase 2 will add persistence

### Risk 2: Memory Limitations
**Impact**: Very large task lists (1000+) might impact performance
**Mitigation**: Design storage layer (TaskStorage class) with future database migration in mind; test with at least 100 tasks

### Risk 3: Input Validation Complexity
**Impact**: Edge cases in user input might cause unexpected behavior
**Mitigation**: Comprehensive test suite covering boundary conditions, invalid inputs, and unicode characters

### Risk 4: Terminal Compatibility
**Impact**: Different terminals may render formatting differently
**Mitigation**: Use basic text formatting (spaces, dashes, brackets) that works across all terminals; avoid complex ASCII art or terminal-specific features

## Notes

- This specification intentionally avoids implementation details (no mention of dataclasses, Pydantic, specific storage mechanisms)
- Architecture should anticipate Phase 2 database migration by using abstraction layers (storage interface)
- All features are independently testable and can be demonstrated in isolation
- Priority order (P1→P5) reflects MVP thinking: Create→View→Complete→Update→Delete
