"""Unit tests for target string sanitization."""

from __future__ import annotations

from veylith.safety.sanitizer import sanitize_target_string


def test_sanitize_ansi_escape_sequences() -> None:
    malicious = "\x1b[31mRed Alert\x1b[0m and \x1b[2JClear Screen"
    sanitized = sanitize_target_string(malicious)
    assert sanitized == "Red Alert and Clear Screen"


def test_sanitize_control_characters() -> None:
    malicious = "Hello\x00World\x07\x08!"
    sanitized = sanitize_target_string(malicious)
    assert sanitized == "HelloWorld!"


def test_sanitize_truncation() -> None:
    long_str = "A" * 5000
    sanitized = sanitize_target_string(long_str, max_length=100)
    assert len(sanitized) == 100 + len("...[TRUNCATED]")
    assert sanitized.endswith("...[TRUNCATED]")
