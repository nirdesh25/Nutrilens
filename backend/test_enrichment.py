import os, sys

# Setup - MUST happen before any app imports to ensure .env is found
backend_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.abspath(os.getcwd()) != backend_dir:
    os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, HealthProfile
from app.utils.auth import get_password_hash
from app.services.health_service import health_service
from app.services.nutrition_service import NutritionService

async def test_enrichment():
    print("=== Nutri-Health Enrichment Test ===")
    
    # 1. Create a test user with a health profile
    db = SessionLocal()
    try:
        # Create user if not exists
        test_email = "tester@nutrilens.com"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                name="Test User",
                email=test_email,
                password_hash=get_password_hash("test123"),
                age=30
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"   Created test user: {test_email}")
        
        # Create health profile (Diabetes + High BP)
        profile = db.query(HealthProfile).filter(HealthProfile.user_id == user.id).first()
        if not profile:
            profile = HealthProfile(
                user_id=user.id,
                diabetes=True,
                high_bp=True,
                weight_loss=True
            )
            db.add(profile)
            db.commit()
            print("   Created health profile (Diabetes, High BP, Weight Loss)")
        else:
            profile.diabetes = True
            profile.high_bp = True
            profile.weight_loss = True
            db.commit()
            print("   Updated existing health profile")

        # 2. Test Analyze Food for User
        print("\n--- Individual Food Analysis ---")
        test_foods = ["Apple", "Banana", "Tomato", "Potato", "Samosa", "Soy beans"]
        
        for food in test_foods:
            analysis = health_service.analyze_food_for_user(food, user.id, db)
            nutrition = NutritionService.get_food_nutrition(food)
            
            cals = nutrition.get('calories') if nutrition else 'N/A'
            tags = ", ".join(analysis['tags']) if analysis['tags'] else "None"
            
            print(f"Food: {food:10} | Cals: {str(cals):5} | Status: {analysis['status']:11} | Tags: {tags}")

        print("\n--- Verification Complete ---")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_enrichment())
