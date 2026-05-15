from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GroceryBase(BaseModel):
    food_name: str
    category: Optional[str] = None
    quantity: float = 1.0
    freshness_status: str = "unknown"
    image_url: Optional[str] = None

class GroceryCreate(GroceryBase):
    pass

class GroceryUpdate(BaseModel):
    food_name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    freshness_status: Optional[str] = None
    image_url: Optional[str] = None

class GroceryResponse(GroceryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
