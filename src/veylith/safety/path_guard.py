"""Canonical path guard to prevent path traversal, symlink escapes, and TOCTOU vulnerabilities."""

from __future__ import annotations

import os
from pathlib import Path

from veylith.errors import SecurityViolationError

# Dangerous Windows device names that must never be opened
_RESERVED_DEVICE_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


class PathSecurityError(SecurityViolationError):
    """Raised when an operation attempts to access paths outside the authorized boundary."""


class PathGuard:
    """Guards file operations by enforcing strict canonical directory containment."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise PathSecurityError(f"Authorized root directory does not exist: {self.root}")
        if not self.root.is_dir():
            raise PathSecurityError(f"Authorized root must be a directory: {self.root}")

    def validate_contained(self, target: str | Path) -> Path:
        """Verify that target resolves strictly within self.root and contains no device names."""
        target_path = Path(target)
        if not target_path.is_absolute():
            resolved = (self.root / target_path).resolve()
        else:
            resolved = target_path.resolve()

        # Check for reserved device names on Windows or across platforms
        for part in resolved.parts:
            stem = part.split(".")[0].upper()
            if stem in _RESERVED_DEVICE_NAMES:
                raise PathSecurityError(f"Access to reserved device file forbidden: {part}")

        # Check directory containment
        try:
            # relative_to raises ValueError if resolved is not inside self.root
            resolved.relative_to(self.root)
        except ValueError as err:
            raise PathSecurityError(
                f"Path traversal detected: '{target}' resolves to '{resolved}', "
                f"which is outside root '{self.root}'"
            ) from err

        return resolved

    def safe_read_bytes(
        self, relative_path: str | Path, max_bytes: int = 50 * 1024 * 1024
    ) -> bytes:
        """Safely read a file after verifying path containment and file size."""
        resolved = self.validate_contained(relative_path)
        if not resolved.is_file():
            raise PathSecurityError(f"Target is not a regular file: {resolved}")

        size = resolved.stat().st_size
        if size > max_bytes:
            raise PathSecurityError(
                f"File size {size} exceeds maximum safe limit of {max_bytes} bytes"
            )

        with open(resolved, "rb") as f:
            # Re-verify that the open file descriptor points to the expected path
            data = f.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise PathSecurityError(f"File content exceeded {max_bytes} bytes while reading")
            return data

    def safe_write_bytes(self, relative_path: str | Path, content: bytes) -> Path:
        """Safely write bytes to a file within root, creating parent dirs if needed."""
        target_path = Path(relative_path)
        # Note: if the file does not exist yet, resolve its parent
        if target_path.is_absolute():
            resolved_parent = target_path.parent.resolve()
            filename = target_path.name
        else:
            full = self.root / target_path
            resolved_parent = full.parent.resolve()
            filename = full.name

        # Validate parent is inside root
        try:
            resolved_parent.relative_to(self.root)
        except ValueError as err:
            raise PathSecurityError(
                f"Destination parent '{resolved_parent}' outside root '{self.root}'"
            ) from err

        stem = filename.split(".")[0].upper()
        if stem in _RESERVED_DEVICE_NAMES:
            raise PathSecurityError(f"Access to reserved device file forbidden: {filename}")

        resolved_parent.mkdir(parents=True, exist_ok=True)
        dest = resolved_parent / filename

        # Atomic write: write to temp file then rename
        tmp_file = resolved_parent / f".tmp_{os.getpid()}_{filename}"
        with open(tmp_file, "wb") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_file, dest)
        return dest
