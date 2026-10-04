"""
Phase 5 — AI Query Executor
---------------------------
Executes validated SQL queries against the database and returns the results.
"""

import pandas as pd
import logging
import sys
from pathlib import Path

# Add streamlit_app to path to access database connection
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent / "streamlit_app"))
try:
    from database.connection import get_db_connection
except ImportError:
    get_db_connection = None

logger = logging.getLogger(__name__)

def execute_query(sql_query: str) -> pd.DataFrame:
    """
    Executes a safe SQL query and returns a pandas DataFrame.
    """
    if not sql_query:
        return pd.DataFrame()
        
    try:
        if get_db_connection:
            conn, _ = get_db_connection()
            if conn:
                df = pd.read_sql(sql_query, conn)
                conn.close()
                return df
        
        # If MySQL connection is unavailable, return empty dataframe
        logger.warning("Database connection unavailable for AI SQL execution.")
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Failed to execute AI SQL query: {e}")
        return pd.DataFrame()
