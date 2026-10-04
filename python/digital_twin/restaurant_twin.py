"""
Phase 7 — Restaurant Twin
-------------------------
Analyzes and constructs the Restaurant twin state.
"""

import pandas as pd

def get_restaurant_twin_state(restaurants_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict:
    return {
        "Total_Restaurants": len(restaurants_df),
        "Active_Restaurants": orders_df["restaurant_id"].nunique() if not orders_df.empty else 0
    }
