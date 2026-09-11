# fleet_utils.py
# Shared helpers for the KM-Waechter fleet service. Modernized.

KM_PER_MILE = 1.60934
MILES_PER_KM = 1.0 / KM_PER_MILE  # ≈ 0.621371


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles."""
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a number as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list) -> float:
    """Return the arithmetic mean of a list of numbers, or 0 if the list is empty."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def is_due(pct: float, threshold: float) -> bool:
    """Return True if pct is at or above threshold."""
    return pct >= threshold
