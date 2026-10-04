import random
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"

orders_df = pd.read_csv(RAW_DIR / "orders.csv")

# Filter for delivered orders to sample ratings
delivered_orders = orders_df[orders_df["order_status"] == "Delivered"]
sample_orders = delivered_orders.sample(n=min(28792, len(delivered_orders)), random_state=42)

ratings = []

for idx, (_, row) in enumerate(sample_orders.iterrows(), start=1):
    ratings.append({
        "review_id": f"RV{idx:07d}",
        "order_id": row["order_id"],
        "customer_id": row["customer_id"],
        "restaurant_rating": random.choices([1, 2, 3, 4, 5], weights=[3, 5, 12, 40, 40])[0],
        "delivery_rating": random.choices([1, 2, 3, 4, 5], weights=[2, 4, 10, 38, 46])[0]
    })

df = pd.DataFrame(ratings)
output_path = RAW_DIR / "ratings_reviews.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} ratings & reviews -> {output_path}")