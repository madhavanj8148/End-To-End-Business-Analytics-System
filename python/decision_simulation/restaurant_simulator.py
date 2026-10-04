"""
Phase 6 — Restaurant Simulator
------------------------------
Simulates restaurant revenue, volume, and health metrics.
"""

import pandas as pd

def simulate_restaurant_impact(restaurants_df: pd.DataFrame, orders_df: pd.DataFrame, scenario_params: dict) -> dict:
    base_restaurants = len(restaurants_df)
    
    if base_restaurants == 0 or len(orders_df) == 0:
        return _empty_rest_result()
        
    base_gross_revenue = orders_df['order_amount'].sum()
    base_commission_rate = 0.20
    base_commission = base_gross_revenue * base_commission_rate
    base_restaurant_revenue = base_gross_revenue - base_commission
    
    # Apply scenario parameters
    aov_mult = 1.0 + (scenario_params.get("aov_change_pct", 0) / 100.0)
    demand_mult = 1.0 + (scenario_params.get("demand_change_pct", 0) / 100.0)
    comm_mult = 1.0 + (scenario_params.get("commission_change_pct", 0) / 100.0)
    
    sim_gross_revenue = base_gross_revenue * demand_mult * aov_mult
    sim_commission_rate = base_commission_rate * comm_mult
    sim_commission = sim_gross_revenue * sim_commission_rate
    sim_restaurant_revenue = sim_gross_revenue - sim_commission
    
    return {
        "baseline": {
            "Active_Restaurants": base_restaurants,
            "Total_Restaurant_Revenue": base_restaurant_revenue,
            "Avg_Platform_Commission": base_commission_rate
        },
        "simulated": {
            "Active_Restaurants": base_restaurants,
            "Total_Restaurant_Revenue": sim_restaurant_revenue,
            "Avg_Platform_Commission": sim_commission_rate
        },
        "impact": {
            "Revenue_Diff": sim_restaurant_revenue - base_restaurant_revenue,
            "Commission_Rate_Diff": sim_commission_rate - base_commission_rate
        }
    }

def _empty_rest_result():
    return {
        "baseline": {"Active_Restaurants": 0, "Total_Restaurant_Revenue": 0, "Avg_Platform_Commission": 0},
        "simulated": {"Active_Restaurants": 0, "Total_Restaurant_Revenue": 0, "Avg_Platform_Commission": 0},
        "impact": {"Revenue_Diff": 0, "Commission_Rate_Diff": 0}
    }
