from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.services import ph_service

router = APIRouter(prefix="/api/ph", tags=["pH Analysis"])

@router.post("/analyze")
async def analyze_ph_strip(
    file: UploadFile = File(...),
    food_type: str = Form("default"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze pH strip image to determine food spoilage.
    
    Dataset: Custom pH strip images (to be collected)
    Model: Color detection + pH mapping
    
    Args:
        file: pH strip image
        food_type: Type of food (milk, juice, meat, default)
    """
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Analyze pH strip
    result = await ph_service.analyze_ph_strip(image_bytes, food_type)
    
    return result

@router.get("/food-types")
async def get_supported_food_types():
    """Get list of supported food types for pH analysis."""
    
    return {
        'food_types': [
            {'value': 'milk', 'label': 'Milk', 'safe_range': '6.4 - 6.8'},
            {'value': 'juice', 'label': 'Juice', 'safe_range': '3.0 - 4.5'},
            {'value': 'meat', 'label': 'Meat', 'safe_range': '5.4 - 6.2'},
            {'value': 'default', 'label': 'Other', 'safe_range': '6.0 - 7.0'}
        ]
    }
