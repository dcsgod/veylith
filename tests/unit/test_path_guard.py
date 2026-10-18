"""Unit tests for PathGuard canonical containment and security checks."""

from __future__ import annotations

from pathlib import Path

import pytest

from veylith.safety.path_guard import PathGuard, PathSecurityError


def test_path_guard_valid_containment(tmp_path: Path) -> None:
    guard = PathGuard(tmp_path)
    subfile = tmp_path / "safe.txt"
    subfile.write_text("safe content")

    validated = guard.validate_contained("safe.txt")
    assert validated == subfile.resolve()


def test_path_guard_rejects_parent_traversal(tmp_path: Path) -> None:
    guard = PathGuard(tmp_path)
    with pytest.raises(PathSecurityError, match="Path traversal detected"):
        guard.validate_contained("../outside.txt")


def test_path_guard_rejects_absolute_path_escape(tmp_path: Path) -> None:
    guard = PathGuard(tmp_path)
    outside = tmp_path.parent / "escape.txt"
    outside.write_text("danger")

    with pytest.raises(PathSecurityError, match="Path traversal detected"):
        guard.validate_contained(outside)


def test_path_guard_rejects_device_names(tmp_path: Path) -> None:
    guard = PathGuard(tmp_path)
    with pytest.raises(PathSecurityError, match="reserved device file"):
        guard.validate_contained("CON.txt")

    with pytest.raises(PathSecurityError, match="reserved device file"):
        guard.validate_contained("NUL")


def test_path_guard_atomic_write_and_read(tmp_path: Path) -> None:
    guard = PathGuard(tmp_path)
    content = b"important verified data"
    dest = guard.safe_write_bytes("nested/dir/test.dat", content)

    assert dest.is_file()
    read_back = guard.safe_read_bytes("nested/dir/test.dat")
    assert read_back == content
