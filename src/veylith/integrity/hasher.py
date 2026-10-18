"""Cryptographic hashing and RFC 8785 JSON canonicalization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    """Return hex-encoded SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Stream file and compute hex-encoded SHA-256 digest."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize Python dictionary or list to canonical JSON bytes per RFC 8785 (JCS)."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_json_digest(obj: Any) -> str:
    """Compute SHA-256 digest over canonical JSON serialization."""
    return sha256_bytes(canonical_json_bytes(obj))
