import random
from pathlib import Path
import pandas as pd
from faker import Faker

import sys
sys.path.append(str(Path(__file__).resolve().parent))
from constants import CITIES, CITY_WEIGHTS, PERSONAS

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

customers = []

for i in range(1, 5001):
    persona = random.choice(PERSONAS)
    if persona == "Student":
        occupation = "Student"
        age = random.randint(18, 25)
    elif persona == "Working Professional":
        occupation = random.choice([
            "Software Engineer", "Teacher", "Doctor",
            "Designer", "Accountant", "Business Owner"
        ])
        age = random.randint(23, 50)
    else:
        occupation = random.choice([
            "Homemaker", "Teacher", "Business Owner", "Banker"
        ])
        age = random.randint(28, 60)

    customers.append({
        "customer_id": f"C{i:06d}",
        "customer_name": fake.name(),
        "age": age,
        "gender": random.choice(["Male", "Female"]),
        "city": random.choices(CITIES, weights=CITY_WEIGHTS)[0],
        "persona": persona,
        "occupation": occupation,
        "signup_date": fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d"),
        "subscription_type": random.choice(["Free", "Premium"]),
        "acquisition_channel": random.choice([
            "Instagram", "Google", "Referral", "Campus Campaign", "YouTube"
        ])
    })

df = pd.DataFrame(customers)
output_path = RAW_DIR / "customers.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} customers -> {output_path}")