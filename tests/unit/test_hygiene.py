"""Unit tests for LibCST docstring and comment stripping."""

from __future__ import annotations

from veylith.protection.hygiene import apply_python_hygiene


def test_strip_module_and_function_docstrings() -> None:
    source = '''"""Module level docstring."""

# A comment
def compute(x: int) -> int:
    """Compute something important."""
    # Internal step
    return x * 2
'''
    transformed = apply_python_hygiene(source, strip_docstrings=True, strip_comments=True)

    assert "Module level docstring" not in transformed
    assert "Compute something important" not in transformed
    assert "A comment" not in transformed
    assert "Internal step" not in transformed
    assert "return x * 2" in transformed


def test_function_with_only_docstring_replaces_with_pass() -> None:
    source = '''def empty_fn():
    """Just a docstring."""
'''
    transformed = apply_python_hygiene(source, strip_docstrings=True)
    assert "Just a docstring" not in transformed
    assert "pass" in transformed


def test_class_with_only_docstring_replaces_with_pass() -> None:
    source = '''class EmptyClass:
    """Class docstring."""
'''
    transformed = apply_python_hygiene(source, strip_docstrings=True)
    assert "Class docstring" not in transformed
    assert "pass" in transformed
