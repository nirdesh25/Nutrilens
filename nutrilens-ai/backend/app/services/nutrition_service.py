import sqlite3
import os
from typing import Dict, Any, List, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'datasets', 'nutrition.db'))

class NutritionService:
    @staticmethod
    def get_connection():
        # Ensure we connect to the SQLite DB
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def get_food_nutrition(food_name: str) -> Optional[Dict[str, Any]]:
        """Lookup a food by exact or partial name in the DB"""
        conn = NutritionService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try exact match first
        cursor.execute("SELECT * FROM food_nutrition WHERE name LIKE ? LIMIT 1", (f"%{food_name}%",))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None

    @staticmethod
    def search_foods(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fuzzy search foods"""
        conn = NutritionService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, category, calories FROM food_nutrition WHERE name LIKE ? LIMIT ?", (f"%{query}%", limit))
        rows = cursor.fetchall()
        
        conn.close()
        return [dict(row) for row in rows]
