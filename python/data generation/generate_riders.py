import random
from pathlib import Path
import pandas as pd
from faker import Faker

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from constants import CITIES, CITY_WEIGHTS, VEHICLE_TYPES, SHIFT_TYPES

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

riders = []

for i in range(1, 4001):
    joining_year = random.randint(2020, 2026)
    riders.append({
        "rider_id": f"D{i:05d}",
        "rider_name": fake.name(),
        "city": random.choices(CITIES, weights=CITY_WEIGHTS)[0],
        "vehicle_type": random.choice(VEHICLE_TYPES),
        "experience_years": random.randint(0, 8),
        "joining_year": joining_year,
        "shift_type": random.choice(SHIFT_TYPES)
    })

df = pd.DataFrame(riders)
output_path = RAW_DIR / "riders.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} riders -> {output_path}")