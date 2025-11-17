from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..db import get_session

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.get("/")
async def list_ingredients(limit: int = Query(100, ge=1, le=200)):
    q = """
    MATCH (i:Ingredient)
    RETURN i.ingredient_id AS id, coalesce(i.canonical_name, i.name) AS name
    ORDER BY name
    LIMIT $limit
    """
    with get_session() as s:
        return {"ingredients": [dict(r) for r in s.run(q, limit=limit)]}

@router.get("/{ingredient_id}")
async def get_ingredient(ingredient_id: str):
    q = """
    MATCH (i:Ingredient {ingredient_id:$id})
    RETURN i.ingredient_id AS ingredient_id, coalesce(i.canonical_name, i.name) AS canonical_name,
           i.name AS name, i.category AS category, i.allergen AS allergen,
           i.alternative_names AS alternative_names, i.description AS description,
           i.nutrition_info AS nutrition_info
    """
    with get_session() as s:
        rec = s.run(q, id=ingredient_id).single()
        if not rec:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        return dict(rec)