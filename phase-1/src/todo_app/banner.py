"""CLI Banner Module for MA-TODO-APP.

This module provides banner display functionality for the Todo Console Application.
Displays ASCII art branding with version information and optional ANSI color support.

Features:
- ASCII art banner with "MA-TODO-APP" branding
- Application tagline and copyright information
- Version extraction from package metadata
- Terminal capability detection for color support
- Graceful fallback to plain text when colors not supported

Author: Muhammad Ahmed
Project: Phase I Hackathon - Console Todo Application
"""

# ANSI Color Codes (T003)
BOLD = '\033[1m'
BRIGHT_CYAN = '\033[96m'
CYAN = '\033[36m'
GRAY = '\033[90m'
RESET = '\033[0m'

# ASCII Art - 80 columns, 5 lines (T004)
ASCII_ART_LINES = [
    "  __  __    _      _____ ___  ____   ___       _    ____  ____  ",
    " |  \\/  |  / \\    |_   _/ _ \\|  _ \\ / _ \\     / \\  |  _ \\|  _ \\ ",
    " | |\\/| | / _ \\     | || | | | | | | | | |   / _ \\ | |_) | |_) |",
    " | |  | |/ ___ \\    | || |_| | |_| | |_| |  / ___ \\|  __/|  __/ ",
    " |_|  |_/_/   \\_\\   |_| \\___/|____/ \\___/  /_/   \\_\\_|   |_|    ",
]

# Static Text (T005, T006)
TAGLINE = "Your Personal Task Manager"
COPYRIGHT = "© 2025 Muhammad Ahmed - Phase I Hackathon Project"

# Border (T007)
BORDER = "=" * 80


def get_version() -> str:
    """Extract application version from package metadata (T027).

    Three-tier fallback strategy:
    1. importlib.metadata (for installed packages)
    2. pyproject.toml parsing with tomllib
    3. "dev" fallback

    Returns:
        Version string (e.g., "0.1.0") or "dev" if unavailable

    Performance: <1ms in all scenarios
    """
    # Strategy 1: importlib.metadata (for installed packages)
    try:
        from importlib.metadata import version
        return version('phase-1')  # Package name from pyproject.toml
    except Exception:
        pass

    # Strategy 2: tomllib for pyproject.toml (Python 3.11+)
    try:
        import tomllib
        from pathlib import Path

        # Navigate to project root from src/todo_app/banner.py
        project_root = Path(__file__).parent.parent.parent
        pyproject_path = project_root / 'pyproject.toml'

        with open(pyproject_path, 'rb') as f:
            data = tomllib.load(f)
            return data['project']['version']
    except Exception:
        pass

    # Strategy 3: Fallback to "dev"
    return 'dev'


def detect_terminal_capabilities() -> dict[str, bool | int]:
    """Detect terminal environment (T042, T043).

    Detection methods:
    - width: os.get_terminal_size().columns (fallback: 80)
    - is_interactive: sys.stdout.isatty()
    - supports_color: TERM/COLORTERM env vars + is_interactive

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
    import os
    import sys

    is_interactive = sys.stdout.isatty()

    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80  # Fallback for pipes/redirects

    # T043: Check TERM and COLORTERM environment variables
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

# Pre-computed Banners (T014, T030, T044)
PLAIN_TEXT_BANNER = "\n".join([
    BORDER,
    *ASCII_ART_LINES,
    "",
    f"{TAGLINE:^80}",
    "",
    f"{'Version ' + get_version():^80}",
    f"{COPYRIGHT:^80}",
    BORDER,
])

# T044: Colored banner with ANSI codes (Bright Cyan for title, Gray for metadata)
COLORED_BANNER = "\n".join([
    BORDER,
    *[f"{BRIGHT_CYAN}{line}{RESET}" for line in ASCII_ART_LINES],
    "",
    f"{BOLD}{TAGLINE:^80}{RESET}",
    "",
    f"{GRAY}{'Version ' + get_version():^80}{RESET}",
    f"{GRAY}{COPYRIGHT:^80}{RESET}",
    BORDER,
])


def get_banner_content(use_color: bool = False) -> str:
    """Generate banner content as a string (T013, T045).

    Args:
        use_color: If True, include ANSI color codes

    Returns:
        Complete banner text including ASCII art, tagline,
        version, and copyright information

    Notes:
        - ASCII art is 80-column compatible
        - Total height <= 15 lines
        - Color codes automatically applied if use_color=True
    """
    # T045: Return colored banner when use_color=True
    return COLORED_BANNER if use_color else PLAIN_TEXT_BANNER


def display_banner() -> None:
    """Display the application banner at startup (T015, T046).

    Renders ASCII art banner with version and copyright information.
    Automatically detects terminal capabilities for color support.
    Falls back to plain text if colors not supported.

    Performance: <100ms on standard terminals
    Side Effects: Prints to stdout

    Raises:
        None (errors handled gracefully with fallbacks)
    """
    # T046: Auto-detect terminal capabilities and select appropriate banner
    caps = detect_terminal_capabilities()
    banner = get_banner_content(use_color=caps['supports_color'])
    print(banner)
