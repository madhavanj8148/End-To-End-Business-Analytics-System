"""
Data Filtering Logic for NovaNest Components
"""

import pandas as pd

def apply_global_filters(orders_df: pd.DataFrame, customers_df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Applies global sidebar filters to the orders dataframe.
    """
    df = orders_df.copy()

    # Merge customer info if city or persona filter is active and column not present
    if "city" not in df.columns or "persona" not in df.columns:
        if "customer_id" in df.columns and "customer_id" in customers_df.columns:
            df = df.merge(customers_df[["customer_id", "city", "persona"]], on="customer_id", how="left")

    if filters.get("city") and filters["city"] != "All":
        df = df[df["city"] == filters["city"]]

    if filters.get("persona") and filters["persona"] != "All":
        df = df[df["persona"] == filters["persona"]]

    if filters.get("status") and filters["status"] != "All":
        df = df[df["order_status"] == filters["status"]]

    return df
