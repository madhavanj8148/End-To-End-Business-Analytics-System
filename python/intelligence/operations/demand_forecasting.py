"""
Phase 4 — Demand Forecasting Intelligence
------------------------------------------
Aggregates historical orders into daily/monthly demand time series per city
and overall platform, builds lag/rolling features without future target leakage,
and computes baseline forecast predictions with validation metrics.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def prepare_demand_time_series(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares a clean daily time series of demand aggregated by Date and City.
    """
    orders_clean = orders_df.copy()
    if "order_datetime" in orders_clean.columns:
        orders_clean["date"] = pd.to_datetime(orders_clean["order_datetime"]).dt.date
    elif "date" not in orders_clean.columns:
        raise ValueError("orders_df must contain 'order_datetime' or 'date'")

    # Map city via customers if missing in orders
    if "city" not in orders_clean.columns and "customer_id" in orders_clean.columns and customers_df is not None:
        orders_clean = orders_clean.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")
    
    if "city" not in orders_clean.columns:
        orders_clean["city"] = "All Cities"
    else:
        orders_clean["city"] = orders_clean["city"].fillna("Unknown")

    # Aggregate daily demand
    daily_demand = orders_clean.groupby(["date", "city"]).agg(
        actual_orders=("order_id", "count"),
        total_revenue=("final_amount" if "final_amount" in orders_clean.columns else "order_amount", "sum"),
        cancellations=("cancellation_flag" if "cancellation_flag" in orders_clean.columns else "order_id", lambda x: (x == 1).sum() if "cancellation_flag" in orders_clean.columns else 0)
    ).reset_index()

    daily_demand["date"] = pd.to_datetime(daily_demand["date"])
    daily_demand = daily_demand.sort_values(["city", "date"]).reset_index(drop=True)

    return daily_demand


def train_and_forecast_demand(daily_demand_df: pd.DataFrame, forecast_horizon_days: int = 14) -> tuple[pd.DataFrame, dict]:
    """
    Trains a time-series regression model (using pure NumPy OLS least-squares) 
    with lag and rolling window features. Returns forecast results DataFrame and evaluation metrics.
    """
    results_list = []
    overall_metrics = {}

    cities = daily_demand_df["city"].unique()

    total_actual = []
    total_predicted = []

    for city in cities:
        city_df = daily_demand_df[daily_demand_df["city"] == city].copy().sort_values("date").reset_index(drop=True)

        if len(city_df) < 7:
            continue

        # Feature Engineering (Strictly past values to prevent leakage)
        city_df["day_of_week"] = city_df["date"].dt.dayofweek
        city_df["is_weekend"] = city_df["day_of_week"].apply(lambda d: 1 if d in [5, 6] else 0)
        city_df["lag_1"] = city_df["actual_orders"].shift(1)
        city_df["lag_7"] = city_df["actual_orders"].shift(7)
        city_df["rolling_7"] = city_df["actual_orders"].shift(1).rolling(window=7, min_periods=1).mean()
        city_df["rolling_std_7"] = city_df["actual_orders"].shift(1).rolling(window=7, min_periods=1).std().fillna(0)

        # Drop NaN rows caused by lagging
        train_df = city_df.dropna(subset=["lag_1", "lag_7"]).copy()

        if len(train_df) < 10:
            continue

        # Time-aware split: latest 20% for validation
        split_idx = int(len(train_df) * 0.8)
        train_data = train_df.iloc[:split_idx]
        val_data = train_df.iloc[split_idx:]

        feature_cols = ["day_of_week", "is_weekend", "lag_1", "lag_7", "rolling_7"]
        
        # Prepare Design Matrix X and Target y for OLS
        X_train = train_data[feature_cols].values
        y_train = train_data["actual_orders"].values

        # Add Intercept column
        X_train_b = np.c_[np.ones(len(X_train)), X_train]

        # Solve Normal Equation: beta = (X^T X)^(-1) X^T y
        try:
            beta = np.linalg.pinv(X_train_b.T @ X_train_b) @ (X_train_b.T @ y_train)
        except Exception:
            beta = np.zeros(X_train_b.shape[1])
            beta[0] = np.mean(y_train)

        # In-sample & Validation Predictions
        X_all = train_df[feature_cols].values
        X_all_b = np.c_[np.ones(len(X_all)), X_all]
        train_df["predicted_orders"] = np.round(np.maximum(0, X_all_b @ beta), 1)

        # Error bounds (Residual std error)
        residuals = y_train - (X_train_b @ beta)
        std_err = np.std(residuals) if len(residuals) > 0 else 5.0

        train_df["lower_bound"] = np.maximum(0, np.round(train_df["predicted_orders"] - 1.96 * std_err, 1))
        train_df["upper_bound"] = np.round(train_df["predicted_orders"] + 1.96 * std_err, 1)

        # Validation Metrics
        if len(val_data) > 0:
            X_val = val_data[feature_cols].values
            X_val_b = np.c_[np.ones(len(X_val)), X_val]
            y_val_pred = np.maximum(0, X_val_b @ beta)
            y_val_actual = val_data["actual_orders"].values

            total_actual.extend(y_val_actual)
            total_predicted.extend(y_val_pred)

        # Append historical & forecast output rows
        results_list.append(train_df[["date", "city", "actual_orders", "predicted_orders", "lower_bound", "upper_bound"]])

        # Generate Future Horizon Forecasts
        last_date = city_df["date"].max()
        last_orders = list(city_df["actual_orders"].values[-7:])

        future_rows = []
        curr_orders = last_orders.copy()

        for i in range(1, forecast_horizon_days + 1):
            future_date = last_date + pd.Timedelta(days=i)
            dow = future_date.dayofweek
            is_wknd = 1 if dow in [5, 6] else 0
            l1 = curr_orders[-1]
            l7 = curr_orders[-7] if len(curr_orders) >= 7 else l1
            r7 = float(np.mean(curr_orders[-7:]))

            x_fut = np.array([1.0, dow, is_wknd, l1, l7, r7])
            pred_fut = float(np.maximum(0, np.round(x_fut @ beta, 1)))
            lb_fut = float(np.maximum(0, np.round(pred_fut - 1.96 * std_err, 1)))
            ub_fut = float(np.round(pred_fut + 1.96 * std_err, 1))

            future_rows.append({
                "date": future_date,
                "city": city,
                "actual_orders": np.nan,
                "predicted_orders": pred_fut,
                "lower_bound": lb_fut,
                "upper_bound": ub_fut
            })
            curr_orders.append(pred_fut)

        results_list.append(pd.DataFrame(future_rows))

    if len(results_list) > 0:
        forecast_df = pd.concat(results_list, ignore_index=True)
    else:
        forecast_df = pd.DataFrame(columns=["date", "city", "actual_orders", "predicted_orders", "lower_bound", "upper_bound"])

    # Global Validation Metrics Computation
    if len(total_actual) > 0:
        actual_arr = np.array(total_actual)
        pred_arr = np.array(total_predicted)

        mae = float(np.mean(np.abs(actual_arr - pred_arr)))
        rmse = float(np.sqrt(np.mean((actual_arr - pred_arr) ** 2)))
        mape = float(np.mean(np.abs((actual_arr - pred_arr) / np.maximum(1, actual_arr))) * 100)
        
        ss_tot = np.sum((actual_arr - np.mean(actual_arr)) ** 2)
        ss_res = np.sum((actual_arr - pred_arr) ** 2)
        r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

        overall_metrics = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE_pct": round(mape, 2),
            "R2_Score": round(r2, 4),
            "Model_Type": "Pure NumPy OLS Ridge/Linear Regressor",
            "Validation_Samples": len(actual_arr)
        }
    else:
        overall_metrics = {"MAE": 0.0, "RMSE": 0.0, "MAPE_pct": 0.0, "R2_Score": 0.0}

    return forecast_df, overall_metrics
