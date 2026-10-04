"""
Phase 6 — Validation for Scenario Parameters
--------------------------------------------
Ensures scenario parameters remain within logically valid bounds.
"""

def validate_scenario_parameters(params: dict) -> dict:
    """
    Validates and bounds scenario parameters. Returns the sanitized dictionary.
    """
    validated = {}
    
    # Pricing
    validated["aov_change_pct"] = max(-50.0, min(100.0, params.get("aov_change_pct", 0.0)))
    validated["delivery_fee_change_pct"] = max(-100.0, min(200.0, params.get("delivery_fee_change_pct", 0.0)))
    
    # Promotion
    validated["discount_change_pct"] = max(-100.0, min(100.0, params.get("discount_change_pct", 0.0)))
    
    # Demand
    validated["demand_change_pct"] = max(-50.0, min(200.0, params.get("demand_change_pct", 0.0)))
    
    # Customer
    validated["retention_change_pct"] = max(-50.0, min(50.0, params.get("retention_change_pct", 0.0)))
    validated["churn_reduction_pct"] = max(0.0, min(100.0, params.get("churn_reduction_pct", 0.0)))
    validated["customer_acquisition_pct"] = max(-50.0, min(100.0, params.get("customer_acquisition_pct", 0.0)))
    
    # Operations
    validated["rider_capacity_change_pct"] = max(-50.0, min(100.0, params.get("rider_capacity_change_pct", 0.0)))
    validated["delivery_time_change_pct"] = max(-50.0, min(100.0, params.get("delivery_time_change_pct", 0.0)))
    validated["cancellation_rate_change_pct"] = max(-50.0, min(100.0, params.get("cancellation_rate_change_pct", 0.0)))
    
    # Restaurant
    validated["commission_change_pct"] = max(-50.0, min(50.0, params.get("commission_change_pct", 0.0)))
    validated["prep_time_change_pct"] = max(-50.0, min(50.0, params.get("prep_time_change_pct", 0.0)))
    
    return validated
