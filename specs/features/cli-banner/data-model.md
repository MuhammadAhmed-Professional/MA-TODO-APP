# Data Model: CLI Banner

**Feature**: CLI Banner with Branding
**Date**: 2025-12-05
**Dependencies**: research.md (complete)

## Overview

The CLI banner feature is display-only with no persistent data storage. Data models consist of static configuration constants and runtime-detected terminal capabilities.

---

## Entity 1: Banner Configuration

**Type**: Static Constants (Module-level)

**Purpose**: Store pre-computed banner content for display

### Attributes

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `ASCII_ART_LINES` | `list[str]` | List of ASCII art lines for logo | `["  _____     _   ...", ...]` |
| `TAGLINE` | `str` | Application tagline text | `"Your Personal Task Manager"` |
| `COPYRIGHT` | `str` | Copyright notice template | `"© 2025 Talal - Phase I Hackathon Project"` |
| `PLAIN_TEXT_BANNER` | `str` | Complete banner without ANSI codes | Multi-line string |
| `COLORED_BANNER` | `str` | Complete banner with ANSI color codes | Multi-line string with `\033[...]` |

### Constants

```python
# ANSI Color Codes
BOLD = '\033[1m'
BRIGHT_CYAN = '\033[96m'
CYAN = '\033[36m'
GRAY = '\033[90m'
RESET = '\033[0m'

# ASCII Art (80 columns, 5 lines)
ASCII_ART_LINES = [
    "  _____     _       _       _____ ____    _    ",
    " |_   _|_ _| | __ _| |___  |_   _|  _ \  / \   ",
    "   | |/ _` | |/ _` | / __|   | | | | | |/ _ \  ",
    "   | | (_| | | (_| | \__ \   | | | |_| / ___ \ ",
    "   |_|\__,_|_|\__,_|_|___/   |_| |____/_/   \_\\",
]

# Static Text
TAGLINE = "Your Personal Task Manager"
COPYRIGHT = "© 2025 Talal - Phase I Hackathon Project"

# Border
BORDER = "=" * 80
```

### Constraints

- **Width**: All lines must be ≤ 80 characters
- **Height**: Total banner height ≤ 15 lines
- **Character set**: ASCII only (codes 32-126)
- **Immutability**: Constants defined at module load, never modified

### Lifecycle

1. **Load Time**: Constants defined when `banner.py` module is imported
2. **Runtime**: Constants are referenced but never modified
3. **No Persistence**: Banner content is not saved or loaded from files

---

## Entity 2: Terminal Capabilities

**Type**: Runtime Detection (Transient)

**Purpose**: Detect terminal environment to select appropriate banner rendering

### Attributes

| Attribute | Type | Description | Default Fallback |
|-----------|------|-------------|------------------|
| `width` | `int` | Terminal width in columns | 80 |
| `supports_color` | `bool` | ANSI color support detected | `False` |
| `is_interactive` | `bool` | stdout is a TTY (not pipe/redirect) | `False` |

### Structure

```python
TerminalCapabilities = dict[str, bool | int]

# Example runtime value:
{
    'width': 120,
    'supports_color': True,
    'is_interactive': True
}
```

### Detection Logic

```python
def detect_terminal_capabilities() -> dict[str, bool | int]:
    """Detect terminal environment.

    Detection methods:
    - width: os.get_terminal_size().columns (fallback: 80)
    - is_interactive: sys.stdout.isatty()
    - supports_color: TERM/COLORTERM env vars + is_interactive
    """
    import os
    import sys

    is_interactive = sys.stdout.isatty()

    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80  # Fallback for pipes/redirects

    term = os.environ.get('TERM', '')
    colorterm = os.environ.get('COLORTERM', '')

    supports_color = is_interactive and (
        'color' in term.lower() or
        colorterm or
        term in ['xterm', 'xterm-256color', 'screen', 'tmux', 'linux']
    )

    return {
        'width': width,
        'supports_color': supports_color,
        'is_interactive': is_interactive
    }
```

### Constraints

- **Ephemeral**: Detected at runtime, not stored
- **Non-deterministic**: Values may differ between runs (different terminals)
- **Safe Defaults**: Always falls back to conservative values (80 cols, no color)
- **Performance**: Detection must complete in <0.1ms

### Lifecycle

1. **Detection**: Called once when `display_banner()` is invoked
2. **Usage**: Used to select banner template (colored vs plain)
3. **Disposal**: Dictionary is garbage collected after use

---

## Entity 3: Version Information

**Type**: Extracted Value (Semi-static)

**Purpose**: Display application version in banner

### Attributes

| Attribute | Type | Description | Fallback |
|-----------|------|-------------|----------|
| `version` | `str` | Semantic version (X.Y.Z) | `"dev"` |

### Extraction Strategy

```python
def get_version() -> str:
    """Extract version from metadata or pyproject.toml.

    Fallback chain:
    1. importlib.metadata.version('phase-1') (production)
    2. tomllib parse pyproject.toml (development)
    3. "dev" (safe fallback)
    """
    # Strategy 1: Installed package
    try:
        from importlib.metadata import version
        return version('phase-1')
    except Exception:
        pass

    # Strategy 2: pyproject.toml
    try:
        import tomllib
        from pathlib import Path

        project_root = Path(__file__).parent.parent.parent
        with open(project_root / 'pyproject.toml', 'rb') as f:
            return tomllib.load(f)['project']['version']
    except Exception:
        pass

    # Strategy 3: Fallback
    return 'dev'
```

### Constraints

- **Format**: Semantic versioning (e.g., "1.0.0", "0.1.2")
- **Source of Truth**: `pyproject.toml` `[project] version` field
- **Never Fails**: Always returns a string (minimum: "dev")
- **Performance**: <1ms (file I/O once at module load)

### Lifecycle

1. **Load Time**: Version extracted when `banner.py` module imports
2. **Caching**: Can be module-level constant if extracted once
3. **Updates**: Version changes only when package/pyproject.toml updated

---

## Data Flow

```
┌─────────────────────┐
│  Application Start  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Import banner.py module            │
│  ┌─────────────────────────────┐   │
│  │  Load Constants             │   │
│  │  - ASCII_ART_LINES          │   │
│  │  - TAGLINE, COPYRIGHT       │   │
│  │  - Extract get_version()    │   │
│  │  - Build PLAIN_TEXT_BANNER  │   │
│  │  - Build COLORED_BANNER     │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  main.py calls display_banner()     │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  detect_terminal_capabilities()     │
│  ├─ os.get_terminal_size()          │
│  ├─ sys.stdout.isatty()             │
│  └─ Check TERM env var              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Select banner template              │
│  ├─ COLORED_BANNER if color support │
│  └─ PLAIN_TEXT_BANNER otherwise     │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  print(selected_banner)              │
└─────────────────────────────────────┘
```

---

## No Persistent Storage

**Rationale**: Banner is a display-only feature with no user-modifiable data.

| Aspect | Status | Explanation |
|--------|--------|-------------|
| **Database** | N/A | No persistent data to store |
| **File I/O** | Read-only | Only reads pyproject.toml for version |
| **User Input** | None | No user-configurable banner settings |
| **State Management** | Stateless | Each display is independent |

---

## Implementation Checklist

- [ ] Define ASCII_ART_LINES constant with 80-column compatibility
- [ ] Define ANSI color code constants (BOLD, BRIGHT_CYAN, CYAN, GRAY, RESET)
- [ ] Define TAGLINE and COPYRIGHT constants
- [ ] Implement `get_version()` with three-tier fallback
- [ ] Build PLAIN_TEXT_BANNER at module load
- [ ] Build COLORED_BANNER at module load
- [ ] Implement `detect_terminal_capabilities()` with safe defaults
- [ ] Verify all constants are immutable (UPPER_CASE naming)
- [ ] Test banner width (no line > 80 chars)
- [ ] Test banner height (total ≤ 15 lines)
- [ ] Test version extraction in dev and production environments
- [ ] Test terminal detection in TTY and non-TTY scenarios
- [ ] Verify performance (<1ms end-to-end)

---

## Related Documents

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Quickstart Guide**: [quickstart.md](./quickstart.md) (to be created)
