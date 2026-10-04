"""
Phase 7 — Operations Twin
-------------------------
Analyzes and constructs the Operations twin state.
"""

import pandas as pd

def get_operations_twin_state(orders_df: pd.DataFrame) -> dict:
    if orders_df.empty:
        return {"Total_Orders": 0, "Avg_Delivery_Time": 0, "Late_Deliveries": 0}
        
    return {
        "Total_Orders": len(orders_df),
        "Avg_Delivery_Time": 35.0, # Placeholder
        "Late_Deliveries": int(len(orders_df) * 0.15) # Simulated
    }
