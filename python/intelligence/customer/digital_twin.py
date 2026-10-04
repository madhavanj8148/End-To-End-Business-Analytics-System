"""
Customer Digital Twin Object Representation (Foundation)
---------------------------------------------------------
Encapsulates a customer's real-time state, transaction history, analytical intelligence,
and next-best-action triggers into a structured digital twin model.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class CustomerDigitalTwin:
    customer_id: str
    identity: Dict[str, Any]
    behaviour: Dict[str, Any]
    transaction_summary: Dict[str, Any]
    rfm_intelligence: Dict[str, Any]
    clv_intelligence: Dict[str, Any]
    churn_intelligence: Dict[str, Any]
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def create_customer_digital_twin(profile_360: dict) -> CustomerDigitalTwin:
    """Factory function creating a CustomerDigitalTwin instance from 360 profile dict."""
    identity = profile_360.get("identity", {})
    metrics = profile_360.get("metrics", {})
    intel = profile_360.get("intelligence", {})

    twin = CustomerDigitalTwin(
        customer_id=identity.get("customer_id", "UNKNOWN"),
        identity={
            "Name": identity.get("customer_name"),
            "City": identity.get("city"),
            "Persona": identity.get("persona"),
            "Age": identity.get("age"),
            "Subscription": identity.get("subscription_type")
        },
        behaviour={
            "Acquisition_Channel": identity.get("acquisition_channel"),
            "Signup_Date": identity.get("signup_date")
        },
        transaction_summary={
            "Total_Orders": metrics.get("Total_Orders", 0),
            "Total_Spent": metrics.get("Total_Spent", 0.0),
            "AOV": metrics.get("AOV", 0.0),
            "First_Order": metrics.get("First_Order"),
            "Last_Order": metrics.get("Last_Order")
        },
        rfm_intelligence={
            "RFM_Segment": intel.get("RFM_Segment")
        },
        clv_intelligence={
            "Estimated_CLV": intel.get("Estimated_CLV"),
            "CLV_Segment": intel.get("CLV_Segment")
        },
        churn_intelligence={
            "Churn_Probability": intel.get("Churn_Probability"),
            "Churn_Risk": intel.get("Churn_Risk")
        },
        recommended_action=profile_360.get("recommendation", "N/A")
    )
    return twin
