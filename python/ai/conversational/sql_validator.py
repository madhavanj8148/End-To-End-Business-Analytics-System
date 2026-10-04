"""
Phase 5 — SQL Validator
-----------------------
Provides safety checks to ensure generated SQL is read-only and
does not expose or modify sensitive data.
"""

import re

def validate_sql(sql_query: str) -> bool:
    """
    Validates that a SQL query is safe to execute.
    Must only allow SELECT / WITH / read operations.
    """
    query = sql_query.lower().strip()
    
    # Must start with SELECT or WITH
    if not (query.startswith("select") or query.startswith("with")):
        return False
        
    # Forbidden keywords (Data Manipulation & Definition)
    forbidden = [
        r"\bdrop\b", r"\bdelete\b", r"\bupdate\b", r"\binsert\b",
        r"\balter\b", r"\btruncate\b", r"\bgrant\b", r"\brevoke\b",
        r"\bcommit\b", r"\brollback\b", r"\bexec\b", r"\bexecute\b"
    ]
    
    for pattern in forbidden:
        if re.search(pattern, query):
            return False
            
    return True
