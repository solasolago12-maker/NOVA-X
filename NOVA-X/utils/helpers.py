"""General utility helpers for NOVA-X.

A collection of text processing, formatting, and display utility functions
used across the application.
"""

import re
import shutil
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Text formatting
# ---------------------------------------------------------------------------

def format_text(text: str, width: Optional[int] = None) -> str:
    """Wrap text to the terminal width or a specified width.

    Args:
        text: Input text (may contain newlines).
        width: Desired wrap width. Defaults to terminal width minus 4.

    Returns:
        Wrapped text string.
    """
    import textwrap
    if width is None:
        width = max(shutil.get_terminal_size().columns - 4, 40)
    lines = text.split("\n")
    wrapped: list[str] = []
    for line in lines:
        if line.strip() == "":
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(line, width=width))
    return "\n".join(wrapped)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.

    Args:
        text: Input string.
        max_length: Maximum allowed length including suffix.
        suffix: Truncation indicator appended when trimmed.

    Returns:
        Potentially truncated string.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def strip_markdown(text: str) -> str:
    """Remove common markdown formatting from text.

    Args:
        text: Markdown-formatted string.

    Returns:
        Plain text with markdown syntax removed.
    """
    # Headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Bold / italic
    text = re.sub(r"\*\*?(.+?)\*\*?", r"\1", text)
    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"\1", text)
    # Code blocks
    text = re.sub(r"```[\w]*\n?", "", text)
    # Blockquotes
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    return text.strip()


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def safe_filename(name: str, extension: str = "") -> str:
    """Sanitise a string for use as a filename.

    Replaces spaces with underscores and removes unsafe characters.

    Args:
        name: Desired filename base.
        extension: Optional file extension (e.g. ``txt``).

    Returns:
        Safe filename string.
    """
    safe = re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")
    safe = re.sub(r"_+", "_", safe)
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        if not safe.endswith(ext):
            safe += ext
    return safe


# ---------------------------------------------------------------------------
# Reading & progress helpers
# ---------------------------------------------------------------------------

def estimate_reading_time(text: str, wpm: int = 200) -> str:
    """Estimate the time required to read a piece of text.

    Args:
        text: Content to estimate.
        wpm: Words per minute reading speed (default 200).

    Returns:
        Human-readable string like ``"2 min 30 sec"``.
    """
    words = len(text.split())
    minutes = words // wpm
    seconds = int((words % wpm) / wpm * 60)
    if minutes > 0:
        return f"{minutes} min {seconds} sec"
    return f"{seconds} sec"


def progress_bar(current: int, total: int, width: int = 30) -> str:
    """Render a text-based progress bar.

    Args:
        current: Current progress value.
        total: Maximum value.
        width: Bar width in characters.

    Returns:
        Progress bar string.
    """
    if total <= 0:
        return f"[{' ' * width}] 0%"
    ratio = min(current / total, 1.0)
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(ratio * 100)
    return f"[{bar}] {pct}%"
