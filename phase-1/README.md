# MA-TODO-APP - Phase I: Console Todo App

**Status**: Complete (100%)
**Tests**: 87 passing
**Coverage**: 77%

## Features
- Create, read, update, delete tasks
- Mark tasks as complete
- View tasks by status
- Search tasks
- CLI banner with ASCII art

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
- **Pattern**: Layered (UI -> Operations -> Storage)
- **Storage**: In-memory (data lost on exit)
- **Tests**: Unit + Integration (87 tests)

See `PHASE_COMPLETION.md` for full test report.
