"""
Phase 5 — AI Query Router
-------------------------
Classifies the user's natural language query intent to determine
if it needs NL2SQL, Root Cause Analysis, or General Insight generation.
"""

def route_query(user_input: str) -> str:
    """
    Returns the intent of the user's query: 'NL2SQL', 'ROOT_CAUSE', or 'GENERAL'.
    """
    query = user_input.lower()
    
    root_cause_keywords = ["why", "what caused", "reason", "drop", "spike", "increase", "decrease"]
    sql_keywords = ["how many", "show me", "list", "top", "average", "total", "count", "revenue", "orders"]
    simulation_keywords = ["what if", "simulate", "scenario", "if we change", "compare", "what happens if"]
    
    # Simple heuristic routing
    if any(kw in query for kw in simulation_keywords):
        return "SIMULATION"
    elif any(kw in query for kw in root_cause_keywords) and "why" in query:
        return "ROOT_CAUSE"
    elif any(kw in query for kw in sql_keywords):
        return "NL2SQL"
    else:
        return "GENERAL"
