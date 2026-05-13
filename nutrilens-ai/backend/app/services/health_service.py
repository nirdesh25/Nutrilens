from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import HealthProfile, Grocery
from app.services.nutrition_service import NutritionService

class HealthRecommendationService:
    """
    Health-based food recommendation engine.
    
    Dataset Integration: USDA FoodData Central, Glycemic Index Dataset
    """
    
    # Nutritional guidelines based on health conditions
    HEALTH_RULES = {
        'diabetes': {
            'avoid': ['high_sugar', 'refined_carbs', 'sweetened_beverages'],
            'recommend': ['whole_grains', 'leafy_greens', 'lean_protein'],
            'gi_threshold': 55  # Low GI foods
        },
        'high_bp': {
            'avoid': ['high_sodium', 'processed_foods', 'canned_foods'],
            'recommend': ['potassium_rich', 'whole_grains', 'low_fat_dairy'],
            'sodium_limit': 1500  # mg per day
        },
        'cholesterol': {
            'avoid': ['saturated_fats', 'trans_fats', 'red_meat'],
            'recommend': ['omega3_fish', 'nuts', 'olive_oil', 'oats']
        },
        'surgery_recovery': {
            'avoid': ['spicy_foods', 'hard_to_digest'],
            'recommend': ['protein_rich', 'vitamin_c', 'zinc_rich', 'soft_foods']
        },
        'weight_loss': {
            'avoid': ['high_calorie', 'processed_snacks', 'sugary_drinks'],
            'recommend': ['high_fiber', 'lean_protein', 'vegetables', 'fruits']
        }
    }
    
    def get_recommendations(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get personalized food recommendations based on health profile."""
        
        health_profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == user_id
        ).first()
        
        if not health_profile:
            return {
                'recommended_foods': [],
                'foods_to_avoid': [],
                'meal_suggestions': []
            }
        
        groceries = db.query(Grocery).filter(Grocery.user_id == user_id).all()
        
        recommended = []
        avoid = []
        
        # Apply health rules
        if health_profile.diabetes:
            recommended.extend(self._get_diabetes_friendly_foods(groceries))
            avoid.extend(self._get_high_gi_foods(groceries))
        
        if health_profile.high_bp:
            recommended.extend(self._get_low_sodium_foods(groceries))
            avoid.extend(self._get_high_sodium_foods(groceries))
        
        if health_profile.cholesterol:
            recommended.extend(self._get_heart_healthy_foods(groceries))
            avoid.extend(self._get_high_fat_foods(groceries))
        
        if health_profile.weight_loss:
            recommended.extend(self._get_low_calorie_foods(groceries))
            avoid.extend(self._get_high_calorie_foods(groceries))
        
        meal_suggestions = self._generate_meal_suggestions(health_profile, groceries)
        
        return {
            'recommended_foods': list(set(recommended)),
            'foods_to_avoid': list(set(avoid)),
            'meal_suggestions': meal_suggestions
        }
    
    def analyze_food_for_user(self, food_name: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Analyze a specific food item against user's health profile."""
        health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
        
        if not health_profile:
            return {"status": "neutral", "tags": [], "message": "Complete your health profile for personalized insights."}

        food_data = NutritionService.get_food_nutrition(food_name) or {}
        tags = []
        status = "neutral"
        
        # Diabetes Check
        if health_profile.diabetes:
            gi = food_data.get('gi_index', 100)
            if gi < 55:
                tags.append("Diabetes Friendly")
                status = "recommended"
            elif gi > 70:
                tags.append("High Glycemic Index")
                status = "avoid"
                
        # High BP Check
        if health_profile.high_bp:
            sodium = food_data.get('sodium', 0)
            if sodium > 400:
                tags.append("High Sodium")
                status = "avoid"
            elif sodium < 140:
                tags.append("Low Sodium")
                if status == "neutral": status = "recommended"

        # Cholesterol Check
        if health_profile.cholesterol:
            fat = food_data.get('fat', 0)
            if fat > 10:
                tags.append("High Fat")
                status = "avoid"
            elif food_name.lower() in ['salmon', 'flax', 'chia', 'spinach', 'apple']:
                tags.append("Heart Healthy")
                if status == "neutral": status = "recommended"

        # Weight Loss Check
        if health_profile.weight_loss:
            cals = food_data.get('calories', 0)
            if cals > 200:
                tags.append("High Calorie")
                if status != "avoid": status = "caution"
            elif cals < 100:
                tags.append("Low Calorie")
                if status == "neutral": status = "recommended"

        return {
            "status": status,
            "tags": tags,
            "message": f"{food_name} is {status} for your profile." if tags else "No specific health flags for this item."
        }
    
    def _get_diabetes_friendly_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get low GI foods suitable for diabetes."""
        friendly = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('gi_index', 100) < 55:
                friendly.append(grocery.food_name)
        return friendly
    
    def _get_high_gi_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get high GI foods to avoid."""
        high_gi = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('gi_index', 0) > 70:
                high_gi.append(grocery.food_name)
        return high_gi
    
    def _get_low_sodium_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get low sodium foods."""
        low_sodium = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('sodium', 0) < 140:
                low_sodium.append(grocery.food_name)
        return low_sodium
    
    def _get_high_sodium_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get high sodium foods to avoid."""
        high_sodium = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('sodium', 0) > 400:
                high_sodium.append(grocery.food_name)
        return high_sodium
    
    def _get_heart_healthy_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get heart-healthy foods."""
        heart_healthy = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('fiber', 0) > 3 or grocery.food_name.lower() in ['salmon', 'flax', 'chia']: # db lacks omega3
                heart_healthy.append(grocery.food_name)
        return heart_healthy
    
    def _get_high_fat_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get high fat foods to limit."""
        high_fat = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('fat', 0) > 10:
                high_fat.append(grocery.food_name)
        return high_fat
    
    def _get_low_calorie_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get low calorie foods for weight loss."""
        low_cal = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('calories', 1000) < 100:
                low_cal.append(grocery.food_name)
        return low_cal
    
    def _get_high_calorie_foods(self, groceries: List[Grocery]) -> List[str]:
        """Get high calorie foods to limit."""
        high_cal = []
        for grocery in groceries:
            food_data = NutritionService.get_food_nutrition(grocery.food_name) or {}
            if food_data.get('calories', 0) > 200:
                high_cal.append(grocery.food_name)
        return high_cal
    
    def _generate_meal_suggestions(self, health_profile: HealthProfile, groceries: List[Grocery]) -> List[str]:
        """Generate simple meal suggestions based on available groceries."""
        suggestions = []
        
        grocery_names = [g.food_name for g in groceries]
        
        if 'Chicken' in grocery_names and 'Lettuce' in grocery_names:
            suggestions.append("Grilled chicken salad with fresh lettuce")
        
        if 'Salmon' in grocery_names and health_profile.cholesterol:
            suggestions.append("Baked salmon (rich in Omega-3 for heart health)")
        
        if 'Apple' in grocery_names and health_profile.diabetes:
            suggestions.append("Apple slices with almond butter (low GI snack)")
        
        if 'Tomato' in grocery_names and 'Lettuce' in grocery_names:
            suggestions.append("Fresh vegetable salad")
        
        return suggestions

health_service = HealthRecommendationService()
