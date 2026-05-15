from pydantic import BaseModel
from datetime import datetime

class WasteLogCreate(BaseModel):
    food_name: str
    action: str
    co2_saved: float = 0.0

class WasteLogResponse(BaseModel):
    id: int
    user_id: int
    food_name: str
    action: str
    co2_saved: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class WasteDecision(BaseModel):
    action: str
    reason: str
    co2_impact: float
