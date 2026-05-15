from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"
    
    FRESHNESS_MODEL_PATH: str = "ml_models/freshness_model.keras"
    FOOD_RECOGNITION_MODEL_PATH: str = "ml_models/food_recognition_model.h5"
    WASTE_MODEL_PATH: str = "ml_models/waste_model.keras"
    MILK_QUALITY_MODEL_PATH: str = "ml_models/milk_quality_model.pkl"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
