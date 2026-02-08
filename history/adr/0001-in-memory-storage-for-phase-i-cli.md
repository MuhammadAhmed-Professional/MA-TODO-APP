# ADR-0001: In-Memory Storage for Phase I CLI

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** console-todo-app (Phase I)
- **Context:** Phase I requires a functional CLI todo application with basic CRUD operations. The primary goals are rapid development, comprehensive testing, and establishing core business logic patterns. Persistence is explicitly out of scope for this phase as the focus is on proving the concept and building a solid foundation for future phases.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Sets data layer pattern
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - File storage, SQLite, PostgreSQL considered
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects testing, deployment, state management
-->

## Decision

Use **in-memory storage** (Python dictionary-based) for the Phase I CLI todo application with the following characteristics:

- **Storage Implementation**: Python `dict` storing Task objects indexed by integer IDs
- **Session Scope**: Data persists only during application runtime (no file I/O)
- **State Management**: Single `InMemoryStorage` class encapsulating all CRUD operations
- **Testing Strategy**: Pure unit tests with fast execution (no I/O mocking required)
- **Migration Path**: Clear interface (`get()`, `save()`, `delete()`, `get_all()`) allows seamless replacement in Phase II

## Consequences

### Positive

- ✅ **Rapid Development**: No database setup, configuration, or connection management required
- ✅ **Fast Test Execution**: 87 tests run in <2 seconds (no I/O overhead)
- ✅ **Zero Dependencies**: No external libraries (SQLAlchemy, sqlite3, etc.) reduces complexity
- ✅ **Pure Business Logic**: Forces focus on core operations logic without persistence concerns
- ✅ **Perfect for Prototyping**: Enables quick iteration and validation of requirements
- ✅ **Deterministic Testing**: No flaky tests due to file system race conditions or database state
- ✅ **Portable**: Runs anywhere Python runs without installation steps
- ✅ **Clear Interface**: Storage abstraction makes Phase II migration straightforward

### Negative

- ❌ **No Persistence**: All data lost on application exit (acceptable for Phase I scope)
- ❌ **Single User Only**: Cannot share data across application instances
- ❌ **No Scalability**: Limited by process memory (not a concern for Phase I)
- ❌ **No Concurrency**: Not thread-safe (single-threaded CLI doesn't need it)
- ❌ **Migration Required**: Phase II will need complete storage rewrite
- ❌ **Limited Demo Value**: Cannot showcase persistence capabilities to stakeholders

## Alternatives Considered

### Alternative 1: File-Based Storage (JSON/Pickle)

**Approach**: Store tasks in `tasks.json` or `tasks.pkl` file

**Pros**:
- Simple persistence across sessions
- No external dependencies
- Human-readable (JSON) or efficient (Pickle)

**Cons**:
- File I/O adds complexity (read/write errors, permissions, corruption)
- Slower tests (need temp file cleanup)
- Concurrency issues (multiple instances could corrupt file)
- Still needs migration for Phase II (not compatible with PostgreSQL)

**Why Rejected**: Added complexity without strategic benefit. Phase II will use PostgreSQL anyway, so file storage doesn't reduce migration effort.

### Alternative 2: SQLite Database

**Approach**: Use embedded SQLite database with `sqlite3` module

**Pros**:
- Relational database experience (closer to Phase II)
- ACID transactions
- SQL query practice
- Persistence across sessions

**Cons**:
- Requires SQL schema definition upfront
- Slower tests (need database setup/teardown)
- Added complexity for Phase I scope
- Migration still required (PostgreSQL has different features)
- Database file management (location, cleanup, portability)

**Why Rejected**: Overengineering for Phase I. The migration effort to PostgreSQL in Phase II is similar whether coming from SQLite or in-memory, but in-memory enables faster development and testing.

### Alternative 3: Start with PostgreSQL (Jump to Phase II)

**Approach**: Skip in-memory, use Neon PostgreSQL from the start

**Pros**:
- No migration needed between phases
- Production-ready architecture from day one
- Learn PostgreSQL patterns early

**Cons**:
- Requires Neon account, connection string, network access
- Significantly slower development (schema migrations, connection handling)
- Much slower tests (network I/O, database cleanup)
- Overcomplicates simple CRUD validation
- High barrier to entry for contributors
- Cannot work offline

**Why Rejected**: Violates Phase I goal of rapid prototyping. In-memory storage allows focus on business logic first, infrastructure second. The migration cost to Phase II is acceptable given the development velocity gains in Phase I.

## References

- Feature Spec: `specs/features/console-todo-app/spec.md`
- Implementation: `phase-1/src/todo_app/storage.py` (195 LoC)
- Test Suite: `phase-1/tests/test_storage.py` (6 test classes, 13 tests)
- Test Coverage: 87 tests passing, 77% code coverage
- Phase Completion Report: `phase-1/PHASE_COMPLETION.md`
- Related ADRs:
  - ADR-0002: UV Package Manager (Python dependency management)
  - ADR-0007: Monorepo with Phase-Wise Organization (project structure)
- Migration Note: Phase II ADR-0005 (Neon PostgreSQL) supersedes this decision for web application

---

**Implementation Evidence**:
- Storage class interface designed for swappability
- All 87 tests pass in 1.67 seconds
- No external dependencies beyond Python 3.13 stdlib
- Clear separation of concerns (storage.py isolated from business logic)

**Evaluation Outcome**: ✅ **PASS** - This ADR meets all significance criteria:
1. ✅ Impact: Sets data layer architecture pattern for all phases
2. ✅ Alternatives: Three alternatives explicitly considered with tradeoffs
3. ✅ Scope: Cross-cutting decision affecting testing, development velocity, and Phase II migration

**Retrospective (2025-12-11)**: Documented retroactively after Phase I completion (100%). Decision proved correct - rapid development enabled 87 comprehensive tests and full feature implementation in minimal time. Migration to PostgreSQL in Phase II was straightforward due to clean storage abstraction.
