"""
Phase 6 — Scenario Comparator
-----------------------------
Compares multiple scenarios and highlights the best outcomes.
"""

def compare_scenarios(baseline_results: dict, scenarios: list) -> dict:
    """
    Takes baseline results and a list of scenario run results,
    returns a comparative matrix.
    """
    comparison = {}
    
    # Simple extraction for demo comparison
    # In reality, this would iterate through the scenarios array and build a pandas DataFrame
    
    best_revenue = None
    max_rev = -99999999
    
    for sc in scenarios:
        rev_impact = sc["results"]["financial"]["impact"]["Platform_Revenue_Diff"]
        if rev_impact > max_rev:
            max_rev = rev_impact
            best_revenue = sc["scenario_name"]
            
    comparison["Best_Revenue_Scenario"] = best_revenue
    
    return comparison
