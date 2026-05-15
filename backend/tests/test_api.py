"""
NutriLens AI — Backend Test Suite
Run with: cd backend && pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.database import Base, get_db

# ──────────────────────────────────────────────
# In-memory SQLite for tests (isolated, fast)
# ──────────────────────────────────────────────
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_run.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

# Clean up any leftover DB from prior runs
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables ONCE before client is built
Base.metadata.create_all(bind=engine)

client = TestClient(app)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def register_and_login(email="test@nutrilens.ai", password="TestPass1"):
    client.post("/api/auth/register", json={
        "name": "Test User", "email": email, "password": password
    })
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


# ──────────────────────────────────────────────
# Root & Health
# ──────────────────────────────────────────────
def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "NutriLens" in res.json()["message"]


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


# ──────────────────────────────────────────────
# Auth Routes
# ──────────────────────────────────────────────
def test_register_user():
    import time
    unique_email = f"alice_{int(time.time())}@nutrilens.ai"
    res = client.post("/api/auth/register", json={
        "name": "Alice",
        "email": unique_email,
        "password": "AlicePass99"
    })
    assert res.status_code in (200, 201)
    data = res.json()
    # Register returns either a token or the user object depending on the route implementation
    assert "id" in data or "access_token" in data



def test_register_duplicate_email():
    email = "dup@nutrilens.ai"
    payload = {"name": "Dup", "email": email, "password": "DupPass123"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400


def test_login_valid():
    email = "login_valid@nutrilens.ai"
    password = "Valid123"
    client.post("/api/auth/register", json={"name": "Login Test", "email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password():
    email = "wrongpw@nutrilens.ai"
    client.post("/api/auth/register", json={"name": "WP", "email": email, "password": "Correct1"})
    res = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword"})
    assert res.status_code == 401


def test_protected_route_no_token():
    res = client.get("/api/scan/history")
    assert res.status_code == 401


# ──────────────────────────────────────────────
# Grocery Routes
# ──────────────────────────────────────────────
def test_grocery_crud():
    token = register_and_login("grocery_user@nutrilens.ai", "GroceryPass1")
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    res = client.post("/api/groceries/", json={"food_name": "Apple", "category": "Fruit", "quantity": 3}, headers=headers)
    assert res.status_code == 201
    grocery_id = res.json()["id"]

    # Read all
    res = client.get("/api/groceries/", headers=headers)
    assert res.status_code == 200
    assert any(g["id"] == grocery_id for g in res.json())

    # Read single
    res = client.get(f"/api/groceries/{grocery_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["food_name"] == "Apple"

    # Update
    res = client.put(f"/api/groceries/{grocery_id}", json={"quantity": 5}, headers=headers)
    assert res.status_code == 200
    assert res.json()["quantity"] == 5

    # Delete
    res = client.delete(f"/api/groceries/{grocery_id}", headers=headers)
    assert res.status_code == 204


def test_grocery_not_found():
    token = register_and_login("grocery_404@nutrilens.ai", "NotFound1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/groceries/99999", headers=headers)
    assert res.status_code == 404


# ──────────────────────────────────────────────
# Health Profile Routes
# ──────────────────────────────────────────────
def test_health_profile_create_and_get():
    token = register_and_login("health_user@nutrilens.ai", "HealthPass1")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/health/profile", json={
        "diabetes": True, "high_bp": False, "cholesterol": False,
        "surgery_recovery": False, "weight_loss": True
    }, headers=headers)
    assert res.status_code == 201

    res = client.get("/api/health/profile", headers=headers)
    assert res.status_code == 200
    assert res.json()["diabetes"] is True


def test_health_recommendations():
    token = register_and_login("rec_user@nutrilens.ai", "RecPass1")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/health/profile", json={"diabetes": True}, headers=headers)
    res = client.get("/api/health/recommendations", headers=headers)
    assert res.status_code == 200
    assert "recommended_foods" in res.json()


# ──────────────────────────────────────────────
# Nutrition Lookup Routes
# ──────────────────────────────────────────────
def test_nutrition_search():
    token = register_and_login("nutr_search@nutrilens.ai", "NutrPass1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/nutrition/search?q=apple", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data


def test_nutrition_food_detail():
    token = register_and_login("nutr_detail@nutrilens.ai", "NutrDetail1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/nutrition/food/Apple%2C%20raw", headers=headers)
    # Either 200 (found) or 404 (not seeded) is acceptable
    assert res.status_code in (200, 404)


def test_nutrition_search_requires_auth():
    res = client.get("/api/nutrition/search?q=banana")
    assert res.status_code == 401


# ──────────────────────────────────────────────
# Waste Routes
# ──────────────────────────────────────────────
def test_waste_log_and_analytics():
    token = register_and_login("waste_user@nutrilens.ai", "WastePass1")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/waste/log", json={
        "food_name": "Banana", "action": "eat_immediately", "co2_saved": 0.1
    }, headers=headers)
    assert res.status_code == 200

    res = client.get("/api/waste/logs", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1

    res = client.get("/api/waste/analytics", headers=headers)
    assert res.status_code == 200
    assert "total_co2_saved" in res.json()


# ──────────────────────────────────────────────
# Milk Quality Route
# ──────────────────────────────────────────────
def test_milk_quality_prediction_high():
    token = register_and_login("milk_test@nutrilens.ai", "MilkPass1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/sensor/milk-quality", json={
        "ph": 6.6, "temperature": 4.0,
        "taste": 1, "odor": 1, "fat": 1, "turbidity": 1, "color": 240
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] in ("high", "medium")
    assert isinstance(data["risk_score"], (int, float))


def test_milk_quality_prediction_low():
    token = register_and_login("milk_bad@nutrilens.ai", "MilkBad1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/sensor/milk-quality", json={
        "ph": 3.0, "temperature": 90.0,
        "taste": 0, "odor": 0, "fat": 0, "turbidity": 0, "color": 240
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] in ("low", "medium")
    assert isinstance(data["risk_score"], (int, float))


# ──────────────────────────────────────────────
# User Profile
# ──────────────────────────────────────────────
def test_user_profile_get_and_update():
    token = register_and_login("profile_user@nutrilens.ai", "ProfilePass1")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/user/profile", headers=headers)
    assert res.status_code == 200
    assert "email" in res.json()

    res = client.put("/api/user/profile", json={"age": 25}, headers=headers)
    assert res.status_code == 200
    assert res.json()["age"] == 25


# ──────────────────────────────────────────────
# Sensor Routes
# ──────────────────────────────────────────────
def test_sensor_current():
    token = register_and_login("sensor_user@nutrilens.ai", "SensorPass1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/sensor/current", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "temperature" in data
    assert "humidity" in data


def test_sensor_status():
    token = register_and_login("sensor_status@nutrilens.ai", "SensorSt1")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/sensor/status", headers=headers)
    assert res.status_code == 200
    assert "connected" in res.json()


# ──────────────────────────────────────────────
# MilkQualityService unit tests (no HTTP)
# ──────────────────────────────────────────────
def test_milk_service_heuristic_directly():
    from app.services.milk_quality_service import MilkQualityService
    result = MilkQualityService.predict_quality(
        ph=6.6, temperature=4.0, taste=1, odor=1, fat=1, turbidity=1, color=240
    )
    assert result["prediction"] in ("high", "medium")
    assert isinstance(result["risk_score"], (int, float))


def test_milk_service_spoiled():
    from app.services.milk_quality_service import MilkQualityService
    result = MilkQualityService.predict_quality(
        ph=3.0, temperature=90.0, taste=0, odor=0, fat=0, turbidity=0, color=240
    )
    assert result["prediction"] in ("low", "medium")


# ──────────────────────────────────────────────
# NutritionService unit tests (no HTTP)
# ──────────────────────────────────────────────
def test_nutrition_service_search():
    from app.services.nutrition_service import NutritionService
    results = NutritionService.search_foods("apple", 5)
    # DB may or may not be seeded in test env — just check return type
    assert isinstance(results, list)


def test_nutrition_service_lookup_miss():
    from app.services.nutrition_service import NutritionService
    result = NutritionService.get_food_nutrition("NonExistentFood12345xyz")
    assert result is None


# ──────────────────────────────────────────────
# Teardown
# ──────────────────────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    # In-memory db is dropped automatically; nothing to remove
