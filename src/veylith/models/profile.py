"""Protection profile configuration model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from veylith.models.base import VeylithBaseModel


class SensitivityAnnotation(VeylithBaseModel):
    """Owner-declared sensitivity marking for a module, class, or function."""

    target: str = Field(description="Target identifier (module name, function name, or file path)")
    sensitivity_level: Literal["low", "medium", "high", "critical"] = "high"
    reason: str = Field(default="", description="Why this logic is flagged as sensitive")


class ProtectionProfile(VeylithBaseModel):
    """Configuration profile declaring what transformations and controls to apply."""

    name: str = Field(default="default", description="Profile name")
    description: str = Field(default="", description="Human-readable description of this profile")
    enabled_transformations: list[str] = Field(
        default_factory=lambda: [
            "hygiene.remove_sourcemaps",
            "hygiene.strip_debug",
            "hygiene.strip_docstrings",
        ],
        description="Ordered list of transformation IDs to apply",
    )
    exclusions: list[str] = Field(
        default_factory=lambda: [".git", "__pycache__", ".venv", "node_modules", "tests"],
        description="Path patterns excluded from output",
    )
    strip_docstrings: bool = Field(default=True, description="Whether to remove Python docstrings")
    strip_comments: bool = Field(default=True, description="Whether to remove code comments")
    remove_sourcemaps: bool = Field(default=True, description="Whether to remove .map files")
    safe_rename: bool = Field(
        default=False, description="Enable LibCST-based local identifier renaming"
    )
    sign_manifest: bool = Field(
        default=False, description="Require Ed25519 signing of the release manifest"
    )
    sensitive_annotations: list[SensitivityAnnotation] = Field(
        default_factory=list, description="Operator-declared sensitive code targets"
    )
