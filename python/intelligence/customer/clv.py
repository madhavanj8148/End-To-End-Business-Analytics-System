"""
Customer Lifetime Value (CLV) Analytical Engine
------------------------------------------------
Calculates historical and projected CLV using purchase frequency, AOV, and customer tenure.
Categorizes customers into: Very High Value, High Value, Medium Value, Low Value.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_customer_clv(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes analytical Customer Lifetime Value (CLV).
    Formula:
      Historical Spend = Sum(final_amount)
      AOV = Historical Spend / Total Orders
      Frequency per Month = Total Orders / Tenure (Months)
      Estimated CLV = Historical Spend + (AOV * Frequency per Month * 12 * Projected Growth Factor)
    """
    df_orders = orders_df.copy()
    df_orders["order_datetime"] = pd.to_datetime(df_orders["order_datetime"])
    max_date = df_orders["order_datetime"].max()

    clv_df = df_orders.groupby("customer_id").agg(
        Total_Orders=("order_id", "count"),
        Total_Revenue=("final_amount", "sum"),
        First_Order=("order_datetime", "min"),
        Last_Order=("order_datetime", "max")
    ).reset_index()

    clv_df["AOV"] = (clv_df["Total_Revenue"] / clv_df["Total_Orders"]).round(2)
    clv_df["Tenure_Days"] = (max_date - clv_df["First_Order"]).dt.days.clip(lower=1)
    clv_df["Tenure_Months"] = (clv_df["Tenure_Days"] / 30.0).clip(lower=1.0)
    clv_df["Monthly_Frequency"] = (clv_df["Total_Orders"] / clv_df["Tenure_Months"]).round(2)

    # Project 12-month future value based on current monthly velocity
    clv_df["Projected_12M_Spend"] = (clv_df["AOV"] * clv_df["Monthly_Frequency"] * 12).round(2)
    clv_df["Estimated_CLV"] = (clv_df["Total_Revenue"] + clv_df["Projected_12M_Spend"] * 0.5).round(2)

    # CLV Value Tiers
    q75 = clv_df["Estimated_CLV"].quantile(0.75)
    q50 = clv_df["Estimated_CLV"].quantile(0.50)
    q25 = clv_df["Estimated_CLV"].quantile(0.25)

    def assign_clv_tier(clv_val):
        if clv_val >= q75:
            return "Very High Value"
        elif clv_val >= q50:
            return "High Value"
        elif clv_val >= q25:
            return "Medium Value"
        else:
            return "Low Value"

    clv_df["CLV_Segment"] = clv_df["Estimated_CLV"].apply(assign_clv_tier)

    # Merge customer demographic metadata
    result = customers_df[["customer_id", "customer_name", "city", "persona"]].merge(clv_df, on="customer_id", how="left")
    result["Total_Orders"] = result["Total_Orders"].fillna(0).astype(int)
    result["Total_Revenue"] = result["Total_Revenue"].fillna(0.0)
    result["Estimated_CLV"] = result["Estimated_CLV"].fillna(0.0)
    result["CLV_Segment"] = result["CLV_Segment"].fillna("Low Value")

    return result
