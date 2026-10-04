"""
Phase 4 — Operational Early Warning Intelligence
------------------------------------------------
Unified Operational Early Warning Engine synthesizing signals across demand spikes/drops,
ETA degradation, rider workload imbalance, restaurant cancellations, and revenue leakage.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def generate_operational_early_warnings(orders_df: pd.DataFrame, deliveries_df: pd.DataFrame,
                                         riders_df: pd.DataFrame = None, restaurants_df: pd.DataFrame = None,
                                         anomalies_df: pd.DataFrame = None, leakage_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Generates structured operational early warning alerts across the 5 core operational vectors.
    """
    alerts = []

    # 1. Delivery SLA & ETA Degradation Alert
    if deliveries_df is not None and "delivery_duration" in deliveries_df.columns:
        avg_dur = deliveries_df["delivery_duration"].mean()
        delayed_pct = (deliveries_df["delivery_duration"] > 45).mean() * 100

        if delayed_pct > 20.0:
            alerts.append({
                "Severity": "🔴 Critical",
                "Category": "Delivery ETA",
                "Entity": "Platform Logistics Fleet",
                "Metric": "Late Delivery Rate (>45m)",
                "Current_Value": f"{delayed_pct:.1f}%",
                "Threshold": "15.0%",
                "Explanation": f"High proportion of deliveries failing 45-minute SLA benchmark (Avg duration: {avg_dur:.1f} mins).",
                "Recommended_Action": "Rebalance active rider fleet shifts and temporarily widen delivery radius constraints."
            })
        elif delayed_pct > 12.0:
            alerts.append({
                "Severity": "🟠 Warning",
                "Category": "Delivery ETA",
                "Entity": "Platform Logistics Fleet",
                "Metric": "Late Delivery Rate (>45m)",
                "Current_Value": f"{delayed_pct:.1f}%",
                "Threshold": "10.0%",
                "Explanation": "SLA delivery times elevating above operational baseline target.",
                "Recommended_Action": "Monitor driver dispatch bottlenecks in peak hour zones."
            })

    # 2. Rider Workload Imbalance Alert
    if riders_df is not None and deliveries_df is not None:
        rider_counts = deliveries_df.groupby("rider_id").size()
        mean_load = rider_counts.mean() if len(rider_counts) > 0 else 10
        overloaded = (rider_counts > mean_load * 1.5).sum()
        overloaded_pct = (overloaded / max(1, len(riders_df))) * 100

        if overloaded_pct > 15.0:
            alerts.append({
                "Severity": "🔴 Critical",
                "Category": "Rider Operations",
                "Entity": "Delivery Rider Network",
                "Metric": "Rider Overload Ratio",
                "Current_Value": f"{overloaded_pct:.1f}%",
                "Threshold": "10.0%",
                "Explanation": f"{overloaded} riders carrying orders >1.5x fleet average load.",
                "Recommended_Action": "Deploy Smart Rider Allocation rebalancing and activate incentive bonuses for offline riders."
            })

    # 3. Restaurant Cancellation Spike Alert
    if orders_df is not None and "order_status" in orders_df.columns:
        canc_rate = (orders_df["order_status"] == "Cancelled").mean() * 100

        if canc_rate > 5.0:
            alerts.append({
                "Severity": "🔴 Critical",
                "Category": "Restaurant Operations",
                "Entity": "Partner Restaurants",
                "Metric": "Platform Order Cancellation Rate",
                "Current_Value": f"{canc_rate:.1f}%",
                "Threshold": "3.5%",
                "Explanation": "High cancellation volume causing customer disappointment and lost GTV.",
                "Recommended_Action": "Audit kitchen preparation bottlenecks and adjust prep time expectations in app algorithm."
            })

    # 4. Revenue & Discount Leakage Alert
    if leakage_df is not None and not leakage_df.empty:
        crit_leakage = (leakage_df["risk_level"] == "Critical Leakage").sum()
        total_leak_amt = leakage_df["potential_leakage_amount"].sum()

        if crit_leakage > 50 or total_leak_amt > 100000:
            alerts.append({
                "Severity": "🔴 Critical",
                "Category": "Financial Intelligence",
                "Entity": "Platform Discount & Fee Engine",
                "Metric": "Potential Financial Leakage",
                "Current_Value": f"₹{total_leak_amt:,.0f}",
                "Threshold": "₹50,000",
                "Explanation": f"{crit_leakage} critical orders identified with excessive subsidies or negative margins.",
                "Recommended_Action": "Review high-discount promotion rules and restrict unconstrained delivery fee waivers."
            })

    # 5. Demand Spike Alert
    if orders_df is not None and "order_datetime" in orders_df.columns:
        orders_df["date"] = pd.to_datetime(orders_df["order_datetime"]).dt.date
        recent_daily = orders_df.groupby("date").size()
        if len(recent_daily) >= 7:
            last_day_vol = recent_daily.iloc[-1]
            avg_vol = recent_daily.iloc[:-1].mean()
            if last_day_vol > avg_vol * 1.25:
                alerts.append({
                    "Severity": "🟠 Warning",
                    "Category": "Demand Forecasting",
                    "Entity": "City Demand Outlets",
                    "Metric": "Daily Order Volume Surge",
                    "Current_Value": f"{last_day_vol:,} orders",
                    "Threshold": f"{avg_vol*1.2:.0f} orders",
                    "Explanation": f"Recent daily demand exceeds 7-day average baseline by {round(((last_day_vol-avg_vol)/avg_vol)*100,1)}%.",
                    "Recommended_Action": "Increase rider capacity scheduling and ensure restaurant prep queue readiness."
                })

    alerts_df = pd.DataFrame(alerts)
    if alerts_df.empty:
        alerts_df = pd.DataFrame([{
            "Severity": "🟢 Healthy",
            "Category": "Operations Overview",
            "Entity": "NovaNest Platform",
            "Metric": "System Operational Status",
            "Current_Value": "Optimal",
            "Threshold": "Normal Range",
            "Explanation": "All operational metrics within standard performance bounds.",
            "Recommended_Action": "Continue regular monitoring."
        }])

    return alerts_df
