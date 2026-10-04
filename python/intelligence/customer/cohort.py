"""
Customer Cohort Retention Analysis Engine
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_cohort_matrix(orders_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes Cohort Retention Matrix (Month 0, Month 1, Month 2...)
    Returns (retention_percentage_matrix, cohort_summary_df)
    """
    df = orders_df.copy()
    df["order_datetime"] = pd.to_datetime(df["order_datetime"])
    df["order_month"] = df["order_datetime"].dt.to_period("M")

    # Determine First Order Month per customer
    df["first_order_month"] = df.groupby("customer_id")["order_month"].transform("min")

    # Calculate Period Offset (Month Index 0, 1, 2, ...)
    df["cohort_index"] = (df["order_month"].dt.year - df["first_order_month"].dt.year) * 12 + \
                         (df["order_month"].dt.month - df["first_order_month"].dt.month)

    cohort_data = df.groupby(["first_order_month", "cohort_index"])["customer_id"].nunique().reset_index()

    cohort_pivot = cohort_data.pivot(index="first_order_month", columns="cohort_index", values="customer_id")
    cohort_sizes = cohort_pivot.iloc[:, 0]

    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0).round(4) * 100

    # Format Index for Display
    retention_matrix.index = retention_matrix.index.astype(str)

    cohort_summary = df.groupby("first_order_month").agg(
        Cohort_Size=("customer_id", "nunique"),
        Total_Orders=("order_id", "count"),
        Total_Revenue=("final_amount", "sum")
    ).reset_index()
    cohort_summary["first_order_month"] = cohort_summary["first_order_month"].astype(str)

    return retention_matrix, cohort_summary
