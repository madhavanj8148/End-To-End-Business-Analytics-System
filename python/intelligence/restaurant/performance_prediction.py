"""
Restaurant Performance Feature Extraction & Prediction Prep
"""

from pathlib import Path
import pandas as pd
import numpy as np

def extract_restaurant_features(restaurants_df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts restaurant-level features for predicting future order throughput.
    """
    df_rest = restaurants_df.copy()

    order_agg = orders_df.groupby("restaurant_id").agg(
        Total_Orders=("order_id", "count"),
        Total_Revenue=("final_amount", "sum"),
        Cancellations=("order_status", lambda x: (x == "Cancelled").sum())
    ).reset_index()

    order_agg["AOV"] = (order_agg["Total_Revenue"] / order_agg["Total_Orders"].clip(lower=1)).round(2)
    order_agg["Cancellation_Rate"] = (order_agg["Cancellations"] / order_agg["Total_Orders"].clip(lower=1) * 100).round(2)

    merged = df_rest.merge(order_agg, on="restaurant_id", how="left")
    merged["Total_Orders"] = merged["Total_Orders"].fillna(0)
    merged["Total_Revenue"] = merged["Total_Revenue"].fillna(0.0)
    merged["AOV"] = merged["AOV"].fillna(0.0)
    merged["Cancellation_Rate"] = merged["Cancellation_Rate"].fillna(0.0)

    # Simulated Next-Period Target: Projected Orders (Total_Orders + normal variation)
    np.random.seed(42)
    merged["Predicted_Next_Month_Orders"] = (merged["Total_Orders"] * np.random.uniform(0.9, 1.15, size=len(merged))).round(0)

    return merged
