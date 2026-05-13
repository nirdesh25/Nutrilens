import sys
import os
import asyncio
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test_ml_service():
    from app.services.ml_service import MLService
    
    print("--- Initializing ML Service ---")
    service = MLService()
    
    # Check if models loaded
    print(f"Freshness Model: {'LOADED' if service.freshness_model else 'NOT LOADED'}")
    print(f"Recognition Model: {'LOADED' if service.food_recognition_model else 'NOT LOADED'}")
    
    # Create a red box (mock Tomato)
    red_box = Image.new('RGB', (224, 224), color=(255, 0, 0))
    img_byte_arr = io.BytesIO()
    red_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Red Image (Simulated Tomato) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Category: {recognition['category']}, Confidence: {recognition['confidence']})")
    
    # Create a purple/dark box (mock Eggplant/Brinjal)
    purple_box = Image.new('RGB', (224, 224), color=(48, 25, 52)) # Dark purple
    img_byte_arr = io.BytesIO()
    purple_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Purple Image (Simulated Brinjal) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Category: {recognition['category']}, Confidence: {recognition['confidence']})")

if __name__ == "__main__":
    asyncio.run(test_ml_service())
