"""
Phase 5 — Recommendation Explanations
-------------------------------------
Generates natural language explanations for why an item was recommended.
"""

def generate_explanation(item_name: str, cf_score: float, cb_score: float) -> str:
    """
    Generates a contextual explanation based on the dominant score.
    """
    if cf_score > cb_score and cf_score > 0.5:
        return f"Because customers with similar tastes to yours often enjoy {item_name}."
    elif cb_score > cf_score and cb_score > 0.5:
        return f"Because {item_name} matches the cuisines and flavors you usually order."
    elif cf_score > 0 and cb_score > 0:
        return f"A perfect blend of what's popular and your personal taste preferences."
    else:
        return f"A trending dish we thought you might like."
