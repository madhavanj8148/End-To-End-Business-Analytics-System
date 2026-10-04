"""
Phase 4 — Revenue Leakage Intelligence
---------------------------------------
Rule-based detection of potential platform financial leakage including excessive
promotional discounts, delivery fee waivers, cancellation losses, and negative profit margins.

Clearly labeled: Potential Leakage — Rule-Based Detection
"""

from pathlib import Path
import pandas as pd
import numpy as np

DISCLAIMER_TEXT = "Potential Leakage — Rule-Based Detection"

def detect_revenue_leakage(orders_eng_df: pd.DataFrame, customers_df: pd.DataFrame = None, 
                           restaurants_df: pd.DataFrame = None) -> tuple[pd.DataFrame, dict]:
    """
    Analyzes engineered orders to detect financial leakage triggers and risk categories.
    Returns detailed leakage transactions DataFrame and summary KPIs dictionary.
    """
    df = orders_eng_df.copy()

    leakage_records = []

    for _, row in df.iterrows():
        order_id = row["order_id"]
        cust_id = row.get("customer_id", "N/A")
        rest_id = row.get("restaurant_id", "N/A")
        order_amt = float(row.get("order_amount", row.get("final_amount", 0)))
        disc_amt = float(row.get("discount_amount", 0))
        deliv_fee = float(row.get("delivery_fee", 0))
        final_amt = float(row.get("final_amount", order_amt - disc_amt + deliv_fee))
        est_profit = float(row.get("estimated_profit", 0.0))
        status = str(row.get("order_status", "Delivered"))
        disc_pct = float(row.get("discount_percentage", (disc_amt / max(1, order_amt)) * 100))

        reasons = []
        leakage_amt = 0.0

        # Rule 1: Negative or Loss-Making Profit Margin
        if est_profit < 0:
            reasons.append("Negative Profit Margin")
            leakage_amt += abs(est_profit)

        # Rule 2: Excessive Discounting (> 25% or > ₹250)
        if disc_pct > 25.0 and disc_amt > 150:
            reasons.append(f"Excessive Discount Subsidy ({disc_pct:.1f}% / ₹{disc_amt:.0f})")
            leakage_amt += (disc_amt - 100)

        # Rule 3: Cancellation Loss
        if status == "Cancelled" and final_amt > 0:
            reasons.append("Cancelled Order Revenue Loss")
            leakage_amt += final_amt

        # Rule 4: Zero Delivery Fee on Low Basket Size (< ₹300)
        if deliv_fee == 0 and order_amt < 300:
            reasons.append("Waived Delivery Fee on Low-Value Order")
            leakage_amt += 35.0

        if reasons:
            if leakage_amt > 300 or est_profit < -100 or status == "Cancelled":
                risk_level = "Critical Leakage"
            elif leakage_amt > 150 or disc_pct > 30:
                risk_level = "High Leakage"
            else:
                risk_level = "Watch"

            leakage_records.append({
                "order_id": order_id,
                "customer_id": cust_id,
                "restaurant_id": rest_id,
                "order_amount": order_amt,
                "discount_amount": disc_amt,
                "delivery_fee": deliv_fee,
                "final_amount": final_amt,
                "estimated_profit": est_profit,
                "leakage_reason": " | ".join(reasons),
                "potential_leakage_amount": round(leakage_amt, 2),
                "risk_level": risk_level
            })

    leakage_df = pd.DataFrame(leakage_records)

    if leakage_df.empty:
        leakage_df = pd.DataFrame(columns=[
            "order_id", "customer_id", "restaurant_id", "order_amount", "discount_amount", 
            "delivery_fee", "final_amount", "estimated_profit", "leakage_reason", 
            "potential_leakage_amount", "risk_level"
        ])
    else:
        # Merge restaurant name and customer name if available
        if restaurants_df is not None and "restaurant_id" in leakage_df.columns:
            leakage_df = leakage_df.merge(restaurants_df[["restaurant_id", "restaurant_name"]], on="restaurant_id", how="left")
        if customers_df is not None and "customer_id" in leakage_df.columns:
            leakage_df = leakage_df.merge(customers_df[["customer_id", "customer_name"]], on="customer_id", how="left")

    total_leakage = float(leakage_df["potential_leakage_amount"].sum()) if not leakage_df.empty else 0.0
    total_orders = len(df)
    flagged_orders = len(leakage_df)
    leakage_rate = round((flagged_orders / max(1, total_orders)) * 100, 2)

    kpis = {
        "Total_Potential_Leakage": total_leakage,
        "Flagged_Orders_Count": flagged_orders,
        "Total_Orders_Audited": total_orders,
        "Leakage_Rate_PCT": leakage_rate,
        "Critical_Risk_Count": int((leakage_df["risk_level"] == "Critical Leakage").sum()) if not leakage_df.empty else 0,
        "High_Risk_Count": int((leakage_df["risk_level"] == "High Leakage").sum()) if not leakage_df.empty else 0,
        "Disclaimer": DISCLAIMER_TEXT
    }

    return leakage_df, kpis
