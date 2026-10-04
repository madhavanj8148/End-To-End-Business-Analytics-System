"""
Phase 6 — Scenario Engine
-------------------------
Coordinates the sub-simulators to produce a complete Scenario run.
"""

from .validation import validate_scenario_parameters
from .financial_simulator import simulate_financials
from .customer_simulator import simulate_customer_impact
from .restaurant_simulator import simulate_restaurant_impact
from .operations_simulator import simulate_operations
from .decision_recommendation import generate_recommendation

def run_scenario(scenario_name: str, params: dict, data_dict: dict) -> dict:
    """
    Executes a full scenario simulation across all domains.
    data_dict contains the loaded dataframes: 'orders', 'customers', 'restaurants'.
    """
    # 1. Validate inputs
    validated_params = validate_scenario_parameters(params)
    
    # 2. Run simulators
    orders_df = data_dict.get('orders')
    customers_df = data_dict.get('customers')
    restaurants_df = data_dict.get('restaurants')
    
    financial_results = simulate_financials(orders_df, validated_params)
    customer_results = simulate_customer_impact(customers_df, validated_params)
    restaurant_results = simulate_restaurant_impact(restaurants_df, orders_df, validated_params)
    ops_results = simulate_operations(orders_df, validated_params)
    
    # 3. Generate Decision Recommendation
    recommendation = generate_recommendation(
        scenario_name,
        financial_results,
        customer_results,
        ops_results
    )
    
    return {
        "scenario_name": scenario_name,
        "parameters": validated_params,
        "results": {
            "financial": financial_results,
            "customer": customer_results,
            "restaurant": restaurant_results,
            "operations": ops_results
        },
        "recommendation": recommendation
    }
