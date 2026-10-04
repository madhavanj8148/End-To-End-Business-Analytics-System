"""
Phase 8 — Final Test Runner & Validation
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "python"))

from ai.conversational.sql_validator import validate_sql
from digital_twin.twin_engine import build_digital_twin_state
import pandas as pd

class TestNovaNestPlatform(unittest.TestCase):
    
    def test_sql_safety_validator(self):
        """Tests that dangerous SQL queries are blocked and safe ones pass."""
        safe_queries = [
            "SELECT * FROM orders;",
            "WITH cte AS (SELECT * FROM customers) SELECT * FROM cte;",
            "select sum(order_amount) from orders where status='DELIVERED'"
        ]
        dangerous_queries = [
            "DROP TABLE customers;",
            "DELETE FROM orders WHERE id=1;",
            "UPDATE restaurants SET rating=5.0;",
            "INSERT INTO customers (id) VALUES (1);",
            "ALTER TABLE orders DROP COLUMN amount;",
            "TRUNCATE TABLE deliveries;",
            "GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';",
            "REVOKE ALL PRIVILEGES ON *.* FROM 'user'@'localhost';"
        ]
        
        for q in safe_queries:
            self.assertTrue(validate_sql(q), f"Safe query blocked: {q}")
            
        for q in dangerous_queries:
            self.assertFalse(validate_sql(q), f"Dangerous query allowed: {q}")
            
    def test_digital_twin_empty_dataframe(self):
        """Tests that the twin engine handles empty dataframes gracefully."""
        empty_data = {
            "orders": pd.DataFrame(),
            "customers": pd.DataFrame(),
            "restaurants": pd.DataFrame()
        }
        twin = build_digital_twin_state(empty_data)
        self.assertIsNotNone(twin)
        
    def test_digital_twin_missing_dataframe(self):
        """Tests that the twin engine handles missing keys safely."""
        missing_data = {
            "orders": pd.DataFrame()
            # missing others
        }
        twin = build_digital_twin_state(missing_data)
        self.assertIsNotNone(twin)

if __name__ == "__main__":
    unittest.main()
