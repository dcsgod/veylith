#!/usr/bin/env python3
"""Cross-platform check runner for Veylith (ruff, ruff format, mypy, pytest)."""

from __future__ import annotations

import subprocess
import sys

COMMANDS: list[list[str]] = [
    ["uv", "run", "ruff", "check", "."],
    ["uv", "run", "ruff", "format", "--check", "."],
    ["uv", "run", "mypy", "--strict", "src", "tests"],
    ["uv", "run", "pytest"],
]


def main() -> int:
    for cmd in COMMANDS:
        print(f"\n==> Running: {' '.join(cmd)}")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(
                f"\n[FAIL] Command failed with code {res.returncode}: {' '.join(cmd)}",
                file=sys.stderr,
            )
            return res.returncode
    print("\n[OK] All verification checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
