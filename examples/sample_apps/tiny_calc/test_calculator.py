"""Tests for sample tiny calculator."""

from calculator import add, calculate_total


def test_add() -> None:
    assert add(2.0, 3.0) == 5.0


def test_calculate_total() -> None:
    assert calculate_total(100.0) == 105.0
