from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from ..services.recommender import recommend as rec_impl


router = APIRouter(prefix="/recommend", tags=["Recommend"])


class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    ingredient_ids: Optional[List[str]] = None
    ingredient_names: Optional[List[str]] = None
    max_cook_time: Optional[int] = None
    recipe_category: Optional[str] = None
    preferred_cuisines: Optional[List[str]] = None
    limit: int = 20
    min_match_ratio: float = 0.3


@router.post("/", summary="Get recipe recommendations")
async def post_recommend(req: RecommendRequest):
    """
    Get recipe recommendations using GraphHybridRecommender.
    
    Supports all parameters from recommend_graph.py:
    - user_id: User ID for personalized recommendations
    - ingredient_ids: List of ingredient IDs
    - ingredient_names: List of ingredient names (will be mapped to IDs)
    - max_cook_time: Maximum cooking time in minutes
    - recipe_category: Filter by recipe category/meal type (use 'no preference'/'none'/'all' for no filter)
    - preferred_cuisines: List of preferred cuisines for priority ranking (use "All" for no preference)
    - limit: Maximum number of results
    - min_match_ratio: Minimum Jaccard match ratio (default: 0.3)
    """
    try:
        # Normalize preferred_cuisines: "All" = None (no preference)
        normalized_preferred_cuisines = req.preferred_cuisines
        if normalized_preferred_cuisines:
            # Check if "All" is in the list (case-insensitive)
            if any(c.strip().lower() == "all" for c in normalized_preferred_cuisines):
                normalized_preferred_cuisines = None  # No preference
        
        # Log request for debugging
        print(f"🔍 Recommendation request received:")
        print(f"  - user_id: {req.user_id}")
        print(f"  - ingredient_ids: {req.ingredient_ids} (count: {len(req.ingredient_ids) if req.ingredient_ids else 0})")
        print(f"  - ingredient_names: {req.ingredient_names} (count: {len(req.ingredient_names) if req.ingredient_names else 0})")
        print(f"  - max_cook_time: {req.max_cook_time}")
        print(f"  - limit: {req.limit}")
        print(f"  - min_match_ratio: {req.min_match_ratio}")
        print(f"  - preferred_cuisines (original): {req.preferred_cuisines}")
        print(f"  - preferred_cuisines (normalized): {normalized_preferred_cuisines}")
        
        results = rec_impl(
            user_id=req.user_id,
            ingredient_ids=req.ingredient_ids,
            ingredient_names=req.ingredient_names,
            limit=req.limit,
            max_cook_time=req.max_cook_time,
            recipe_category=req.recipe_category,
            preferred_cuisines=normalized_preferred_cuisines,
            min_match_ratio=req.min_match_ratio
        )
        
        print(f"✅ Recommendation results: {len(results)} recipes found")
        return {"results": results, "total": len(results)}
    except Exception as e:
        print(f"❌ Recommendation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="GET variant for quick testing")
async def get_recommend(
    user_id: Optional[str] = Query(None, description="User ID for personalized recommendations"),
    ingredient_ids: Optional[str] = Query(None, description="Comma-separated ingredient IDs"),
    ingredient_names: Optional[str] = Query(None, description="Comma-separated ingredient names (will be mapped to IDs)"),
    max_cook_time: Optional[int] = Query(None, description="Maximum cooking time in minutes"),
    recipe_category: Optional[str] = Query(None, description="Filter by recipe category (use 'no preference'/'none'/'all' for no filter)"),
    preferred_cuisines: Optional[str] = Query(None, description="Comma-separated preferred cuisines (e.g., 'Korean,Vietnamese,American' or 'All' for no preference)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    min_match_ratio: float = Query(0.3, ge=0.0, le=1.0, description="Minimum Jaccard match ratio (default: 0.3)"),
):
    """
    GET variant for quick testing.
    
    Supports all parameters from recommend_graph.py.
    """
    ing_list = [x.strip() for x in ingredient_ids.split(",")] if ingredient_ids else None
    ing_names_list = [x.strip() for x in ingredient_names.split(",")] if ingredient_names else None
    preferred_cuisines_list = [x.strip() for x in preferred_cuisines.split(",")] if preferred_cuisines else None
    
    # Normalize preferred_cuisines: "All" = None (no preference)
    normalized_preferred_cuisines = preferred_cuisines_list
    if normalized_preferred_cuisines:
        # Check if "All" is in the list (case-insensitive)
        if any(c.strip().lower() == "all" for c in normalized_preferred_cuisines):
            normalized_preferred_cuisines = None  # No preference
    
    results = rec_impl(
        user_id=user_id,
        ingredient_ids=ing_list,
        ingredient_names=ing_names_list,
        limit=limit,
        max_cook_time=max_cook_time,
        recipe_category=recipe_category,
        preferred_cuisines=normalized_preferred_cuisines,
        min_match_ratio=min_match_ratio
    )
    return {"results": results, "total": len(results)}