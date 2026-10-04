"""
Phase 7 — Digital Twin State
----------------------------
Represents the current unified analytical state of NovaNest.
"""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class TwinState:
    """Unified snapshot of the business at a point in time."""
    timestamp: str
    
    # Core States
    customer_state: Dict[str, Any] = field(default_factory=dict)
    restaurant_state: Dict[str, Any] = field(default_factory=dict)
    operations_state: Dict[str, Any] = field(default_factory=dict)
    financial_state: Dict[str, Any] = field(default_factory=dict)
    
    # Intelligence States
    ai_state: Dict[str, Any] = field(default_factory=dict)
    simulation_state: Dict[str, Any] = field(default_factory=dict)
    
    # Unified Alerts & Recommendations
    alerts: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "customer_state": self.customer_state,
            "restaurant_state": self.restaurant_state,
            "operations_state": self.operations_state,
            "financial_state": self.financial_state,
            "ai_state": self.ai_state,
            "simulation_state": self.simulation_state,
            "alerts": self.alerts,
            "recommendations": self.recommendations
        }
