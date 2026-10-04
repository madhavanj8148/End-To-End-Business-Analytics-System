"""
Phase 4 — Operational Anomaly, Revenue Leakage & Early Warning Processing Pipeline
----------------------------------------------------------------------------------
Executes statistical anomaly detection, revenue leakage intelligence, smart rider allocation,
and operational early warning generation, saving datasets to datasets/engineered/ and
model metrics to models/anomaly_detection/anomaly_metrics.json.
"""

import json
from pathlib import Path
import pandas as pd
import sys

# Ensure python/ directory is in path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "python"))

from intelligence.operations.anomaly_detection import detect_operational_anomalies
from intelligence.operations.revenue_leakage import detect_revenue_leakage
from intelligence.operations.rider_allocation import recommend_rider_allocation, calculate_rider_workload
from intelligence.operations.demand_heatmap import generate_demand_hotspots
from intelligence.operations.operational_early_warning import generate_operational_early_warnings

def main():
    print("=" * 60)
    print("Running Phase 4 Operational Intelligence & Anomaly Pipeline...")
    print("=" * 60)

    cleaned_dir = BASE_DIR / "datasets" / "cleaned"
    engineered_dir = BASE_DIR / "datasets" / "engineered"
    models_dir = BASE_DIR / "models" / "anomaly_detection"

    engineered_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    orders_path = cleaned_dir / "orders.csv"
    orders_eng_path = engineered_dir / "orders_engineered.csv"
    deliveries_path = cleaned_dir / "deliveries.csv"
    customers_path = cleaned_dir / "customers.csv"
    restaurants_path = cleaned_dir / "restaurants.csv"
    riders_path = cleaned_dir / "riders.csv"

    orders_df = pd.read_csv(orders_path)
    orders_eng_df = pd.read_csv(orders_eng_path) if orders_eng_path.exists() else orders_df
    deliveries_df = pd.read_csv(deliveries_path)
    customers_df = pd.read_csv(customers_path) if customers_path.exists() else None
    restaurants_df = pd.read_csv(restaurants_path) if restaurants_path.exists() else None
    riders_df = pd.read_csv(riders_path) if riders_path.exists() else None

    # 1. Operational Anomalies
    print("Detecting operational anomalies (Z-score & IQR)...")
    anomalies_df = detect_operational_anomalies(orders_df, deliveries_df, restaurants_df, customers_df)
    anomalies_path = engineered_dir / "operational_anomalies.csv"
    anomalies_df.to_csv(anomalies_path, index=False)
    print(f"Saved operational anomalies ({len(anomalies_df):,} rows) -> {anomalies_path}")

    # 2. Revenue Leakage
    print("Analyzing potential revenue leakage...")
    leakage_df, leakage_kpis = detect_revenue_leakage(orders_eng_df, customers_df, restaurants_df)
    leakage_path = engineered_dir / "revenue_leakage.csv"
    leakage_df.to_csv(leakage_path, index=False)
    print(f"Saved revenue leakage ({len(leakage_df):,} rows) -> {leakage_path}")

    # 3. Smart Rider Allocation
    print("Running Smart Rider Allocation scoring...")
    rider_alloc_df = recommend_rider_allocation(orders_df, deliveries_df, riders_df, customers_df)
    alloc_path = engineered_dir / "rider_allocation.csv"
    rider_alloc_df.to_csv(alloc_path, index=False)
    print(f"Saved rider allocations ({len(rider_alloc_df):,} rows) -> {alloc_path}")

    # 4. Demand Heatmap & Hotspots
    print("Analyzing demand hotspots & city trends...")
    hotspots_df = generate_demand_hotspots(orders_df, customers_df)
    hotspot_path = engineered_dir / "demand_heatmap.csv"
    hotspots_df.to_csv(hotspot_path, index=False)
    print(f"Saved demand hotspots ({len(hotspots_df):,} rows) -> {hotspot_path}")

    # 5. Operational Early Warnings
    print("Synthesizing Operational Early Warnings...")
    alerts_df = generate_operational_early_warnings(orders_df, deliveries_df, riders_df, restaurants_df, anomalies_df, leakage_df)
    alerts_path = engineered_dir / "operational_alerts.csv"
    alerts_df.to_csv(alerts_path, index=False)
    print(f"Saved operational alerts ({len(alerts_df):,} rows) -> {alerts_path}")

    # Save summary metrics
    metrics = {
        "Total_Anomalies_Detected": len(anomalies_df),
        "Revenue_Leakage_KPIs": leakage_kpis,
        "Active_Alerts_Count": len(alerts_df),
        "Detection_Methodology": "Z-Score & IQR Statistical Bounds + Transparent Rule Scoring"
    }

    metrics_path = models_dir / "anomaly_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved anomaly metrics -> {metrics_path}")

    print("[SUCCESS] Operational Intelligence Pipeline Complete!\n")

if __name__ == "__main__":
    main()
