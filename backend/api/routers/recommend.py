from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from ..services.recommender import recommend as rec_impl
import sys
import math
from pathlib import Path

router = APIRouter(prefix="/recommend", tags=["Recommend"])


def sanitize_json_float(obj: Any) -> Any:
    """
    Recursively sanitize float values in dictionaries/lists to replace
    inf, -inf, and nan with None (which is JSON-compliant).
    
    This prevents "ValueError: Out of range float values are not JSON compliant"
    errors when serializing FastAPI responses.
    
    Also handles numpy float types that might be returned from Neo4j queries.
    """
    if isinstance(obj, dict):
        return {key: sanitize_json_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json_float(item) for item in obj]
    elif isinstance(obj, float) or (hasattr(obj, '__float__') and not isinstance(obj, (int, bool, str))):
        try:
            # Convert to Python float (handles numpy types)
            float_val = float(obj)
            if math.isnan(float_val) or math.isinf(float_val):
                return None
            return float_val
        except (ValueError, TypeError, OverflowError):
            # If conversion fails, return as-is (will likely fail JSON serialization anyway)
            return obj
    return obj


@router.get("/test-import", summary="Test GraphHybridRecommender import status")
async def test_import():
    """
    Test endpoint to check if GraphHybridRecommender can be imported.
    Useful for debugging why fallback query is being used.
    """
    from ..services import recommender as recommender_module
    
    backend_dir = Path(__file__).parent.parent.parent
    result = {
        "backend_dir": str(backend_dir),
        "scripts_path": str(backend_dir / "scripts"),
        "recommend_graph_exists": (backend_dir / "scripts" / "recommend_graph.py").exists(),
        "import_success": False,
        "import_error": None,
        "class_available": False
    }
    
    # Check module-level import status
    if hasattr(recommender_module, '_import_error'):
        result["module_import_error"] = recommender_module._import_error
    
    if hasattr(recommender_module, '_recommender_class'):
        result["class_available"] = recommender_module._recommender_class is not None
        result["import_success"] = recommender_module._recommender_class is not None
    
    # Try to import directly
    try:
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        
        from scripts.recommend_graph import GraphHybridRecommender
        result["import_success"] = True
        result["class_available"] = GraphHybridRecommender is not None
        result["class_name"] = GraphHybridRecommender.__name__ if GraphHybridRecommender else None
    except Exception as e:
        result["import_error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result


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
        print(f"🔍 Recommendation request received:", flush=True)
        print(f"  - user_id: {req.user_id}", flush=True)
        print(f"  - ingredient_ids: {req.ingredient_ids} (count: {len(req.ingredient_ids) if req.ingredient_ids else 0})", flush=True)
        print(f"  - ingredient_names: {req.ingredient_names} (count: {len(req.ingredient_names) if req.ingredient_names else 0})", flush=True)
        print(f"  - max_cook_time: {req.max_cook_time}", flush=True)
        print(f"  - limit: {req.limit}", flush=True)
        print(f"  - min_match_ratio: {req.min_match_ratio}", flush=True)
        print(f"  - preferred_cuisines (original): {req.preferred_cuisines}", flush=True)
        print(f"  - preferred_cuisines (normalized): {normalized_preferred_cuisines}", flush=True)
        print(f"  - recipe_category: {req.recipe_category}", flush=True)
        
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
        
        print(f"✅ Recommendation results: {len(results)} recipes found", flush=True)
        if not results or len(results) == 0:
            print(f"⚠️ No recipes found - returning empty array", flush=True)
        else:
            # Log first few recipe titles to see what we're returning
            first_few = results[:3] if len(results) >= 3 else results
            titles = [r.get('title', 'N/A') for r in first_few]
            match_percents = [r.get('match_percent', 'N/A') for r in first_few]
            print(f"📋 First {len(titles)} recipes: {titles}", flush=True)
            print(f"📊 Match percents: {match_percents}", flush=True)
            # Log full details of first recipe for debugging
            if len(results) > 0:
                first_recipe = results[0]
                print(f"🔍 First recipe details:", flush=True)
                print(f"  - recipe_id: {first_recipe.get('recipe_id')}", flush=True)
                print(f"  - title: {first_recipe.get('title')}", flush=True)
                print(f"  - match_percent: {first_recipe.get('match_percent')}", flush=True)
                print(f"  - cuisine: {first_recipe.get('cuisine')}", flush=True)
                print(f"  - matched_ing: {first_recipe.get('matched_ing', [])}", flush=True)
                print(f"  - missing_ing: {first_recipe.get('missing_ing', [])}", flush=True)
        # Sanitize results to remove inf/nan float values before JSON serialization
        sanitized_results = sanitize_json_float(results or [])
        return {"results": sanitized_results, "total": len(sanitized_results)}
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
    # Sanitize results to remove inf/nan float values before JSON serialization
    sanitized_results = sanitize_json_float(results)
    return {"results": sanitized_results, "total": len(sanitized_results)}