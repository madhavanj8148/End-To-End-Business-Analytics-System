"""
Cached Data Loader for NovaNest Streamlit Application
"""

from pathlib import Path
import pandas as pd
import streamlit as st
from database.connection import get_db_connection

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"

@st.cache_data(ttl=3600)
def load_all_datasets():
    """
    Loads all datasets cleanly with caching.
    Tries MySQL database first; falls back to CSV file store seamlessly.
    """
    conn, source_type = get_db_connection()
    data = {}

    if conn is not None:
        try:
            data["customers"] = pd.read_sql("SELECT * FROM customers", conn)
            data["restaurants"] = pd.read_sql("SELECT * FROM restaurants", conn)
            data["menu_items"] = pd.read_sql("SELECT * FROM menu_items", conn)
            data["riders"] = pd.read_sql("SELECT * FROM riders", conn)
            data["orders"] = pd.read_sql("SELECT * FROM orders", conn)
            data["payments"] = pd.read_sql("SELECT * FROM payments", conn)
            data["deliveries"] = pd.read_sql("SELECT * FROM deliveries", conn)
            data["app_events"] = pd.read_sql("SELECT * FROM app_events", conn)
            data["promotions"] = pd.read_sql("SELECT * FROM promotions", conn)
            data["ratings_reviews"] = pd.read_sql("SELECT * FROM ratings_reviews", conn)
            conn.close()

            # Load engineered datasets from local CSVs
            _load_engineered_csvs(data)
            return data, "MySQL Database"
        except Exception:
            if conn:
                conn.close()

    # Fallback to Cleaned CSVs
    data["customers"] = pd.read_csv(CLEANED_DIR / "customers.csv")
    data["restaurants"] = pd.read_csv(CLEANED_DIR / "restaurants.csv")
    data["menu_items"] = pd.read_csv(CLEANED_DIR / "menu_items.csv")
    data["riders"] = pd.read_csv(CLEANED_DIR / "riders.csv")
    data["orders"] = pd.read_csv(CLEANED_DIR / "orders.csv")
    data["payments"] = pd.read_csv(CLEANED_DIR / "payments.csv")
    data["deliveries"] = pd.read_csv(CLEANED_DIR / "deliveries.csv")
    data["app_events"] = pd.read_csv(CLEANED_DIR / "app_events.csv")
    data["promotions"] = pd.read_csv(CLEANED_DIR / "promotions.csv")
    data["ratings_reviews"] = pd.read_csv(CLEANED_DIR / "ratings_reviews.csv")

    _load_engineered_csvs(data)

    return data, "CSV File Store (Cleaned & Engineered)"

def _load_engineered_csvs(data: dict):
    """
    Safely loads all engineered datasets for Phase 3 and Phase 4.
    """
    csv_map = {
        "orders_engineered": "orders_engineered.csv",
        "customer_churn_predictions": "customer_churn_predictions.csv",
        "restaurant_predictions": "restaurant_predictions.csv",
        "demand_forecasts": "demand_forecasts.csv",
        "demand_heatmap": "demand_heatmap.csv",
        "eta_predictions": "eta_predictions.csv",
        "rider_allocation": "rider_allocation.csv",
        "operational_anomalies": "operational_anomalies.csv",
        "revenue_leakage": "revenue_leakage.csv",
        "operational_alerts": "operational_alerts.csv",
    }

    for key, filename in csv_map.items():
        path = ENGINEERED_DIR / filename
        if path.exists():
            data[key] = pd.read_csv(path)
        else:
            data[key] = pd.DataFrame()
