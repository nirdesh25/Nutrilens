import os, sys

# Setup - MUST happen before any app imports to ensure .env is found
backend_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.abspath(os.getcwd()) != backend_dir:
    os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, MilkAnalysis
from app.utils.auth import get_password_hash

async def test_hardware_sync():
    print("=== Hardware-Backend Sync Test ===")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Ensure test user exists
        test_email = "hardware_test@nutrilens.com"
        user = db.query(User).filter(User.email == test_email).first()
        if not user:
            user = User(
                name="Hardware Tester",
                email=test_email,
                password_hash=get_password_hash("test123"),
                age=25
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"   Created test user: {test_email}")

        # 2. Simulate ESP32 Payload
        payload = {
            "ph": 6.6,
            "temperature": 4.5,
            "taste": 1,
            "odor": 1,
            "fat": 1,
            "turbidity": 1,
            "color": 255
        }
        
        # 3. Test API Endpoint (Manually call service logic or use httpx if running server)
        print("\n   Simulating ESP32 POST logic...")
        from app.services.milk_quality_service import MilkQualityService
        
        result = MilkQualityService.predict_quality(**payload)
        print(f"   ML Prediction: {result['prediction']} (Risk: {result.get('risk_score')})")
        
        # 4. Save to DB (Persistence Check)
        analysis = MilkAnalysis(
            user_id=user.id,
            ph=payload['ph'],
            temperature=payload['temperature'],
            taste=payload['taste'],
            odor=payload['odor'],
            fat=payload['fat'],
            turbidity=payload['turbidity'],
            color=payload['color'],
            prediction=result['prediction'],
            risk_score=result.get('risk_score', 0.0)
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        print(f"\n   SUCCESS! MilkAnalysis record created with ID: {analysis.id}")
        print(f"   Stored Values: ph={analysis.ph}, temp={analysis.temperature}, prediction={analysis.prediction}")

        # 5. Verify Retrieval
        history = db.query(MilkAnalysis).filter(MilkAnalysis.user_id == user.id).all()
        print(f"\n   History check: User has {len(history)} analysis records.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_hardware_sync())
