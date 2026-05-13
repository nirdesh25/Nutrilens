import sqlite3
import os

def build_db():
    db_path = os.path.join(os.path.dirname(__file__), 'nutrition.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS food_nutrition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        category TEXT,
        calories REAL,
        protein REAL,
        fat REAL,
        carbs REAL,
        fiber REAL,
        sugar REAL,
        sodium REAL,
        gi_index REAL
    )
    ''')

    # Realistic mock data, mixing USDA style with Indian foods
    foods = [
        ("Apple, raw", "Fruit", 52, 0.3, 0.2, 14, 2.4, 10.4, 1, 36),
        ("Banana, raw", "Fruit", 89, 1.1, 0.3, 23, 2.6, 12.2, 1, 51),
        ("Chicken Breast, cooked", "Meat", 165, 31, 3.6, 0, 0, 0, 74, 0),
        ("Rice, white, cooked", "Grain", 130, 2.7, 0.3, 28, 0.4, 0.1, 1, 73),
        ("Milk, whole", "Dairy", 61, 3.2, 3.3, 4.8, 0, 5.1, 40, 31),
        ("Paneer (Indian Cottage Cheese)", "Dairy", 265, 18, 20, 1.2, 0, 1.2, 18, 27),
        ("Chicken Biryani", "Mixed", 150, 12, 5, 18, 1.5, 2, 450, 65),
        ("Dal Makhani", "Legume", 120, 6, 4, 15, 4, 2, 350, 42),
        ("Roti (Chapati)", "Grain", 297, 9, 3, 60, 9, 1, 120, 55),
        ("Samosa", "Snack", 262, 3, 15, 24, 2, 1, 400, 70),
        ("Palak Paneer", "Mixed", 130, 8, 9, 5, 2, 2, 350, 35),
        ("Mango, raw", "Fruit", 60, 0.8, 0.4, 15, 1.6, 14, 1, 51),
        ("Tomato, raw", "Vegetable", 18, 0.9, 0.2, 3.9, 1.2, 2.6, 5, 15),
        ("Beetroot, raw", "Vegetable", 43, 1.6, 0.2, 10, 2.8, 6.8, 78, 64),
        ("Bell pepper, green", "Vegetable", 20, 0.9, 0.2, 4.6, 1.7, 2.4, 3, 15),
        ("Cabbage, raw", "Vegetable", 25, 1.3, 0.1, 5.8, 2.5, 3.2, 18, 10),
        ("Carrot, raw", "Vegetable", 41, 0.9, 0.2, 10, 2.8, 4.7, 69, 39),
        ("Cauliflower, raw", "Vegetable", 25, 1.9, 0.3, 5, 2, 1.9, 30, 15),
        ("Cucumber, raw", "Vegetable", 15, 0.7, 0.1, 3.6, 0.5, 1.7, 2, 15),
        ("Eggplant (Brinjal), raw", "Vegetable", 25, 1, 0.2, 6, 3, 3.5, 2, 15),
        ("Garlic, raw", "Spice", 149, 6.4, 0.5, 33, 2.1, 1, 17, 70),
        ("Ginger, raw", "Spice", 80, 1.8, 0.8, 18, 2, 1.7, 13, 15),
        ("Grapes, raw", "Fruit", 69, 0.7, 0.2, 18, 0.9, 15, 2, 59),
        ("Kiwi, raw", "Fruit", 61, 1.1, 0.5, 15, 3, 9, 3, 50),
        ("Lemon, raw", "Fruit", 29, 1.1, 0.3, 9, 2.8, 2.5, 2, 20),
        ("Lettuce, raw", "Vegetable", 15, 1.4, 0.2, 2.9, 1.3, 0.8, 28, 15),
        ("Onion, raw", "Vegetable", 40, 1.1, 0.1, 9, 1.7, 4.2, 4, 10),
        ("Orange, raw", "Fruit", 47, 0.9, 0.1, 12, 2.4, 9, 0, 43),
        ("Pear, raw", "Fruit", 57, 0.4, 0.1, 15, 3.1, 9.8, 1, 38),
        ("Peas, green, raw", "Vegetable", 81, 5, 0.4, 14, 5, 5.7, 5, 22),
        ("Pineapple, raw", "Fruit", 50, 0.5, 0.1, 13, 1.4, 9.9, 1, 59),
        ("Pomegranate, raw", "Fruit", 83, 1.7, 1.2, 19, 4, 13.7, 3, 35),
        ("Potato, raw", "Vegetable", 77, 2, 0.1, 17, 2.2, 0.8, 6, 82),
        ("Radish, raw", "Vegetable", 16, 0.7, 0.1, 3.4, 1.6, 1.9, 39, 15),
        ("Soy beans, raw", "Legume", 446, 36, 20, 30, 9, 7, 2, 18),
        ("Spinach, raw", "Vegetable", 23, 2.9, 0.4, 3.6, 2.2, 0.4, 79, 15),
        ("Sweetcorn, raw", "Grain", 86, 3.2, 1.2, 19, 2, 6.3, 15, 52),
        ("Sweet potato, raw", "Vegetable", 86, 1.6, 0.1, 20, 3, 4.2, 55, 50),
        ("Watermelon, raw", "Fruit", 30, 0.6, 0.2, 8, 0.4, 6.2, 1, 72)
    ]

    for f in foods:
        try:
            cursor.execute('''
            INSERT INTO food_nutrition (name, category, calories, protein, fat, carbs, fiber, sugar, sodium, gi_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', f)
        except sqlite3.IntegrityError:
            pass # Already exists

    conn.commit()
    conn.close()
    print(f"Database created successfully with {len(foods)} items at {db_path}")

if __name__ == "__main__":
    build_db()
