import random
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

promo_types = [
    "Flat Discount",
    "Percentage Discount",
    "Free Delivery",
    "Cashback"
]

promotions = []

for i in range(1, 201):
    promotions.append({
        "promo_id": f"PR{i:04d}",
        "promo_name": f"Campaign_{i}",
        "promo_type": random.choice(promo_types),
        "discount_percentage": random.randint(5, 40),
        "campaign_budget": random.randint(10000, 100000)
    })

df = pd.DataFrame(promotions)
output_path = RAW_DIR / "promotions.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} promotions -> {output_path}")