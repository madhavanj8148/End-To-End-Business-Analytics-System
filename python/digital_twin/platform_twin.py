"""
Phase 7 — Platform Twin
-----------------------
Aggregates the sub-twins to establish the platform's macro state.
"""

from .customer_twin import get_customer_twin_state
from .restaurant_twin import get_restaurant_twin_state
from .operations_twin import get_operations_twin_state
from .financial_twin import get_financial_twin_state

def get_platform_twin_state(data: dict) -> dict:
    orders = data.get("orders")
    customers = data.get("customers")
    restaurants = data.get("restaurants")
    
    return {
        "customer_state": get_customer_twin_state(customers, orders),
        "restaurant_state": get_restaurant_twin_state(restaurants, orders),
        "operations_state": get_operations_twin_state(orders),
        "financial_state": get_financial_twin_state(orders)
    }
