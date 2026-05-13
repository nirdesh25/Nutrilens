from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ScanResult
from app.schemas import ScanResultResponse, FreshnessPrediction
from app.utils.auth import get_current_user
from app.services import ml_service, waste_service

router = APIRouter(prefix="/api/scan", tags=["Food Scanner"])

@router.post("/predict", response_model=FreshnessPrediction)
async def predict_freshness(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict food freshness from uploaded image.
    
    Dataset: Fruits Fresh & Rotten Dataset
    Model: CNN for freshness classification
    """
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Predict freshness using unified ML logic (Recognition + Freshness)
    prediction = await ml_service.predict_unified(image_bytes)
    
    # Enrich with Nutrition Data
    from app.services.nutrition_service import NutritionService
    from app.services.health_service import health_service
    
    food_name = prediction['food_name']
    prediction['nutrition'] = NutritionService.get_food_nutrition(food_name)
    
    # Enrich with Health Recommendations
    prediction['health_analysis'] = health_service.analyze_food_for_user(
        food_name, current_user.id, db
    )
    
    # Save scan result to database (note: db schema hasn't changed, 
    # but we can return the enriched data in the response)
    scan_result = ScanResult(
        user_id=current_user.id,
        food_name=food_name,
        freshness_status=prediction['freshness_status'],
        risk_score=prediction['risk_score'],
        recommendation=prediction['recommendation']
    )
    
    db.add(scan_result)
    db.commit()
    
    return prediction

@router.get("/history", response_model=list[ScanResultResponse])
async def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's scan history."""
    
    scans = db.query(ScanResult).filter(
        ScanResult.user_id == current_user.id
    ).order_by(ScanResult.created_at.desc()).limit(50).all()
    
    return scans

@router.get("/waste-decision/{scan_id}")
async def get_waste_decision(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get waste decision recommendation for a scan result."""
    
    scan = db.query(ScanResult).filter(
        ScanResult.id == scan_id,
        ScanResult.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan result not found")
    
    decision = waste_service.get_waste_decision(
        scan.food_name,
        scan.freshness_status,
        scan.risk_score
    )
    
    return decision
