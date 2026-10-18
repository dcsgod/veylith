"""Secret and credential redaction filters for logs and error messages."""

from __future__ import annotations

import re

# Comprehensive compiled patterns for sensitive tokens
_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("OPENAI_KEY", re.compile(r"sk-[a-zA-Z0-9]{20,T3BlbkFJ[a-zA-Z0-9]{20,}")),
    ("GENERIC_BEARER", re.compile(r"(?i)(bearer\s+)[a-zA-Z0-9_\-\.]{20,}")),
    ("GITHUB_PAT", re.compile(r"gh[pousr]_[a-zA-Z0-9]{36,}")),
    ("AWS_KEY_ID", re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}")),
    (
        "PRIVATE_KEY",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----[^-]+-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL
        ),
    ),
    (
        "PASSWORD_KV",
        re.compile(
            r"(?i)(['\"]?(?:password|secret|api_key|token)['\"]?\s*[:=]\s*)['\"][^'\"]{4,}['\"]"
        ),
    ),
]


def redact_secrets(text: str) -> str:
    """Scrub recognized credentials, private keys, and API tokens from text."""
    if not text:
        return text

    scrubbed = text
    for rule_id, pattern in _PATTERNS:
        if rule_id == "PASSWORD_KV":
            scrubbed = pattern.sub(r"\1'[REDACTED]'", scrubbed)
        elif rule_id == "GENERIC_BEARER":
            scrubbed = pattern.sub(r"\1[REDACTED_BEARER_TOKEN]", scrubbed)
        elif rule_id == "PRIVATE_KEY":
            scrubbed = pattern.sub("[REDACTED_PRIVATE_KEY]", scrubbed)
        else:
            scrubbed = pattern.sub(f"[REDACTED:{rule_id}]", scrubbed)

    return scrubbed
