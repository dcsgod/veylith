"""Veylith typed exception hierarchy mapped to stable exit codes."""

from __future__ import annotations

from veylith.exitcodes import (
    EXIT_AUTHORIZATION_MISSING,
    EXIT_CANCELLED,
    EXIT_GATE_FAILED,
    EXIT_GENERIC_FAILURE,
    EXIT_INTEGRITY_FAILED,
    EXIT_REQUIRED_PROVIDER_UNAVAILABLE,
    EXIT_SANDBOX_UNAVAILABLE_OR_UNSAFE,
    EXIT_UNSUPPORTED_ARTIFACT,
    EXIT_USAGE_ERROR,
)


class VeylithError(Exception):
    """Base exception for all Veylith errors."""

    exit_code: int = EXIT_GENERIC_FAILURE

    def __init__(self, message: str, exit_code: int | None = None) -> None:
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class UsageError(VeylithError):
    """Command-line or configuration usage error."""

    exit_code = EXIT_USAGE_ERROR


class AuthorizationMissingError(VeylithError):
    """Raised when target owner authorization is missing or invalid."""

    exit_code = EXIT_AUTHORIZATION_MISSING


class IntegrityVerificationError(VeylithError):
    """Raised when release manifest, digest, or signature verification fails."""

    exit_code = EXIT_INTEGRITY_FAILED


class UnsupportedArtifactError(VeylithError):
    """Raised when an artifact format is unknown or unsupported."""

    exit_code = EXIT_UNSUPPORTED_ARTIFACT


class RequiredProviderUnavailableError(VeylithError):
    """Raised when an operation requires an external or local provider that is unavailable."""

    exit_code = EXIT_REQUIRED_PROVIDER_UNAVAILABLE


class GateFailedError(VeylithError):
    """Raised when benchmark or policy gate thresholds are not met."""

    exit_code = EXIT_GATE_FAILED


class SandboxUnavailableOrUnsafeError(VeylithError):
    """Raised when dynamic execution is requested but safe sandbox isolation is missing."""

    exit_code = EXIT_SANDBOX_UNAVAILABLE_OR_UNSAFE


class OperationCancelledError(VeylithError):
    """Raised when an operation is cancelled by user signal."""

    exit_code = EXIT_CANCELLED


class SecurityViolationError(VeylithError):
    """Raised when an intake path traversal, zip bomb, or trust boundary violation is detected."""

    exit_code = EXIT_USAGE_ERROR
