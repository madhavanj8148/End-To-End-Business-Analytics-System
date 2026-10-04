"""
Phase 4 — Demand Heatmap & Hotspot Analysis Intelligence
---------------------------------------------------------
Generates city-level demand intensity matrices (City x Day of Week, City x Hour)
and identifies demand hotspots, growing cities, declining cities, and peak periods.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def generate_demand_heatmap_matrix(orders_df: pd.DataFrame, customers_df: pd.DataFrame, dim: str = "day_of_week") -> pd.DataFrame:
    """
    Generates a city-level demand heatmap matrix.
    dim can be 'day_of_week' or 'hour'.
    """
    df = orders_df.copy()

    # Map city if missing
    if "city" not in df.columns and "customer_id" in df.columns and customers_df is not None:
        df = df.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")

    if "city" not in df.columns:
        df["city"] = "All Cities"
    else:
        df["city"] = df["city"].fillna("Unknown")

    if "order_datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["order_datetime"])
        if dim == "day_of_week":
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            df["dimension"] = df["datetime"].dt.dayofweek.map(lambda x: days[x] if x < len(days) else "Unknown")
        elif dim == "hour":
            df["dimension"] = df["datetime"].dt.hour.map(lambda h: f"{h:02d}:00")
        else:
            df["dimension"] = df[dim] if dim in df.columns else "All"
    else:
        df["dimension"] = "All"

    pivot_matrix = df.groupby(["city", "dimension"]).size().unstack(fill_value=0)
    return pivot_matrix


def generate_demand_hotspots(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes cities to rank demand volume, trend percentage, peak periods, and demand status.
    """
    df = orders_df.copy()

    if "city" not in df.columns and "customer_id" in df.columns and customers_df is not None:
        df = df.merge(customers_df[["customer_id", "city"]], on="customer_id", how="left")

    if "city" not in df.columns:
        df["city"] = "Unknown"
    else:
        df["city"] = df["city"].fillna("Unknown")

    df["datetime"] = pd.to_datetime(df["order_datetime"])
    df["date"] = df["datetime"].dt.date
    df["day_name"] = df["datetime"].dt.day_name()
    df["hour"] = df["datetime"].dt.hour

    # Split into recent period vs previous period for trend calculation
    max_date = df["date"].max()
    cutoff = max_date - pd.Timedelta(days=30)
    prev_cutoff = cutoff - pd.Timedelta(days=30)

    recent_df = df[df["date"] > cutoff]
    prev_df = df[(df["date"] <= cutoff) & (df["date"] > prev_cutoff)]

    city_stats = []

    for city, grp in df.groupby("city"):
        total_orders = len(grp)
        recent_orders = len(recent_df[recent_df["city"] == city])
        prev_orders = len(prev_df[prev_df["city"] == city])

        if prev_orders > 0:
            trend_pct = round(((recent_orders - prev_orders) / prev_orders) * 100, 1)
        else:
            trend_pct = 0.0

        # Peak day and hour
        peak_day = grp["day_name"].mode()[0] if len(grp) > 0 else "N/A"
        peak_hour = int(grp["hour"].mode()[0]) if len(grp) > 0 else 0
        peak_period = f"{peak_day}s ({peak_hour:02d}:00-{peak_hour+1:02d}:00)"

        # Demand Status
        if total_orders >= 10000:
            status = "🔴 High Demand"
        elif total_orders >= 5000:
            status = "🟠 Medium Demand"
        else:
            status = "🟡 Moderate Demand"

        city_stats.append({
            "City": city,
            "Demand_Status": status,
            "Total_Orders": total_orders,
            "Recent_30D_Orders": recent_orders,
            "Trend_Pct": trend_pct,
            "Peak_Period": peak_period,
            "Cancellation_Rate_Pct": round((grp["order_status"] == "Cancelled").mean() * 100, 1) if "order_status" in grp.columns else 0.0
        })

    hotspot_df = pd.DataFrame(city_stats).sort_values("Total_Orders", ascending=False).reset_index(drop=True)
    return hotspot_df
