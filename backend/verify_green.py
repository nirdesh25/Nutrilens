import sys
import os
import asyncio
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test_green_produce():
    from app.services.ml_service import MLService
    
    service = MLService()
    
    # 1. Test Lady's Finger (Heuristic)
    # Simulator: Medium green with specific tint
    lady_finger_box = Image.new('RGB', (224, 224), color=(110, 160, 50))
    img_byte_arr = io.BytesIO()
    lady_finger_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Lady's Finger (Heuristic) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Source: {recognition['category']})")
    
    # 2. Test Bitter Gourd (Heuristic)
    # Simulator: Darker saturated green
    bitter_gourd_box = Image.new('RGB', (224, 224), color=(50, 145, 40))
    img_byte_arr = io.BytesIO()
    bitter_gourd_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Bitter Gourd (Heuristic) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Source: {recognition['category']})")

    # 3. Test Freshness Logic Switch
    print("\n--- Testing Freshness Logic Routing ---")
    
    # Apple (Should use Model)
    apple_bytes = image_bytes # using the same bytes just to trigger logic
    freshness_apple = await service.predict_freshness(apple_bytes, food_name_override="Apple")
    print(f"Apple Freshness Processed. Status: {freshness_apple['freshness_status']} (Confidence: {freshness_apple['confidence']})")
    
    # Lady's Finger (Should use Heuristic)
    freshness_lf = await service.predict_freshness(image_bytes, food_name_override="Lady's Finger")
    print(f"Lady's Finger Freshness Processed. Status: {freshness_lf['freshness_status']} (Confidence: {freshness_lf['confidence']})")

if __name__ == "__main__":
    asyncio.run(test_green_produce())
