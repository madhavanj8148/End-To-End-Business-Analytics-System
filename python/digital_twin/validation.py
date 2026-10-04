"""
Phase 7 — Digital Twin Validation
---------------------------------
Validates inputs to the digital twin state builders.
"""

def validate_twin_inputs(data: dict) -> bool:
    required_keys = ["orders", "customers", "restaurants"]
    for k in required_keys:
        if k not in data or data[k] is None or data[k].empty:
            return False
    return True
