import random
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"

customers_records = pd.read_csv(RAW_DIR / "customers.csv").to_dict("records")
restaurants_records = pd.read_csv(RAW_DIR / "restaurants.csv").to_dict("records")
menu_records = pd.read_csv(RAW_DIR / "menu_items.csv").to_dict("records")
riders_records = pd.read_csv(RAW_DIR / "riders.csv").to_dict("records")

# Indexing for sub-millisecond lookup
riders_by_city = {}
for r in riders_records:
    riders_by_city.setdefault(r["city"], []).append(r)

menu_by_restaurant = {}
for m in menu_records:
    menu_by_restaurant.setdefault(m["restaurant_id"], []).append(m)

customers_by_city = {}
for c in customers_records:
    customers_by_city.setdefault(c["city"], []).append(c)

TOTAL_ORDERS = 50000
orders = []

random.seed(42)

start_date = datetime.now() - timedelta(days=365)
hour_weights = [1,1,1,1,1,2,3,4,6,8,12,15,18,14,8,6,7,10,16,20,18,12,6,3]
hour_choices = list(range(24))

for i in range(1, TOTAL_ORDERS + 1):
    restaurant = random.choice(restaurants_records)
    restaurant_id = restaurant["restaurant_id"]
    rest_city = restaurant["city"]

    # Customer Selection (90% same city, 10% visitor)
    if rest_city in customers_by_city and random.random() < 0.9:
        customer = random.choice(customers_by_city[rest_city])
    else:
        customer = random.choice(customers_records)

    # Menu Item Selection (belongs to this restaurant)
    rest_items = menu_by_restaurant.get(restaurant_id)
    if not rest_items:
        rest_items = menu_records
    item = random.choice(rest_items)

    # Rider Selection (matched by city)
    city_riders = riders_by_city.get(rest_city)
    if not city_riders:
        rider = random.choice(riders_records)
    else:
        rider = random.choice(city_riders)

    quantity = random.randint(1, 4)
    order_amount = int(item["price"] * quantity)

    # Persona based discount
    persona = customer["persona"]
    if persona == "Student":
        discount_pct = random.randint(15, 45)
    elif persona == "Working Professional":
        discount_pct = random.randint(5, 30)
    else:
        discount_pct = random.randint(0, 20)

    discount_amount = int((order_amount * discount_pct) / 100)
    delivery_fee = random.randint(20, 60)
    final_amount = max(50, order_amount - discount_amount + delivery_fee)

    order_status = "Delivered" if random.random() < 0.96 else "Cancelled"

    # Datetime distribution
    random_days = random.randint(0, 364)
    selected_hour = random.choices(hour_choices, weights=hour_weights)[0]
    dt = start_date + timedelta(days=random_days, hours=selected_hour, minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    orders.append({
        "order_id": f"O{i:07d}",
        "customer_id": customer["customer_id"],
        "restaurant_id": restaurant_id,
        "item_id": item["item_id"],
        "rider_id": rider["rider_id"],
        "order_datetime": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "quantity": quantity,
        "order_amount": order_amount,
        "discount_amount": discount_amount,
        "delivery_fee": delivery_fee,
        "final_amount": final_amount,
        "order_status": order_status
    })

df = pd.DataFrame(orders)
df = df.sort_values("order_datetime").reset_index(drop=True)
output_path = RAW_DIR / "orders.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} orders -> {output_path}")