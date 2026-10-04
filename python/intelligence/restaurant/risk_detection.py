"""
Restaurant Risk Detection Engine
---------------------------------
Evaluates partner metrics and identifies operational, quality, or financial risks
with mandatory human-readable textual explanations.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def detect_restaurant_risks(health_df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates restaurant risk profile and generates risk status & explanations.
    Risk Levels: Healthy, Watch, At Risk, Critical.
    """
    df = health_df.copy()

    def evaluate_risk(row):
        reasons = []
        severity_points = 0

        # 1. Quality Risk
        if row["avg_rating"] < 3.5:
            reasons.append(f"Severe Low Rating ({row['avg_rating']} ⭐)")
            severity_points += 3
        elif row["avg_rating"] < 3.9:
            reasons.append(f"Below Avg Rating ({row['avg_rating']} ⭐)")
            severity_points += 1

        # 2. Operational Risk
        if row["Cancellation_Rate"] > 6.0:
            reasons.append(f"Excessive Cancellations ({row['Cancellation_Rate']:.1f}%)")
            severity_points += 3
        elif row["Cancellation_Rate"] > 3.5:
            reasons.append(f"Elevated Cancellations ({row['Cancellation_Rate']:.1f}%)")
            severity_points += 1

        # 3. Revenue / Volume Risk
        if row["Total_Revenue"] < 15000:
            reasons.append("Low Platform Revenue Generation (<₹15k)")
            severity_points += 2

        if row["Total_Orders"] < 10:
            reasons.append("Low Order Volume (<10 orders)")
            severity_points += 2

        # Risk Category Classification
        if severity_points >= 5:
            risk_category = "Critical"
        elif severity_points >= 3:
            risk_category = "At Risk"
        elif severity_points >= 1:
            risk_category = "Watch"
        else:
            risk_category = "Healthy"
            reasons.append("Optimal operational performance")

        return pd.Series([risk_category, " | ".join(reasons)], index=["Risk_Category", "Risk_Reasons"])

    risk_eval = df.apply(evaluate_risk, axis=1)
    df["Risk_Category"] = risk_eval["Risk_Category"]
    df["Risk_Reasons"] = risk_eval["Risk_Reasons"]

    return df
