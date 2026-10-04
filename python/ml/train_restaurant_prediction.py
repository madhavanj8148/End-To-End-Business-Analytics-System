"""
Machine Learning Training Pipeline: Restaurant Performance Prediction (Pure NumPy Baseline)
-----------------------------------------------------------------------------------------
Trains Linear Regression model using NumPy least squares (OLS) to predict next-period order throughput.
Evaluates MAE, RMSE, R², feature importances, and outputs predictions.
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"
MODELS_DIR = BASE_DIR / "models" / "restaurant_prediction"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.append(str(BASE_DIR / "python" / "intelligence" / "restaurant"))
from performance_prediction import extract_restaurant_features

def train_restaurant_regressor():
    print("==================================================")
    print("   TRAINING RESTAURANT PERFORMANCE MODEL          ")
    print("==================================================")

    restaurants_df = pd.read_csv(CLEANED_DIR / "restaurants.csv")
    orders_df = pd.read_csv(CLEANED_DIR / "orders.csv")

    df_features = extract_restaurant_features(restaurants_df, orders_df)

    feature_cols = ["avg_rating", "delivery_radius_km", "commission_percentage", "Total_Orders", "Total_Revenue", "Cancellation_Rate", "AOV"]
    X = df_features[feature_cols].values
    y = df_features["Predicted_Next_Month_Orders"].values

    # Train / Test split (80/20)
    np.random.seed(42)
    indices = np.random.permutation(len(X))
    test_size = int(len(X) * 0.2)

    test_idx = indices[:test_size]
    train_idx = indices[test_size:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]

    # Standard Scaling
    mean = np.mean(X_train, axis=0)
    std = np.std(X_train, axis=0) + 1e-8

    X_train_scaled = (X_train - mean) / std
    X_test_scaled = (X_test - mean) / std
    X_scaled = (X - mean) / std

    # Fit Ordinary Least Squares (OLS) via NumPy lstsq
    X_b_train = np.c_[np.ones((X_train_scaled.shape[0], 1)), X_train_scaled]
    weights, residuals, rank, s = np.linalg.lstsq(X_b_train, y_train, rcond=None)

    # Predict on test set
    X_b_test = np.c_[np.ones((X_test_scaled.shape[0], 1)), X_test_scaled]
    y_pred = np.dot(X_b_test, weights)

    mae = np.mean(np.abs(y_test - y_pred))
    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
    ss_res = np.sum((y_test - y_pred) ** 2)
    r2 = 1.0 - (ss_res / (ss_tot + 1e-10))

    metrics = {
        "model_type": "Linear Regression OLS (NumPy Engine)",
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2_score": round(float(r2), 4),
        "feature_importances": dict(zip(feature_cols, np.abs(weights[1:]).round(4).tolist()))
    }

    print(f"Restaurant Prediction Metrics: {metrics}")

    # Save Model Artifacts
    with open(MODELS_DIR / "restaurant_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    # Full Predictions
    X_b_full = np.c_[np.ones((X_scaled.shape[0], 1)), X_scaled]
    df_features["Predicted_Next_Month_Orders"] = np.dot(X_b_full, weights).round(0)
    df_features["Predicted_Next_Month_Orders"] = df_features["Predicted_Next_Month_Orders"].clip(lower=0)

    output_path = ENGINEERED_DIR / "restaurant_predictions.csv"
    df_features.to_csv(output_path, index=False)
    print(f"Saved restaurant predictions ({len(df_features)} rows) -> {output_path}")
    print("==================================================")

if __name__ == "__main__":
    train_restaurant_regressor()
