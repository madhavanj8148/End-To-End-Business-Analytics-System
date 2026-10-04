"""
Phase 6 — Operations Simulator
------------------------------
Simulates delivery operations, ETA, and rider SLA compliance.
"""

import pandas as pd

def simulate_operations(orders_df: pd.DataFrame, scenario_params: dict) -> dict:
    """
    Estimates operational capacity, SLA compliance, and delivery delays.
    """
    base_orders = len(orders_df)
    if base_orders == 0:
        return _empty_ops_result()
        
    # Assume historical averages
    base_avg_eta = 35.0  # minutes
    base_sla_compliance = 0.85 # 85% of orders delivered within target time
    
    # Apply scenario parameters
    delivery_time_mult = 1.0 + (scenario_params.get("delivery_time_change_pct", 0) / 100.0)
    capacity_mult = 1.0 + (scenario_params.get("rider_capacity_change_pct", 0) / 100.0)
    demand_mult = 1.0 + (scenario_params.get("demand_change_pct", 0) / 100.0)
    
    # Calculate simulated metrics
    sim_orders = int(base_orders * demand_mult)
    
    # If demand goes up and capacity goes down, delivery times increase drastically
    # Simple congestion ratio
    congestion_ratio = demand_mult / capacity_mult if capacity_mult > 0 else 1.5
    
    # Simulated ETA considers the manual ETA adjustment + congestion impact
    sim_avg_eta = base_avg_eta * delivery_time_mult * (1.0 + (congestion_ratio - 1.0) * 0.5)
    
    # SLA compliance drops if ETA goes up
    # A simple linear model: for every 10% increase in ETA, SLA drops by 5%
    eta_increase_ratio = sim_avg_eta / base_avg_eta
    sla_penalty = (eta_increase_ratio - 1.0) * 0.5
    sim_sla_compliance = max(0.0, min(1.0, base_sla_compliance - sla_penalty))
    
    return {
        "baseline": {
            "Total_Deliveries": base_orders,
            "Avg_ETA_Mins": base_avg_eta,
            "SLA_Compliance": base_sla_compliance
        },
        "simulated": {
            "Total_Deliveries": sim_orders,
            "Avg_ETA_Mins": sim_avg_eta,
            "SLA_Compliance": sim_sla_compliance
        },
        "impact": {
            "ETA_Diff_Mins": sim_avg_eta - base_avg_eta,
            "SLA_Diff_Pct": sim_sla_compliance - base_sla_compliance
        }
    }

def _empty_ops_result():
    return {
        "baseline": {"Total_Deliveries": 0, "Avg_ETA_Mins": 0, "SLA_Compliance": 0},
        "simulated": {"Total_Deliveries": 0, "Avg_ETA_Mins": 0, "SLA_Compliance": 0},
        "impact": {"ETA_Diff_Mins": 0, "SLA_Diff_Pct": 0}
    }
