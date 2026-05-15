from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Grocery
from app.schemas import GroceryCreate, GroceryUpdate, GroceryResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/groceries", tags=["Grocery Manager"])

@router.post("/", response_model=GroceryResponse, status_code=status.HTTP_201_CREATED)
async def create_grocery(
    grocery: GroceryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new grocery item."""
    
    db_grocery = Grocery(
        user_id=current_user.id,
        **grocery.dict()
    )
    
    db.add(db_grocery)
    db.commit()
    db.refresh(db_grocery)
    
    return db_grocery

@router.get("/", response_model=List[GroceryResponse])
async def get_groceries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all groceries for current user."""
    
    groceries = db.query(Grocery).filter(
        Grocery.user_id == current_user.id
    ).order_by(Grocery.created_at.desc()).all()
    
    return groceries

@router.get("/{grocery_id}", response_model=GroceryResponse)
async def get_grocery(
    grocery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific grocery item."""
    
    grocery = db.query(Grocery).filter(
        Grocery.id == grocery_id,
        Grocery.user_id == current_user.id
    ).first()
    
    if not grocery:
        raise HTTPException(status_code=404, detail="Grocery not found")
    
    return grocery

@router.put("/{grocery_id}", response_model=GroceryResponse)
async def update_grocery(
    grocery_id: int,
    grocery_update: GroceryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a grocery item."""
    
    grocery = db.query(Grocery).filter(
        Grocery.id == grocery_id,
        Grocery.user_id == current_user.id
    ).first()
    
    if not grocery:
        raise HTTPException(status_code=404, detail="Grocery not found")
    
    # Update fields
    update_data = grocery_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grocery, field, value)
    
    db.commit()
    db.refresh(grocery)
    
    return grocery

@router.delete("/{grocery_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grocery(
    grocery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a grocery item."""
    
    grocery = db.query(Grocery).filter(
        Grocery.id == grocery_id,
        Grocery.user_id == current_user.id
    ).first()
    
    if not grocery:
        raise HTTPException(status_code=404, detail="Grocery not found")
    
    db.delete(grocery)
    db.commit()
    
    return None
