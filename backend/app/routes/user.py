from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, ScanResult, WasteLog
from app.schemas import UserResponse
from app.utils.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/user", tags=["User"])

class UserUpdateRequest(BaseModel):
    age: Optional[int] = None

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    
    # Update age if provided
    if update_data.age is not None:
        if update_data.age < 0 or update_data.age > 150:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age must be between 0 and 150"
            )
        current_user.age = update_data.age
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated stats for the dashboard (scan count, CO2 saved, waste reduction)."""

    total_scans = db.query(func.count(ScanResult.id)).filter(
        ScanResult.user_id == current_user.id
    ).scalar() or 0

    total_co2 = db.query(func.sum(WasteLog.co2_saved)).filter(
        WasteLog.user_id == current_user.id
    ).scalar() or 0.0

    total_waste_actions = db.query(func.count(WasteLog.id)).filter(
        WasteLog.user_id == current_user.id
    ).scalar() or 0

    # Waste reduction % - actions taken vs total scans (0-100%)
    waste_reduction_pct = 0
    if total_scans > 0:
        waste_reduction_pct = min(100, round((total_waste_actions / total_scans) * 100))

    return {
        "total_scans": total_scans,
        "co2_saved": round(float(total_co2), 2),
        "waste_reduction_pct": waste_reduction_pct,
    }
