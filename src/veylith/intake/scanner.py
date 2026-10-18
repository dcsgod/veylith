"""Safe directory scanner and inventory manifest generator."""

from __future__ import annotations

import os
from pathlib import Path

from veylith.errors import SecurityViolationError
from veylith.integrity.hasher import canonical_json_digest, sha256_file
from veylith.models.manifest import FileRecord, InventoryManifest
from veylith.safety.path_guard import PathGuard

DEFAULT_EXCLUSIONS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".hypothesis",
    ".DS_Store",
    "Thumbs.db",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_FILES = 10_000


def detect_file_type(path: Path) -> str:
    """Classify file type by suffix or magic signature."""
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyi"}:
        return "python"
    elif suffix in {".js", ".jsx", ".mjs", ".cjs"}:
        return "javascript"
    elif suffix in {".ts", ".tsx"}:
        return "typescript"
    elif suffix in {".json", ".yaml", ".yml", ".toml", ".xml"}:
        return "config"
    elif suffix in {".md", ".rst", ".txt"}:
        return "documentation"
    elif suffix in {".map"}:
        return "sourcemap"
    return "binary" if suffix in {".exe", ".dll", ".so", ".dylib", ".jar", ".bin"} else "text"


class ProjectScanner:
    """Safely scans an authorized target project and produces an immutable InventoryManifest."""

    def __init__(self, root: str | Path, exclusions: set[str] | None = None) -> None:
        self.guard = PathGuard(root)
        self.root = self.guard.root
        self.exclusions = set(exclusions) if exclusions is not None else set(DEFAULT_EXCLUSIONS)

    def scan(self) -> InventoryManifest:
        """Walk the directory, check path security, and compute deterministic file digests."""
        records: list[FileRecord] = []
        total_bytes = 0
        file_count = 0

        # We walk deterministically by sorting dirnames and filenames
        for dirpath, dirnames, filenames in os.walk(self.root, followlinks=False):
            # Prune excluded directories in-place
            dirnames[:] = sorted([d for d in dirnames if d not in self.exclusions])
            filenames = sorted(filenames)

            rel_dir = Path(dirpath).resolve()
            # Ensure current directory is within root
            self.guard.validate_contained(rel_dir)

            for filename in filenames:
                if filename in self.exclusions:
                    continue

                full_path = rel_dir / filename
                # If symlink, ensure it does not escape root
                if full_path.is_symlink():
                    try:
                        resolved_symlink = full_path.resolve()
                        self.guard.validate_contained(resolved_symlink)
                    except SecurityViolationError as err:
                        raise SecurityViolationError(
                            f"Symlink breakout detected: '{full_path}' -> '{full_path.readlink()}'"
                        ) from err

                # Validate containment
                validated = self.guard.validate_contained(full_path)
                if not validated.is_file():
                    continue

                file_count += 1
                if file_count > MAX_TOTAL_FILES:
                    raise SecurityViolationError(
                        f"Target contains excessive file count (> {MAX_TOTAL_FILES})"
                    )

                size = validated.stat().st_size
                if size > MAX_FILE_SIZE:
                    raise SecurityViolationError(
                        f"File '{filename}' exceeds maximum allowed size ({size} > {MAX_FILE_SIZE})"
                    )

                rel_path_str = validated.relative_to(self.root).as_posix()
                digest = sha256_file(validated)
                total_bytes += size

                records.append(
                    FileRecord(
                        path=rel_path_str,
                        sha256=digest,
                        size_bytes=size,
                        file_type=detect_file_type(validated),
                    )
                )

        # Sort records deterministically by normalized relative path
        records.sort(key=lambda r: r.path)

        manifest = InventoryManifest(
            root=self.root.as_posix(),
            files=records,
            total_files=len(records),
            total_bytes=total_bytes,
        )

        # Compute canonical manifest digest over the serialized files
        files_dict = [r.model_dump() for r in records]
        manifest.manifest_digest = canonical_json_digest(files_dict)

        return manifest
