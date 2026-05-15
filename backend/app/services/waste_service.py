from typing import Dict, Any

class WasteDecisionService:
    """
    Waste decision engine for food waste reduction.
    Calculates CO2 impact and provides actionable recommendations.
    """
    
    # CO2 emissions per kg of food waste (approximate values)
    CO2_EMISSIONS = {
        'fruit': 0.5,  # kg CO2 per kg food
        'vegetable': 0.4,
        'meat': 2.5,
        'dairy': 1.2,
        'grain': 0.6,
        'default': 0.8
    }
    
    def get_waste_decision(self, food_name: str, freshness_status: str, risk_score: float) -> Dict[str, Any]:
        """
        Determine best action for food based on freshness.
        
        Args:
            food_name: Name of the food item
            freshness_status: 'fresh', 'slightly_aged', 'rotten'
            risk_score: Risk score (0-100)
        
        Returns:
            {
                'action': str,
                'reason': str,
                'co2_impact': float
            }
        """
        
        if freshness_status == 'fresh' and risk_score < 30:
            return {
                'action': 'store_properly',
                'reason': 'Food is fresh. Store properly to extend shelf life.',
                'co2_impact': 0.0
            }
        
        elif freshness_status == 'slightly_aged' or (30 <= risk_score < 70):
            return {
                'action': 'eat_immediately',
                'reason': 'Food is still safe but aging. Consume within 1-2 days.',
                'co2_impact': self._calculate_co2_saved(food_name, 0.5)
            }
        
        elif risk_score >= 70 and risk_score < 85:
            return {
                'action': 'repurpose',
                'reason': 'Food quality declining. Use in cooked dishes, smoothies, or soups.',
                'co2_impact': self._calculate_co2_saved(food_name, 0.7)
            }
        
        elif risk_score >= 85 and risk_score < 95:
            return {
                'action': 'compost',
                'reason': 'Food is spoiled. Compost to reduce environmental impact.',
                'co2_impact': self._calculate_co2_saved(food_name, 0.3)
            }
        
        else:
            return {
                'action': 'discard',
                'reason': 'Food is completely spoiled and unsafe. Dispose properly.',
                'co2_impact': 0.0
            }
    
    def _calculate_co2_saved(self, food_name: str, efficiency: float) -> float:
        """
        Calculate CO2 saved by taking action.
        
        Args:
            food_name: Name of food
            efficiency: Action efficiency (0-1)
        
        Returns:
            CO2 saved in kg
        """
        # Estimate average food weight (kg)
        avg_weight = 0.2
        
        # Get food category
        category = self._get_food_category(food_name)
        
        # Calculate CO2 saved
        co2_per_kg = self.CO2_EMISSIONS.get(category, self.CO2_EMISSIONS['default'])
        co2_saved = avg_weight * co2_per_kg * efficiency
        
        return round(co2_saved, 3)
    
    def _get_food_category(self, food_name: str) -> str:
        """Categorize food for CO2 calculation."""
        food_name_lower = food_name.lower()
        
        fruits = ['apple', 'banana', 'orange', 'mango', 'grape', 'berry']
        vegetables = ['tomato', 'lettuce', 'carrot', 'potato', 'onion', 'pepper']
        meats = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey']
        dairy = ['milk', 'cheese', 'yogurt', 'butter']
        grains = ['bread', 'rice', 'pasta', 'wheat']
        
        if any(fruit in food_name_lower for fruit in fruits):
            return 'fruit'
        elif any(veg in food_name_lower for veg in vegetables):
            return 'vegetable'
        elif any(meat in food_name_lower for meat in meats):
            return 'meat'
        elif any(d in food_name_lower for d in dairy):
            return 'dairy'
        elif any(grain in food_name_lower for grain in grains):
            return 'grain'
        else:
            return 'default'

waste_service = WasteDecisionService()
