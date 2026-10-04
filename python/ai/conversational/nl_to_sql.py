"""
Phase 5 — Natural Language to SQL (NL2SQL) Fallback Engine
----------------------------------------------------------
Translates natural language to SQL. Uses pattern matching templates
as a robust fallback when an external LLM provider is unavailable.
"""

import re

# Pre-defined templates mapping intent regex to safe SQL
SQL_TEMPLATES = [
    {
        "pattern": r"top (\d+) restaurants",
        "sql": "SELECT r.restaurant_name, COUNT(o.order_id) as total_orders FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id GROUP BY r.restaurant_name ORDER BY total_orders DESC LIMIT {0};"
    },
    {
        "pattern": r"revenue by city",
        "sql": "SELECT r.city, SUM(o.final_amount) as total_revenue FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id GROUP BY r.city ORDER BY total_revenue DESC;"
    },
    {
        "pattern": r"total orders",
        "sql": "SELECT COUNT(*) as total_orders FROM orders;"
    },
    {
        "pattern": r"average delivery fee",
        "sql": "SELECT AVG(delivery_fee) as avg_delivery_fee FROM orders;"
    }
]

def generate_sql(user_input: str) -> str:
    """
    Attempts to map user input to a predefined SQL template.
    Returns SQL query if matched, else an empty string.
    """
    query = user_input.lower()
    
    for template in SQL_TEMPLATES:
        match = re.search(template["pattern"], query)
        if match:
            # If there are groups (like limit number), format the SQL
            if match.groups():
                return template["sql"].format(*match.groups())
            else:
                return template["sql"]
                
    # Fallback to a safe, default query if it looks like a revenue question
    if "revenue" in query:
        return "SELECT SUM(final_amount) as total_revenue FROM orders;"
        
    return ""
