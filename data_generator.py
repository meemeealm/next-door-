import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
from database import db_path, init_db

# Initialize Faker with local setting
fake = Faker(['en_PH', 'en_US']) 

# Specific SEA items to keep the "Pasar" vibe
FOOD_ITEMS = {
    "Vegetables": ["Talong", "Ampalaya", "Kangkong", "Bok Choy", "Okra", "Sitaw"],
    "Fruit": ["Carabao Mango", "Calamansi", "Rambutan", "Papaya", "Lanzones"],
    "Cooked Meal": ["Adobo", "Pancit Canton", "Sinigang", "Lumpia", "Biko"],
    "Herbs": ["Lemongrass", "Pandan", "Thai Basil", "Turmeric", "Curry Leaves"],
    "Other": ["Ube Halaya", "Coconut Milk", "Salted Eggs", "Patis"]
}

# Neighborhood Center (Bacoor/Las Piñas area)
BASE_LAT = 14.4445
BASE_LON = 120.9473

def seed_database(num_entries=40):
    init_db() # Ensure schema is ready
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print(f"🚀 Generating {num_entries} realistic neighborhood posts...")

    for _ in range(num_entries):
        # 1. Real-sounding local name
        user = fake.name()
        
        # 2. Localized phone number
        phone = fake.phone_number()
        
        # 3. Category & Item logic
        category = random.choice(list(FOOD_ITEMS.keys()))
        item_base = random.choice(FOOD_ITEMS[category])
        item = f"{fake.word().capitalize()} {item_base}" # e.g. "Fresh Talong"
        
        # 4. Quantity
        qty = f"{random.randint(1, 5)} {random.choice(['kg', 'bundles', 'packs', 'pcs'])}"
        
        # 5. Precise Timestamp (ISO format for SQL sorting)
        posted = fake.date_time_between(start_date='-3d', end_date='now').strftime("%Y-%m-%d %H:%M:%S")
        
        # 6. Realistic Local Coordinates
        # 0.02 range keeps pins within a few kilometers
        lat = float(fake.coordinate(center=BASE_LAT, radius=0.03))
        lon = float(fake.coordinate(center=BASE_LON, radius=0.03))

        c.execute('''
            INSERT INTO food_items (user, phone, item, category, quantity, posted, status, lat, lon) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (user, phone, item, category, qty, posted, 'Available', lat, lon)
        )
    
    conn.commit()
    conn.close()
    print("✅ Success! Database seeded with high-quality test data.")

if __name__ == "__main__":
    seed_database(60)