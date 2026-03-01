import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data", "food_swap.db")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            phone TEXT,
            item TEXT,
            category TEXT,
            quantity TEXT,
            posted DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Available'
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized!") 


def add_item(user, phone, item, category, quantity):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO food_items (user, phone, item, category, quantity) 
        VALUES (?, ?, ?, ?, ?)''', 
        (user, phone, item, category, quantity)
    )
    conn.commit()
    conn.close()

def get_all_items():
    conn = sqlite3.connect(db_path)
    # Sort by 'posted' descending so the latest food is at the top
    df = pd.read_sql_query("SELECT * FROM food_items ORDER BY posted DESC", conn)
    conn.close()
    return df

def toggle_claim(item_id, current_status):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # If it's available, mark as Reserved. If reserved, mark as Available.
    new_status = 'Reserved' if current_status == 'Available' else 'Available'
    c.execute("UPDATE food_items SET status = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    conn.close()

def get_user_items(user_name):
    conn = sqlite3.connect(db_path)
    # Using lowercase 'user' to match your schema
    query = "SELECT * FROM food_items WHERE user = ? ORDER BY posted DESC"
    df = pd.read_sql_query(query, conn, params=(user_name,))
    conn.close()
    return df