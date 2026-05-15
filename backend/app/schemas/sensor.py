from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SensorDataCreate(BaseModel):
    device_id: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    gas_level: Optional[float] = None
    light_level: Optional[float] = None
    status: str = "normal"

class SensorDataResponse(BaseModel):
    id: int
    user_id: int
    device_id: Optional[str]
    temperature: Optional[float]
    humidity: Optional[float]
    gas_level: Optional[float]
    light_level: Optional[float]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MilkQualityRequest(BaseModel):
    ph: float
    temperature: float
    taste: int
    odor: int
    fat: int
    turbidity: int
    color: int

class MilkAnalysisResponse(BaseModel):
    id: int
    user_id: int
    ph: float
    temperature: float
    taste: int
    odor: int
    fat: int
    turbidity: int
    color: int
    prediction: str
    risk_score: float
    created_at: datetime

    class Config:
        from_attributes = True
