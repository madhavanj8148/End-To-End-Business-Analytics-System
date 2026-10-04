"""
Customer 360 Analytics Engine
"""

from pathlib import Path
import pandas as pd
import numpy as np

def build_customer_360_profile(
    customer_id: str,
    customers_df: pd.DataFrame,
    orders_df: pd.DataFrame,
    rfm_df: pd.DataFrame,
    clv_df: pd.DataFrame,
    churn_df: pd.DataFrame
) -> dict:
    """
    Builds a complete 360-degree profile for a given customer.
    """
    cust_base = customers_df[customers_df["customer_id"] == customer_id]
    if cust_base.empty:
        return {}
    cust_info = cust_base.iloc[0].to_dict()

    cust_orders = orders_df[orders_df["customer_id"] == customer_id]
    total_orders = len(cust_orders)
    total_spent = cust_orders["final_amount"].sum() if total_orders > 0 else 0.0
    aov = (total_spent / total_orders) if total_orders > 0 else 0.0

    cust_rfm = rfm_df[rfm_df["customer_id"] == customer_id]
    rfm_segment = cust_rfm.iloc[0]["RFM_Segment"] if not cust_rfm.empty else "N/A"

    cust_clv = clv_df[clv_df["customer_id"] == customer_id]
    est_clv = cust_clv.iloc[0]["Estimated_CLV"] if not cust_clv.empty else total_spent
    clv_segment = cust_clv.iloc[0]["CLV_Segment"] if not cust_clv.empty else "N/A"

    cust_churn = churn_df[churn_df["customer_id"] == customer_id]
    churn_prob = cust_churn.iloc[0]["Churn_Probability"] if not cust_churn.empty else 0.0
    churn_risk = cust_churn.iloc[0]["Churn_Risk"] if not cust_churn.empty else "Low Risk"

    # Preliminary Rule-Based Recommendation
    if churn_risk == "High Risk" and est_clv >= 10000:
        recommendation = "High-Value At-Risk Customer: Trigger VIP Retention Offer (25% off + Free Delivery)."
    elif churn_risk == "High Risk":
        recommendation = "At-Risk Customer: Send re-engagement push notification with discount coupon."
    elif rfm_segment in ["Champions", "Loyal Customers"]:
        recommendation = "Loyal Advocate: Invite to NovaNest Premium Subscription Loyalty Club."
    else:
        recommendation = "Standard Engagement: Recommend top-rated restaurants in customer's city."

    profile = {
        "identity": cust_info,
        "metrics": {
            "Total_Orders": total_orders,
            "Total_Spent": total_spent,
            "AOV": aov,
            "First_Order": cust_orders["order_datetime"].min() if total_orders > 0 else "N/A",
            "Last_Order": cust_orders["order_datetime"].max() if total_orders > 0 else "N/A"
        },
        "intelligence": {
            "RFM_Segment": rfm_segment,
            "Estimated_CLV": est_clv,
            "CLV_Segment": clv_segment,
            "Churn_Probability": churn_prob,
            "Churn_Risk": churn_risk
        },
        "recommendation": recommendation
    }

    return profile
