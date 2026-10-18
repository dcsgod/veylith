"""Tiny calculator module for verification testing."""

# Internal constant for tax rate
TAX_RATE = 0.05


def add(a: float, b: float) -> float:
    """Calculate the sum of two numbers."""
    # Addition logic
    return a + b


def calculate_total(subtotal: float) -> float:
    """Calculate total including tax rate."""
    # Compute tax
    tax = subtotal * TAX_RATE
    return subtotal + tax
