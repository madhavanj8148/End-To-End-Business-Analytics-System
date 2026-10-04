import random
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"

orders_df = pd.read_csv(RAW_DIR / "orders.csv")
menu_df = pd.read_csv(RAW_DIR / "menu_items.csv")

# Create lookup dict for menu preparation times
prep_time_dict = dict(zip(menu_df["item_id"], menu_df["preparation_time"]))

payments = []
deliveries = []

payment_methods = ["UPI", "Credit Card", "Debit Card", "Cash", "Wallet"]
payment_weights = [55, 15, 10, 10, 10]

for _, row in orders_df.iterrows():
    order_id = row["order_id"]
    rider_id = row["rider_id"]
    item_id = row["item_id"]
    status = row["order_status"]

    payment_id = f"P{order_id[1:]}"
    delivery_id = f"DV{order_id[1:]}"

    payment_method = random.choices(payment_methods, weights=payment_weights)[0]
    payment_status = "Refunded" if status == "Cancelled" else "Success"

    if status == "Delivered":
        distance = round(random.uniform(1.0, 12.0), 1)
        prep_time = prep_time_dict.get(item_id, 20)
        # Realism: delivery_duration = prep_time + travel time (distance * 2.5 mins/km) + transit buffer
        delivery_duration = int(prep_time + (distance * 2.5) + random.randint(3, 12))
        delivery_duration = max(15, min(90, delivery_duration))
    else:
        # Cancelled orders
        distance = round(random.uniform(0.5, 5.0), 1)
        delivery_duration = random.randint(5, 15)  # Time before cancellation

    payments.append({
        "payment_id": payment_id,
        "order_id": order_id,
        "payment_method": payment_method,
        "payment_status": payment_status
    })

    deliveries.append({
        "delivery_id": delivery_id,
        "order_id": order_id,
        "rider_id": rider_id,
        "distance_km": distance,
        "delivery_duration": delivery_duration
    })

payments_df = pd.DataFrame(payments)
deliveries_df = pd.DataFrame(deliveries)

payments_path = RAW_DIR / "payments.csv"
deliveries_path = RAW_DIR / "deliveries.csv"

payments_df.to_csv(payments_path, index=False)
deliveries_df.to_csv(deliveries_path, index=False)

print(f"Generated {len(payments_df)} payments -> {payments_path}")
print(f"Generated {len(deliveries_df)} deliveries -> {deliveries_path}")