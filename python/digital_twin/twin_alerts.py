"""
Phase 7 — Twin Alert Engine
---------------------------
Aggregates and prioritizes cross-domain business alerts.
"""

def generate_twin_alerts(fin_metrics: dict, ops_metrics: dict, cust_metrics: dict) -> list:
    """
    Generates unified business health alerts.
    """
    alerts = []
    
    if fin_metrics.get("Profit_Margin", 0) < 0.05:
        alerts.append({
            "Severity": "Critical",
            "Category": "Financial",
            "Entity": "Platform",
            "Signal": "Margin Compression",
            "Business_Impact": "Severe risk of operating at a net loss.",
            "Recommended_Action": "Immediate reduction in discount budgets or restructuring of delivery fees."
        })
        
    if fin_metrics.get("Revenue_Leakage_Est", 0) > (fin_metrics.get("Gross_Revenue", 1) * 0.10):
        alerts.append({
            "Severity": "High",
            "Category": "Financial",
            "Entity": "Discounts",
            "Signal": "High Revenue Leakage",
            "Business_Impact": "Discounting exceeds 10% of gross revenue, harming unit economics.",
            "Recommended_Action": "Audit promotion targeting algorithms."
        })
        
    if ops_metrics.get("Late_Deliveries", 0) > (ops_metrics.get("Total_Orders", 1) * 0.10):
        alerts.append({
            "Severity": "High",
            "Category": "Operations",
            "Entity": "Fleet",
            "Signal": "High Late Delivery Ratio",
            "Business_Impact": "Customer satisfaction drop and likely refund spikes.",
            "Recommended_Action": "Increase active rider allocation immediately."
        })
        
    if not alerts:
        alerts.append({
            "Severity": "Informational",
            "Category": "System",
            "Entity": "Platform",
            "Signal": "Healthy Operations",
            "Business_Impact": "No major risks detected.",
            "Recommended_Action": "Maintain current operational parameters."
        })
        
    return alerts
