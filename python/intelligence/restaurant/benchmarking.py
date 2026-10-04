"""
Restaurant Peer Group Benchmarking Engine
------------------------------------------
Calculates city and cuisine peer percentile ranks for revenue, order volume, and ratings.
"""

from pathlib import Path
import pandas as pd
import numpy as np

def calculate_restaurant_benchmarks(health_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes percentile rankings (0-100%) against city and cuisine peer groups.
    """
    df = health_df.copy()

    # Calculate percentile within city cohort
    df["City_Revenue_Percentile"] = (df.groupby("city")["Total_Revenue"].rank(pct=True) * 100).round(1)
    df["City_Order_Percentile"] = (df.groupby("city")["Total_Orders"].rank(pct=True) * 100).round(1)
    df["City_Rating_Percentile"] = (df.groupby("city")["avg_rating"].rank(pct=True) * 100).round(1)

    # Calculate percentile within cuisine cohort
    df["Cuisine_Revenue_Percentile"] = (df.groupby("cuisine_type")["Total_Revenue"].rank(pct=True) * 100).round(1)
    df["Cuisine_Order_Percentile"] = (df.groupby("cuisine_type")["Total_Orders"].rank(pct=True) * 100).round(1)

    # Overall Platform Benchmark Percentile
    df["Overall_Percentile"] = (df["Health_Score"].rank(pct=True) * 100).round(1)

    return df
