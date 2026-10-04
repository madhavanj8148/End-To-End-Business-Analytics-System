"""
Phase 7 — Customer Twin
-----------------------
Analyzes and constructs the Customer twin state.
"""

import pandas as pd

def get_customer_twin_state(customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict:
    if customers_df.empty:
        return {"Total_Customers": 0, "Active_Customers": 0}
        
    total_cust = len(customers_df)
    active = orders_df["customer_id"].nunique() if not orders_df.empty else 0
    
    return {
        "Total_Customers": total_cust,
        "Active_Customers": active,
        "Order_Frequency": len(orders_df) / total_cust if total_cust > 0 else 0,
        "AOV": orders_df["order_amount"].sum() / len(orders_df) if not orders_df.empty else 0
    }
