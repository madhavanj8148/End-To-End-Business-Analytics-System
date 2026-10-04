"""
Phase 4 — Smart Rider Allocation & Workload Intelligence
---------------------------------------------------------
Rule-based scoring framework for ranking delivery riders for pending/eligible orders
and computing fleet workload metrics.

Allocation Weights:
- City Match: 40%
- Workload:   25%
- Performance: 20%
- Distance/Exp: 15%
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_rider_workload(deliveries_df: pd.DataFrame, riders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes workload and performance metrics for all delivery riders.
    """
    rider_stats = deliveries_df.groupby("rider_id").agg(
        orders_handled=("delivery_id", "count"),
        avg_delivery_duration=("delivery_duration", "mean"),
        total_distance_km=("distance_km", "sum")
    ).reset_index()

    merged = riders_df.merge(rider_stats, on="rider_id", how="left").fillna({
        "orders_handled": 0,
        "avg_delivery_duration": 40.0,
        "total_distance_km": 0.0
    })

    mean_orders = merged["orders_handled"].mean() if len(merged) > 0 else 10.0

    def categorize_workload(orders):
        if orders > mean_orders * 1.3:
            return "Overloaded"
        elif orders < mean_orders * 0.7:
            return "Underutilized"
        else:
            return "Optimal"

    merged["workload_tier"] = merged["orders_handled"].apply(categorize_workload)
    merged["avg_delivery_duration"] = merged["avg_delivery_duration"].round(1)
    merged["total_distance_km"] = merged["total_distance_km"].round(1)

    return merged


def recommend_rider_allocation(orders_df: pd.DataFrame, deliveries_df: pd.DataFrame,
                                riders_df: pd.DataFrame, customers_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Ranks available riders for orders using the 4-part transparent scoring system.
    Returns recommended allocations with scores and explanation reasons.
    """
    orders_sample = orders_df.copy()

    if "city" not in orders_sample.columns and "customer_id" in orders_sample.columns and customers_df is not None:
        orders_sample = orders_sample.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")

    orders_sample["city"] = orders_sample.get("city", "Chennai").fillna("Chennai")

    workload_df = calculate_rider_workload(deliveries_df, riders_df)
    avg_fleet_duration = workload_df["avg_delivery_duration"].mean()
    max_orders = max(1, workload_df["orders_handled"].max())

    allocations = []

    # Map each order to the best available rider in fleet
    for _, order in orders_sample.head(2000).iterrows():  # Top 2000 active orders
        order_id = order["order_id"]
        order_city = order.get("city", "Chennai")

        # Score all riders for this order city
        candidate_riders = workload_df.copy()

        # 1. City Match (40%)
        candidate_riders["city_score"] = np.where(candidate_riders["city"] == order_city, 100.0, 0.0)

        # 2. Workload Score (25%) - Lower workload gets higher score
        candidate_riders["workload_score"] = 100.0 * (1.0 - (candidate_riders["orders_handled"] / max_orders))

        # 3. Performance Score (20%) - Lower avg duration gets higher score
        candidate_riders["perf_score"] = np.clip(100.0 * (1.0 - ((candidate_riders["avg_delivery_duration"] - 20) / 40)), 0, 100)

        # 4. Distance / Experience Score (15%)
        candidate_riders["exp_score"] = np.clip(candidate_riders["experience_years"] * 10.0, 0, 100)

        # Final Weighted Allocation Score
        candidate_riders["allocation_score"] = np.round(
            0.40 * candidate_riders["city_score"] +
            0.25 * candidate_riders["workload_score"] +
            0.20 * candidate_riders["perf_score"] +
            0.15 * candidate_riders["exp_score"],
            1
        )

        # Pick top scoring rider
        top_rider = candidate_riders.sort_values("allocation_score", ascending=False).iloc[0]

        reasons = []
        if top_rider["city_score"] == 100:
            reasons.append(f"City Match ({order_city})")
        if top_rider["workload_tier"] == "Underutilized" or top_rider["workload_score"] > 60:
            reasons.append("Optimal Workload Capacity")
        if top_rider["avg_delivery_duration"] <= avg_fleet_duration:
            reasons.append(f"Fast SLA ({top_rider['avg_delivery_duration']}m avg)")
        if top_rider["experience_years"] >= 5:
            reasons.append(f"High Experience ({top_rider['experience_years']} yrs)")

        allocations.append({
            "order_id": order_id,
            "order_city": order_city,
            "recommended_rider_id": top_rider["rider_id"],
            "recommended_rider_name": top_rider["rider_name"],
            "rider_city": top_rider["city"],
            "allocation_score": top_rider["allocation_score"],
            "workload_tier": top_rider["workload_tier"],
            "allocation_reasons": " | ".join(reasons) if reasons else "Default System Match"
        })

    return pd.DataFrame(allocations)
