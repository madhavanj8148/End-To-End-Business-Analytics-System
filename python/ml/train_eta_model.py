"""
Phase 4 — ML Training Script: Delivery ETA Prediction Model
-----------------------------------------------------------
Trains the delivery ETA prediction regressor, evaluates MAE/RMSE/R2,
saves metrics to models/eta_prediction/eta_metrics.json, and outputs
predictions to datasets/engineered/eta_predictions.csv.
"""

import json
from pathlib import Path
import pandas as pd
import sys

# Ensure python/ directory is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "python"))

from intelligence.operations.eta_prediction import train_and_predict_eta

def main():
    print("=" * 60)
    print("Training Phase 4 Delivery ETA Prediction Model...")
    print("=" * 60)

    cleaned_dir = BASE_DIR / "datasets" / "cleaned"
    engineered_dir = BASE_DIR / "datasets" / "engineered"
    models_dir = BASE_DIR / "models" / "eta_prediction"

    engineered_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    deliveries_path = cleaned_dir / "deliveries.csv"
    orders_path = cleaned_dir / "orders.csv"
    customers_path = cleaned_dir / "customers.csv"
    riders_path = cleaned_dir / "riders.csv"

    if not deliveries_path.exists() or not orders_path.exists():
        raise FileNotFoundError("Missing required deliveries or orders datasets.")

    deliveries_df = pd.read_csv(deliveries_path)
    orders_df = pd.read_csv(orders_path)
    customers_df = pd.read_csv(customers_path) if customers_path.exists() else None
    riders_df = pd.read_csv(riders_path) if riders_path.exists() else None

    print(f"Loaded {len(deliveries_df):,} delivery trips for ETA prediction.")

    # Train ETA Model
    eta_df, metrics = train_and_predict_eta(deliveries_df, orders_df, customers_df, riders_df)

    # Save engineered predictions dataset
    output_csv = engineered_dir / "eta_predictions.csv"
    eta_df.to_csv(output_csv, index=False)
    print(f"Saved ETA predictions dataset ({len(eta_df):,} rows) -> {output_csv}")

    # Save metrics JSON
    metrics_path = models_dir / "eta_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved ETA metrics -> {metrics_path}")

    print("\nETA Model Performance Summary:")
    for k, v in metrics.items():
        print(f"  - {k}: {v}")
    print("[SUCCESS] Delivery ETA Model Training Complete!\n")

if __name__ == "__main__":
    main()
