from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, WasteLog
from app.schemas import WasteLogCreate, WasteLogResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/waste", tags=["Waste Management"])

@router.post("/log", response_model=WasteLogResponse)
async def log_waste_action(
    waste_log: WasteLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a waste action."""
    
    db_waste_log = WasteLog(
        user_id=current_user.id,
        **waste_log.dict()
    )
    
    db.add(db_waste_log)
    db.commit()
    db.refresh(db_waste_log)
    
    return db_waste_log

@router.get("/logs", response_model=list[WasteLogResponse])
async def get_waste_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's waste logs."""
    
    logs = db.query(WasteLog).filter(
        WasteLog.user_id == current_user.id
    ).order_by(WasteLog.created_at.desc()).limit(100).all()
    
    return logs

@router.get("/analytics")
async def get_waste_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get waste analytics and statistics."""
    
    # Total CO2 saved
    total_co2 = db.query(func.sum(WasteLog.co2_saved)).filter(
        WasteLog.user_id == current_user.id
    ).scalar() or 0.0
    
    # Total waste actions
    total_actions = db.query(func.count(WasteLog.id)).filter(
        WasteLog.user_id == current_user.id
    ).scalar() or 0
    
    # Actions by type
    actions_by_type = db.query(
        WasteLog.action,
        func.count(WasteLog.id).label('count')
    ).filter(
        WasteLog.user_id == current_user.id
    ).group_by(WasteLog.action).all()
    
    # Most wasted foods
    most_wasted = db.query(
        WasteLog.food_name,
        func.count(WasteLog.id).label('count')
    ).filter(
        WasteLog.user_id == current_user.id
    ).group_by(WasteLog.food_name).order_by(func.count(WasteLog.id).desc()).limit(10).all()
    
    # Last 30 days trend
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_logs = db.query(WasteLog).filter(
        WasteLog.user_id == current_user.id,
        WasteLog.created_at >= thirty_days_ago
    ).all()
    
    return {
        'total_co2_saved': round(total_co2, 2),
        'total_actions': total_actions,
        'actions_by_type': [{'action': action, 'count': count} for action, count in actions_by_type],
        'most_wasted_foods': [{'food': food, 'count': count} for food, count in most_wasted],
        'recent_activity_count': len(recent_logs)
    }
