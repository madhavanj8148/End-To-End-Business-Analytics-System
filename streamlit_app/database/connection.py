"""
NovaNest Database Connector with Seamless CSV Fallback
"""

import os
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"

def get_db_connection():
    """Attempts to establish MySQL database connection."""
    try:
        import mysql.connector
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", 3306))
        db_user = os.getenv("DB_USER", "root")
        db_pass = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "novanest")

        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_pass,
            database=db_name,
            connect_timeout=3
        )
        if conn.is_connected():
            return conn, "MySQL Database"
    except Exception:
        pass
    return None, "CSV File Store"
