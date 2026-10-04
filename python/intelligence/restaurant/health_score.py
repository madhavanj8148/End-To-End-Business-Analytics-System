"""
Enhanced Restaurant Health Score Engine (0-100)
------------------------------------------------
Calculates composite Health Score using 5 weighted business dimensions:
1. Revenue Score (max 30 pts)
2. Order Volume Score (max 30 pts)
3. Average Rating Score (max 20 pts)
4. Operational Reliability / Low Cancellation Score (max 10 pts)
5. Review Volume / Engagement Score (max 10 pts)
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_restaurant_health_score(
    restaurants_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    ratings_df: pd.DataFrame = None
) -> pd.DataFrame:
    """
    Computes transparent composite Restaurant Health Scores (0-100) with detailed component breakdowns.
    """
    df_rest = restaurants_df.copy()

    # Aggregate order metrics per restaurant
    order_agg = orders_df.groupby("restaurant_id").agg(
        Total_Orders=("order_id", "count"),
        Total_Revenue=("final_amount", "sum"),
        Cancellations=("order_status", lambda x: (x == "Cancelled").sum())
    ).reset_index()

    order_agg["Cancellation_Rate"] = (order_agg["Cancellations"] / order_agg["Total_Orders"] * 100).fillna(0.0)

    # Aggregate review count per restaurant
    if ratings_df is not None and not ratings_df.empty:
        # Merge orders to find restaurant_id
        ratings_rest = ratings_df.merge(orders_df[["order_id", "restaurant_id"]], on="order_id", how="left")
        review_counts = ratings_rest.groupby("restaurant_id")["review_id"].count().reset_index()
        review_counts.columns = ["restaurant_id", "Review_Count"]
    else:
        review_counts = pd.DataFrame(columns=["restaurant_id", "Review_Count"])

    merged = df_rest.merge(order_agg, on="restaurant_id", how="left").merge(review_counts, on="restaurant_id", how="left")
    merged["Total_Orders"] = merged["Total_Orders"].fillna(0)
    merged["Total_Revenue"] = merged["Total_Revenue"].fillna(0.0)
    merged["Cancellation_Rate"] = merged["Cancellation_Rate"].fillna(0.0)
    merged["Review_Count"] = merged["Review_Count"].fillna(0)

    max_rev = merged["Total_Revenue"].max() if merged["Total_Revenue"].max() > 0 else 1.0
    max_orders = merged["Total_Orders"].max() if merged["Total_Orders"].max() > 0 else 1.0
    max_reviews = merged["Review_Count"].max() if merged["Review_Count"].max() > 0 else 1.0

    # Component Scores
    merged["Score_Revenue"] = (merged["Total_Revenue"] / max_rev * 30.0).round(1)
    merged["Score_Orders"] = (merged["Total_Orders"] / max_orders * 30.0).round(1)
    merged["Score_Rating"] = (merged["avg_rating"].clip(lower=1.0, upper=5.0) / 5.0 * 20.0).round(1)
    merged["Score_Operations"] = ((1.0 - (merged["Cancellation_Rate"] / 100.0).clip(upper=1.0)) * 10.0).round(1)
    merged["Score_Engagement"] = (merged["Review_Count"] / max_reviews * 10.0).round(1)

    merged["Health_Score"] = (
        merged["Score_Revenue"] +
        merged["Score_Orders"] +
        merged["Score_Rating"] +
        merged["Score_Operations"] +
        merged["Score_Engagement"]
    ).round(1)

    return merged
