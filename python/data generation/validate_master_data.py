import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from constants import CITIES, PERSONAS, CUISINES, RESTAURANT_TYPES, VEHICLE_TYPES

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"

datasets_info = {
    "customers": ("customers.csv", "customer_id"),
    "restaurants": ("restaurants.csv", "restaurant_id"),
    "menu_items": ("menu_items.csv", "item_id"),
    "riders": ("riders.csv", "rider_id"),
    "orders": ("orders.csv", "order_id"),
    "payments": ("payments.csv", "payment_id"),
    "deliveries": ("deliveries.csv", "delivery_id"),
    "app_events": ("app_events.csv", "event_id"),
    "promotions": ("promotions.csv", "promo_id"),
    "ratings_reviews": ("ratings_reviews.csv", "review_id")
}

print("==================================================")
print("       NOVANEST MASTER DATA QUALITY REPORT        ")
print("==================================================")

total_score = 0
num_datasets = len(datasets_info)

# Pre-load primary keys for foreign key validation
pk_maps = {}
for name, (fname, pk) in datasets_info.items():
    if (CLEANED_DIR / fname).exists():
        df_temp = pd.read_csv(CLEANED_DIR / fname)
        pk_maps[name] = set(df_temp[pk].dropna())

for name, (fname, pk) in datasets_info.items():
    file_path = CLEANED_DIR / fname
    if not file_path.exists():
        print(f"\n[ERROR] File {fname} missing!")
        continue

    df = pd.read_csv(file_path)
    rows = len(df)
    cols = len(df.columns)

    dups = df.duplicated(subset=[pk]).sum()
    nulls = df.isnull().sum().sum()

    # Rule checks
    rule_violations = 0

    if name == "customers":
        rule_violations += (~df["city"].isin(CITIES)).sum()
        rule_violations += (~df["persona"].isin(PERSONAS)).sum()
        rule_violations += ((df["age"] < 18) | (df["age"] > 100)).sum()
    elif name == "restaurants":
        rule_violations += (~df["city"].isin(CITIES)).sum()
        rule_violations += (~df["cuisine_type"].isin(CUISINES)).sum()
        rule_violations += ((df["avg_rating"] < 1.0) | (df["avg_rating"] > 5.0)).sum()
    elif name == "orders":
        rule_violations += ((df["quantity"] < 1)).sum()
        rule_violations += ((df["final_amount"] < 0)).sum()
        rule_violations += (~df["customer_id"].isin(pk_maps.get("customers", set()))).sum()
        rule_violations += (~df["restaurant_id"].isin(pk_maps.get("restaurants", set()))).sum()
        rule_violations += (~df["rider_id"].isin(pk_maps.get("riders", set()))).sum()
    elif name == "payments":
        rule_violations += (~df["order_id"].isin(pk_maps.get("orders", set()))).sum()
    elif name == "deliveries":
        rule_violations += (~df["order_id"].isin(pk_maps.get("orders", set()))).sum()
        rule_violations += ((df["distance_km"] <= 0)).sum()
        rule_violations += ((df["delivery_duration"] <= 0)).sum()

    # Quality Score Calculation (Start at 100, deduct for errors)
    penalty = (dups * 5) + (nulls * 2) + (rule_violations * 2)
    score = max(0, 100 - penalty)
    total_score += score

    print(f"\nDataset: {fname}")
    print(f"  Rows: {rows:,} | Columns: {cols}")
    print(f"  Duplicate Primary Key ({pk}): {dups}")
    print(f"  Total Null Values: {nulls}")
    print(f"  Business Rule Violations: {rule_violations}")
    print(f"  Quality Score: {score}/100")

overall_avg = round(total_score / num_datasets, 1)
print("\n==================================================")
print(f"  OVERALL PLATFORM DATA QUALITY SCORE: {overall_avg}/100")
print("==================================================")