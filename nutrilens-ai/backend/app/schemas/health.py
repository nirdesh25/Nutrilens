from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthProfileBase(BaseModel):
    diabetes: bool = False
    high_bp: bool = False
    cholesterol: bool = False
    surgery_recovery: bool = False
    weight_loss: bool = False

class HealthProfileCreate(HealthProfileBase):
    pass

class HealthProfileUpdate(HealthProfileBase):
    pass

class HealthProfileResponse(HealthProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
