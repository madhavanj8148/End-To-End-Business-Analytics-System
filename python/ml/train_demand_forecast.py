"""
Phase 4 — ML Training Script: Demand Forecast Model
---------------------------------------------------
Trains the pure NumPy OLS time-series demand regressor, evaluates MAE/RMSE/R2,
saves metrics to models/demand_forecast/demand_metrics.json, and outputs
forecasts to datasets/engineered/demand_forecasts.csv.
"""

import json
from pathlib import Path
import pandas as pd
import sys

# Ensure python/ directory is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "python"))

from intelligence.operations.demand_forecasting import prepare_demand_time_series, train_and_forecast_demand

def main():
    print("=" * 60)
    print("Training Phase 4 Demand Forecast Model...")
    print("=" * 60)

    cleaned_dir = BASE_DIR / "datasets" / "cleaned"
    engineered_dir = BASE_DIR / "datasets" / "engineered"
    models_dir = BASE_DIR / "models" / "demand_forecast"

    engineered_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    orders_path = cleaned_dir / "orders.csv"
    customers_path = cleaned_dir / "customers.csv"

    if not orders_path.exists():
        raise FileNotFoundError(f"Missing required dataset: {orders_path}")

    orders_df = pd.read_csv(orders_path)
    customers_df = pd.read_csv(customers_path) if customers_path.exists() else None

    print(f"Loaded {len(orders_df):,} orders for demand forecasting.")

    # Prepare time series & train model
    daily_demand_df = prepare_demand_time_series(orders_df, customers_df)
    forecast_df, metrics = train_and_forecast_demand(daily_demand_df, forecast_horizon_days=14)

    # Save engineered dataset
    output_csv = engineered_dir / "demand_forecasts.csv"
    forecast_df.to_csv(output_csv, index=False)
    print(f"Saved demand forecasts dataset ({len(forecast_df):,} rows) -> {output_csv}")

    # Save metrics JSON
    metrics_path = models_dir / "demand_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved model metrics -> {metrics_path}")

    print("\nModel Performance Summary:")
    for k, v in metrics.items():
        print(f"  - {k}: {v}")
    print("[SUCCESS] Demand Forecast Model Training Complete!\n")

if __name__ == "__main__":
    main()
