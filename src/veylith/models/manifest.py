"""Inventory manifest and transformation record models."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from veylith.models.base import VeylithBaseModel


class FileRecord(VeylithBaseModel):
    """Metadata and SHA-256 digest for an individual inventoried file."""

    path: str = Field(description="Normalized relative path with forward slashes")
    sha256: str = Field(description="Hex-encoded SHA-256 digest of file contents")
    size_bytes: int = Field(description="Size in bytes")
    file_type: str = Field(default="unknown", description="Detected format or extension")


class InventoryManifest(VeylithBaseModel):
    """Canonical inventory manifest of all files within an authorized project."""

    root: str = Field(description="Normalized project root")
    files: list[FileRecord] = Field(default_factory=list, description="Sorted list of file records")
    total_files: int = Field(default=0, description="Total file count")
    total_bytes: int = Field(default=0, description="Total size in bytes")
    manifest_digest: str = Field(
        default="", description="SHA-256 digest over the canonical manifest JSON"
    )


class TransformationRecord(VeylithBaseModel):
    """Record of a transformation step applied to an artifact."""

    id: str = Field(description="Transformation identifier (e.g. 'hygiene.strip_docstrings')")
    version: str = Field(default="0.1.0", description="Transformation implementation version")
    input_digest: str = Field(description="Input file or manifest SHA-256 digest")
    output_digest: str = Field(description="Output file or manifest SHA-256 digest")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters supplied to transform"
    )
    skip_reasons: list[str] = Field(
        default_factory=list, description="Explicit reasons if any part was skipped for safety"
    )
    deterministic: bool = Field(
        default=True, description="True if output is strictly bit-for-bit reproducible"
    )
    rollback_handle: str | None = Field(
        default=None, description="Identifier or path to restore original state"
    )
