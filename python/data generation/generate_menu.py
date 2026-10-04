import random
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"

restaurants_df = pd.read_csv(RAW_DIR / "restaurants.csv")

food_catalog = {
    "South Indian": ["Masala Dosa", "Idli", "Vada", "Pongal", "Uttapam", "Rava Dosa", "Filter Coffee"],
    "Biryani": ["Chicken Biryani", "Mutton Biryani", "Veg Biryani", "Paneer Biryani", "Egg Biryani", "Hyderabadi Biryani"],
    "North Indian": ["Butter Naan", "Paneer Butter Masala", "Dal Makhani", "Chole Bhature", "Kadhai Paneer", "Tandoori Roti"],
    "Chinese": ["Fried Rice", "Noodles", "Manchurian", "Spring Roll", "Momos", "Chilli Chicken"],
    "Pizza": ["Margherita Pizza", "Farmhouse Pizza", "Veg Supreme Pizza", "Pepperoni Pizza", "Cheese Burst Pizza"],
    "Burger": ["Veg Burger", "Chicken Burger", "Cheese Burger", "Crispy Veg Burger", "Double Patty Burger"],
    "Healthy Foods": ["Salad Bowl", "Grilled Chicken", "Protein Bowl", "Fruit Salad", "Avocado Toast"],
    "Desserts": ["Brownie", "Chocolate Cake", "Ice Cream", "Gulab Jamun", "Rasgulla", "Tiramisu"],
    "Beverages": ["Mojito", "Cold Coffee", "Lemon Juice", "Mango Lassi", "Iced Tea", "Fresh Juice"]
}

menu_items = []

for i in range(1, 15001):
    restaurant = restaurants_df.sample(1).iloc[0]
    cuisine = restaurant["cuisine_type"]
    items_available = food_catalog.get(cuisine, ["Special Dish"])
    item_name = random.choice(items_available)

    menu_items.append({
        "item_id": f"M{i:06d}",
        "restaurant_id": restaurant["restaurant_id"],
        "cuisine_type": cuisine,
        "item_name": item_name,
        "price": random.randint(80, 700),
        "preparation_time": random.randint(10, 45)
    })

df = pd.DataFrame(menu_items)
output_path = RAW_DIR / "menu_items.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} menu items -> {output_path}")