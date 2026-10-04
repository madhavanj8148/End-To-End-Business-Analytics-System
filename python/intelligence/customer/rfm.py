"""
Advanced 9-Segment RFM Segmentation Engine
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_advanced_rfm(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates R, F, M quantile scores (1-5) and assigns 9 transparent RFM segments.
    """
    df_orders = orders_df.copy()
    df_orders["order_datetime"] = pd.to_datetime(df_orders["order_datetime"])
    max_date = df_orders["order_datetime"].max()

    rfm = df_orders.groupby("customer_id").agg(
        Recency=("order_datetime", lambda x: (max_date - x.max()).days),
        Frequency=("order_id", "count"),
        Monetary=("final_amount", "sum")
    ).reset_index()

    # Recency score (Lower days = Higher score 5)
    rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Frequency score (Higher frequency = Higher score 5)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Monetary score (Higher monetary = Higher score 5)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)

    def assign_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif f >= 4:
            return "Loyal Customers"
        elif r >= 4 and f >= 2:
            return "Potential Loyalists"
        elif r >= 4 and f == 1:
            return "New Customers"
        elif r >= 3 and f >= 2:
            return "Promising"
        elif r <= 2 and f >= 3 and m >= 3:
            return "Can't Lose Them"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Hibernating"
        else:
            return "Lost"

    rfm["RFM_Segment"] = rfm.apply(assign_segment, axis=1)

    result = customers_df[["customer_id", "customer_name", "city", "persona"]].merge(rfm, on="customer_id", how="left")
    result["Recency"] = result["Recency"].fillna(999).astype(int)
    result["Frequency"] = result["Frequency"].fillna(0).astype(int)
    result["Monetary"] = result["Monetary"].fillna(0.0)
    result["RFM_Segment"] = result["RFM_Segment"].fillna("Lost")

    return result
