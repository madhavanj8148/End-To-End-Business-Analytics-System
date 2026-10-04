"""
Phase 7 — Twin Dependency Graph
-------------------------------
Represents the business impact chains programmatically.
"""

def get_impact_chain(event_type: str) -> list:
    """
    Returns the sequence of downstream impacts for a given event.
    """
    chains = {
        "demand_spike": [
            "Demand Increase",
            "Rider Capacity Pressure",
            "Higher Delivery Time",
            "Late Deliveries",
            "Customer Satisfaction Risk",
            "Potential Retention Impact"
        ],
        "high_discount": [
            "High Discount Usage",
            "Lower Net Revenue",
            "Margin Compression",
            "Potential Revenue Leakage"
        ],
        "restaurant_churn": [
            "Restaurant Churn",
            "Lower Local Variety",
            "Customer Order Frequency Drop",
            "Revenue Decline"
        ]
    }
    
    return chains.get(event_type, ["Event", "Direct Business Impact"])
