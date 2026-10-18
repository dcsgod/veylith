"""Report, claim, and evidence models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from veylith.models.base import MetricValue, VeylithBaseModel
from veylith.models.manifest import TransformationRecord


class EvidenceRecord(VeylithBaseModel):
    """Structured record of an observed, reported, or inferred finding."""

    id: str = Field(description="Unique evidence identifier")
    category: Literal[
        "direct_observation",
        "tool_reported_fact",
        "derived_inference",
        "unknown",
        "contradiction",
        "validation_result",
    ] = Field(description="Category of evidence according to trust classification")
    source: str = Field(description="Origin or provider of the observation")
    source_ref: str = Field(description="File, AST node, or tool output reference")
    digest: str | None = Field(
        default=None, description="SHA-256 digest of relevant artifact or log"
    )
    confidence: Literal["calibrated", "uncalibrated"] = Field(
        default="uncalibrated", description="Whether confidence has a calibrated empirical basis"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC observation timestamp",
    )


class Claim(VeylithBaseModel):
    """A factual claim made regarding exposure, protection, or behavior."""

    id: str = Field(description="Unique claim identifier")
    proposition: str = Field(description="The assertion being claimed")
    tier: Literal["T0", "T1", "T2", "T3", "T4"] = Field(
        description="Attacker tier against which this claim is evaluated"
    )
    kind: Literal["observed", "inferred", "unknown"] = Field(
        description="Observation classification"
    )
    supporting_refs: list[str] = Field(
        default_factory=list, description="IDs of supporting evidence records"
    )
    contradicting_refs: list[str] = Field(
        default_factory=list, description="IDs of contradicting evidence records"
    )
    validation_procedure: str = Field(description="Procedure used to validate this claim")
    outcome: Literal["verified", "unverified", "contradicted"] = Field(
        default="unverified", description="Outcome of independent validation"
    )


class ControlStatus(VeylithBaseModel):
    """Status of an individual defensive control."""

    name: str = Field(description="Name or ID of the control")
    status: Literal["verified", "unverified", "failed"] = Field(
        default="unverified",
        description="Only 'verified' if verified by a passing automated test",
    )
    details: str = Field(default="", description="Verification notes or failure reason")


class ProtectionReport(VeylithBaseModel):
    """Complete, reproducible protection and evaluation report."""

    run_id: str = Field(description="Unique run execution identifier")
    target_digest: str = Field(description="SHA-256 digest of the original target manifest")
    protected_digest: str | None = Field(
        default=None, description="SHA-256 digest of protected output manifest"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC run timestamp",
    )
    controls: list[ControlStatus] = Field(
        default_factory=list, description="Verification status of all applied controls"
    )
    transformations: list[TransformationRecord] = Field(
        default_factory=list, description="Log of all executed transformations"
    )
    metrics: dict[str, MetricValue] = Field(
        default_factory=dict, description="Keyed metric results using tri-state representation"
    )
    residual_risks: list[str] = Field(
        default_factory=list, description="Identified residual exposure risks"
    )
    not_shown_caveats: list[str] = Field(
        default_factory=lambda: [
            (
                "This report does not prove that software cannot be reversed "
                "by a Tier 4 (skilled human) attacker."
            ),
            (
                "Client-side controls delay and increase the cost of automated reconstruction, "
                "but cannot guarantee confidentiality of secrets."
            ),
            (
                "Dynamic runtime observation was not performed unless "
                "explicitly enabled and sandboxed."
            ),
        ],
        description="Explicit 'What this report does not show' boundaries",
    )
