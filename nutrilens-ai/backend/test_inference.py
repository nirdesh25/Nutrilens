import os, sys, io
import numpy as np
from PIL import Image

# Setup sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

print("=== NutriLens Inference Test ===")
from app.services.ml_service import MLService
import asyncio

async def test_inference():
    svc = MLService()
    
    # Create a dummy RGB image (224x224)
    img = Image.new('RGB', (224, 224), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n1. Testing Unified Prediction (Recognition + Freshness)...")
    try:
        result = await svc.predict_unified(image_bytes)
        print(f"   Success! Result: {result['food_name']} - {result['freshness_status']} (Risk: {result['risk_score']}, Conf: {result['confidence']})")
    except Exception as e:
        print(f"   FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n2. Testing Waste Classification...")
    try:
        result = await svc.classify_waste(image_bytes)
        print(f"   Success! Result: {result['waste_type']} (Recyclable: {result['recyclable']}, Conf: {result['confidence']})")
    except Exception as e:
        print(f"   FAILED: {e}")
        
    print("\n3. Testing Milk Quality (via service)...")
    from app.services.milk_quality_service import MilkQualityService
    try:
        # High quality test
        res = MilkQualityService.predict_quality(ph=6.6, temperature=3.0, taste=1, odor=1, fat=1, turbidity=1, color=240)
        print(f"   Success (Good Milk)! Prediction: {res['prediction']}, Model: {res['model']}")
    except Exception as e:
        print(f"   FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_inference())
