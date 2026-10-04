"""
Phase 7 — Digital Twin Engine
-----------------------------
Orchestrates the creation of the unified analytical Digital Twin State.
"""

from datetime import datetime
from typing import Dict, Any

from .twin_state import TwinState
from .customer_twin import get_customer_twin_state
from .restaurant_twin import get_restaurant_twin_state
from .operations_twin import get_operations_twin_state
from .financial_twin import get_financial_twin_state
from .twin_alerts import generate_twin_alerts
from .validation import validate_twin_inputs

def build_digital_twin_state(data: Dict[str, Any]) -> TwinState:
    """
    Builds the current analytical digital twin state from the raw/engineered datasets.
    """
    orders_df = data.get("orders")
    customers_df = data.get("customers")
    restaurants_df = data.get("restaurants")
    
    # Check if essential data is missing
    if not validate_twin_inputs(data):
        return TwinState(timestamp=datetime.now().isoformat())
        
    fin_state = get_financial_twin_state(orders_df)
    cust_state = get_customer_twin_state(customers_df, orders_df)
    rest_state = get_restaurant_twin_state(restaurants_df, orders_df)
    ops_state = get_operations_twin_state(orders_df)
    
    alerts = generate_twin_alerts(fin_state, ops_state, cust_state)
    
    # Calculate Business Health Score (0-100)
    health_score = 100
    if fin_state["Profit_Margin"] < 0.10: health_score -= 15
    if ops_state["Late_Deliveries"] > (ops_state["Total_Orders"] * 0.10): health_score -= 15
    if fin_state["Revenue_Leakage_Est"] > (fin_state["Gross_Revenue"] * 0.10): health_score -= 10
    
    fin_state["Business_Health_Score"] = max(0, health_score)
    
    return TwinState(
        timestamp=datetime.now().isoformat(),
        financial_state=fin_state,
        customer_state=cust_state,
        restaurant_state=rest_state,
        operations_state=ops_state,
        alerts=alerts
    )
