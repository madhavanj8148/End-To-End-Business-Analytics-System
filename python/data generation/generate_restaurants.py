import random
from pathlib import Path
import pandas as pd
from faker import Faker

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from constants import CITIES, CITY_WEIGHTS, RESTAURANT_TYPES, CUISINES, CUISINE_WEIGHTS

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

restaurants = []

for i in range(1, 1501):
    restaurants.append({
        "restaurant_id": f"R{i:05d}",
        "restaurant_name": fake.company(),
        "city": random.choices(CITIES, weights=CITY_WEIGHTS)[0],
        "restaurant_type": random.choice(RESTAURANT_TYPES),
        "cuisine_type": random.choices(CUISINES, weights=CUISINE_WEIGHTS)[0],
        "opening_year": random.randint(2016, 2026),
        "avg_rating": round(random.uniform(3.5, 5.0), 1),
        "delivery_radius_km": round(random.uniform(2.0, 10.0), 1),
        "commission_percentage": random.randint(15, 30)
    })

df = pd.DataFrame(restaurants)
output_path = RAW_DIR / "restaurants.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} restaurants -> {output_path}")