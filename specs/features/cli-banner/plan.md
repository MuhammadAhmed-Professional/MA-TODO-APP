# Implementation Plan: CLI Banner with Branding

**Branch**: `002-cli-banner` | **Date**: 2025-12-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-cli-banner/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement a professional ASCII art banner displaying "Talal's TDA - Your Personal Task Manager" at application startup. The banner will include version information, copyright notice, and optional ANSI color enhancement with graceful fallback. Technical approach involves creating a banner display module with terminal capability detection, integrating with the existing application startup sequence in main.py, and ensuring 80-column compatibility with sub-100ms rendering performance.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: Python standard library only (no external dependencies)
**Storage**: N/A (banner content stored as static constants)
**Testing**: pytest with mocking for terminal capabilities and output capture
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows/WSL2)
**Project Type**: Single project (existing todo_app module extension)
**Performance Goals**: <100ms banner display time, imperceptible to users
**Constraints**:
- Maximum 15 lines height to preserve screen real estate
- 80-column width compatibility (industry standard terminal minimum)
- No external dependencies (use only Python stdlib)
- ASCII-only characters (codes 32-126) for maximum compatibility
**Scale/Scope**: Small feature addition to existing Phase I console app (single module, ~3-4 functions)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅ PASS
- ✅ Feature specification exists at `specs/002-cli-banner/spec.md`
- ✅ Spec includes clear user stories (P1-P3 prioritized)
- ✅ Acceptance criteria defined with Given/When/Then scenarios
- ✅ Edge cases identified (terminal width, encoding, colors)
- ✅ Success criteria are measurable and testable

### Principle II: Clean Code & Pythonic Standards ✅ PASS
- ✅ Will follow PEP 8 style guidelines
- ✅ Type hints required for all banner functions
- ✅ Descriptive function names (e.g., `display_banner()`, `detect_terminal_capabilities()`)
- ✅ Functions will be under 50 lines (simple banner display logic)
- ✅ Docstrings required for all public functions

### Principle III: Test-First Development (TDD) ✅ PASS
- ✅ Will follow Red-Green-Refactor cycle
- ✅ Unit tests for banner rendering functions
- ✅ Mocking terminal capabilities for deterministic testing
- ✅ Output capture tests to verify banner content
- ✅ Target: 100% coverage for banner module

### Principle IV: Simple In-Memory Storage ✅ PASS (N/A)
- ✅ No storage required (banner is display-only feature)
- ✅ Banner content stored as static constants (not persisted data)

### Principle V: CLI Interface Excellence ✅ PASS
- ✅ Banner enhances user experience with professional branding
- ✅ Clear separation between banner and menu (blank line)
- ✅ Graceful fallback when terminal doesn't support colors
- ✅ No disruption to existing menu system

### Principle VI: Python 3.13+ Modern Practices ✅ PASS
- ✅ Python 3.13+ (matches existing project)
- ✅ No new dependencies (uses stdlib only)
- ✅ Modern type hints (`str | None` instead of `Optional[str]`)
- ✅ Match/case not applicable (simple conditional logic)

**Gate Status**: ✅ ALL GATES PASS - Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/002-cli-banner/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (N/A for display-only feature)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/todo_app/
├── __init__.py
├── main.py              # MODIFIED: Add banner display call at startup
├── models.py            # Unchanged
├── storage.py           # Unchanged
├── operations.py        # Unchanged
├── ui.py                # MODIFIED: Add banner display functions
└── banner.py            # NEW: Banner rendering logic

tests/
├── test_models.py       # Unchanged
├── test_storage.py      # Unchanged
├── test_operations.py   # Unchanged
├── test_ui.py           # MODIFIED: Add banner display tests
├── test_integration.py  # Unchanged
└── test_banner.py       # NEW: Banner module unit tests
```

**Structure Decision**: Single project structure maintained. Banner functionality added as a new module (`banner.py`) with display functions integrated into the existing UI layer. This minimizes coupling and allows for easy testing in isolation.

## Complexity Tracking

> No constitution violations. This section is empty.

---

## Phase 0: Research & Investigation

### Research Tasks

#### R1: ASCII Art Design for "Talal's TDA"

**Objective**: Design professional ASCII art that displays "Talal's TDA" within 80 columns and under 15 lines.

**Investigation Areas**:
1. ASCII art generation tools (patorjk.com, figlet, text-to-ascii)
2. Font selection for maximum readability in 80-column constraint
3. Banner layout with tagline and metadata placement
4. Visual hierarchy (title prominent, metadata subtle)

**Deliverable**: 2-3 ASCII art banner designs for selection

#### R2: Terminal Capability Detection

**Objective**: Determine reliable methods to detect terminal width and color support using Python stdlib only.

**Investigation Areas**:
1. `os.get_terminal_size()` for width detection (stdlib)
2. `sys.stdout.isatty()` for interactive terminal detection
3. Environment variables for color support (`TERM`, `COLORTERM`)
4. ANSI color code standards (256-color, 16-color, monochrome fallback)
5. Cross-platform compatibility (Linux, macOS, Windows/WSL2)

**Deliverable**: Terminal detection strategy with fallback chain

#### R3: Version Information Extraction

**Objective**: Identify best practice for extracting version number from pyproject.toml or package metadata.

**Investigation Areas**:
1. `importlib.metadata.version()` for installed packages
2. Direct `pyproject.toml` parsing with `tomllib` (Python 3.11+)
3. Fallback strategies when version unavailable (dev environment)
4. Performance implications of different approaches

**Deliverable**: Version extraction implementation pattern

#### R4: ANSI Color Best Practices

**Objective**: Research ANSI color codes and best practices for cross-platform terminal styling.

**Investigation Areas**:
1. ANSI escape code standards (foreground, background, reset)
2. Color palette selection for accessibility (contrast ratios)
3. Graceful degradation when colors not supported
4. Testing color output in different terminal emulators
5. Windows Terminal vs WSL2 vs legacy cmd.exe compatibility

**Deliverable**: Color scheme and fallback strategy

#### R5: Banner Display Performance

**Objective**: Validate that banner display can meet <100ms performance target.

**Investigation Areas**:
1. String concatenation vs list join performance
2. Print buffering and flush strategies
3. Impact of terminal capability detection overhead
4. Caching strategies for repeated calls (though banner shown once)

**Deliverable**: Performance benchmark results and optimization recommendations

### Research Consolidation

All research findings will be consolidated in `research.md` with the following format:
- **Decision**: What approach/tool/pattern was selected
- **Rationale**: Why this choice is optimal for the feature
- **Alternatives Considered**: What other options were evaluated and why they were rejected
- **Implementation Notes**: Key details for Phase 1 design

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all decisions finalized

### D1: Data Model (`data-model.md`)

**Banner Configuration Entity**:
- `ASCII_ART`: Multi-line string constant for "Talal's TDA" artwork
- `TAGLINE`: String constant for "Your Personal Task Manager"
- `VERSION`: String extracted from package metadata or pyproject.toml
- `COPYRIGHT`: String constant for "© 2025 Talal"

**Terminal Capabilities Entity**:
- `terminal_width`: Integer (detected width in columns)
- `supports_color`: Boolean (ANSI color support detected)
- `is_interactive`: Boolean (stdout is a TTY)

**No database schema or relationships required (display-only feature)**

### D2: Function Contracts

**Module**: `src/todo_app/banner.py`

#### Function: `display_banner()`
```python
def display_banner() -> None:
    """Display the application banner at startup.

    Renders ASCII art banner with version and copyright information.
    Automatically detects terminal capabilities for color support.
    Falls back to plain text if colors not supported.

    Performance: <100ms on standard terminals
    Side Effects: Prints to stdout

    Raises:
        None (errors handled gracefully with fallbacks)
    """
```

#### Function: `get_banner_content(use_color: bool = False) -> str`
```python
def get_banner_content(use_color: bool = False) -> str:
    """Generate banner content as a string.

    Args:
        use_color: If True, include ANSI color codes

    Returns:
        Complete banner text including ASCII art, tagline,
        version, and copyright information

    Notes:
        - ASCII art is 80-column compatible
        - Total height <= 15 lines
        - Color codes automatically stripped if use_color=False
    """
```

#### Function: `detect_terminal_capabilities() -> dict[str, Any]`
```python
def detect_terminal_capabilities() -> dict[str, Any]:
    """Detect terminal width and color support.

    Returns:
        Dictionary with keys:
        - 'width': Terminal width in columns (int)
        - 'supports_color': ANSI color support (bool)
        - 'is_interactive': stdout is a TTY (bool)

    Fallbacks:
        - Default width: 80 columns
        - Default color: False (safe default)
        - Default interactive: False for pipes
    """
```

#### Function: `get_version() -> str`
```python
def get_version() -> str:
    """Extract application version from package metadata.

    Returns:
        Version string (e.g., "1.0.0")

    Fallback:
        Returns "dev" if version cannot be determined

    Implementation:
        Uses importlib.metadata.version() or pyproject.toml parsing
    """
```

### D3: Integration Contract

**Module**: `src/todo_app/main.py`

**Change**: Add banner display call at application startup (before menu loop)

```python
def main() -> None:
    """Main application entry point with menu loop and exception handling."""
    # Initialize storage
    storage = InMemoryStorage()

    # NEW: Display banner at startup
    display_banner()

    # Existing welcome message
    print("Welcome to Todo List Application!")
    print("=" * 40)

    # ... existing menu loop ...
```

### D4: Test Contracts

**Module**: `tests/test_banner.py`

Test Coverage Requirements:
- ✅ `test_display_banner_with_color()` - Verify color codes present
- ✅ `test_display_banner_without_color()` - Verify plain text fallback
- ✅ `test_get_banner_content_structure()` - Verify line count, width constraints
- ✅ `test_detect_terminal_capabilities()` - Mock different terminal scenarios
- ✅ `test_get_version_success()` - Extract version correctly
- ✅ `test_get_version_fallback()` - Handle missing version gracefully
- ✅ `test_banner_width_80_columns()` - Ensure no line exceeds 80 chars
- ✅ `test_banner_height_under_15_lines()` - Ensure total height <= 15
- ✅ `test_color_codes_stripped_when_disabled()` - Verify color fallback works

### D5: Quickstart Guide (`quickstart.md`)

**Content**: Developer guide for banner implementation

Sections:
1. **Feature Overview**: What the banner does and why
2. **Files to Modify**: List of files with change summaries
3. **Step-by-Step Implementation**:
   - Step 1: Create `banner.py` with ASCII art constant
   - Step 2: Implement terminal detection functions
   - Step 3: Implement version extraction
   - Step 4: Implement banner display function
   - Step 5: Integrate into `main.py` startup
   - Step 6: Write unit tests
4. **Testing Strategy**: How to test banner in different scenarios
5. **Verification Checklist**: Final checks before completion

### D6: Agent Context Update

Run: `.specify/scripts/bash/update-agent-context.sh claude`

**Technologies to Add**:
- ASCII art design patterns
- ANSI color code usage
- Terminal capability detection with `os.get_terminal_size()`
- Version extraction with `importlib.metadata`

**Preserve Existing Context**: All existing application architecture and patterns

---

## Phase 2: Implementation Planning

**Out of Scope**: This phase is handled by the `/sp.tasks` command, not `/sp.plan`.

The `/sp.tasks` command will generate:
- Detailed task breakdown with TDD cycles
- Test-first implementation order
- Acceptance criteria for each task
- Estimated complexity and dependencies

---

## Success Criteria (from Spec)

Implementation must satisfy:
- ✅ **SC-001**: 100% of application launches display the banner before the main menu
- ✅ **SC-002**: Banner displays correctly (no wrapping or distortion) in terminals with widths of 80 columns or greater
- ✅ **SC-003**: Banner loads and displays in under 100 milliseconds to avoid noticeable delay
- ✅ **SC-004**: Users can visually identify the application brand (Talal's TDA) within 1 second of launch
- ✅ **SC-005**: Version information in banner matches the actual application version in 100% of cases
- ✅ **SC-006**: Banner displays without errors or warnings in at least 95% of common terminal environments (Linux Terminal, Windows Terminal, macOS Terminal, WSL2)

---

## Next Steps

1. ✅ **Complete**: Specification validation (all checks passed)
2. ✅ **Complete**: Plan creation (this file)
3. 🔄 **Next**: Execute Phase 0 research tasks (create `research.md`)
4. ⏳ **Then**: Execute Phase 1 design artifacts (`data-model.md`, `quickstart.md`)
5. ⏳ **Finally**: Run `/sp.tasks` to generate implementation task breakdown

**Status**: Plan complete, ready for Phase 0 research execution
