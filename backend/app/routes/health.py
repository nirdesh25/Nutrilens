from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, HealthProfile
from app.schemas import HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse
from app.utils.auth import get_current_user
from app.services import health_service

router = APIRouter(prefix="/api/health", tags=["Health Profile"])

@router.post("/profile", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_health_profile(
    profile: HealthProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update health profile."""
    
    # Check if profile already exists
    existing_profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Health profile already exists. Use PUT to update."
        )
    
    db_profile = HealthProfile(
        user_id=current_user.id,
        **profile.dict()
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@router.get("/profile", response_model=HealthProfileResponse)
async def get_health_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's health profile."""
    
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    return profile

@router.put("/profile", response_model=HealthProfileResponse)
async def update_health_profile(
    profile_update: HealthProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update health profile."""
    
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not found")
    
    # Update fields
    for field, value in profile_update.dict().items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile

@router.get("/recommendations")
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized food recommendations based on health profile.
    
    Dataset: USDA FoodData Central, Glycemic Index Dataset
    """
    
    recommendations = health_service.get_recommendations(current_user.id, db)
    
    return recommendations
