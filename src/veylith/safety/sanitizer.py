"""Sanitizer for target-derived strings to prevent terminal injection and exploits."""

from __future__ import annotations

import re

# Match ANSI escape sequences
_ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

# Match dangerous ASCII control characters except \n, \r, \t
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def sanitize_target_string(value: str, max_length: int = 4096) -> str:
    """Sanitize an untrusted string derived from an analyzed target."""
    if not value:
        return ""

    # Strip ANSI escape codes
    clean = _ANSI_ESCAPE_PATTERN.sub("", value)

    # Strip raw control characters
    clean = _CONTROL_CHAR_PATTERN.sub("", clean)

    # Truncate if excessively long
    if len(clean) > max_length:
        clean = clean[:max_length] + "...[TRUNCATED]"

    return clean
