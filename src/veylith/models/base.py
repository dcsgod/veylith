"""Base Pydantic models and versioning for Veylith schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CURRENT_SCHEMA_VERSION = "0.1.0"


class VeylithBaseModel(BaseModel):
    """Base model with schema versioning and frozen/strict attributes where appropriate."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str = Field(default=CURRENT_SCHEMA_VERSION, description="SemVer schema version")


class MetricMeasured(VeylithBaseModel):
    """A metric value that was successfully measured."""

    status: Literal["measured"] = "measured"
    value: float
    n: int = Field(default=1, description="Number of independent sample runs")
    uncertainty: float | None = Field(
        default=None, description="Standard deviation or margin of error"
    )


class MetricUnavailable(VeylithBaseModel):
    """A metric value that could not be computed because tools, dependencies or data were absent."""

    status: Literal["unavailable"] = "unavailable"
    reason: str = Field(description="Explicit explanation of why the metric could not be measured")


class MetricNotApplicable(VeylithBaseModel):
    """A metric value that does not apply to this artifact type or profile."""

    status: Literal["not_applicable"] = "not_applicable"
    reason: str = Field(description="Explanation of why this metric is inapplicable")


MetricValue = MetricMeasured | MetricUnavailable | MetricNotApplicable
