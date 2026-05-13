from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MilkAnalysisBase(BaseModel):
    ph: float
    temperature: float
    taste: int
    odor: int
    fat: int
    turbidity: int
    color: int

class MilkAnalysisCreate(MilkAnalysisBase):
    pass

class MilkAnalysisResponse(MilkAnalysisBase):
    id: int
    user_id: int
    prediction: str
    risk_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True
