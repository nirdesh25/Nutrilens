from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.utils.auth import get_current_user
from app.services.nutrition_service import NutritionService

router = APIRouter(prefix="/api/nutrition", tags=["Nutrition Lookup"])


@router.get("/search")
async def search_foods(
    q: str = Query(..., min_length=1, description="Food name to search for"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """
    Search the nutrition database by food name.
    Returns partial matches ordered by name.
    Dataset: nutrition.db built from USDA/Indian food data.
    """
    results = NutritionService.search_foods(q, limit)
    return {"query": q, "count": len(results), "results": results}


@router.get("/food/{food_name}")
async def get_food_nutrition(
    food_name: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get full nutritional breakdown for a specific food.
    Returns calories, protein, fat, carbs, fiber, sugar, sodium, GI index.
    """
    data = NutritionService.get_food_nutrition(food_name)
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No nutrition data found for '{food_name}'. Try a different spelling."
        )
    return data


@router.get("/all")
async def list_all_foods(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    """List all foods in the nutrition database."""
    results = NutritionService.search_foods("", limit)
    return {"count": len(results), "results": results}
