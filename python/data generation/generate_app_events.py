import random
from pathlib import Path
import pandas as pd

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from constants import EVENT_TYPES_FUNNEL

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"

customers_df = pd.read_csv(RAW_DIR / "customers.csv")
orders_df = pd.read_csv(RAW_DIR / "orders.csv")

events = []
event_counter = 1
TOTAL_TARGET_EVENTS = 100000

# First: Generate successful order clickstreams for orders in orders_df
for _, order in orders_df.iterrows():
    if event_counter > TOTAL_TARGET_EVENTS:
        break
    cust_id = order["customer_id"]

    # Full funnel sequence leading to Order Complete
    funnel_sequence = [
        "App Open",
        "Restaurant View",
        "Menu View",
        "Add To Cart",
        "Checkout",
        "Order Complete"
    ]

    for stage in funnel_sequence:
        if event_counter > TOTAL_TARGET_EVENTS:
            break
        events.append({
            "event_id": f"E{event_counter:07d}",
            "customer_id": cust_id,
            "event_type": stage
        })
        event_counter += 1

# Second: Fill remaining events with realistic dropped sessions (funnel drop-offs)
customer_ids = customers_df["customer_id"].tolist()

while event_counter <= TOTAL_TARGET_EVENTS:
    cust_id = random.choice(customer_ids)
    # Random drop-off depth (1 = App Open only, 2 = up to Rest View, 3 = up to Menu View, 4 = up to Add To Cart)
    drop_depth = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]

    for stage_idx in range(drop_depth):
        if event_counter > TOTAL_TARGET_EVENTS:
            break
        events.append({
            "event_id": f"E{event_counter:07d}",
            "customer_id": cust_id,
            "event_type": EVENT_TYPES_FUNNEL[stage_idx]
        })
        event_counter += 1

df = pd.DataFrame(events)
output_path = RAW_DIR / "app_events.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} realistic app events -> {output_path}")