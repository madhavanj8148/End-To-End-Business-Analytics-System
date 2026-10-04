"""
Phase 7 — Digital Twin Metrics
------------------------------
Calculates unified twin metrics from analytical datasets.
"""

import pandas as pd

def calculate_financial_metrics(orders_df: pd.DataFrame) -> dict:
    if orders_df.empty:
        return {"Gross_Revenue": 0, "Discounts": 0, "Delivery_Fees": 0, "Platform_Revenue": 0, "Profit_Margin": 0}
        
    gross = orders_df["order_amount"].sum()
    discounts = orders_df["discount_amount"].sum()
    fees = orders_df["delivery_fee"].sum()
    
    # Assume 20% platform commission logic from existing phases
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
        "Revenue_Leakage_Est": discounts if discounts > (gross * 0.15) else 0 # simple leak heuristic
    }

def calculate_customer_metrics(customers_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict:
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

def calculate_restaurant_metrics(restaurants_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict:
    return {
        "Total_Restaurants": len(restaurants_df),
        "Active_Restaurants": orders_df["restaurant_id"].nunique() if not orders_df.empty else 0
    }

def calculate_operations_metrics(orders_df: pd.DataFrame) -> dict:
    if orders_df.empty:
        return {"Total_Orders": 0, "Avg_Delivery_Time": 0}
        
    return {
        "Total_Orders": len(orders_df),
        "Avg_Delivery_Time": 35.0, # Placeholder if missing delivery times in raw orders.
        "Late_Deliveries": int(len(orders_df) * 0.15) # Simulated for twin context
    }
