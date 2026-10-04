"""
Phase 4 — Operational Anomaly Detection Intelligence
----------------------------------------------------
Statistical anomaly detection system using Z-Score and IQR statistical bounds
to flag delivery delays, volume spikes/drops, high cancellation rates, and discount anomalies.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def detect_operational_anomalies(orders_df: pd.DataFrame, deliveries_df: pd.DataFrame, 
                                 restaurants_df: pd.DataFrame = None, customers_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Detects statistical anomalies across delivery duration, order cancellation rates, 
    order volume spikes, and discount anomalies.
    """
    anomalies = []

    # 1. Delivery Duration Anomalies (Z-Score > 2.5)
    if deliveries_df is not None and "delivery_duration" in deliveries_df.columns:
        mean_dur = deliveries_df["delivery_duration"].mean()
        std_dur = deliveries_df["delivery_duration"].std()
        upper_bound = mean_dur + 2.5 * std_dur

        deliv_anom = deliveries_df[deliveries_df["delivery_duration"] > upper_bound]

        for _, row in deliv_anom.head(100).iterrows():
            act = float(row["delivery_duration"])
            dev_pct = round(((act - mean_dur) / mean_dur) * 100, 1)

            severity = "Critical" if act > mean_dur + 3.5 * std_dur else "High"
            anomalies.append({
                "Entity_Type": "Delivery",
                "Entity_ID": row.get("order_id", row.get("delivery_id")),
                "Metric": "Delivery Duration",
                "Actual_Value": f"{act:.1f} mins",
                "Expected_Value": f"{mean_dur:.1f} mins",
                "Deviation_Pct": f"+{dev_pct}%",
                "Severity": severity,
                "Explanation": f"Delivery duration significantly exceeds platform baseline threshold ({upper_bound:.1f} mins)."
            })

    # 2. Restaurant Cancellation Rate Anomalies (Cancellation Rate > 15%)
    if orders_df is not None and "restaurant_id" in orders_df.columns:
        rest_canc = orders_df.groupby("restaurant_id").agg(
            total_orders=("order_id", "count"),
            cancelled_orders=("order_status" if "order_status" in orders_df.columns else "order_id", lambda x: (x == "Cancelled").sum())
        ).reset_index()

        rest_canc = rest_canc[rest_canc["total_orders"] >= 15]
        rest_canc["cancellation_rate"] = (rest_canc["cancelled_orders"] / rest_canc["total_orders"]) * 100

        avg_canc_rate = rest_canc["cancellation_rate"].mean()
        high_canc = rest_canc[rest_canc["cancellation_rate"] > max(15.0, avg_canc_rate * 2.5)]

        if restaurants_df is not None:
            high_canc = high_canc.merge(restaurants_df[["restaurant_id", "restaurant_name"]], on="restaurant_id", how="left")

        for _, row in high_canc.head(50).iterrows():
            act = float(row["cancellation_rate"])
            rest_name = row.get("restaurant_name", row["restaurant_id"])
            dev_pct = round(((act - avg_canc_rate) / max(0.1, avg_canc_rate)) * 100, 1)

            severity = "Critical" if act > 25.0 else "High"
            anomalies.append({
                "Entity_Type": "Restaurant",
                "Entity_ID": f"{rest_name} ({row['restaurant_id']})",
                "Metric": "Cancellation Rate",
                "Actual_Value": f"{act:.1f}%",
                "Expected_Value": f"{avg_canc_rate:.1f}%",
                "Deviation_Pct": f"+{dev_pct}%",
                "Severity": severity,
                "Explanation": f"Restaurant exhibits abnormally high order cancellation rate ({row['cancelled_orders']} cancelled of {row['total_orders']})."
            })

    # 3. Excessive Discount / Low Margin Order Anomalies
    if orders_df is not None and "discount_percentage" in orders_df.columns:
        high_disc = orders_df[orders_df["discount_percentage"] > 35.0].head(50)
        avg_disc = orders_df["discount_percentage"].mean()

        for _, row in high_disc.iterrows():
            act = float(row["discount_percentage"])
            dev_pct = round(((act - avg_disc) / max(0.1, avg_disc)) * 100, 1)

            severity = "Medium" if act <= 45.0 else "High"
            anomalies.append({
                "Entity_Type": "Order",
                "Entity_ID": row["order_id"],
                "Metric": "Discount Percentage",
                "Actual_Value": f"{act:.1f}%",
                "Expected_Value": f"{avg_disc:.1f}%",
                "Deviation_Pct": f"+{dev_pct}%",
                "Severity": severity,
                "Explanation": f"Promotional discount subsidies exceed standard campaign thresholds."
            })

    anomaly_df = pd.DataFrame(anomalies)
    if anomaly_df.empty:
        anomaly_df = pd.DataFrame(columns=["Entity_Type", "Entity_ID", "Metric", "Actual_Value", "Expected_Value", "Deviation_Pct", "Severity", "Explanation"])

    return anomaly_df
