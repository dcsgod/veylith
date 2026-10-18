"""Project and Owner Declaration models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from veylith.models.base import VeylithBaseModel


class OwnerDeclaration(VeylithBaseModel):
    """Explicit declaration that operator owns or is authorized to analyze this software."""

    declared_by: str = Field(
        description="Name or identifier of the operator claiming authorization"
    )
    scope: str = Field(
        description="Scope of authorization (e.g. 'internal-testing', 'security-evaluation')"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when declaration was recorded",
    )
    authorized: bool = Field(default=True, description="Explicit authorization confirmation")


class Project(VeylithBaseModel):
    """Target software project metadata and ownership record."""

    id: str = Field(description="Unique project identifier")
    name: str = Field(description="Human-readable project name")
    owner_declaration: OwnerDeclaration = Field(description="Required owner declaration")
    artifact_location: str = Field(description="Canonical path or URI to the project root")
    artifact_type: Literal["python", "javascript", "native", "jar", "unknown"] = Field(
        default="unknown", description="Detected artifact classification"
    )
    digest: str | None = Field(
        default=None, description="SHA-256 digest of project manifest if computed"
    )
    platform: str = Field(default="cross-platform", description="Target platform architecture")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC creation timestamp",
    )
