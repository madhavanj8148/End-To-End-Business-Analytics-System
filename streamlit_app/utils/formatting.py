"""
Formatting Utilities for NovaNest Analytics
"""

def format_currency(value: float) -> str:
    """Formats numeric values into INR currency representation (₹)."""
    if value is None or value != value:
        return "₹0.00"
    if abs(value) >= 1_000_000_07:
        return f"₹{value / 1_000_000_07:.2f} Cr"
    elif abs(value) >= 100_000:
        return f"₹{value / 100_000:.2f} L"
    elif abs(value) >= 1_000:
        return f"₹{value / 1_000:.1f}k"
    else:
        return f"₹{value:,.2f}"

def format_number(value: float) -> str:
    """Formats large integer counts into k/M human readable values."""
    if value is None or value != value:
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}k"
    else:
        return f"{int(value):,}"

def format_percent(value: float) -> str:
    """Formats decimal or float value to percentage string."""
    if value is None or value != value:
        return "0.0%"
    return f"{value:.1f}%"
