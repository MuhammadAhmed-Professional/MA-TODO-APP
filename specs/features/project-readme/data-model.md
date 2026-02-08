# Data Model: Project README File (Documentation of existing data model)

**Feature**: 003-project-readme
**Date**: 2025-12-06

## Existing Data Model Reference: Phase I Console Application Tasks

While the `README.md` feature itself does not introduce a new data model, it documents the "Evolution of Todo" project, which in Phase I utilizes an in-memory data model for `Task` entities. This section serves to reference that existing model for completeness within the planning artifacts.

### Entity: Task

Represents a single To-Do item in the console application.

*   **Fields**:
    *   `id` (int): Unique identifier for the task. Automatically generated.
    *   `title` (str): A concise description of the task. (e.g., "Buy groceries").
    *   `description` (str, optional): A more detailed explanation of the task.
    *   `status` (enum: `pending`, `completed`): The current state of the task.
    *   `created_at` (datetime): Timestamp when the task was created.
    *   `updated_at` (datetime): Timestamp when the task was last modified.

*   **Relationships**: None in Phase I (in-memory, single-user context).

*   **Validation Rules (as per `operations.py`)**:
    *   `title` cannot be empty.
    *   `title` should have a reasonable length (e.g., 3-100 characters).
    *   `description` (if provided) should also have a reasonable length.
    *   `id` must exist for update/delete/complete operations.

*   **State Transitions**:
    *   `pending` -> `completed`
    *   (Future phases might introduce more complex states)

**Reference**: The detailed implementation of this data model can be found in `src/todo_app/models.py` and its management in `src/todo_app/storage.py` and `src/todo_app/operations.py`.
