import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).resolve().parent / "data generation"))
from constants import CITIES, PERSONAS, CUISINES, RESTAURANT_TYPES, VEHICLE_TYPES

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)

print("==================================================")
print("     NOVANEST DATA CLEANING PIPELINE STARTED      ")
print("==================================================")

# 1. Clean Customers
print("\n[1/10] Cleaning customers.csv...")
df_customers = pd.read_csv(RAW_DIR / "customers.csv")
orig_len = len(df_customers)
df_customers.drop_duplicates(subset=["customer_id"], inplace=True)

# Trim text strings
for col in ["customer_name", "city", "persona", "occupation", "subscription_type", "acquisition_channel"]:
    df_customers[col] = df_customers[col].astype(str).str.strip()

# Validate categories and ranges
df_customers["age"] = df_customers["age"].clip(lower=18, upper=100)
df_customers = df_customers[df_customers["city"].isin(CITIES)]
df_customers = df_customers[df_customers["persona"].isin(PERSONAS)]
df_customers["signup_date"] = pd.to_datetime(df_customers["signup_date"], errors="coerce").dt.strftime("%Y-%m-%d")
df_customers.dropna(subset=["customer_id", "signup_date"], inplace=True)

df_customers.to_csv(CLEANED_DIR / "customers.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_customers)} records saved to cleaned/customers.csv")

# 2. Clean Restaurants
print("\n[2/10] Cleaning restaurants.csv...")
df_restaurants = pd.read_csv(RAW_DIR / "restaurants.csv")
orig_len = len(df_restaurants)
df_restaurants.drop_duplicates(subset=["restaurant_id"], inplace=True)

for col in ["restaurant_name", "city", "restaurant_type", "cuisine_type"]:
    df_restaurants[col] = df_restaurants[col].astype(str).str.strip()

df_restaurants["avg_rating"] = df_restaurants["avg_rating"].clip(lower=1.0, upper=5.0)
df_restaurants["delivery_radius_km"] = df_restaurants["delivery_radius_km"].clip(lower=0.5, upper=25.0)
df_restaurants["commission_percentage"] = df_restaurants["commission_percentage"].clip(lower=5, upper=40)
df_restaurants = df_restaurants[df_restaurants["city"].isin(CITIES)]
df_restaurants = df_restaurants[df_restaurants["cuisine_type"].isin(CUISINES)]

df_restaurants.to_csv(CLEANED_DIR / "restaurants.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_restaurants)} records saved to cleaned/restaurants.csv")

# 3. Clean Menu Items
print("\n[3/10] Cleaning menu_items.csv...")
df_menu = pd.read_csv(RAW_DIR / "menu_items.csv")
orig_len = len(df_menu)
df_menu.drop_duplicates(subset=["item_id"], inplace=True)

for col in ["cuisine_type", "item_name"]:
    df_menu[col] = df_menu[col].astype(str).str.strip()

df_menu["price"] = df_menu["price"].clip(lower=10)
df_menu["preparation_time"] = df_menu["preparation_time"].clip(lower=5, upper=120)
# Foreign key validation
valid_restaurants = set(df_restaurants["restaurant_id"])
df_menu = df_menu[df_menu["restaurant_id"].isin(valid_restaurants)]

df_menu.to_csv(CLEANED_DIR / "menu_items.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_menu)} records saved to cleaned/menu_items.csv")

# 4. Clean Riders
print("\n[4/10] Cleaning riders.csv...")
df_riders = pd.read_csv(RAW_DIR / "riders.csv")
orig_len = len(df_riders)
df_riders.drop_duplicates(subset=["rider_id"], inplace=True)

for col in ["rider_name", "city", "vehicle_type", "shift_type"]:
    df_riders[col] = df_riders[col].astype(str).str.strip()

df_riders["experience_years"] = df_riders["experience_years"].clip(lower=0, upper=40)
df_riders = df_riders[df_riders["city"].isin(CITIES)]

df_riders.to_csv(CLEANED_DIR / "riders.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_riders)} records saved to cleaned/riders.csv")

# 5. Clean Orders
print("\n[5/10] Cleaning orders.csv...")
df_orders = pd.read_csv(RAW_DIR / "orders.csv")
orig_len = len(df_orders)
df_orders.drop_duplicates(subset=["order_id"], inplace=True)

# Foreign key integrity checks
valid_customers = set(df_customers["customer_id"])
valid_items = set(df_menu["item_id"])
valid_riders = set(df_riders["rider_id"])

df_orders = df_orders[
    df_orders["customer_id"].isin(valid_customers) &
    df_orders["restaurant_id"].isin(valid_restaurants) &
    df_orders["item_id"].isin(valid_items) &
    df_orders["rider_id"].isin(valid_riders)
]

df_orders["quantity"] = df_orders["quantity"].clip(lower=1)
df_orders["order_amount"] = df_orders["order_amount"].clip(lower=0)
df_orders["discount_amount"] = df_orders["discount_amount"].clip(lower=0)
df_orders["delivery_fee"] = df_orders["delivery_fee"].clip(lower=0)
df_orders["final_amount"] = df_orders["final_amount"].clip(lower=0)
df_orders["order_datetime"] = pd.to_datetime(df_orders["order_datetime"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S")
df_orders.dropna(subset=["order_id", "order_datetime"], inplace=True)

df_orders.to_csv(CLEANED_DIR / "orders.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_orders)} records saved to cleaned/orders.csv")

# 6. Clean Payments
print("\n[6/10] Cleaning payments.csv...")
df_payments = pd.read_csv(RAW_DIR / "payments.csv")
orig_len = len(df_payments)
df_payments.drop_duplicates(subset=["payment_id"], inplace=True)

valid_orders = set(df_orders["order_id"])
df_payments = df_payments[df_payments["order_id"].isin(valid_orders)]

df_payments.to_csv(CLEANED_DIR / "payments.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_payments)} records saved to cleaned/payments.csv")

# 7. Clean Deliveries
print("\n[7/10] Cleaning deliveries.csv...")
df_deliveries = pd.read_csv(RAW_DIR / "deliveries.csv")
orig_len = len(df_deliveries)
df_deliveries.drop_duplicates(subset=["delivery_id"], inplace=True)

df_deliveries = df_deliveries[
    df_deliveries["order_id"].isin(valid_orders) &
    df_deliveries["rider_id"].isin(valid_riders)
]

df_deliveries["distance_km"] = df_deliveries["distance_km"].clip(lower=0.1, upper=30.0)
df_deliveries["delivery_duration"] = df_deliveries["delivery_duration"].clip(lower=1, upper=180)

df_deliveries.to_csv(CLEANED_DIR / "deliveries.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_deliveries)} records saved to cleaned/deliveries.csv")

# 8. Clean App Events
print("\n[8/10] Cleaning app_events.csv...")
df_events = pd.read_csv(RAW_DIR / "app_events.csv")
orig_len = len(df_events)
df_events.drop_duplicates(subset=["event_id"], inplace=True)

df_events = df_events[df_events["customer_id"].isin(valid_customers)]

df_events.to_csv(CLEANED_DIR / "app_events.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_events)} records saved to cleaned/app_events.csv")

# 9. Clean Promotions
print("\n[9/10] Cleaning promotions.csv...")
df_promotions = pd.read_csv(RAW_DIR / "promotions.csv")
orig_len = len(df_promotions)
df_promotions.drop_duplicates(subset=["promo_id"], inplace=True)

df_promotions["discount_percentage"] = df_promotions["discount_percentage"].clip(lower=1, upper=100)
df_promotions["campaign_budget"] = df_promotions["campaign_budget"].clip(lower=0)

df_promotions.to_csv(CLEANED_DIR / "promotions.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_promotions)} records saved to cleaned/promotions.csv")

# 10. Clean Ratings & Reviews
print("\n[10/10] Cleaning ratings_reviews.csv...")
df_ratings = pd.read_csv(RAW_DIR / "ratings_reviews.csv")
orig_len = len(df_ratings)
df_ratings.drop_duplicates(subset=["review_id"], inplace=True)

df_ratings = df_ratings[
    df_ratings["order_id"].isin(valid_orders) &
    df_ratings["customer_id"].isin(valid_customers)
]

df_ratings["restaurant_rating"] = df_ratings["restaurant_rating"].clip(lower=1, upper=5)
df_ratings["delivery_rating"] = df_ratings["delivery_rating"].clip(lower=1, upper=5)

df_ratings.to_csv(CLEANED_DIR / "ratings_reviews.csv", index=False)
print(f"  Processed {orig_len} -> {len(df_ratings)} records saved to cleaned/ratings_reviews.csv")

print("\n==================================================")
print("     ALL DATASETS CLEANED & PRESERVED SUCCESSFULLY ")
print("==================================================")