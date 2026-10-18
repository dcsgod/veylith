"""Unit tests for claims linter."""

from __future__ import annotations

from veylith.reporting.claims_lint import lint_text_claims


def test_claims_lint_flags_banned_phrases() -> None:
    bad_text = """
    Our software is completely unbreakable.
    This module stops REA from analyzing bytecode.
    Protection is guaranteed.
    """
    violations = lint_text_claims(bad_text)
    assert len(violations) == 3
    rule_ids = {v.rule_id for v in violations}
    assert "UNBREAKABLE" in rule_ids
    assert "STOPS_REA" in rule_ids
    assert "GUARANTEED" in rule_ids


def test_claims_lint_accepts_honest_reporting() -> None:
    good_text = """
    Measured against REA version 0.4.0 on sample tiny_calc.
    Residual risk remains for Tier 4 human analysts.
    Control verified by automated regression test suite.
    """
    violations = lint_text_claims(good_text)
    assert len(violations) == 0
