"""
Phase 4 — Delivery ETA Prediction Intelligence
-----------------------------------------------
Builds an ETA prediction regressor for delivery duration in minutes based on
trip distance, order hour, day of week, rider experience, and restaurant locality.

Note: Traffic conditions are not directly modeled because live traffic data is unavailable.
"""

from pathlib import Path
import pandas as pd
import numpy as np

DISCLAIMER_TEXT = "Traffic conditions are not directly modeled because live traffic data is unavailable."

def train_and_predict_eta(deliveries_df: pd.DataFrame, orders_df: pd.DataFrame, 
                          customers_df: pd.DataFrame = None, riders_df: pd.DataFrame = None) -> tuple[pd.DataFrame, dict]:
    """
    Trains an ETA prediction model and predicts delivery duration for all deliveries.
    Returns predicted deliveries DataFrame and evaluation metrics dictionary.
    """
    df = deliveries_df.copy()

    # Merge order datetime and customer city if available
    if "order_id" in df.columns and orders_df is not None:
        df = df.merge(orders_df[["order_id", "order_datetime", "customer_id", "restaurant_id"]], on="order_id", how="left")

    if "customer_id" in df.columns and customers_df is not None:
        df = df.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")

    if "rider_id" in df.columns and riders_df is not None:
        df = df.merge(riders_df[["rider_id", "experience_years", "vehicle_type"]], on="rider_id", how="left")

    # Feature Engineering
    if "order_datetime" in df.columns and df["order_datetime"].notna().any():
        dt = pd.to_datetime(df["order_datetime"])
        df["hour"] = dt.dt.hour.fillna(14)
        df["day_of_week"] = dt.dt.dayofweek.fillna(3)
        df["is_weekend"] = df["day_of_week"].apply(lambda d: 1 if d in [5, 6] else 0)
    else:
        df["hour"] = 14
        df["day_of_week"] = 3
        df["is_weekend"] = 0

    df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(df["distance_km"].median() if len(df) > 0 else 5.0)
    df["experience_years"] = pd.to_numeric(df.get("experience_years", 3), errors="coerce").fillna(3)

    # City one-hot encoding proxy
    cities = df["city"].fillna("Unknown").unique()
    for c in cities[:5]:  # top 5 cities
        df[f"city_{c}"] = (df["city"] == c).astype(int)

    city_cols = [f"city_{c}" for c in cities[:5]]
    feature_cols = ["distance_km", "hour", "day_of_week", "is_weekend", "experience_years"] + city_cols

    # Prepare matrix X and target y
    clean_mask = df["delivery_duration"].notna() & (df["delivery_duration"] > 0)
    train_df = df[clean_mask].copy()

    if len(train_df) < 20:
        raise ValueError("Insufficient delivery records to train ETA model.")

    # Split train/test (80/20)
    split_idx = int(len(train_df) * 0.8)
    X = train_df[feature_cols].values
    y = train_df["delivery_duration"].values

    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Solve OLS via pure NumPy: beta = (X^T X)^(-1) X^T y
    X_train_b = np.c_[np.ones(len(X_train)), X_train]
    X_test_b = np.c_[np.ones(len(X_test)), X_test]
    X_all_b = np.c_[np.ones(len(X)), X]

    try:
        beta = np.linalg.pinv(X_train_b.T @ X_train_b) @ (X_train_b.T @ y_train)
    except Exception:
        beta = np.zeros(X_train_b.shape[1])
        beta[0] = np.mean(y_train)

    # Predictions
    y_test_pred = np.maximum(10, np.round(X_test_b @ beta, 1))
    train_df["predicted_eta"] = np.maximum(10, np.round(X_all_b @ beta, 1))
    train_df["eta_error"] = np.round(np.abs(train_df["delivery_duration"] - train_df["predicted_eta"]), 1)
    train_df["accuracy_pct"] = np.round(np.maximum(0, 1 - (train_df["eta_error"] / train_df["delivery_duration"])) * 100, 1)

    # Accuracy Bucketing
    def categorize_error(err):
        if err <= 5.0:
            return "Excellent (<=5 min error)"
        elif err <= 15.0:
            return "Acceptable (5-15 min error)"
        else:
            return "Delayed (>15 min error)"

    train_df["accuracy_bucket"] = train_df["eta_error"].apply(categorize_error)

    # Evaluate Test Metrics
    mae = float(np.mean(np.abs(y_test - y_test_pred)))
    rmse = float(np.sqrt(np.mean((y_test - y_test_pred) ** 2)))
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    ss_res = np.sum((y_test - y_test_pred) ** 2)
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    metrics = {
        "MAE_minutes": round(mae, 2),
        "RMSE_minutes": round(rmse, 2),
        "R2_Score": round(r2, 4),
        "Disclaimer": DISCLAIMER_TEXT,
        "Total_Deliveries_Evaluated": len(train_df),
        "Excellent_PCT": round((train_df["accuracy_bucket"].str.startswith("Excellent")).mean() * 100, 1),
        "Acceptable_PCT": round((train_df["accuracy_bucket"].str.startswith("Acceptable")).mean() * 100, 1),
        "Delayed_PCT": round((train_df["accuracy_bucket"].str.startswith("Delayed")).mean() * 100, 1),
    }

    out_cols = ["order_id", "delivery_id", "rider_id", "distance_km", "delivery_duration", 
                "predicted_eta", "eta_error", "accuracy_pct", "accuracy_bucket"]
    out_cols = [c for c in out_cols if c in train_df.columns]

    return train_df[out_cols], metrics
