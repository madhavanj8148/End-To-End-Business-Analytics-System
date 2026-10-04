"""
NovaNest Feature Engineering Module
------------------------------------
Reads cleaned order and restaurant datasets to derive high-value features
for analytics, machine learning, and business intelligence.

Profit Calculation Methodology:
- Platform Estimated Profit is dynamically calculated using restaurant-specific commission:
    Platform Revenue = (Order Amount * Restaurant Commission %) + Delivery Fee
    Net Profit = Platform Revenue - Discount Amount (borne by platform)
  If restaurant data is unavailable, falls back to standard 20% platform commission assumption.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"
ENGINEERED_DIR.mkdir(parents=True, exist_ok=True)

print("Loading cleaned datasets for feature engineering...")
orders = pd.read_csv(CLEANED_DIR / "orders.csv")
restaurants = pd.read_csv(CLEANED_DIR / "restaurants.csv")

# Parse Datetime
orders["order_datetime"] = pd.to_datetime(orders["order_datetime"])

# 1. Hour of Day
orders["hour"] = orders["order_datetime"].dt.hour

# 2. Peak Hour Flag (Lunch: 12-14, Dinner: 18-21)
orders["peak_hour_flag"] = np.where(
    orders["hour"].between(12, 14) | orders["hour"].between(18, 21),
    1,
    0
)

# 3. Weekend Flag (Saturday=5, Sunday=6)
orders["weekend_flag"] = np.where(orders["order_datetime"].dt.dayofweek >= 5, 1, 0)

# 4. Cancellation Flag
orders["cancellation_flag"] = np.where(orders["order_status"] == "Cancelled", 1, 0)

# 5. Discount Percentage
orders["discount_percentage"] = np.where(
    orders["order_amount"] > 0,
    ((orders["discount_amount"] / orders["order_amount"]) * 100).round(2),
    0.0
)

# 6. Dynamic Estimated Platform Profit
# Merge restaurant commission percentage
orders = orders.merge(
    restaurants[["restaurant_id", "commission_percentage"]],
    on="restaurant_id",
    how="left"
)
orders["commission_percentage"] = orders["commission_percentage"].fillna(20.0)

# Platform Revenue = (order_amount * commission %) + delivery_fee
# Net Profit = Platform Revenue - discount_amount
orders["estimated_profit"] = (
    (orders["order_amount"] * (orders["commission_percentage"] / 100.0))
    + orders["delivery_fee"]
    - orders["discount_amount"]
).round(2)

# Drop temporary merge column for clean output schema
orders.drop(columns=["commission_percentage"], inplace=True)

# 7. Order Size Binning
orders["order_size"] = pd.cut(
    orders["final_amount"],
    bins=[0, 300, 750, 100000],
    labels=["Small", "Medium", "Large"]
)

# 8. Extra Derived Features
orders["order_month"] = orders["order_datetime"].dt.strftime("%Y-%m")
orders["day_of_week"] = orders["order_datetime"].dt.day_name()
orders["is_net_positive_profit"] = np.where(orders["estimated_profit"] > 0, 1, 0)

output_file = ENGINEERED_DIR / "orders_engineered.csv"
orders.to_csv(output_file, index=False)
print(f"Engineered dataset created with {len(orders)} rows and {len(orders.columns)} columns -> {output_file}")