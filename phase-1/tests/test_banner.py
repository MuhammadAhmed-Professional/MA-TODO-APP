"""Tests for CLI Banner Module.

Test suite for banner display functionality including:
- Banner content generation (plain text and colored)
- Terminal capability detection
- Version extraction with fallback strategies
- Width and height constraints validation
- Cross-platform compatibility

Follows TDD RED-GREEN-REFACTOR cycle as per constitution.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.todo_app.banner import (
    get_banner_content,
    display_banner,
    get_version,
    detect_terminal_capabilities,
    TAGLINE,
    ASCII_ART_LINES,
    COPYRIGHT,
    BRIGHT_CYAN,
    GRAY,
    RESET,
)


# ===== User Story 1 Tests (RED Phase: T008-T011) =====


def test_get_banner_content_plain_text():
    """T008: Verify plain banner structure without colors."""
    banner = get_banner_content(use_color=False)

    # Banner should be a non-empty string
    assert isinstance(banner, str)
    assert len(banner) > 0

    # Should contain ASCII art lines
    for art_line in ASCII_ART_LINES:
        assert art_line in banner

    # Should contain tagline
    assert TAGLINE in banner

    # Should NOT contain ANSI color codes when use_color=False
    assert '\033[' not in banner


def test_banner_width_constraint():
    """T009: Verify no line exceeds 80 characters."""
    banner = get_banner_content(use_color=False)
    lines = banner.split('\n')

    for i, line in enumerate(lines):
        # Allow empty lines but check non-empty ones
        if line.strip():
            assert len(line) <= 80, f"Line {i+1} exceeds 80 characters: {len(line)} chars"


def test_banner_height_constraint():
    """T010: Verify total height ≤ 15 lines."""
    banner = get_banner_content(use_color=False)
    lines = banner.split('\n')

    # Total height should be 15 lines or fewer
    assert len(lines) <= 15, f"Banner height is {len(lines)} lines (max: 15)"


def test_banner_contains_tagline():
    """T011: Verify tagline appears in banner output."""
    banner = get_banner_content(use_color=False)

    # Tagline should be present in the banner
    assert TAGLINE in banner, f"Tagline '{TAGLINE}' not found in banner"

    # Tagline should appear after ASCII art (rough check)
    tagline_index = banner.find(TAGLINE)
    ascii_last_line = ASCII_ART_LINES[-1]
    ascii_index = banner.find(ascii_last_line)

    assert tagline_index > ascii_index, "Tagline should appear after ASCII art"


# ===== User Story 2 Tests (RED Phase: T021-T025) =====


def test_get_version_from_metadata():
    """T021: Verify version extraction from importlib.metadata."""
    with patch('importlib.metadata.version', return_value='1.2.3'):
        version = get_version()
        assert version == '1.2.3', "Should extract version from importlib.metadata"


def test_get_version_from_pyproject():
    """T022: Verify version extraction from pyproject.toml when metadata fails."""
    # Mock importlib.metadata to raise exception
    with patch('importlib.metadata.version', side_effect=Exception("Not installed")):
        version = get_version()

        # Should fall back to pyproject.toml and get the actual version
        # or "dev" if pyproject.toml is not found or malformed
        assert isinstance(version, str)
        assert len(version) > 0
        # Accept either actual version from pyproject.toml or "dev" fallback
        assert version == "dev" or version.count('.') >= 1


def test_get_version_fallback():
    """T023: Verify fallback to 'dev' when both sources fail."""
    # Mock both importlib.metadata and file operations to fail
    with patch('importlib.metadata.version', side_effect=Exception("Not installed")):
        with patch('builtins.open', side_effect=FileNotFoundError("No pyproject.toml")):
            version = get_version()
            assert version == "dev", "Should fallback to 'dev' when all sources fail"


def test_banner_contains_version():
    """T024: Verify version appears in banner output."""
    banner = get_banner_content(use_color=False)

    # Banner should contain "Version" text
    assert "Version" in banner or "v" in banner.lower(), "Banner should mention version"

    # Should contain the actual version string
    version = get_version()
    assert version in banner, f"Banner should contain version '{version}'"


def test_banner_contains_copyright():
    """T025: Verify copyright appears in banner output."""
    banner = get_banner_content(use_color=False)

    # Copyright should be present
    assert COPYRIGHT in banner, f"Banner should contain copyright '{COPYRIGHT}'"

    # Should contain copyright symbol and year
    assert "©" in banner or "(c)" in banner.lower(), "Banner should contain copyright symbol"
    assert "2025" in banner, "Banner should contain the year 2025"


# ===== User Story 3 Tests (RED Phase: T035-T040) =====


def test_detect_terminal_capabilities_interactive():
    """T035: Verify color detection when stdout.isatty() is True."""
    with patch('sys.stdout.isatty', return_value=True):
        with patch('os.environ.get') as mock_env:
            mock_env.side_effect = lambda key, default='': 'xterm-256color' if key == 'TERM' else default

            caps = detect_terminal_capabilities()

            assert caps['is_interactive'] is True
            assert caps['supports_color'] is True


def test_detect_terminal_capabilities_non_interactive():
    """T036: Verify no color when stdout.isatty() is False."""
    with patch('sys.stdout.isatty', return_value=False):
        caps = detect_terminal_capabilities()

        assert caps['is_interactive'] is False
        assert caps['supports_color'] is False


def test_detect_terminal_width_success():
    """T037: Verify os.get_terminal_size() success case."""
    mock_size = MagicMock()
    mock_size.columns = 120

    with patch('os.get_terminal_size', return_value=mock_size):
        caps = detect_terminal_capabilities()
        assert caps['width'] == 120


def test_detect_terminal_width_fallback():
    """T038: Verify width fallback to 80 on OSError."""
    with patch('os.get_terminal_size', side_effect=OSError("No terminal")):
        caps = detect_terminal_capabilities()
        assert caps['width'] == 80, "Should fallback to 80 columns"


def test_get_banner_content_with_color():
    """T039: Verify ANSI codes present when use_color=True."""
    banner = get_banner_content(use_color=True)

    # Should contain ANSI color codes
    assert '\033[' in banner, "Colored banner should contain ANSI escape codes"

    # Should contain specific color codes (Bright Cyan, Gray, Reset)
    assert BRIGHT_CYAN in banner or GRAY in banner, "Should use defined color codes"
    assert RESET in banner, "Should contain RESET code to restore colors"


def test_display_banner_auto_detect_color():
    """T040: Verify display_banner() uses terminal detection."""
    # Mock terminal as color-supporting
    with patch('sys.stdout.isatty', return_value=True):
        with patch('os.environ.get') as mock_env:
            mock_env.side_effect = lambda key, default='': 'xterm-256color' if key == 'TERM' else default

            # Capture print output
            with patch('builtins.print') as mock_print:
                display_banner()

                # Should have called print with some content
                assert mock_print.called
                printed_content = str(mock_print.call_args)

                # Content should include banner text (checking for ASCII art or tagline)
                assert any(keyword in printed_content for keyword in [TAGLINE, 'MA-TODO'])
