"""
Customer Churn Feature Engineering & Dataset Preparation
"""

from pathlib import Path
import pandas as pd
import numpy as np

def extract_churn_features(orders_df: pd.DataFrame, customers_df: pd.DataFrame, ratings_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Extracts customer-level feature vector for Machine Learning Churn Prediction.
    Churn Definition: Churned (1) if Recency > 90 days, else Active (0).
    """
    df_orders = orders_df.copy()
    df_orders["order_datetime"] = pd.to_datetime(df_orders["order_datetime"])
    max_date = df_orders["order_datetime"].max()

    features = df_orders.groupby("customer_id").agg(
        Recency=("order_datetime", lambda x: (max_date - x.max()).days),
        Frequency=("order_id", "count"),
        Monetary=("final_amount", "sum"),
        Total_Discounts=("discount_amount", "sum"),
        Cancellations=("order_status", lambda x: (x == "Cancelled").sum()),
        First_Order=("order_datetime", "min")
    ).reset_index()

    features["AOV"] = (features["Monetary"] / features["Frequency"]).round(2)
    features["Tenure_Days"] = (max_date - features["First_Order"]).dt.days.clip(lower=1)
    features["Cancellation_Rate"] = (features["Cancellations"] / features["Frequency"] * 100).round(2)
    features["Discount_Usage_Pct"] = (features["Total_Discounts"] / (features["Monetary"] + features["Total_Discounts"] + 1e-5) * 100).round(2)

    # Ratings feature
    if ratings_df is not None and not ratings_df.empty:
        avg_ratings = ratings_df.groupby("customer_id")["restaurant_rating"].mean().reset_index()
        avg_ratings.columns = ["customer_id", "Avg_Rating_Given"]
        features = features.merge(avg_ratings, on="customer_id", how="left")
        features["Avg_Rating_Given"] = features["Avg_Rating_Given"].fillna(4.0)
    else:
        features["Avg_Rating_Given"] = 4.0

    # Churn Label Definition: Recency > 90 days
    features["Is_Churned"] = np.where(features["Recency"] > 90, 1, 0)

    # Merge Customer Persona / Sub Type
    result = customers_df[["customer_id", "persona", "subscription_type", "city"]].merge(features, on="customer_id", how="inner")

    return result
