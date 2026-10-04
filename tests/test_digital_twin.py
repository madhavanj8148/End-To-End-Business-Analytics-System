"""
Unit Tests for Phase 7: Digital Twin
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "python"))

from digital_twin.twin_engine import build_digital_twin_state
from digital_twin.twin_dependencies import get_impact_chain

def mock_data():
    orders = pd.DataFrame({
        "order_id": [1, 2],
        "customer_id": ["C1", "C2"],
        "restaurant_id": ["R1", "R2"],
        "order_amount": [100.0, 150.0],
        "discount_amount": [10.0, 0.0],
        "delivery_fee": [20.0, 20.0]
    })
    customers = pd.DataFrame({"customer_id": ["C1", "C2", "C3"]})
    restaurants = pd.DataFrame({"restaurant_id": ["R1", "R2"]})
    
    return {
        "orders": orders,
        "customers": customers,
        "restaurants": restaurants
    }

def test_twin_state_creation():
    data = mock_data()
    twin = build_digital_twin_state(data)
    
    assert twin.timestamp is not None
    assert twin.financial_state["Gross_Revenue"] == 250.0
    assert twin.financial_state["Discounts"] == 10.0
    assert twin.customer_state["Total_Customers"] == 3
    assert twin.customer_state["Active_Customers"] == 2
    assert twin.restaurant_state["Total_Restaurants"] == 2
    print("test_twin_state_creation PASSED")

def test_health_score():
    data = mock_data()
    twin = build_digital_twin_state(data)
    # With this mock data, margin = (250*0.2 + 40 - 10) / 250 = 80 / 250 = 32% (healthy)
    assert twin.financial_state["Business_Health_Score"] >= 85
    print("test_health_score PASSED")

def test_alert_generation():
    data = mock_data()
    twin = build_digital_twin_state(data)
    alerts = twin.alerts
    assert len(alerts) > 0
    assert alerts[0]["Category"] == "System" # Healthy system fallback
    print("test_alert_generation PASSED")

def test_dependencies():
    chain = get_impact_chain("demand_spike")
    assert "Demand Increase" in chain[0]
    print("test_dependencies PASSED")

if __name__ == "__main__":
    test_twin_state_creation()
    test_health_score()
    test_alert_generation()
    test_dependencies()
    print("ALL TESTS PASSED")
