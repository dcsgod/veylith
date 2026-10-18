"""Unit tests for credential and secret redaction."""

from __future__ import annotations

from veylith.safety.redaction import redact_secrets


def test_redact_bearer_token() -> None:
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz"
    scrubbed = redact_secrets(text)
    assert "[REDACTED_BEARER_TOKEN]" in scrubbed
    assert "eyJhbGci" not in scrubbed


def test_redact_github_pat() -> None:
    text = "git clone https://ghp_123456789012345678901234567890123456@github.com"
    scrubbed = redact_secrets(text)
    assert "[REDACTED:GITHUB_PAT]" in scrubbed
    assert "ghp_" not in scrubbed


def test_redact_aws_key() -> None:
    text = "Access key AKIAIOSFODNN7EXAMPLE used"
    scrubbed = redact_secrets(text)
    assert "[REDACTED:AWS_KEY_ID]" in scrubbed
    assert "AKIA" not in scrubbed


def test_redact_password_assignment() -> None:
    text = "database_config = {'password': 'super_secret_db_password'}"
    scrubbed = redact_secrets(text)
    assert "[REDACTED]" in scrubbed
    assert "super_secret_db_password" not in scrubbed
