"""
Phase 6 — Financial Simulator
-----------------------------
Simulates financial impact of decision scenarios on revenue, profit, and margins.
"""

import pandas as pd

def simulate_financials(orders_df: pd.DataFrame, scenario_params: dict) -> dict:
    """
    Simulates financial metrics based on baseline orders and scenario parameters.
    """
    # Baseline calculations
    base_orders = len(orders_df)
    
    # Handle empty case safely
    if base_orders == 0:
        return _empty_financial_result()

    base_gross_revenue = orders_df['order_amount'].sum()
    base_discount = orders_df['discount_amount'].sum()
    base_delivery_fee = orders_df['delivery_fee'].sum()
    
    # Assume 20% average commission if not explicitly in data
    base_commission_rate = 0.20
    base_commission_revenue = base_gross_revenue * base_commission_rate
    
    base_platform_revenue = base_commission_revenue + base_delivery_fee - base_discount
    base_aov = base_gross_revenue / base_orders
    base_margin = (base_platform_revenue / base_gross_revenue) if base_gross_revenue > 0 else 0
    
    # Apply scenario parameters
    aov_mult = 1.0 + (scenario_params.get("aov_change_pct", 0) / 100.0)
    demand_mult = 1.0 + (scenario_params.get("demand_change_pct", 0) / 100.0)
    discount_mult = 1.0 + (scenario_params.get("discount_change_pct", 0) / 100.0)
    fee_mult = 1.0 + (scenario_params.get("delivery_fee_change_pct", 0) / 100.0)
    comm_mult = 1.0 + (scenario_params.get("commission_change_pct", 0) / 100.0)
    
    # Simulated calculations
    sim_orders = int(base_orders * demand_mult)
    sim_aov = base_aov * aov_mult
    sim_gross_revenue = sim_orders * sim_aov
    
    # Average discount and fee per order, then multiply by new demand and their specific multipliers
    avg_discount = (base_discount / base_orders) * discount_mult if base_orders > 0 else 0
    avg_fee = (base_delivery_fee / base_orders) * fee_mult if base_orders > 0 else 0
    
    sim_discount = sim_orders * avg_discount
    sim_delivery_fee = sim_orders * avg_fee
    
    sim_commission_rate = base_commission_rate * comm_mult
    sim_commission_revenue = sim_gross_revenue * sim_commission_rate
    
    sim_platform_revenue = sim_commission_revenue + sim_delivery_fee - sim_discount
    sim_margin = (sim_platform_revenue / sim_gross_revenue) if sim_gross_revenue > 0 else 0
    
    return {
        "baseline": {
            "Orders": base_orders,
            "AOV": base_aov,
            "Gross_Revenue": base_gross_revenue,
            "Discount_Cost": base_discount,
            "Delivery_Fee_Revenue": base_delivery_fee,
            "Platform_Revenue": base_platform_revenue,
            "Profit_Margin": base_margin
        },
        "simulated": {
            "Orders": sim_orders,
            "AOV": sim_aov,
            "Gross_Revenue": sim_gross_revenue,
            "Discount_Cost": sim_discount,
            "Delivery_Fee_Revenue": sim_delivery_fee,
            "Platform_Revenue": sim_platform_revenue,
            "Profit_Margin": sim_margin
        },
        "impact": {
            "Orders_Diff": sim_orders - base_orders,
            "Platform_Revenue_Diff": sim_platform_revenue - base_platform_revenue,
            "Margin_Diff": sim_margin - base_margin
        }
    }

def _empty_financial_result():
    return {
        "baseline": {"Orders": 0, "AOV": 0, "Gross_Revenue": 0, "Discount_Cost": 0, "Delivery_Fee_Revenue": 0, "Platform_Revenue": 0, "Profit_Margin": 0},
        "simulated": {"Orders": 0, "AOV": 0, "Gross_Revenue": 0, "Discount_Cost": 0, "Delivery_Fee_Revenue": 0, "Platform_Revenue": 0, "Profit_Margin": 0},
        "impact": {"Orders_Diff": 0, "Platform_Revenue_Diff": 0, "Margin_Diff": 0}
    }
