"""
Next Best Action (NBA) Decision Intelligence Engine — Phase 3 & 4 Extended
---------------------------------------------------------------------------
Generates prioritized, actionable business interventions for high-value customers,
partner restaurants, and operations/logistics managers based on behavioral risk,
performance triggers, and operational early warnings.
"""

from pathlib import Path
import pandas as pd

def generate_customer_next_best_actions(churn_df: pd.DataFrame, clv_df: pd.DataFrame, rfm_df: pd.DataFrame) -> list[dict]:
    """
    Generates rule-based Next Best Actions for customers.
    """
    actions = []

    merged = churn_df.merge(clv_df[["customer_id", "Estimated_CLV", "CLV_Segment"]], on="customer_id", how="left")
    merged = merged.merge(rfm_df[["customer_id", "RFM_Segment"]], on="customer_id", how="left")

    for _, row in merged.iterrows():
        cust_id = row["customer_id"]
        clv = row.get("Estimated_CLV", 0)
        risk = row.get("Churn_Risk", "Low Risk")
        segment = row.get("RFM_Segment", "Lost")

        if risk == "High Risk" and clv >= 10000:
            actions.append({
                "target_type": "Customer",
                "entity_id": cust_id,
                "detected_condition": f"High CLV (₹{clv:,.0f}) with High Churn Risk ({row['Churn_Probability']:.2f})",
                "recommended_action": "Trigger VIP Retention Intervention: Dedicated 25% Off + Free Delivery Coupon",
                "reason": "High-value customer showing imminent churn signs",
                "priority": "High"
            })
        elif risk == "High Risk":
            actions.append({
                "target_type": "Customer",
                "entity_id": cust_id,
                "detected_condition": f"High Churn Risk ({row['Churn_Probability']:.2f})",
                "recommended_action": "Send Automated Re-engagement Push Notification",
                "reason": "Inactive beyond typical purchase cycle",
                "priority": "Medium"
            })
        elif segment == "Champions":
            actions.append({
                "target_type": "Customer",
                "entity_id": cust_id,
                "detected_condition": "Champion RFM Segment (High Recency, Frequency & Spend)",
                "recommended_action": "Enroll in NovaNest VIP Brand Ambassador Club",
                "reason": "Reward high-loyalty advocate to maximize advocacy",
                "priority": "Low"
            })

    return actions

def generate_restaurant_next_best_actions(risk_df: pd.DataFrame, bench_df: pd.DataFrame) -> list[dict]:
    """
    Generates rule-based Next Best Actions for restaurants.
    """
    actions = []

    merged = risk_df.merge(bench_df[["restaurant_id", "Overall_Percentile"]], on="restaurant_id", how="left")

    for _, row in merged.iterrows():
        rest_id = row["restaurant_id"]
        name = row["restaurant_name"]
        risk_cat = row.get("Risk_Category", "Healthy")
        rating = row.get("avg_rating", 4.0)
        cancellation_rate = row.get("Cancellation_Rate", 0.0)
        revenue = row.get("Total_Revenue", 0.0)

        if risk_cat == "Critical":
            actions.append({
                "target_type": "Restaurant",
                "entity_id": rest_id,
                "entity_name": name,
                "detected_condition": f"Critical Risk Category: {row.get('Risk_Reasons')}",
                "recommended_action": "Initiate Account Manager Intervention & Kitchen Quality Audit",
                "reason": "Partner is exhibiting severe operational or customer dissatisfaction risk",
                "priority": "High"
            })
        elif rating < 3.8 and revenue >= 50000:
            actions.append({
                "target_type": "Restaurant",
                "entity_id": rest_id,
                "entity_name": name,
                "detected_condition": f"High Revenue Partner with Low Rating ({rating} ⭐)",
                "recommended_action": "Conduct Food Packaging & Preparation Quality Audit",
                "reason": "High order volume experiencing customer rating degradation",
                "priority": "High"
            })
        elif cancellation_rate > 5.0:
            actions.append({
                "target_type": "Restaurant",
                "entity_id": rest_id,
                "entity_name": name,
                "detected_condition": f"Elevated Cancellation Rate ({cancellation_rate:.1f}%)",
                "recommended_action": "Adjust Kitchen Prep Time Benchmark (+5 mins) in App Algorithm",
                "reason": "Kitchen order acceptance bottleneck causing cancellations",
                "priority": "Medium"
            })

    return actions

def generate_operational_next_best_actions(alerts_df: pd.DataFrame, leakage_df: pd.DataFrame) -> list[dict]:
    """
    Generates operational Next Best Actions for logistics, rider allocation, and revenue leakage.
    """
    actions = []

    if alerts_df is not None and not alerts_df.empty:
        for _, alert in alerts_df.iterrows():
            actions.append({
                "target_type": "Operations & Logistics",
                "entity_id": alert.get("Entity", "System"),
                "entity_name": alert.get("Category", "Operations"),
                "detected_condition": f"[{alert['Severity']}] {alert['Metric']}: {alert['Current_Value']} (Threshold: {alert['Threshold']})",
                "recommended_action": alert.get("Recommended_Action", "Investigate metric anomaly."),
                "reason": alert.get("Explanation", "Operational baseline threshold breached."),
                "priority": "High" if "Critical" in alert.get("Severity", "") else "Medium"
            })

    if leakage_df is not None and not leakage_df.empty:
        crit_leakage = leakage_df[leakage_df["risk_level"] == "Critical Leakage"]
        if len(crit_leakage) > 0:
            actions.append({
                "target_type": "Revenue Operations",
                "entity_id": "Financial Engine",
                "entity_name": "Discount & Fee Subsidies",
                "detected_condition": f"Detected {len(crit_leakage):,} orders with Critical Revenue Leakage (Total: ₹{crit_leakage['potential_leakage_amount'].sum():,.0f})",
                "recommended_action": "Cap Maximum Promotional Discount Percentage to 25% & Enforce Delivery Fee Min Threshold",
                "reason": "Subsidies causing negative order margins and unrecovered delivery costs",
                "priority": "High"
            })

    return actions
