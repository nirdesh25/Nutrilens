from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class ScanResultResponse(BaseModel):
    id: int
    user_id: int
    food_name: str
    freshness_status: str
    risk_score: float
    recommendation: Optional[str]
    nutrition: Optional[Dict[str, Any]] = None
    health_analysis: Optional[Dict[str, Any]] = None
    image_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class FreshnessPrediction(BaseModel):
    food_name: str
    freshness_status: str
    risk_score: float
    recommendation: str
    confidence: float
    nutrition: Optional[Dict[str, Any]] = None
    health_analysis: Optional[Dict[str, Any]] = None
