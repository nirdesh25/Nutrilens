import sys
import os
import asyncio
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

async def test_fallback():
    from app.services.ml_service import MLService
    
    service = MLService()
    # Force models to None to test fallback
    service.freshness_model = None
    service.food_recognition_model = None
    
    # Create a red box (Tomato)
    red_box = Image.new('RGB', (224, 224), color=(255, 0, 0))
    img_byte_arr = io.BytesIO()
    red_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Red Image (Fallback) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Category: {recognition['category']})")
    
    # Create a purple box (Brinjal)
    purple_box = Image.new('RGB', (224, 224), color=(48, 25, 52))
    img_byte_arr = io.BytesIO()
    purple_box.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    print("\n--- Testing Purple Image (Fallback) ---")
    recognition = await service.recognize_food(image_bytes)
    print(f"Recognized: {recognition['food_name']} (Category: {recognition['category']})")

if __name__ == "__main__":
    asyncio.run(test_fallback())
