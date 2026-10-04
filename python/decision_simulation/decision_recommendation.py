"""
Phase 6 — Decision Recommendation Engine
----------------------------------------
Converts simulation outputs into actionable recommendations.
"""

def generate_recommendation(scenario_name: str, fin_results: dict, cust_results: dict, ops_results: dict) -> dict:
    """
    Analyzes simulated impacts and generates a business recommendation.
    """
    profit_impact = fin_results["impact"]["Margin_Diff"]
    revenue_impact = fin_results["impact"]["Platform_Revenue_Diff"]
    churn_impact = cust_results["impact"]["Churn_Reduction"]
    sla_impact = ops_results["impact"]["SLA_Diff_Pct"]
    
    # Build recommendation text based on strongest signals
    benefits = []
    risks = []
    
    if profit_impact > 0.02:
        benefits.append(f"Significant profit margin improvement of {(profit_impact*100):.1f}%.")
    elif profit_impact < -0.02:
        risks.append(f"Severe profit margin compression of {(profit_impact*100):.1f}%.")
        
    if revenue_impact > 0:
        benefits.append("Positive overall platform revenue growth.")
    elif revenue_impact < 0:
        risks.append("Estimated decline in total platform revenue.")
        
    if churn_impact > 0:
        benefits.append("Reduces customer churn.")
    elif churn_impact < 0:
        risks.append("Increases customer churn risk.")
        
    if sla_impact < -0.05:
        risks.append("Operational degradation: SLA compliance drops noticeably.")
        
    if not benefits:
        benefits.append("No clear dominant business benefit.")
    if not risks:
        risks.append("No major risks detected.")
        
    # Decide
    decision = "PROCEED WITH CAUTION"
    if profit_impact > 0 and revenue_impact > 0 and sla_impact >= -0.02:
        decision = "HIGHLY RECOMMENDED"
    elif profit_impact < 0 and revenue_impact < 0:
        decision = "NOT RECOMMENDED"
        
    return {
        "Decision": decision,
        "Expected_Benefit": " ".join(benefits),
        "Main_Risk": " ".join(risks),
        "Confidence": "Moderate (Based on deterministic linear simulation)"
    }
