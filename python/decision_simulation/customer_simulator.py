"""
Phase 6 — Customer Impact Simulator
-----------------------------------
Simulates the impact of decisions on customer retention, churn, and active base.
"""

import pandas as pd

def simulate_customer_impact(customers_df: pd.DataFrame, scenario_params: dict) -> dict:
    """
    Estimates changes to customer retention and active base.
    """
    base_customers = len(customers_df)
    
    if base_customers == 0:
        return _empty_customer_result()
        
    # Assume a baseline average monthly churn of 15% if no historical data is passed
    # In a fully connected app, this might come from the Phase 3 ML churn model outputs.
    base_churn_rate = 0.15 
    base_churned = int(base_customers * base_churn_rate)
    base_retained = base_customers - base_churned
    
    # Apply scenario parameters
    # E.g. retention improvement of +5% means churn decreases
    retention_mult = 1.0 + (scenario_params.get("retention_change_pct", 0) / 100.0)
    churn_reduction = scenario_params.get("churn_reduction_pct", 0) / 100.0
    acq_mult = 1.0 + (scenario_params.get("customer_acquisition_pct", 0) / 100.0)
    
    sim_churn_rate = base_churn_rate * (1.0 - churn_reduction)
    # Retention improvement can act as a secondary buffer against churn
    sim_churn_rate = sim_churn_rate / retention_mult
    
    sim_churned = int(base_customers * sim_churn_rate)
    sim_retained = base_customers - sim_churned
    
    # Assume average acquisition is 20% of base normally
    base_acquired = int(base_customers * 0.20)
    sim_acquired = int(base_acquired * acq_mult)
    
    sim_total_active = sim_retained + sim_acquired
    base_total_active = base_retained + base_acquired
    
    return {
        "baseline": {
            "Total_Customers": base_customers,
            "Churn_Rate": base_churn_rate,
            "Churned_Customers": base_churned,
            "Retained_Customers": base_retained,
            "New_Acquisitions": base_acquired,
            "Ending_Active_Base": base_total_active
        },
        "simulated": {
            "Total_Customers": base_customers,
            "Churn_Rate": sim_churn_rate,
            "Churned_Customers": sim_churned,
            "Retained_Customers": sim_retained,
            "New_Acquisitions": sim_acquired,
            "Ending_Active_Base": sim_total_active
        },
        "impact": {
            "Active_Base_Diff": sim_total_active - base_total_active,
            "Churn_Reduction": base_churned - sim_churned
        }
    }

def _empty_customer_result():
    return {
        "baseline": {"Total_Customers": 0, "Churn_Rate": 0, "Churned_Customers": 0, "Retained_Customers": 0, "New_Acquisitions": 0, "Ending_Active_Base": 0},
        "simulated": {"Total_Customers": 0, "Churn_Rate": 0, "Churned_Customers": 0, "Retained_Customers": 0, "New_Acquisitions": 0, "Ending_Active_Base": 0},
        "impact": {"Active_Base_Diff": 0, "Churn_Reduction": 0}
    }
