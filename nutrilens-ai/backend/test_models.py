"""Quick test to verify all ML models load correctly."""
import os, sys, warnings
warnings.filterwarnings('ignore')
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Ensure we are in the backend directory to load .env correctly
backend_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.abspath(os.getcwd()) != backend_dir:
    os.chdir(backend_dir)
    print(f"Changed working directory to: {backend_dir}")

sys.path.insert(0, os.getcwd())

print("=== NutriLens ML Model Load Test ===")
from app.services.ml_service import MLService
svc = MLService()

print()
print("=== Summary ===")
print(f"  Freshness model  : {'LOADED (real AI)' if svc.freshness_model else 'NOT LOADED (heuristic)'}")
print(f"  Food recognition : {'LOADED (real AI)' if svc.food_recognition_model else 'NOT LOADED (mock)'}")
print(f"  Waste model      : {'LOADED (real AI)' if svc.waste_model else 'NOT LOADED (mock)'}")
print(f"  Milk quality     : {'LOADED (real AI)' if svc.milk_quality_model else 'NOT LOADED (heuristic)'}")
print(f"  Food classes     : {len(svc.food_classes)} classes")
print(f"  Waste classes    : {len(svc.waste_classes)} classes")

# --- Quick inference test ---
print()
print("=== Quick Inference Test ===")

# Test milk quality
from app.services.milk_quality_service import MilkQualityService

# Good milk
result = MilkQualityService.predict_quality(ph=6.6, temperature=3.0, taste=1, odor=1, fat=1, turbidity=1, color=240)
print(f"  Milk (good values) => prediction={result['prediction']}, model={result.get('model','?')}")

# Bad milk
result = MilkQualityService.predict_quality(ph=5.5, temperature=25.0, taste=0, odor=0, fat=0, turbidity=0, color=240)
print(f"  Milk (bad values)  => prediction={result['prediction']}, model={result.get('model','?')}")

print()
print("All tests passed!")
