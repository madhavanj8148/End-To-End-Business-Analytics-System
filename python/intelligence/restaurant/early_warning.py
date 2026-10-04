"""
Restaurant Early Warning System (Alert Engine)
-----------------------------------------------
Monitors ratings, cancellation spikes, and revenue anomalies to produce structured operational alerts.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def generate_restaurant_early_warnings(benchmarked_df: pd.DataFrame) -> list[dict]:
    """
    Evaluates benchmarked partner dataset and returns structured operational alert signals.
    """
    alerts = []

    for _, row in benchmarked_df.iterrows():
        rest_id = row["restaurant_id"]
        name = row["restaurant_name"]
        city = row["city"]

        # Alert 1: Critical Rating Drop
        if row["avg_rating"] < 3.5:
            alerts.append({
                "entity_id": rest_id,
                "entity_name": name,
                "city": city,
                "metric": "Average Rating",
                "current_value": f"{row['avg_rating']} ⭐",
                "benchmark": ">= 4.0 ⭐",
                "severity": "🔴 Critical",
                "explanation": f"Rating dropped severely to {row['avg_rating']} ⭐. Partner quality intervention required immediately."
            })

        # Alert 2: High Cancellation Spike
        if row["Cancellation_Rate"] > 6.0:
            alerts.append({
                "entity_id": rest_id,
                "entity_name": name,
                "city": city,
                "metric": "Cancellation Rate",
                "current_value": f"{row['Cancellation_Rate']:.1f}%",
                "benchmark": "<= 3.5%",
                "severity": "🔴 Critical",
                "explanation": f"Cancellation rate spike detected at {row['Cancellation_Rate']:.1f}%. Kitchen throughput issue probable."
            })

        # Alert 3: Low Revenue Watch
        elif row["City_Revenue_Percentile"] < 15.0 and row["Total_Revenue"] > 0:
            alerts.append({
                "entity_id": rest_id,
                "entity_name": name,
                "city": city,
                "metric": "City Revenue Rank",
                "current_value": f"Bottom {row['City_Revenue_Percentile']:.1f}%",
                "benchmark": "> 25th Percentile",
                "severity": "🟠 Warning",
                "explanation": f"Revenue ranks in bottom 15% of {city} partners. Marketing assistance recommended."
            })

    return alerts
