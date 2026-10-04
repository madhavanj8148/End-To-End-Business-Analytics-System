"""
Phase 7 — Financial Twin
------------------------
Analyzes and constructs the Financial twin state.
"""

import pandas as pd

def get_financial_twin_state(orders_df: pd.DataFrame) -> dict:
    if orders_df.empty:
        return {"Gross_Revenue": 0, "Discounts": 0, "Delivery_Fees": 0, "Platform_Revenue": 0, "Profit_Margin": 0, "Revenue_Leakage_Est": 0}
        
    gross = orders_df["order_amount"].sum()
    discounts = orders_df["discount_amount"].sum()
    fees = orders_df["delivery_fee"].sum()
    
    commissions = gross * 0.20
    platform_rev = commissions + fees - discounts
    margin = platform_rev / gross if gross > 0 else 0
    
    return {
        "Gross_Revenue": gross,
        "Discounts": discounts,
        "Delivery_Fees": fees,
        "Commissions": commissions,
        "Platform_Revenue": platform_rev,
        "Profit_Margin": margin,
        "Revenue_Leakage_Est": discounts if discounts > (gross * 0.15) else 0
    }
