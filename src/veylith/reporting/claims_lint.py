"""Claims linter enforcing strict rules against overpromising or unqualified claims."""

from __future__ import annotations

import re

# Banned terms and overpromising phrases per §2 claims policy
BANNED_CLAIM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("UNBREAKABLE", re.compile(r"\bunbreakable\b", re.IGNORECASE)),
    ("IMPOSSIBLE_TO_REVERSE", re.compile(r"\bimpossible to reverse\b", re.IGNORECASE)),
    ("UNCRACKABLE", re.compile(r"\buncrackable\b", re.IGNORECASE)),
    ("GUARANTEED", re.compile(r"\bguaranteed\b", re.IGNORECASE)),
    ("STOPS_REA", re.compile(r"\bstops rea\b", re.IGNORECASE)),
    ("DEFEATS_REA", re.compile(r"\bdefeats rea\b", re.IGNORECASE)),
    ("100_PERCENT_SECURE", re.compile(r"\b100% secure\b", re.IGNORECASE)),
]


class ClaimsViolation:
    """Represents an identified claims policy violation."""

    def __init__(self, rule_id: str, matched_text: str, line_number: int, context: str) -> None:
        self.rule_id = rule_id
        self.matched_text = matched_text
        self.line_number = line_number
        self.context = context

    def __str__(self) -> str:
        return (
            f"[ClaimsViolation] Rule '{self.rule_id}' matched '{self.matched_text}' "
            f"at line {self.line_number}: {self.context.strip()}"
        )


def lint_text_claims(text: str) -> list[ClaimsViolation]:
    """Scan text against claims policy rules and return all violations."""
    violations: list[ClaimsViolation] = []
    lines = text.splitlines()

    for idx, line in enumerate(lines, start=1):
        for rule_id, pattern in BANNED_CLAIM_PATTERNS:
            match = pattern.search(line)
            if match:
                violations.append(
                    ClaimsViolation(
                        rule_id=rule_id,
                        matched_text=match.group(0),
                        line_number=idx,
                        context=line,
                    )
                )

    return violations
